"""Widoczność towarów IdoSell według eksportu Shoparena (kolumna active) i powiązań Base.

Reguła: widoczny = active 1 w Shoparenie ORAZ towar jest w powiazania_base_idosell.csv.
Każdy inny towar sklepu — ukryty. Wyjątek: towar powiązany z Base, którego nie ma
w eksporcie Shoparena (brak informacji o aktywności), zostaje bez zmian.
Wysyła tylko zmiany: najpierw plan do pliku, potem próba na 3 towarach, potem reszta.
Szczegóły: ANALIZA_widocznosc_towarow.md.
"""

import csv
import glob
import json
import os
import sys
from collections import Counter
from datetime import datetime

from api_kod_producenta import KlientApi, PLIK_KONFIGURACJI, FOLDER_WYNIKOW
from api_nowe_towary import bledy_z
from api_nowe_towary_naprawa import stan_rozmiarow

PLIK_SHOPARENA = os.path.join("eksport_shoparena", "products_filtered_*.csv")
PLIK_POWIAZAN = "powiazania_base_idosell.csv"
ROZMIAR_ODCZYTU = 50
ROZMIAR_PACZKI = 100
LICZBA_PROBNYCH = 3


def najnowszy(wzorzec: str) -> str:
    """Zwraca najnowszy plik pasujący do wzorca albo zgłasza błąd."""
    pliki = sorted(glob.glob(wzorzec), key=os.path.getmtime, reverse=True)
    if not pliki:
        raise FileNotFoundError(f"brak pliku {wzorzec}")
    return pliki[0]


def kod_shoparena(kod_zewnetrzny: str) -> str:
    """Kod Shoparena z kodu zewnętrznego IdoSell (KZS-<kod> albo <kod>_<data>)."""
    return kod_zewnetrzny[4:] if kod_zewnetrzny.startswith("KZS-") else kod_zewnetrzny


def odczytaj_towary(api: KlientApi, ids: list) -> dict:
    """Zwraca istniejące towary: ID -> (nazwa, bieżąca widoczność y/n)."""
    towary = {}
    for start in range(0, len(ids), ROZMIAR_ODCZYTU):
        print(f"\r  odczyt {min(start + ROZMIAR_ODCZYTU, len(ids))}/{len(ids)}", end="")
        odp = api.zapytanie("GET", "products/products?productIds=" +
                            ",".join(map(str, ids[start:start + ROZMIAR_ODCZYTU])))
        for t in odp.get("results") or []:
            if t.get("productIsDeleted") == "y":
                continue
            nazwa = next((d.get("productName", "") for d in
                          (t.get("productDescriptionsLangData") or []) if d.get("langId") == "pol"), "")
            towary[int(t["productId"])] = (nazwa, t.get("productIsVisible", ""))
    print()
    return towary


def wyslij(api: KlientApi, plan: list) -> None:
    """Ustawia widoczność paczkami; wpisuje wynik do pozycji planu."""
    for start in range(0, len(plan), ROZMIAR_PACZKI):
        paczka = plan[start:start + ROZMIAR_PACZKI]
        print(f"\r  zapis {start + len(paczka)}/{len(plan)}", end="")
        odp = api.zapytanie("PUT", "products/products", {"params": {"products": [
            {"productId": p["id"], "productInVisible": p["docelowo"]} for p in paczka]}})
        wyniki = {int(r.get("productId", 0)): bledy_z(r.get("faults"))
                  for r in ((odp.get("results") or {}).get("productsResults") or [])}
        ogolny = bledy_z(odp.get("errors") and [odp["errors"]]) or ("" if wyniki else "brak odpowiedzi")
        for p in paczka:
            blad = wyniki.get(p["id"], ogolny)
            p["wynik"] = f"błąd: {blad}" if blad else "wysłano"
    print()


def sprawdz(api: KlientApi, plan: list) -> None:
    """Odczyt kontrolny: czy widoczność w sklepie jest docelowa."""
    stan = odczytaj_towary(api, [p["id"] for p in plan])
    for p in plan:
        if p.get("wynik") == "wysłano":
            teraz = stan.get(p["id"], ("", "?"))[1]
            p["wynik"] = "zmieniono" if teraz == p["docelowo"] else f"niezgodne po zapisie ({teraz})"


def zapisz(sciezka: str, wiersze: list, kolumny: list) -> None:
    """Zapisuje listę słowników do CSV (UTF-8 z BOM, przecinek)."""
    with open(sciezka, "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.DictWriter(plik, fieldnames=kolumny, extrasaction="ignore")
        pisarz.writeheader()
        pisarz.writerows(wiersze)


def main() -> int:
    """Buduje plan widoczności, pyta o zgodę, wysyła zmiany i sprawdza wynik."""
    bez_pytania = "--bez-pytania" in sys.argv
    csv.field_size_limit(2**31 - 1)
    try:
        with open(PLIK_KONFIGURACJI, encoding="utf-8") as plik:
            konf = json.load(plik)
        with open(najnowszy(PLIK_SHOPARENA), encoding="utf-8-sig", newline="") as plik:
            aktywnosc = {w["product_code"].strip(): w["active"].strip() for w in csv.DictReader(plik)}
        with open(PLIK_POWIAZAN, encoding="utf-8") as plik:
            powiazane = {int(l.split(";")[1]) for l in plik if l.strip()}
    except (OSError, ValueError, KeyError, IndexError) as blad:
        print(f"Błąd odczytu danych wejściowych: {blad}")
        return 1

    os.makedirs(FOLDER_WYNIKOW, exist_ok=True)
    znacznik = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    sciezka = os.path.join(FOLDER_WYNIKOW, f"api_widocznosc_{znacznik}")
    with open(sciezka + ".jsonl", "w", encoding="utf-8") as dziennik:
        api = KlientApi(konf["domena"], konf["klucz_api"], dziennik)
        print("Odczyt stanu sklepu…")
        zewnetrzne, _, _ = stan_rozmiarow(api)
        kody_towaru = {}
        for kod, ids in zewnetrzne.items():
            for ident in ids:
                kody_towaru.setdefault(ident, []).append(kod)
        towary = odczytaj_towary(api, sorted(kody_towaru))

        wszystkie = []
        for ident, (nazwa, teraz) in sorted(towary.items()):
            kody = sorted({kod_shoparena(k) for k in kody_towaru[ident]})
            active = next((aktywnosc[k] for k in kody if k in aktywnosc), "")
            if not active and ident in powiazane:
                # Brak w eksporcie Shoparena = brak informacji o aktywności — bez zmian.
                docelowo = teraz
            else:
                docelowo = "y" if active == "1" and ident in powiazane else "n"
            wszystkie.append({"id": ident, "nazwa": nazwa, "kod_shoparena": ", ".join(kody),
                              "active": active or "brak w Shoparenie",
                              "powiazany_base": "tak" if ident in powiazane else "nie",
                              "teraz": teraz, "docelowo": docelowo,
                              "wynik": "bez zmian" if teraz == docelowo else ""})
        plan = [w for w in wszystkie if w["wynik"] == ""]
        kolumny = ["id", "nazwa", "kod_shoparena", "active", "powiazany_base", "teraz", "docelowo", "wynik"]
        zapisz(sciezka + "_plan.csv", wszystkie, kolumny)

        print(f"\nTowarów w sklepie: {len(wszystkie)}")
        for (active, pow_, teraz, doc), n in sorted(Counter(
                (w["active"], w["powiazany_base"], w["teraz"], w["docelowo"]) for w in wszystkie).items()):
            print(f"  active={active:<18} Base={pow_:<4} teraz={teraz} -> {doc}: {n}")
        brak_powiazanych = powiazane - set(towary)
        if brak_powiazanych:
            print(f"Uwaga: {len(brak_powiazanych)} ID z pliku powiązań nie ma w sklepie: "
                  f"{sorted(brak_powiazanych)[:20]}")
        print(f"\nDo zmiany: pokaż {sum(p['docelowo'] == 'y' for p in plan)}, "
              f"ukryj {sum(p['docelowo'] == 'n' for p in plan)}")
        print(f"Plan: {sciezka}_plan.csv")
        if not plan:
            return 0

        # Próba: po jednym pokazaniu i ukrywaniu, reszta do LICZBA_PROBNYCH.
        proba = ([p for p in plan if p["docelowo"] == "y"][:1] + [p for p in plan if p["docelowo"] == "n"])
        proba = proba[:LICZBA_PROBNYCH]
        if not bez_pytania and input(f"\nWysłać próbę ({', '.join(str(p['id']) for p in proba)})? [t/N] ") \
                .strip().lower() != "t":
            return 0
        wyslij(api, proba)
        sprawdz(api, proba)
        for p in proba:
            print(f"  {p['id']} {p['teraz']} -> {p['docelowo']}: {p['wynik']}")
        if any(p["wynik"] != "zmieniono" for p in proba):
            print("Próba nieudana — przerywam.")
            zapisz(sciezka + ".csv", wszystkie, kolumny)
            return 1

        reszta = [p for p in plan if not p["wynik"]]
        if not bez_pytania and input(f"\nWysłać pozostałe {len(reszta)}? [t/N] ").strip().lower() != "t":
            zapisz(sciezka + ".csv", wszystkie, kolumny)
            return 0
        wyslij(api, reszta)
        print("Odczyt kontrolny…")
        sprawdz(api, reszta)

    zapisz(sciezka + ".csv", wszystkie, kolumny)
    print("\nWynik:")
    for wynik, n in Counter(p["wynik"] for p in plan).most_common():
        print(f"  {wynik}: {n}")
    print(f"Dziennik: {sciezka}.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
