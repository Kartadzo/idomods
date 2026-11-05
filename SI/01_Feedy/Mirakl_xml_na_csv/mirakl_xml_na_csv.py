#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Konwersja feeda XML (format Mirakl / IAI: import > products > product > attribute)
na plik CSV.

Uruchomienie: python mirakl_xml_na_csv.py
Skrypt sam wykrywa pliki .xml w swoim folderze i pozwala wybrac zrodlo.
"""

import csv
import os
import sys
import xml.etree.ElementTree as ET

SEPARATORY = {
    "1": (";", "srednik  ;  (domyslny dla Mirakl / Excel PL)"),
    "2": (",", "przecinek  ,"),
    "3": ("\t", "tabulator"),
    "4": ("|", "pionowa kreska  |"),
}


def folder_skryptu():
    return os.path.dirname(os.path.abspath(sys.argv[0])) or os.getcwd()


def znajdz_pliki_xml(folder):
    pliki = [n for n in os.listdir(folder)
             if n.lower().endswith(".xml") and os.path.isfile(os.path.join(folder, n))]
    return sorted(pliki, key=str.lower)


def wybierz_plik(folder):
    pliki = znajdz_pliki_xml(folder)
    if not pliki:
        print("\nW folderze nie ma zadnego pliku .xml:")
        print("  " + folder)
        print("Wgraj plik XML do tego folderu i uruchom skrypt ponownie.")
        return None

    print("\nZnalezione pliki XML:")
    for i, nazwa in enumerate(pliki, 1):
        rozmiar = os.path.getsize(os.path.join(folder, nazwa)) / 1024.0
        print("  [%d] %-60s %8.1f KB" % (i, nazwa, rozmiar))

    if len(pliki) == 1:
        print("\n(Enter = jedyny plik na liscie)")

    while True:
        wybor = raw_input_compat("\nNumer pliku zrodlowego [1]: ").strip() or "1"
        if wybor.isdigit() and 1 <= int(wybor) <= len(pliki):
            return os.path.join(folder, pliki[int(wybor) - 1])
        print("Podaj numer z zakresu 1-%d." % len(pliki))


def wybierz_separator():
    print("\nSeparator kolumn w CSV:")
    for klucz in sorted(SEPARATORY):
        print("  [%s] %s" % (klucz, SEPARATORY[klucz][1]))
    while True:
        wybor = raw_input_compat("Wybor [1]: ").strip() or "1"
        if wybor in SEPARATORY:
            return SEPARATORY[wybor][0]
        print("Podaj numer z listy.")


def raw_input_compat(komunikat):
    try:
        return input(komunikat)
    except EOFError:
        return ""


def zbierz_kolumny(sciezka_xml):
    """Pierwszy przebieg: kolejnosc kolumn wg pierwszego wystapienia kodu."""
    kolumny = []
    widziane = set()
    liczba_produktow = 0
    for zdarzenie, element in ET.iterparse(sciezka_xml, events=("end",)):
        if strip_ns(element.tag) != "product":
            continue
        liczba_produktow += 1
        for atrybut in element:
            if strip_ns(atrybut.tag) != "attribute":
                continue
            kod = (atrybut.findtext("code") or "").strip()
            if kod and kod not in widziane:
                widziane.add(kod)
                kolumny.append(kod)
        element.clear()
    return kolumny, liczba_produktow


def strip_ns(tag):
    return tag.split("}", 1)[-1] if isinstance(tag, str) and "}" in tag else tag


def konwertuj(sciezka_xml, sciezka_csv, kolumny, separator):
    """Drugi przebieg: zapis wierszy."""
    zapisane = 0
    with open(sciezka_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=separator, quotechar='"',
                            quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
        writer.writerow(kolumny)
        for zdarzenie, element in ET.iterparse(sciezka_xml, events=("end",)):
            if strip_ns(element.tag) != "product":
                continue
            wiersz = {}
            for atrybut in element:
                if strip_ns(atrybut.tag) != "attribute":
                    continue
                kod = (atrybut.findtext("code") or "").strip()
                if not kod:
                    continue
                wartosc = atrybut.findtext("value") or ""
                wartosc = wartosc.strip()
                if kod in wiersz and wiersz[kod]:
                    # ten sam kod kilka razy w jednym produkcie - laczymy wartosci
                    wiersz[kod] = wiersz[kod] + "|" + wartosc
                else:
                    wiersz[kod] = wartosc
            writer.writerow([wiersz.get(kod, "") for kod in kolumny])
            zapisane += 1
            element.clear()
    return zapisane


def main():
    folder = folder_skryptu()
    print("=" * 70)
    print("  XML -> CSV  (format Mirakl: product / attribute -> code + value)")
    print("=" * 70)
    print("Folder roboczy: " + folder)

    sciezka_xml = wybierz_plik(folder)
    if not sciezka_xml:
        return 1

    separator = wybierz_separator()

    print("\nAnalizuje strukture pliku...")
    try:
        kolumny, liczba_produktow = zbierz_kolumny(sciezka_xml)
    except ET.ParseError as blad:
        print("BLAD: plik XML jest uszkodzony lub niepoprawny -> %s" % blad)
        return 1

    if not kolumny:
        print("BLAD: nie znaleziono zadnego <product><attribute><code> w pliku.")
        return 1

    print("Produktow: %d" % liczba_produktow)
    print("Kolumn:    %d  ->  %s" % (len(kolumny), ", ".join(kolumny)))

    sciezka_csv = os.path.splitext(sciezka_xml)[0] + ".csv"
    if os.path.exists(sciezka_csv):
        odp = raw_input_compat("\nPlik %s juz istnieje. Nadpisac? [T/n]: "
                               % os.path.basename(sciezka_csv)).strip().lower()
        if odp and odp not in ("t", "tak", "y", "yes"):
            print("Przerwano.")
            return 1

    zapisane = konwertuj(sciezka_xml, sciezka_csv, kolumny, separator)

    print("\nGOTOWE")
    print("  Plik wynikowy: %s" % sciezka_csv)
    print("  Wierszy danych: %d (+ naglowek)" % zapisane)
    print("  Kodowanie: UTF-8 (bez BOM), separator: %r" % separator)
    return 0


if __name__ == "__main__":
    try:
        kod = main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez uzytkownika.")
        kod = 1
    if sys.stdout.isatty():
        raw_input_compat("\nNacisnij Enter, aby zamknac...")
    sys.exit(kod)
