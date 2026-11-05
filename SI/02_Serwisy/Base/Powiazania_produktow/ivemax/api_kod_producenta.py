"""Wysyłka kodów producenta do IdoSell przez REST Admin API (PUT products/sizes).

Źródło: aktualizacja_kod_producenta.csv + kod_producenta_raport.csv (nazwy, do reguły
zamienników). Przed zapisem czyta stan sklepu na żywo i pomija towary, które mają już
kod producenta, oraz kody zajęte przez inny towar. Najpierw próba na 3 towarach
z odczytem kontrolnym, potem reszta paczkami po 100. Decyzje: ANALIZA_api_aktualizacja_idosell.md.

Uruchomienie: run_api_kod_producenta.bat (pyta o potwierdzenie). Skrót: --bez-pytania.
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

PLIK_KONFIGURACJI = "config.json"
PLIK_AKTUALIZACJI = "aktualizacja_kod_producenta.csv"
PLIK_RAPORTU = "kod_producenta_raport.csv"
FOLDER_WYNIKOW = "wyniki"

ROZMIAR_PACZKI = 100
LICZBA_PROBNYCH = 3
PROBY_PONOWIEN = 5
SLOWO_ZAMIENNIK = "zamiennik"

STATUS_ZAPISANO = "zapisano"
STATUS_BLAD = "błąd"
STATUS_MA_KOD = "pominięto - towar ma już kod"
STATUS_KOD_ZAJETY = "pominięto - kod zajęty w sklepie"
STATUS_DUPLIKAT = "pominięto - duplikat kodu (decyzja klienta)"
STATUS_ZAMIENNIK = "pominięto - zamiennik z kodem oryginału"
STATUS_BRAK_TOWARU = "pominięto - brak towaru w sklepie"


def skroc(obiekt, limit: int = 300):
    """Kopia obiektu do dziennika z obciętymi długimi tekstami (np. zdjęcia w base64)."""
    if isinstance(obiekt, dict):
        return {k: skroc(v, limit) for k, v in obiekt.items()}
    if isinstance(obiekt, list):
        return [skroc(v, limit) for v in obiekt]
    if isinstance(obiekt, str) and len(obiekt) > limit:
        return obiekt[:limit] + f"…[{len(obiekt)} znaków]"
    return obiekt


class KlientApi:
    """Minimalny klient REST Admin API v8 (stdlib), z ponawianiem przy 429/5xx."""

    def __init__(self, domena: str, klucz: str, dziennik) -> None:
        self.baza = f"https://{domena}/api/admin/v8/"
        self.klucz = klucz
        self.dziennik = dziennik

    def zapytanie(self, metoda: str, sciezka: str, dane: Optional[dict] = None) -> dict:
        """Wysyła żądanie i zwraca JSON odpowiedzi; zapisuje parę żądanie/odpowiedź w dzienniku."""
        tresc = json.dumps(dane).encode("utf-8") if dane is not None else None
        for proba in range(1, PROBY_PONOWIEN + 1):
            zadanie = urllib.request.Request(
                self.baza + sciezka,
                data=tresc,
                method=metoda,
                headers={
                    "X-API-KEY": self.klucz,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(zadanie, timeout=120) as odp:
                    wynik = json.load(odp)
                    kod_http = odp.status
            except urllib.error.HTTPError as blad:
                kod_http = blad.code
                surowe = blad.read().decode("utf-8", "replace")
                if kod_http in (429, 500, 502, 503, 504) and proba < PROBY_PONOWIEN:
                    time.sleep(2 * proba)
                    continue
                try:
                    wynik = json.loads(surowe)
                except ValueError:
                    wynik = {"blad_http": kod_http, "tresc": surowe[:2000]}
            except (urllib.error.URLError, TimeoutError) as blad:
                # POST nie jest idempotentny: po przekroczeniu czasu serwer mógł już utworzyć
                # towar, a ponowienie tworzy duplikat (tak powstały dublety 2026-10-21).
                if proba < PROBY_PONOWIEN and metoda != "POST":
                    time.sleep(2 * proba)
                    continue
                raise
            if metoda != "GET":
                self.dziennik.write(
                    json.dumps(
                        {"czas": datetime.now().isoformat(timespec="seconds"), "metoda": metoda,
                         "sciezka": sciezka, "http": kod_http, "zadanie": skroc(dane),
                         "odpowiedz": wynik},
                        ensure_ascii=False,
                    ) + "\n"
                )
                self.dziennik.flush()
            return wynik
        return {}


def stan_sklepu(api: KlientApi) -> Dict[int, Dict[str, str]]:
    """Czyta wszystkie rozmiary sklepu: productId -> {sizeId: kod producenta}."""
    stan: Dict[int, Dict[str, str]] = {}
    strona = 0
    while True:
        odp = api.zapytanie(
            "GET", f"products/sizes?result::page={strona}&result::pageNumber={ROZMIAR_PACZKI}"
        )
        wyniki = odp.get("results") or {}
        pozycje = wyniki.values() if isinstance(wyniki, dict) else wyniki
        for towar in pozycje:
            stan[int(towar["productId"])] = {
                r["sizeId"]: (r.get("productProducerCode") or "").strip()
                for r in towar.get("sizesResult", [])
            }
        stron = int((odp.get("result") or {}).get("pageAll", 0))
        strona += 1
        print(f"\r  odczyt stanu: strona {strona}/{stron}", end="")
        if strona >= stron:
            print()
            return stan


def zaplanuj(stan: Dict[int, Dict[str, str]]) -> Tuple[List[dict], List[dict]]:
    """Zwraca (do_wyslania, pominiete) wg reguł: duplikaty, zamienniki, stan sklepu."""
    nazwy = {}
    with open(PLIK_RAPORTU, encoding="utf-8-sig", newline="") as plik:
        for w in csv.DictReader(plik):
            nazwy[w["id"]] = w["nazwa"]
    pozycje = []
    with open(PLIK_AKTUALIZACJI, encoding="utf-8", newline="") as plik:
        for w in csv.DictReader(plik):
            pozycje.append({
                "id": int(w["@id"]), "rozmiar": w["/sizes/size@id"],
                "kod": w["/sizes/size@code_producer"], "nazwa": nazwy.get(w["@id"], ""),
            })

    grupy = defaultdict(list)
    for p in pozycje:
        grupy[p["kod"]].append(p)
    zajete = defaultdict(set)
    for towar_id, rozmiary in stan.items():
        for kod in rozmiary.values():
            if kod:
                zajete[kod].add(towar_id)

    do_wyslania, pominiete = [], []
    for kod, grupa in grupy.items():
        oryginaly = [p for p in grupa if SLOWO_ZAMIENNIK not in p["nazwa"].lower()]
        for p in grupa:
            if len(grupa) > 1:
                if len(oryginaly) != 1:
                    p["status"] = STATUS_DUPLIKAT
                elif p is not oryginaly[0]:
                    p["status"] = STATUS_ZAMIENNIK
            if "status" not in p:
                if p["id"] not in stan or p["rozmiar"] not in stan[p["id"]]:
                    p["status"] = STATUS_BRAK_TOWARU
                elif stan[p["id"]][p["rozmiar"]]:
                    p["status"] = STATUS_MA_KOD
                elif zajete.get(kod, set()) - {p["id"]}:
                    p["status"] = STATUS_KOD_ZAJETY
            if "status" in p:
                if p["status"] == STATUS_KOD_ZAJETY:
                    p["uwagi"] = "towar " + ", ".join(map(str, sorted(zajete[kod])))
                pominiete.append(p)
            else:
                do_wyslania.append(p)
    return do_wyslania, pominiete


def wyslij(api: KlientApi, paczka: List[dict]) -> None:
    """Wysyła paczkę kodów (mode=edit) i wpisuje status do każdej pozycji."""
    dane = {
        "mode": "edit",
        "sizesProductsData": [
            {"productId": p["id"],
             "sizes": [{"sizeId": p["rozmiar"], "sizeData": {"codeProducer": p["kod"]}}]}
            for p in paczka
        ],
    }
    odp = api.zapytanie("PUT", "products/sizes", dane)
    bledy = {}
    for wynik in odp.get("results") or []:
        teksty = [b.get("faultString", "") for b in wynik.get("errors") or [] if b.get("faultCode")]
        for rozmiar in wynik.get("sizes") or []:
            teksty += [b.get("faultString", "") for b in rozmiar.get("errors") or []
                       if b.get("faultCode")]
        if teksty:
            bledy[int(wynik.get("productId") or 0)] = "; ".join(teksty)
    ogolny = "" if odp.get("results") else json.dumps(odp, ensure_ascii=False)[:300]
    for p in paczka:
        if ogolny:
            p["status"], p["uwagi"] = STATUS_BLAD, ogolny
        elif p["id"] in bledy:
            p["status"], p["uwagi"] = STATUS_BLAD, bledy[p["id"]]
        else:
            p["status"] = STATUS_ZAPISANO


def main() -> int:
    """Planuje, wykonuje próbę, pyta o zgodę, wysyła resztę, weryfikuje i zapisuje dziennik."""
    bez_pytania = "--bez-pytania" in sys.argv
    try:
        with open(PLIK_KONFIGURACJI, encoding="utf-8") as plik:
            konf = json.load(plik)
    except (OSError, ValueError) as blad:
        print(f"Brak lub błędny {PLIK_KONFIGURACJI}: {blad}")
        return 1
    os.makedirs(FOLDER_WYNIKOW, exist_ok=True)
    znacznik = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    sciezka_dziennika = os.path.join(FOLDER_WYNIKOW, f"api_kod_producenta_{znacznik}")

    with open(sciezka_dziennika + ".jsonl", "w", encoding="utf-8") as dziennik:
        api = KlientApi(konf["domena"], konf["klucz_api"], dziennik)
        print("Odczyt stanu sklepu…")
        stan = stan_sklepu(api)
        do_wyslania, pominiete = zaplanuj(stan)
        print(f"Do wysłania: {len(do_wyslania)}, pominięte: {len(pominiete)}")

        if do_wyslania:
            proba = do_wyslania[:LICZBA_PROBNYCH]
            print("\nPróba:", ", ".join(f"{p['id']}={p['kod']}" for p in proba))
            wyslij(api, proba)
            stan_po = stan_sklepu(api)
            for p in proba:
                if p["status"] == STATUS_ZAPISANO and stan_po.get(p["id"], {}).get(p["rozmiar"]) != p["kod"]:
                    p["status"], p["uwagi"] = STATUS_BLAD, "odczyt kontrolny nie zgadza się"
                print(f"  {p['id']}: {p['status']} {p.get('uwagi', '')}")
            reszta = do_wyslania[LICZBA_PROBNYCH:]
            udana = all(p["status"] == STATUS_ZAPISANO for p in proba)
            if not udana:
                print("Próba nieudana — przerywam przed pełną wysyłką.")
            elif reszta and (bez_pytania or input(
                    f"\nWysłać pozostałe {len(reszta)}? [t/N]: ").strip().lower() == "t"):
                for start in range(0, len(reszta), ROZMIAR_PACZKI):
                    wyslij(api, reszta[start:start + ROZMIAR_PACZKI])
                    print(f"\r  wysłano {min(start + ROZMIAR_PACZKI, len(reszta))}/{len(reszta)}", end="")
                print("\nWeryfikacja po wysyłce…")
                stan_po = stan_sklepu(api)
                for p in reszta:
                    if p["status"] == STATUS_ZAPISANO and stan_po.get(p["id"], {}).get(p["rozmiar"]) != p["kod"]:
                        p["status"], p["uwagi"] = STATUS_BLAD, "odczyt kontrolny nie zgadza się"
            for p in reszta:
                p.setdefault("status", "nie wysłano")

    wszystkie = sorted(do_wyslania + pominiete, key=lambda p: p["id"])
    try:
        with open(sciezka_dziennika + ".csv", "w", encoding="utf-8-sig", newline="") as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow(["id", "rozmiar", "kod_producenta", "nazwa", "status", "uwagi"])
            for p in wszystkie:
                pisarz.writerow([p["id"], p["rozmiar"], p["kod"], p["nazwa"], p["status"],
                                 p.get("uwagi", "")])
    except OSError as blad:
        print(f"Błąd zapisu dziennika: {blad}")
        return 1

    print("\nPodsumowanie:")
    licznik = defaultdict(int)
    for p in wszystkie:
        licznik[p["status"]] += 1
    for status, liczba in sorted(licznik.items(), key=lambda x: -x[1]):
        print(f"  {status}: {liczba}")
    print(f"\nDziennik: {sciezka_dziennika}.csv (+ .jsonl z odpowiedziami API)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
