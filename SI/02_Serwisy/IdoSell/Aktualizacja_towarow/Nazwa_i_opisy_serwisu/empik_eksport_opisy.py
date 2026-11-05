# -*- coding: utf-8 -*-
"""
Eksport IdoSell dla Empik (IdoSell_empikProducts_*.csv, separator ';') ->
ta sama treść, ale w ProductDescriptionLong opis długi bez znaczników <a ...> i </a>.

Struktura pola od IdoSell:
  "\n<div><b>TYTUŁ</b></div>\n<div>" + OPIS_DŁUGI + "</div>\n<div>" + TABELA_PARAMETRÓW + "</div>\n"
Zmieniany jest tylko OPIS_DŁUGI. Reszta pliku zostaje bajt w bajt (podmiana na surowym tekście).

Użycie: python empik_eksport_opisy.py [plik.csv]
Bez argumentu bierze najnowszy IdoSell_empikProducts_*.csv z folderu skryptu.
"""

import csv
import glob
import io
import os
import re
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
KOL_OPIS = "ProductDescriptionLong"

RE_NAGLOWEK = re.compile(r"\n<div><b>.*?</b></div>\n<div>", re.S)
RE_A_OTWARCIE = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
RE_A_ZAMKNIECIE = re.compile(r"</a\s*>", re.IGNORECASE)


def usun_linki(html):
    bez, n = RE_A_OTWARCIE.subn("", html)
    return RE_A_ZAMKNIECIE.sub("", bez), n


def zakoduj(pole):
    return '"' + pole.replace('"', '""') + '"'


def main():
    if len(sys.argv) > 1:
        sciezka = sys.argv[1]
    else:
        pliki = [p for p in glob.glob(os.path.join(FOLDER, "IdoSell_empikProducts_*.csv"))
                 if not p.endswith("_bez_linkow.csv")]
        sciezka = max(pliki, key=os.path.getmtime) if pliki else None
    if not sciezka or not os.path.isfile(sciezka):
        print("Nie znaleziono pliku IdoSell_empikProducts_*.csv.")
        return 1
    print("Wejście: %s" % os.path.abspath(sciezka))

    with open(sciezka, encoding="utf-8", newline="") as f:
        surowy = f.read()
    wiersze = list(csv.reader(io.StringIO(surowy, newline=""), delimiter=";"))
    naglowek = wiersze[0]
    if KOL_OPIS not in naglowek:
        print("Brak kolumny %s." % KOL_OPIS)
        return 1
    i_opis = naglowek.index(KOL_OPIS)

    wynik = surowy
    zmienione = 0
    linkow = 0
    for w in wiersze[1:]:
        if len(w) != len(naglowek):
            print("UWAGA - pominięto wiersz o nietypowej liczbie kolumn: %s" % w[:1])
            continue
        opis = w[i_opis]
        m = RE_NAGLOWEK.match(opis)
        if not m or "</div>\n<div>" not in opis[m.end():]:
            print("UWAGA - nietypowa struktura opisu, pominięto IAICode %s" % w[0])
            continue
        srodek, ogon = opis[m.end():].rsplit("</div>\n<div>", 1)
        nowy_srodek, n = usun_linki(srodek)
        if not n:
            continue
        nowy = opis[:m.end()] + nowy_srodek + "</div>\n<div>" + ogon
        stary_kod = zakoduj(opis)
        if wynik.count(stary_kod) != 1:
            print("UWAGA - nie da się jednoznacznie podmienić opisu IAICode %s" % w[0])
            continue
        wynik = wynik.replace(stary_kod, zakoduj(nowy))
        zmienione += 1
        linkow += n

    wyjscie = os.path.splitext(sciezka)[0] + "_bez_linkow.csv"
    with open(wyjscie, "w", encoding="utf-8", newline="") as f:
        f.write(wynik)

    print("Towarów: %d, zmienionych opisów: %d (usuniętych linków: %d)"
          % (len(wiersze) - 1, zmienione, linkow))
    print("Wyjście: %s" % wyjscie)
    return 0


if __name__ == "__main__":
    kod = main()
    if len(sys.argv) <= 1:
        input("\nNaciśnij Enter, aby zamknąć...")
    sys.exit(kod)
