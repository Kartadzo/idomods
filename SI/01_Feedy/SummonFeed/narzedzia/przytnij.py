#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usuwanie ze sterownika elementów wyjściowych, których serwis nie obsługuje.

Użycie:
    python przytnij.py <sterownik.xml> --dozwolone g:id,g:title,...  [--rekord item]
                       [--zostaw-szablony] [--proba]

Sterownik jest nadpisywany (kopia, nie szablon źródłowy!). Z --proba tylko wypisuje,
co zostałoby usunięte.

Usuwa:
  1. elementy dzieci rekordu (xsl:element name="g:…" i literalne <g:…>) spoza listy
     dozwolonych, wraz z komentarzami stojącymi bezpośrednio przed nimi,
  2. puste po usunięciu xsl:if / xsl:for-each oraz xsl:choose z samymi pustymi gałęziami,
  3. zmienne lokalne, do których nic się już nie odwołuje,
  4. nazwane szablony, których nic już nie wywołuje (chyba że --zostaw-szablony).
Kroki 2–4 powtarza do ustalenia się wyniku. Zmienne globalne (konfiguracja) zostają.
Elementy zagnieżdżone w dozwolonych (np. g:country w g:shipping) nie są sprawdzane.
"""

import argparse
import re
import sys

from lxml import etree

XSL_NS = 'http://www.w3.org/1999/XSL/Transform'
G_NS = 'http://base.google.com/ns/1.0'
XSL = '{%s}' % XSL_NS
KONTENERY = [XSL + n for n in ('if', 'for-each', 'choose')]


def nazwa_wyjsciowa(element):
    """Nazwa elementu wyjściowego w zapisie z prefiksem (g:title) albo None."""
    if element.tag == XSL + 'element':
        return element.get('name')
    if isinstance(element.tag, str) and not element.tag.startswith(XSL):
        qname = etree.QName(element)
        if qname.namespace == G_NS:
            return 'g:' + qname.localname
        if qname.namespace is None:
            return qname.localname
    return None


def usun(element):
    """Usuwa element razem z jego wierszem (wcięcie przejmuje poprzedni węzeł)."""
    rodzic = element.getparent()
    poprzedni = element.getprevious()
    ogon = element.tail
    if poprzedni is not None:
        poprzedni.tail = ogon
    else:
        rodzic.text = ogon
    rodzic.remove(element)


def usun_z_komentarzami(element):
    usuniete = []
    poprzedni = element.getprevious()
    while poprzedni is not None and poprzedni.tag is etree.Comment and not (poprzedni.tail or '').strip():
        nastepny = poprzedni.getprevious()
        usuniete.append(poprzedni)
        poprzedni = nastepny
    usun(element)
    for komentarz in usuniete:
        usun(komentarz)


def czy_pusty(element):
    """Pusty = brak tekstu i elementów (komentarze się nie liczą).
    xsl:choose jest pusty dopiero, gdy puste są wszystkie jego gałęzie — pojedynczej
    pustej gałęzi when nie usuwamy, bo zmieniłoby to, która gałąź się wykona."""
    if element.tag == XSL + 'choose':
        return all(czy_pusty(galaz) for galaz in element if isinstance(galaz.tag, str))
    if (element.text or '').strip():
        return False
    for dziecko in element:
        if (dziecko.tail or '').strip():
            return False
        if dziecko.tag is not etree.Comment:
            return False
    return True


def odwolania(drzewo):
    """Zbiór nazw zmiennych użytych w wyrażeniach ($nazwa) w całym sterowniku."""
    nazwy = set()
    for element in drzewo.iter():
        if not isinstance(element.tag, str):
            continue
        for wartosc in element.attrib.values():
            nazwy.update(re.findall(r'\$([\w.\-]+)', wartosc))
    return nazwy


def przytnij(drzewo, dozwolone, rekord, zostaw_szablony):
    raport = {'elementy': [], 'kontenery': 0, 'zmienne': [], 'szablony': []}
    korzen = drzewo.getroot()

    # 1. elementy wyjściowe rekordu leżą w nim samym albo w nazwanych szablonach
    #    wywoływanych z rekordu — usuwamy te, nad którymi nie ma innego elementu wyjściowego
    for element in list(korzen.iter()):
        if not isinstance(element.tag, str) or element.getparent() is None:
            continue
        nazwa = nazwa_wyjsciowa(element)
        if nazwa is None or nazwa == rekord or nazwa in dozwolone:
            continue
        # tylko elementy najwyższego poziomu rekordu: żaden przodek nie jest elementem wyjściowym
        przodek = element.getparent()
        zagniezdzony = False
        while przodek is not None:
            nazwa_przodka = nazwa_wyjsciowa(przodek)
            if nazwa_przodka is not None and nazwa_przodka != rekord:
                zagniezdzony = True
                break
            przodek = przodek.getparent()
        if zagniezdzony:
            continue
        if not nazwa.startswith('g:'):
            # elementy bez prefiksu g: (np. struktura rss/channel) nie są ruszane
            continue
        raport['elementy'].append('%s (linia %s)' % (nazwa, element.sourceline))
        usun_z_komentarzami(element)

    zmiana = True
    while zmiana:
        zmiana = False
        # 2. puste kontenery
        for element in list(korzen.iter(*KONTENERY)):
            if element.getparent() is not None and czy_pusty(element):
                usun_z_komentarzami(element)
                raport['kontenery'] += 1
                zmiana = True
        # 3. nieużywane zmienne lokalne
        uzyte = odwolania(drzewo)
        for element in list(korzen.iter(XSL + 'variable')):
            if element.getparent() is korzen:
                continue
            if element.get('name') not in uzyte:
                raport['zmienne'].append(element.get('name'))
                usun_z_komentarzami(element)
                zmiana = True
        # 4. niewywoływane nazwane szablony
        if not zostaw_szablony:
            wywolane = {e.get('name') for e in korzen.iter(XSL + 'call-template')}
            for element in list(korzen.findall(XSL + 'template')):
                if element.get('name') and not element.get('match') and element.get('name') not in wywolane:
                    raport['szablony'].append(element.get('name'))
                    usun_z_komentarzami(element)
                    zmiana = True
    return raport


def main():
    parser = argparse.ArgumentParser(description='Usuwanie nieobsługiwanych elementów ze sterownika')
    parser.add_argument('sterownik')
    parser.add_argument('--dozwolone', required=True)
    parser.add_argument('--rekord', default='item')
    parser.add_argument('--zostaw-szablony', action='store_true')
    parser.add_argument('--proba', action='store_true')
    argumenty = parser.parse_args()

    if 'xslt/szablony' in argumenty.sterownik.replace('\\', '/'):
        raise SystemExit('To jest szablon źródłowy — przycinam tylko kopie w sterowniki/<domena>/')

    dozwolone = {n.strip() for n in argumenty.dozwolone.split(',') if n.strip()}
    parser_xml = etree.XMLParser(strip_cdata=False, remove_blank_text=False)
    drzewo = etree.parse(argumenty.sterownik, parser_xml)
    raport = przytnij(drzewo, dozwolone, argumenty.rekord, argumenty.zostaw_szablony)

    print('Usunięte elementy (%d):' % len(raport['elementy']))
    for wpis in raport['elementy']:
        print('  ' + wpis)
    print('Usunięte puste kontenery: %d' % raport['kontenery'])
    print('Usunięte zmienne lokalne (%d): %s' % (len(raport['zmienne']), ', '.join(raport['zmienne'])))
    print('Usunięte nazwane szablony (%d): %s' % (len(raport['szablony']), ', '.join(raport['szablony'])))

    if argumenty.proba:
        print('Tryb próby — plik bez zmian.')
        return
    with open(argumenty.sterownik, 'wb') as plik:
        plik.write(etree.tostring(drzewo, encoding='utf-8'))
    print('Zapisano: %s' % argumenty.sterownik)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
