"""Plik powiązań Base: produkty wFirmy z katalogu BL -> towary IdoSell (IVEMAX).

Wejście (ten folder): data (37).csv (ID BL do powiązania), katalog Base (SKU, nazwy),
eksport Shoparena, eksport IdoSell, nowe_towary_shoparena.csv. ID towarów dodanych
przez API po eksporcie IdoSell pobiera ze sklepu na żywo (config.json).
Metody dopasowania i reguły: ANALIZA_powiazanie_base_idosell.md.

Wyjście: powiazania_base_idosell.csv (do wczytania w Base, integracja IVEMAX-IdoSell)
oraz powiazania_base_raport.csv (wszystkie produkty z metodą i nazwami).
"""

import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Callable, Dict, Iterable, Optional, Set

from api_kod_producenta import KlientApi, PLIK_KONFIGURACJI
from api_nowe_towary_naprawa import stan_rozmiarow
from kod_producenta_z_nazwy import kody_z_nazwy

PLIK_DO_POWIAZANIA = "data (37).csv"
PLIK_NOWYCH = "nowe_towary_shoparena.csv"
PLIK_WYNIKU = "powiazania_base_idosell.csv"
PLIK_RAPORTU = "powiazania_base_raport.csv"
NOWY = "NOWY:"


def najnowszy(wzorzec: str) -> str:
    """Zwraca najnowszy plik pasujący do wzorca albo zgłasza błąd."""
    pliki = sorted(glob.glob(wzorzec), key=os.path.getmtime, reverse=True)
    if not pliki:
        raise FileNotFoundError(f"brak pliku {wzorzec}")
    return pliki[0]


def norm(tekst: str) -> str:
    """Kod bez separatorów i białych znaków, wielkimi literami."""
    return re.sub(r"[\s.\-,/]", "", tekst).upper()


def czesci(tekst: str) -> Set[str]:
    """Rozbija pole z kilkoma kodami (`a ; b / c`, także w HTML) na znormalizowane kody."""
    return {norm(t) for t in re.split(r"[;/]", re.sub(r"<[^>]+>", " ", tekst)) if norm(t)}


class IndeksKodow:
    """Indeks pola z kodami: cała wartość oraz pojedyncze kody -> identyfikatory."""

    def __init__(self) -> None:
        self.cale = defaultdict(set)
        self.pojedyncze = defaultdict(set)

    def dodaj(self, wartosc: str, ident: str) -> None:
        """Dodaje wartość pola (np. krótki opis) dla identyfikatora."""
        if not wartosc.strip():
            return
        self.cale[norm(re.sub(r"<[^>]+>", "", wartosc))].add(ident)
        for kod in czesci(wartosc):
            self.pojedyncze[kod].add(ident)

    def szukaj(self, sku: str, przeloz: Callable[[str], Iterable[str]] = lambda x: [x]) -> Optional[str]:
        """Zwraca jedyny cel dla SKU (całość, a gdy brak — część wspólna kodów) albo None."""
        trafione = self.cale.get(norm(sku)) or set()
        if not trafione and czesci(sku):
            trafione = set.intersection(*[self.pojedyncze.get(k, set()) for k in czesci(sku)])
        cele = {cel for t in trafione for cel in przeloz(t)}
        return next(iter(cele)) if len(cele) == 1 else None


def main() -> int:
    """Dopasowuje produkty, rozwiązuje ID nowych towarów i zapisuje plik oraz raport."""
    csv.field_size_limit(2**31 - 1)
    try:
        with open(PLIK_DO_POWIAZANIA, encoding="utf-8-sig", errors="replace") as plik:
            do_powiazania = [l.split(";")[0].strip() for l in plik if l.strip()]
        katalog = {}
        with open(najnowszy("Base__Produkty__domylny*.csv"), encoding="utf-8-sig", newline="") as plik:
            for w in csv.DictReader(plik, delimiter=";"):
                katalog[w["produkt_id"]] = w
        with open(najnowszy("shopArena*.csv"), encoding="utf-8-sig", newline="") as plik:
            shoparena = list(csv.DictReader(plik))
        idosell = {}
        with open(najnowszy("products_export*.csv"), encoding="utf-8-sig", newline="") as plik:
            for w in csv.DictReader(plik):
                idosell[w["@id"]] = w
        with open(PLIK_NOWYCH, encoding="utf-8-sig", newline="") as plik:
            nowe = {w["product_code"]: w for w in csv.DictReader(plik)}
    except (OSError, KeyError, csv.Error) as blad:
        print(f"Błąd odczytu danych wejściowych: {blad}")
        return 1

    # Most Shoparena -> IdoSell po kodzie zewnętrznym (KZS-<kod> albo <kod>_<data>).
    most = defaultdict(set)
    for ident, w in idosell.items():
        kod = w["/sizes/size@code_external"].strip()
        most[kod[4:] if kod.startswith("KZS-") else kod].add(ident)

    def shoparena_na_idosell(kod: str) -> Iterable[str]:
        if kod in most:
            return most[kod]
        return [NOWY + kod] if kod in nowe else []

    metoda_a = IndeksKodow()
    for w in shoparena:
        metoda_a.dodaj(w["short_description"], w["product_code"].strip())
    metoda_c = IndeksKodow()
    for ident, w in idosell.items():
        metoda_c.dodaj(w.get("/description/short_desc[pol]", ""), ident)
    numery = defaultdict(set)
    numery_towaru = {}
    for ident, w in idosell.items():
        numery_towaru[ident] = {norm(k) for k in kody_z_nazwy(w["/description/name[pol]"])}
        for k in numery_towaru[ident]:
            numery[k].add(ident)

    wyniki = []
    for bl_id in do_powiazania:
        produkt = katalog.get(bl_id, {})
        sku = produkt.get("produkt_sku", "")
        nazwa = produkt.get("produkt_nazwa", "")
        trafienia = {}
        if sku.strip():
            a = metoda_a.szukaj(sku, shoparena_na_idosell)
            c = metoda_c.szukaj(sku)
            if a:
                trafienia["A"] = a
            if c:
                trafienia["C"] = c
        kody_bl = {norm(k) for k in kody_z_nazwy(sku + " ; " + nazwa)}
        if kody_bl:
            kandydaci = set().union(*[numery.get(k, set()) for k in kody_bl])
            pelne = [t for t in kandydaci if kody_bl <= numery_towaru[t]]
            if len(pelne) == 1:
                trafienia["B"] = pelne[0]
        cele = set(trafienia.values())
        wyniki.append({"bl": bl_id, "sku": sku, "nazwa": nazwa, "metody": trafienia,
                       "cel": next(iter(cele)) if len(cele) == 1 else "",
                       "status": "brak pary" if not cele else ("sprzeczne" if len(cele) > 1 else "")})

    # ID towarów utworzonych przez API po eksporcie — ze sklepu na żywo.
    if any(w["cel"].startswith(NOWY) for w in wyniki):
        try:
            with open(PLIK_KONFIGURACJI, encoding="utf-8") as plik:
                konf = json.load(plik)
        except (OSError, ValueError) as blad:
            print(f"Brak {PLIK_KONFIGURACJI}, nie rozwiążę ID nowych towarów: {blad}")
            return 1
        print("Odczyt ID nowych towarów ze sklepu…")
        with open(os.devnull, "w", encoding="utf-8") as pusty:
            api = KlientApi(konf["domena"], konf["klucz_api"], pusty)
            wszystkie, _, _ = stan_rozmiarow(api)
            # products/sizes zwraca jeszcze usunięte towary — zostawiam tylko istniejące.
            kandydaci = sorted({i for w in nowe.values() for i in wszystkie.get(w["kod_zewnetrzny"], [])})
            istniejace = set()
            for start in range(0, len(kandydaci), 50):
                odp = api.zapytanie("GET", "products/products?productIds=" +
                                    ",".join(map(str, kandydaci[start:start + 50])))
                istniejace |= {int(t["productId"]) for t in odp.get("results") or []
                               if t.get("productIsDeleted") != "y"}
        zewnetrzne = {}
        for kod, ids in wszystkie.items():
            zywe = [i for i in ids if i in istniejace]
            if len(zywe) == 1:
                zewnetrzne[kod] = zywe[0]
        for w in wyniki:
            if w["cel"].startswith(NOWY):
                nowy = nowe[w["cel"][len(NOWY):]]
                kod_zew = nowy["kod_zewnetrzny"]
                if kod_zew in zewnetrzne:
                    w["cel"], w["nowy"] = str(zewnetrzne[kod_zew]), nowy["name"]
                else:
                    w["status"], w["cel"] = f"czeka na import ({kod_zew})", ""

    # Jeden towar IdoSell może mieć tylko jeden produkt BL — kolizje do weryfikacji.
    licznik = Counter(w["cel"] for w in wyniki if w["cel"])
    for w in wyniki:
        if w["cel"] and licznik[w["cel"]] > 1:
            w["status"] = f"kolizja ({licznik[w['cel']]} produkty BL na towar {w['cel']})"
        elif w["cel"] and not w["status"]:
            w["status"] = "powiązano (nowy towar)" if w.get("nowy") else "powiązano"
    do_pliku = [w for w in wyniki if w["status"].startswith("powiązano")]

    try:
        with open(PLIK_WYNIKU, "w", encoding="utf-8", newline="") as plik:
            for w in do_pliku:
                plik.write(f"{w['bl']};{w['cel']};\r\n")
        with open(PLIK_RAPORTU, "w", encoding="utf-8-sig", newline="") as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow(["id_bl", "sku_wfirma", "nazwa_bl", "id_idosell", "nazwa_idosell",
                             "metody", "status"])
            for w in wyniki:
                nazwa_ido = (idosell.get(w["cel"], {}).get("/description/name[pol]", "")
                             or w.get("nowy", ""))
                pisarz.writerow([w["bl"], w["sku"], w["nazwa"], w["cel"], nazwa_ido.strip(),
                                 "+".join(sorted(w["metody"])), w["status"]])
    except OSError as blad:
        print(f"Błąd zapisu: {blad}")
        return 1

    print(f"\nProduktów do powiązania: {len(wyniki)}")
    for status, liczba in Counter(w["status"] for w in wyniki).most_common():
        print(f"  {status}: {liczba}")
    print(f"\nZapisano: {PLIK_WYNIKU} ({len(do_pliku)} powiązań)")
    print(f"Zapisano: {PLIK_RAPORTU}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
