# -*- coding: utf-8 -*-
"""
Eksport towarów IdoSell (IOF CSV) -> CSV z nazwą i opisem długim dla Empik Marketplace.

Nazwa: kopia /description/name[pol].
Opis długi: kopia /description/long_desc[pol] bez znaczników <a ...> i </a>
(treść linku zostaje).

Użycie: python empik_opisy.py [plik_eksportu.csv]
Bez argumentu bierze najnowszy products_export*.csv z bieżącego folderu albo z ../Sklep.
"""

import csv
import glob
import os
import re
import sys
from datetime import datetime

SITE_ID = "1"
SERVICE_ID = "278"  # Empik Marketplace
LANG = "pol"

KOL_NAZWA = "/description/name[%s]" % LANG
KOL_OPIS = "/description/long_desc[%s]" % LANG

NAGLOWKI = [
    "@id",
    "/services_descriptions/name[%s]" % LANG,
    "/services_descriptions/name@site_id",
    "/services_descriptions/name@service_id",
    "/services_descriptions/long_desc[%s]" % LANG,
    "/services_descriptions/long_desc@site_id",
    "/services_descriptions/long_desc@service_id",
]

RE_A_OTWARCIE = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
RE_A_ZAMKNIECIE = re.compile(r"</a\s*>", re.IGNORECASE)

FOLDER = os.path.dirname(os.path.abspath(__file__))


def znajdz_eksport():
    kandydaci = []
    for katalog in (FOLDER, os.path.join(FOLDER, "..", "Sklep")):
        kandydaci += glob.glob(os.path.join(katalog, "products_export*.csv"))
    if not kandydaci:
        return None
    return max(kandydaci, key=os.path.getmtime)


def usun_linki(html):
    bez, n = RE_A_OTWARCIE.subn("", html)
    bez = RE_A_ZAMKNIECIE.sub("", bez)
    return bez, n


def main():
    sciezka = sys.argv[1] if len(sys.argv) > 1 else znajdz_eksport()
    if not sciezka or not os.path.isfile(sciezka):
        print("Nie znaleziono pliku eksportu products_export*.csv (folder skryptu ani ../Sklep).")
        return 1
    print("Wejście: %s" % os.path.abspath(sciezka))

    with open(sciezka, encoding="utf-8-sig", newline="") as f:
        czytnik = csv.DictReader(f)
        brak = [k for k in ("@id", KOL_NAZWA, KOL_OPIS) if k not in (czytnik.fieldnames or [])]
        if brak:
            print("Brak kolumn w eksporcie: %s" % ", ".join(brak))
            return 1
        wiersze = list(czytnik)

    nazwa_eksportu = os.path.splitext(os.path.basename(sciezka))[0]
    sklep = nazwa_eksportu.split("-")[1] if nazwa_eksportu.count("-") >= 1 else "sklep"
    znacznik = datetime.now().strftime("%Y-%m-%d_%H.%M")
    wyjscie = os.path.join(FOLDER, "empik_nazwy_opisy_%s_%s.csv" % (sklep, znacznik))

    z_linkami = 0
    linkow = 0
    puste = []
    with open(wyjscie, "w", encoding="utf-8", newline="") as f:
        # Jak w eksporcie IdoSell: nagłówek bez cudzysłowów, wartości w cudzysłowach, LF.
        f.write(",".join(NAGLOWKI) + "\n")
        pisarz = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        for w in wiersze:
            opis, n = usun_linki(w[KOL_OPIS])
            if n:
                z_linkami += 1
                linkow += n
            if not w[KOL_NAZWA].strip() or not opis.strip():
                puste.append(w["@id"])
            pisarz.writerow([
                w["@id"],
                w[KOL_NAZWA], SITE_ID, SERVICE_ID,
                opis, SITE_ID, SERVICE_ID,
            ])

    print("Towarów: %d" % len(wiersze))
    print("Towarów z usuniętymi linkami: %d (linków: %d)" % (z_linkami, linkow))
    if puste:
        print("UWAGA - pusta nazwa lub opis dla @id: %s" % ", ".join(puste))
    print("Wyjście: %s" % wyjscie)
    return 0


if __name__ == "__main__":
    kod = main()
    if len(sys.argv) <= 1:
        input("\nNaciśnij Enter, aby zamknąć...")
    sys.exit(kod)
