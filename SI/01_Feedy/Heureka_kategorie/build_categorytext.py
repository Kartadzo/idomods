# -*- coding: utf-8 -*-
"""
Budowa bloku CATEGORYTEXT dla feedu Heureka na podstawie raportów z app.py.

Skrypt składa trzy szablony XSLT 1.0 i wstawia je do arkusza feedu:

  idosell-category-to-heureka   category/@id (menu sklepu)      -> ID kategorii Heureka
  google-category-to-heureka    ID taksonomii Google            -> ID kategorii Heureka
  heureka-id-to-path            ID kategorii Heureka            -> ścieżka CATEGORYTEXT

Ścieżka ma postać "Heureka.sk | <segment> | <kategoria>" -- segment i nazwa
pochodzą z pliku "povinné názvy <lang>". Pełne drzewo Heureki (z poziomami
pośrednimi) nie jest dostępne w tym folderze, patrz NOTATKI_kategorie_heureka.md.

Wejście (szukane w katalogu skryptu, bez argumentów):
  raport_idosell_<lang>.csv        -- mapowanie kategorii menu sklepu
  raport_google_<lang>.csv         -- mapowanie taksonomii Google
  povinné názvy <lang> - *.csv     -- segment + nazwa kategorii Heureka
  <arkusz feedu>.xml               -- XSLT feedu, do którego wstawiamy blok

Wyjście:
  heureka_categorytext.xslt        -- same szablony, do podglądu
  <arkusz feedu>.xml               -- podmieniony blok między znacznikami
                                      HEUREKA-MAP:START / HEUREKA-MAP:END
                                      (kopia zapasowa: <arkusz>.xml.bak)
"""

import csv
import glob
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ZNACZNIK_START = "<!-- HEUREKA-MAP:START -->"
ZNACZNIK_KONIEC = "<!-- HEUREKA-MAP:END -->"

# Usługi porównywarek w IOF, które posługują się ID taksonomii Google.
SERVICE_ID_GOOGLE = ("73", "123", "124")


def escape(tekst):
    return (tekst.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def wybierz(pytanie, kandydaci):
    """Jeden kandydat -- bierzemy bez pytania. Więcej -- pytamy."""
    if not kandydaci:
        return None
    if len(kandydaci) == 1:
        print("%s %s" % (pytanie, os.path.basename(kandydaci[0])))
        return kandydaci[0]
    print("\n%s" % pytanie)
    for i, sciezka in enumerate(kandydaci, 1):
        print("  %d) %s" % (i, os.path.basename(sciezka)))
    while True:
        odp = input("Numer [1]: ").strip() or "1"
        if odp.isdigit() and 1 <= int(odp) <= len(kandydaci):
            return kandydaci[int(odp) - 1]
        print("Nie ma takiej pozycji.")


def czytaj_raport(sciezka):
    """Zwraca listę par (source_id, heureka_id) dla wierszy z dopasowaniem."""
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        wiersze = list(csv.DictReader(plik, delimiter=";"))
    pary = []
    widziane = set()
    for wiersz in wiersze:
        zrodlo = (wiersz.get("source_id") or "").strip()
        heureka = (wiersz.get("heureka_id") or "").strip()
        if not zrodlo or not heureka or zrodlo in widziane:
            continue
        widziane.add(zrodlo)
        pary.append((zrodlo, heureka, (wiersz.get("source_leaf") or "").strip()))
    return pary


def czytaj_kategorie_heureka(sciezka):
    """ID kategorii Heureka -> (segment, nazwa)."""
    mapa = {}
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        czytnik = csv.reader(plik)
        next(czytnik, None)
        for wiersz in czytnik:
            if len(wiersz) < 3:
                continue
            ident = wiersz[1].strip()
            if not ident.isdigit():
                continue
            mapa[ident] = (wiersz[0].strip(), wiersz[2].strip())
    return mapa


def szablon_id_na_id(nazwa, parametr, pary, kategorie, opis):
    linie = ['   <xsl:template name="%s">' % nazwa,
             '      <xsl:param name="%s"/>' % parametr,
             '      <xsl:choose>']
    pominiete = 0
    for zrodlo, heureka, lisc in pary:
        if heureka not in kategorie:
            pominiete += 1
            continue
        komentarz = "%s -> %s" % (lisc or zrodlo, kategorie[heureka][1])
        linie.append('         <xsl:when test="$%s = \'%s\'">%s</xsl:when><!-- %s -->'
                     % (parametr, zrodlo, heureka, escape(komentarz)))
    linie.append('         <xsl:otherwise/><!-- brak dopasowania -->')
    linie.append('      </xsl:choose>')
    linie.append('   </xsl:template>')
    if pominiete:
        print("  %s: pominięto %d wpisów bez nazwy kategorii Heureka" % (opis, pominiete))
    return "\n".join(linie)


def szablon_sciezki(uzyte, kategorie, sklep):
    linie = ['   <xsl:template name="heureka-id-to-path">',
             '      <xsl:param name="heureka_id"/>',
             '      <xsl:choose>']
    for heureka in sorted(uzyte, key=int):
        segment, nazwa = kategorie[heureka]
        czlony = [sklep]
        if segment and segment != "#N/A":
            czlony.append(segment)
        czlony.append(nazwa)
        linie.append('         <xsl:when test="$heureka_id = \'%s\'">%s</xsl:when>'
                     % (heureka, escape(" | ".join(czlony))))
    linie.append('         <xsl:otherwise/><!-- ID spoza mapowania -->')
    linie.append('      </xsl:choose>')
    linie.append('   </xsl:template>')
    return "\n".join(linie)


def zbuduj_blok(pary_idosell, pary_google, kategorie, sklep):
    uzyte = set()
    for zbior in (pary_idosell, pary_google):
        for _, heureka, _ in zbior:
            if heureka in kategorie:
                uzyte.add(heureka)

    naglowek = (
        "   %s\n"
        "   <!--\n"
        "     Mapowanie kategorii na kategorie Heureka. Blok generowany skryptem\n"
        "     build_categorytext.py, nie edytować ręcznie: zmiany nadpisze generator.\n"
        "     Wpisy: menu sklepu %d, taksonomia Google %d, ścieżki Heureka %d.\n"
        "   -->" % (ZNACZNIK_START, len(pary_idosell), len(pary_google), len(uzyte))
    )
    czesci = [
        naglowek,
        szablon_id_na_id("idosell-category-to-heureka", "category_id",
                         pary_idosell, kategorie, "menu sklepu"),
        szablon_id_na_id("google-category-to-heureka", "google_id",
                         pary_google, kategorie, "taksonomia Google"),
        szablon_sciezki(uzyte, kategorie, sklep),
        "   %s" % ZNACZNIK_KONIEC,
    ]
    return "\n\n".join(czesci), len(uzyte)


def wstaw_do_arkusza(sciezka, blok):
    # newline="" -- czytamy i zapisujemy bez tłumaczenia końców linii; arkusze
    # feedów bywają w CRLF i generator nie ma prawa tego zmieniać.
    with open(sciezka, encoding="utf-8", newline="") as plik:
        tresc = plik.read()

    with open(sciezka + ".bak", "w", encoding="utf-8", newline="") as plik:
        plik.write(tresc)

    koniec_linii = "\r\n" if "\r\n" in tresc else "\n"
    blok = blok.replace("\n", koniec_linii)

    if ZNACZNIK_START in tresc and ZNACZNIK_KONIEC in tresc:
        wzorzec = re.compile(
            re.escape(ZNACZNIK_START) + ".*?" + re.escape(ZNACZNIK_KONIEC),
            re.DOTALL)
        nowa = wzorzec.sub(lambda _: blok.strip(), tresc, count=1)
        akcja = "podmieniono"
    else:
        pozycja = tresc.rfind("</xsl:stylesheet>")
        if pozycja < 0:
            raise SystemExit("W pliku %s nie ma </xsl:stylesheet>." % sciezka)
        nowa = (tresc[:pozycja] + koniec_linii + blok
                + koniec_linii + koniec_linii + tresc[pozycja:])
        akcja = "dodano"

    with open(sciezka, "w", encoding="utf-8", newline="") as plik:
        plik.write(nowa)
    return akcja


def main():
    raporty_idosell = sorted(glob.glob(os.path.join(BASE_DIR, "raport_idosell_*.csv")))
    raporty_google = sorted(glob.glob(os.path.join(BASE_DIR, "raport_google_*.csv")))
    kategorie_csv = sorted(glob.glob(os.path.join(BASE_DIR, "povinn* - *.csv")))
    arkusze = sorted(glob.glob(os.path.join(BASE_DIR, "*.xml")))

    plik_idosell = wybierz("Raport kategorii sklepu:", raporty_idosell)
    plik_google = wybierz("Raport taksonomii Google:", raporty_google)
    plik_kategorii = wybierz("Kategorie Heureka (segment + nazwa):", kategorie_csv)
    plik_arkusza = wybierz("Arkusz feedu do uzupełnienia:", arkusze)

    if not (plik_idosell or plik_google) or not plik_kategorii or not plik_arkusza:
        raise SystemExit("Brak kompletu plików wejściowych w katalogu skryptu.")

    jezyk = "SK" if "SK" in os.path.basename(plik_kategorii).upper() else "CZ"
    sklep = "Heureka.sk" if jezyk == "SK" else "Heureka.cz"

    kategorie = czytaj_kategorie_heureka(plik_kategorii)
    pary_idosell = czytaj_raport(plik_idosell) if plik_idosell else []
    pary_google = czytaj_raport(plik_google) if plik_google else []

    print("\nKategorie Heureka (%s): %d" % (sklep, len(kategorie)))
    blok, liczba_sciezek = zbuduj_blok(pary_idosell, pary_google, kategorie, sklep)

    wyjscie = os.path.join(BASE_DIR, "heureka_categorytext.xslt")
    with open(wyjscie, "w", encoding="utf-8", newline="") as plik:
        plik.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<xsl:stylesheet version="1.0" '
                   'xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n\n')
        plik.write(blok)
        plik.write("\n\n</xsl:stylesheet>\n")

    akcja = wstaw_do_arkusza(plik_arkusza, blok)

    print("\nMenu sklepu -> Heureka:      %d wpisów" % len(pary_idosell))
    print("Taksonomia Google -> Heureka: %d wpisów" % len(pary_google))
    print("Ścieżki CATEGORYTEXT:         %d wpisów" % liczba_sciezek)
    print("\nSzablony: %s" % os.path.basename(wyjscie))
    print("Arkusz:   %s (blok %s, kopia .bak obok)"
          % (os.path.basename(plik_arkusza), akcja))
    print("\nID kategorii Google w feedzie bierzemy z price_comparison"
          " o service_id %s." % ", ".join(SERVICE_ID_GOOGLE))


if __name__ == "__main__":
    main()
    input("\nGotowe. Enter kończy.")
