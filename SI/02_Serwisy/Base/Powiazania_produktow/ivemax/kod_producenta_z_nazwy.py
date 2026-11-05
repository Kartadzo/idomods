"""Numer części z nazwy towaru IdoSell -> plik aktualizacji kodu producenta.

Czyta eksport CSV z panelu IdoSell (products_export*.csv) i dla towarów, których nazwa
zawiera dokładnie jeden numer części, przygotowuje plik importu CSV pola kod producenta.
Towary z kilkoma numerami, bez numeru, z rozmiarami albo z już wypełnionym kodem
trafiają wyłącznie do raportu. Szczegóły i decyzje: ANALIZA_kod_producenta_z_nazwy.md.
"""

import csv
import glob
import os
import re
import sys
from collections import Counter
from typing import List, Optional

KOL_ID = "@id"
KOL_ROZMIAR_ID = "/sizes/size@id"
KOL_KOD_PRODUCENTA = "/sizes/size@code_producer"
KOL_KOD_PRODUCENTA_PRODUKT = "@code_producer"
KOL_NAZWA = "/description/name[pol]"

PLIK_AKTUALIZACJI = "aktualizacja_kod_producenta.csv"
PLIK_RAPORTU = "kod_producenta_raport.csv"

# Ciąg liter i cyfr, w środku dopuszczalne . - / (np. 08.9759.10).
WZORZEC_KANDYDATA = re.compile(r"[A-Z0-9][A-Z0-9.\-/]*[A-Z0-9]")
MIN_DLUGOSC_KODU = 6
MIN_CYFR = 4
# Lepkość oleju (85W140, 5W30) wygląda jak kod, ale nim nie jest.
WZORZEC_LEPKOSCI = re.compile(r"\d{1,2}W\d{2,3}")

STATUS_NOWY = "nowy"
STATUS_BEZ_ZMIAN = "bez zmian"
STATUS_ROZNY = "różni się od obecnego"
STATUS_BRAK = "brak kodu w nazwie"
STATUS_WIELE = "wiele kodów - do uzupełnienia przez klienta"
STATUS_ROZMIARY = "towar z rozmiarami - pominięty"


def normalizuj(kod: str) -> str:
    """Zwraca kod bez separatorów i białych znaków, wielkimi literami (do porównań)."""
    return re.sub(r"[\s.\-/,;]", "", kod).upper()


def kody_z_nazwy(nazwa: str) -> List[str]:
    """Zwraca numery części z nazwy w kolejności wystąpienia, bez duplikatów.

    Numer to ciąg min. 6 znaków (po usunięciu separatorów) z min. 4 cyframi, co odsiewa
    roczniki (2014, 98-06), pojemności (2.3), modele (35C, E5) i modele skrzyń (2835.6).
    """
    wynik = []
    widziane = set()
    for kandydat in WZORZEC_KANDYDATA.findall(nazwa.upper()):
        klucz = normalizuj(kandydat)
        if len(klucz) < MIN_DLUGOSC_KODU or len(re.findall(r"\d", klucz)) < MIN_CYFR:
            continue
        if WZORZEC_LEPKOSCI.fullmatch(klucz):
            continue
        if klucz in widziane:
            continue
        widziane.add(klucz)
        wynik.append(kandydat)
    return wynik


def wybierz_eksport() -> Optional[str]:
    """Znajduje eksport IdoSell w bieżącym folderze; przy kilku pyta, którego użyć."""
    pliki = sorted(glob.glob("products_export*.csv"), key=os.path.getmtime, reverse=True)
    if not pliki:
        print("Brak pliku products_export*.csv w folderze:", os.getcwd())
        return None
    if len(pliki) == 1:
        return pliki[0]
    print("Znaleziono kilka eksportów IdoSell (od najnowszego):")
    for nr, plik in enumerate(pliki, 1):
        print(f"  {nr}. {plik}")
    odp = input("Numer pliku [1]: ").strip() or "1"
    if not odp.isdigit() or not 1 <= int(odp) <= len(pliki):
        print("Niepoprawny wybór.")
        return None
    return pliki[int(odp) - 1]


def main() -> int:
    """Czyta eksport, zapisuje plik aktualizacji i raport, wypisuje podsumowanie."""
    csv.field_size_limit(2**31 - 1)
    eksport = wybierz_eksport()
    if not eksport:
        return 1
    print("Eksport:", eksport)

    aktualizacja = []
    raport = []
    try:
        with open(eksport, encoding="utf-8-sig", newline="") as plik:
            czytnik = csv.DictReader(plik)
            brakujace = {KOL_ID, KOL_ROZMIAR_ID, KOL_KOD_PRODUCENTA, KOL_NAZWA} - set(
                czytnik.fieldnames or []
            )
            if brakujace:
                print("W eksporcie brakuje kolumn:", ", ".join(sorted(brakujace)))
                return 1
            for wiersz in czytnik:
                nazwa = wiersz[KOL_NAZWA]
                kody = kody_z_nazwy(nazwa)
                rozmiary = wiersz[KOL_ROZMIAR_ID].split("\n")
                obecny = " | ".join(
                    w.strip()
                    for w in (wiersz[KOL_KOD_PRODUCENTA], wiersz.get(KOL_KOD_PRODUCENTA_PRODUKT, ""))
                    if w.strip()
                )
                wybrany = ""
                if len(rozmiary) > 1:
                    status = STATUS_ROZMIARY
                elif not kody:
                    status = STATUS_BRAK
                elif len(kody) > 1:
                    status = STATUS_WIELE
                elif not obecny:
                    status = STATUS_NOWY
                    wybrany = kody[0]
                    aktualizacja.append([wiersz[KOL_ID], rozmiary[0], wybrany])
                elif normalizuj(obecny) == normalizuj(kody[0]):
                    status = STATUS_BEZ_ZMIAN
                else:
                    status = STATUS_ROZNY
                raport.append(
                    [wiersz[KOL_ID], nazwa.strip(), " ; ".join(kody), wybrany, obecny, status]
                )
    except (OSError, csv.Error) as blad:
        print(f"Błąd odczytu {eksport}: {blad}")
        return 1

    try:
        with open(PLIK_AKTUALIZACJI, "w", encoding="utf-8", newline="") as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow([KOL_ID, KOL_ROZMIAR_ID, KOL_KOD_PRODUCENTA])
            pisarz.writerows(aktualizacja)
        with open(PLIK_RAPORTU, "w", encoding="utf-8-sig", newline="") as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow(
                ["id", "nazwa", "kody_w_nazwie", "kod_do_wpisania", "obecny_kod", "status"]
            )
            pisarz.writerows(raport)
    except OSError as blad:
        print(f"Błąd zapisu: {blad}")
        return 1

    print(f"\nTowarów w eksporcie: {len(raport)}")
    for status, liczba in Counter(w[-1] for w in raport).most_common():
        print(f"  {status}: {liczba}")
    print(f"\nZapisano: {PLIK_AKTUALIZACJI} ({len(aktualizacja)} towarów)")
    print(f"Zapisano: {PLIK_RAPORTU}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
