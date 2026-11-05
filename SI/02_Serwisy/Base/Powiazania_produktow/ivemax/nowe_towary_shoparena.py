"""Lista towarów z Shoparena, których brakuje w IdoSell (dodane po migracji).

Porównuje eksport Shoparena (shopArena*.csv) z eksportem IdoSell (products_export*.csv)
po kodzie zewnętrznym IdoSell (`KZS-<product_code>` albo `<product_code>`). Zapisuje listę
CSV do wgrania w panelu: kolumny Shoparena bez stanu magazynowego + kolumny pomocnicze.
Szczegóły i decyzje: ANALIZA_nowe_towary_shoparena.md.
"""

import csv
import glob
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Set

from kod_producenta_z_nazwy import kody_z_nazwy

KOL_KOD_ZEWNETRZNY = "/sizes/size@code_external"
KOL_NAZWA_IDO = "/description/name[pol]"
PREFIKS_KZS = "KZS-"

# Pozycje sprzed migracji, świadomie nieprzenoszone (decyzja użytkownika 2026-10-21).
POMINIETE_KODY = {"239", "240"}
POMINIETE_KOLUMNY = {"stock"}

PLIK_WYNIKU = "nowe_towary_shoparena.csv"


def wybierz_plik(wzorzec: str, opis: str) -> Optional[str]:
    """Znajduje plik wg wzorca w bieżącym folderze; przy kilku pyta, którego użyć."""
    pliki = sorted(glob.glob(wzorzec), key=os.path.getmtime, reverse=True)
    if not pliki:
        print(f"Brak pliku {opis} ({wzorzec}) w folderze:", os.getcwd())
        return None
    if len(pliki) == 1:
        return pliki[0]
    print(f"Znaleziono kilka plików {opis} (od najnowszego):")
    for nr, plik in enumerate(pliki, 1):
        print(f"  {nr}. {plik}")
    odp = input("Numer pliku [1]: ").strip() or "1"
    if not odp.isdigit() or not 1 <= int(odp) <= len(pliki):
        print("Niepoprawny wybór.")
        return None
    return pliki[int(odp) - 1]


def normalizuj(kod: str) -> str:
    """Zwraca kod bez separatorów i białych znaków, wielkimi literami (do porównań)."""
    return re.sub(r"[\s.\-/,;]", "", kod).upper()


def wczytaj_idosell(sciezka: str) -> (Set[str], Dict[str, Set[str]]):
    """Zwraca kody Shoparena obecne w IdoSell oraz indeks: numer części -> ID towarów."""
    kody_shoparena = set()
    indeks = defaultdict(set)
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        for wiersz in csv.DictReader(plik):
            kod = wiersz[KOL_KOD_ZEWNETRZNY].strip()
            kody_shoparena.add(kod[len(PREFIKS_KZS):] if kod.startswith(PREFIKS_KZS) else kod)
            for numer in kody_z_nazwy(wiersz[KOL_NAZWA_IDO]):
                indeks[normalizuj(numer)].add(wiersz["@id"])
    return kody_shoparena, indeks


def main() -> int:
    """Wybiera brakujące towary, zapisuje listę CSV i wypisuje podsumowanie."""
    csv.field_size_limit(2**31 - 1)
    shoparena = wybierz_plik("shopArena*.csv", "Shoparena")
    idosell = wybierz_plik("products_export*.csv", "IdoSell")
    if not shoparena or not idosell:
        return 1
    print("Shoparena:", shoparena)
    print("IdoSell:  ", idosell)

    try:
        kody_w_idosell, indeks = wczytaj_idosell(idosell)
        with open(shoparena, encoding="utf-8-sig", newline="") as plik:
            czytnik = csv.DictReader(plik)
            kolumny = [k for k in czytnik.fieldnames or [] if k not in POMINIETE_KOLUMNY]
            wszystkie = list(czytnik)
    except (OSError, csv.Error, KeyError) as blad:
        print(f"Błąd odczytu: {blad}")
        return 1

    wynik: List[dict] = []
    duplikaty = 0
    for wiersz in wszystkie:
        kod = wiersz["product_code"].strip()
        if kod in kody_w_idosell or kod in POMINIETE_KODY:
            continue
        numery = kody_z_nazwy(wiersz["name"])
        podobne = sorted(
            {i for n in numery for i in indeks.get(normalizuj(n), ())}, key=int
        )
        if podobne:
            duplikaty += 1
        nowy = {k: wiersz[k] for k in kolumny}
        nowy["kategoria_idosell"] = "/".join(c.strip() for c in wiersz["category"].split(">"))
        # Konwencja z migracji: KZS- tylko przy samym numerze, kod z datą (6913_2025…) bez.
        nowy["kod_zewnetrzny"] = kod if "_" in kod else PREFIKS_KZS + kod
        nowy["kod_producenta"] = numery[0] if len(numery) == 1 else ""
        nowy["uwagi"] = (
            "numer części już w IdoSell: towar " + ", ".join(podobne) if podobne else ""
        )
        wynik.append(nowy)

    try:
        with open(PLIK_WYNIKU, "w", encoding="utf-8-sig", newline="") as plik:
            pisarz = csv.DictWriter(
                plik, kolumny + ["kategoria_idosell", "kod_zewnetrzny", "kod_producenta", "uwagi"]
            )
            pisarz.writeheader()
            pisarz.writerows(wynik)
    except OSError as blad:
        print(f"Błąd zapisu: {blad}")
        return 1

    print(f"\nProduktów w Shoparenie: {len(wszystkie)}")
    print(f"Nowych (brak w IdoSell, bez {', '.join(sorted(POMINIETE_KODY))}): {len(wynik)}")
    print(f"  w tym z numerem części już obecnym w IdoSell: {duplikaty}")
    print(f"  w tym z kodem producenta: {sum(1 for w in wynik if w['kod_producenta'])}")
    print(f"\nZapisano: {PLIK_WYNIKU}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
