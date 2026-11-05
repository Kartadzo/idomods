#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weryfikacja sterownika XSLT 1.0 na próbce oferty IOF.

Użycie:
    python weryfikuj.py <sterownik.xml> [--oferta <oferta.xml>] [--wymagane g:id,g:title,...]
                        [--element item] [--wynik <podglad.xml>]

Sprawdza:
  1. poprawność XML i kompilację przez libxslt (XSLT 1.0, lxml),
  2. użycie funkcji/instrukcji spoza XSLT 1.0 (ostrzeżenia),
  3. transformację próbki oferty (domyślnie SI/01_Feedy/SummonFeed/dane/products_export.xml),
  4. pozostałe placeholdery 00000 w wyniku,
  5. obecność i niepustość elementów wymaganych w każdym rekordzie (--element, domyślnie item),
  6. z --dozwolone: brak elementów, których serwis nie obsługuje.
Kod wyjścia 0 = brak błędów (ostrzeżenia dopuszczalne).
"""

import argparse
import collections
import os
import re
import sys

from lxml import etree

# Katalog repozytorium Domino: pierwszy folder w górę drzewa, który zawiera xslt/szablony.
KATALOG_REPO = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(KATALOG_REPO, 'xslt', 'szablony')) and os.path.dirname(KATALOG_REPO) != KATALOG_REPO:
    KATALOG_REPO = os.path.dirname(KATALOG_REPO)
DOMYSLNA_OFERTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dane', 'products_export.xml')
G_NS = 'http://base.google.com/ns/1.0'

# funkcje XPath 2.0+ i instrukcje XSLT 2.0+, których libxslt nie obsłuży
POZA_XSLT1 = [
    r'\b(tokenize|matches|replace|upper-case|lower-case|string-join|ends-with|'
    r'format-date|format-dateTime|current-date|current-dateTime|distinct-values|'
    r'exists|empty|index-of|reverse|subsequence|max|min|avg|abs|'
    r'normalize-unicode|codepoints-to-string|string-to-codepoints|'
    r'xs:[a-zA-Z]+)\s*\(',
    r'<xsl:(for-each-group|function|sequence|analyze-string|matching-substring|'
    r'non-matching-substring|result-document|next-match|perform-sort|try|catch|iterate)\b',
]


def wyrazenia_xpath(tekst):
    """Zwraca wartości atrybutów XPath (select, test, match, use) — tam szukamy funkcji 2.0."""
    return re.findall(r'\b(?:select|test|match|use)\s*=\s*"([^"]*)"', tekst) + \
        re.findall(r"\b(?:select|test|match|use)\s*=\s*'([^']*)'", tekst)


def nazwa_elementu(nazwa):
    if nazwa.startswith('g:'):
        return '{%s}%s' % (G_NS, nazwa[2:])
    return nazwa


def main():
    parser = argparse.ArgumentParser(description='Weryfikacja sterownika XSLT 1.0')
    parser.add_argument('sterownik')
    parser.add_argument('--oferta', default=DOMYSLNA_OFERTA)
    parser.add_argument('--wymagane', default='g:id,g:title,g:description,g:link,g:image_link,g:price,g:availability')
    parser.add_argument('--element', default='item', help='nazwa rekordu w wyniku (item, o, SHOPITEM…)')
    parser.add_argument('--dozwolone', help='lista elementów obsługiwanych przez serwis; inne w rekordzie = błąd')
    parser.add_argument('--wynik', help='zapis wyniku transformacji (domyślnie podglad_wyniku.xml obok sterownika)')
    argumenty = parser.parse_args()

    bledy, ostrzezenia = [], []

    with open(argumenty.sterownik, 'r', encoding='utf-8') as plik:
        tekst = plik.read()

    try:
        dokument = etree.fromstring(tekst.encode('utf-8'))
    except etree.XMLSyntaxError as blad:
        print('BŁĄD: sterownik nie jest poprawnym XML: %s' % blad)
        sys.exit(1)

    bez_komentarzy = re.sub(r'<!--.*?-->', '', tekst, flags=re.S)
    xpath = ' '.join(wyrazenia_xpath(bez_komentarzy))
    for wzorzec in POZA_XSLT1:
        zrodlo = bez_komentarzy if wzorzec.startswith('<') else xpath
        for trafienie in sorted(set(m.group(0) for m in re.finditer(wzorzec, zrodlo))):
            ostrzezenia.append('Konstrukcja spoza XSLT 1.0: %s' % trafienie)
    if '00000' in bez_komentarzy:
        ostrzezenia.append('Sterownik zawiera placeholder 00000 (%d wystąpień)' % bez_komentarzy.count('00000'))

    try:
        transformacja = etree.XSLT(dokument)
    except etree.XSLTParseError as blad:
        print('BŁĄD: kompilacja XSLT nie powiodła się: %s' % blad)
        for wpis in blad.error_log:
            print('  linia %s: %s' % (wpis.line, wpis.message))
        sys.exit(1)

    oferta = etree.parse(argumenty.oferta)
    try:
        wynik = transformacja(oferta)
    except etree.XSLTApplyError as blad:
        print('BŁĄD: transformacja nie powiodła się: %s' % blad)
        sys.exit(1)
    for wpis in transformacja.error_log:
        ostrzezenia.append('Komunikat procesora: %s' % wpis.message)

    sciezka_wyniku = argumenty.wynik or os.path.join(os.path.dirname(os.path.abspath(argumenty.sterownik)), 'podglad_wyniku.xml')
    wynik.write_output(sciezka_wyniku)
    with open(sciezka_wyniku, 'r', encoding='utf-8') as plik:
        tekst_wyniku = plik.read()

    try:
        korzen = etree.fromstring(tekst_wyniku.encode('utf-8'))
    except etree.XMLSyntaxError as blad:
        print('BŁĄD: wynik nie jest poprawnym XML: %s' % blad)
        sys.exit(1)

    if '00000' in tekst_wyniku:
        bledy.append('Wynik zawiera placeholder 00000 (%d wystąpień)' % tekst_wyniku.count('00000'))

    rekordy = korzen.findall('.//' + nazwa_elementu(argumenty.element))
    produkty = len(oferta.findall('/products/product'))
    if not rekordy:
        bledy.append('Brak rekordów <%s> w wyniku' % argumenty.element)

    wymagane = [w.strip() for w in argumenty.wymagane.split(',') if w.strip()]
    braki = collections.Counter()
    puste = collections.Counter()
    for rekord in rekordy:
        for nazwa in wymagane:
            if nazwa.startswith('@'):
                wartosc = rekord.get(nazwa[1:])
                if wartosc is None:
                    braki[nazwa] += 1
                elif not wartosc.strip():
                    puste[nazwa] += 1
                continue
            element = rekord.find(nazwa_elementu(nazwa))
            if element is None:
                braki[nazwa] += 1
            elif not ''.join(element.itertext()).strip():
                puste[nazwa] += 1

    elementy = collections.Counter()
    for rekord in rekordy:
        for dziecko in rekord:
            if isinstance(dziecko.tag, str):
                elementy[etree.QName(dziecko).localname] += 1

    print('Sterownik: %s' % argumenty.sterownik)
    print('Oferta: %s (%d produktów)' % (argumenty.oferta, produkty))
    print('Wynik: %s (%d rekordów <%s>)' % (sciezka_wyniku, len(rekordy), argumenty.element))
    print('Elementy w rekordach (nazwa: liczba rekordów):')
    for nazwa, liczba in sorted(elementy.items()):
        print('  %s: %d' % (nazwa, liczba))
    if argumenty.dozwolone:
        dozwolone = {n.strip().split(':')[-1] for n in argumenty.dozwolone.split(',') if n.strip()}
        nadmiarowe = sorted(set(elementy) - dozwolone)
        if nadmiarowe:
            bledy.append('Elementy nieobsługiwane przez serwis (usuń przez przytnij.py): %s' % ', '.join(nadmiarowe))
    for nazwa in wymagane:
        if braki[nazwa] or puste[nazwa]:
            bledy.append('Wymagane %s: brak w %d, puste w %d z %d rekordów' % (nazwa, braki[nazwa], puste[nazwa], len(rekordy)))
    for ostrzezenie in ostrzezenia:
        print('OSTRZEŻENIE: %s' % ostrzezenie)
    for blad in bledy:
        print('BŁĄD: %s' % blad)
    print('Wynik weryfikacji: %s' % ('OK' if not bledy else 'BŁĘDY (%d)' % len(bledy)))
    sys.exit(1 if bledy else 0)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
