#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raport danych dostępnych w ofercie IOF IdoSell (/offer/products/product).

Użycie:
    python parametry_oferty.py <oferta.xml> [<raport.md>]

Plik czytany strumieniowo (iterparse), więc działa także dla dużych ofert.
Raport zawiera: parametry (nazwa, id, kontekst, liczba produktów, przykładowe
wartości), magazyny, języki, waluty, flagi hotspotów, grupy wariantów,
nazwy dla porównywarek, przykładowe adresy kart produktu.
Domyślnie raport trafia obok oferty jako parametry_<nazwa oferty>.md.
"""

import collections
import os
import sys
import xml.etree.ElementTree as ET

IAIEXT = '{http://www.iai-shop.com/developers/iof/extensions.phtml}'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
MAKS_PRZYKLADOW = 8


def lokalna(tag):
    return tag.split('}', 1)[1] if '}' in tag else tag


def analizuj(sciezka):
    parametry = collections.OrderedDict()
    magazyny = collections.Counter()
    jezyki = collections.Counter()
    waluty = collections.Counter()
    typy = collections.Counter()
    flagi = collections.Counter()
    karty = []
    statystyki = collections.Counter()

    kontekst = ET.iterparse(sciezka, events=('start', 'end'))
    for zdarzenie, element in kontekst:
        if zdarzenie == 'start':
            if element.tag == 'products' and element.get('language'):
                jezyki['products/@language=' + element.get('language')] += 1
            continue
        if element.tag != 'product':
            continue

        statystyki['produkty'] += 1
        typy[element.get('type', '')] += 1
        waluty[element.get('currency', '')] += 1

        rozmiary = element.findall('sizes/size')
        statystyki['rozmiary'] += len(rozmiary)
        if len(rozmiary) > 1:
            statystyki['produkty z >1 rozmiarem'] += 1
        if element.find('group') is not None:
            statystyki['produkty z group/@id'] += 1
        if any(r.get('code_producer') for r in rozmiary):
            statystyki['produkty z code_producer (GTIN)'] += 1
        if element.find('price/price_marketplace_site/delivery_cost') is not None:
            statystyki['produkty z delivery_cost (profil dostaw)'] += 1
        if element.find('strikethrough_retail_price') is not None or element.find('sizes/size/strikethrough_retail_price') is not None:
            statystyki['produkty z ceną przekreśloną'] += 1

        for nazwa in element.iter(IAIEXT + 'pricecomparator_name'):
            jezyki['pricecomparator_name@' + (nazwa.get(XML_LANG) or '?')] += 1
            break
        for nazwa in element.findall('description/name'):
            jezyki['description/name@' + (nazwa.get(XML_LANG) or 'bez xml:lang')] += 1

        for magazyn in element.iter('stock'):
            magazyny[magazyn.get('id')] += 1

        for flaga in element.iter('flag'):
            if flaga.get('visible') == 'yes':
                flagi[flaga.get('type')] += 1

        karta = element.find('card')
        if karta is not None and len(karty) < 3:
            karty.append(karta.get('url'))

        for parametr in element.findall('parameters/parameter'):
            klucz = (parametr.get('id'), parametr.get('name'))
            wpis = parametry.get(klucz)
            if wpis is None:
                wpis = parametry[klucz] = {
                    'typ': parametr.get('type', ''),
                    'kontekst': set(),
                    'ukryty': collections.Counter(),
                    'produkty': 0,
                    'wartosci': collections.Counter(),
                }
            wpis['produkty'] += 1
            wpis['ukryty'][parametr.get('hide', '')] += 1
            if parametr.get('context_id'):
                wpis['kontekst'].add(parametr.get('context_id'))
            for wartosc in parametr.findall('value'):
                wpis['wartosci'][wartosc.get('name') or wartosc.get('id') or ''] += 1
                if wartosc.get('context_value_id'):
                    wpis['kontekst'].add('wartość:' + wartosc.get('context_value_id'))

        element.clear()

    return {
        'parametry': parametry, 'magazyny': magazyny, 'jezyki': jezyki,
        'waluty': waluty, 'typy': typy, 'flagi': flagi, 'karty': karty,
        'statystyki': statystyki,
    }


def komorka(tekst):
    return str(tekst).replace('|', '\\|').replace('\n', ' ')


def raport(dane, sciezka):
    linie = ['# Dane dostępne w ofercie — %s' % os.path.basename(sciezka), '']
    linie.append('## Podsumowanie')
    for klucz, wartosc in dane['statystyki'].items():
        linie.append('- %s: %d' % (klucz, wartosc))
    linie.append('- typy produktów: %s' % ', '.join('%s (%d)' % kv for kv in dane['typy'].items()))
    linie.append('- waluty: %s' % ', '.join('%s (%d)' % kv for kv in dane['waluty'].items()))
    linie.append('- języki: %s' % ', '.join('%s (%d)' % kv for kv in dane['jezyki'].items()))
    linie.append('- magazyny (stock/@id → wystąpień): %s' % ', '.join('%s (%d)' % kv for kv in sorted(dane['magazyny'].items(), key=lambda kv: int(kv[0] or 0))))
    linie.append('- widoczne flagi hotspotów: %s' % (', '.join('%s (%d)' % kv for kv in dane['flagi'].items()) or 'brak'))
    for url in dane['karty']:
        linie.append('- przykład card/@url: `%s`' % url)

    linie += ['', '## Parametry', '',
              '| ID | Nazwa | Typ | Kontekst | Produktów | hide | Przykładowe wartości |',
              '|---|---|---|---|---|---|---|']
    for (identyfikator, nazwa), wpis in sorted(dane['parametry'].items(), key=lambda kv: -kv[1]['produkty']):
        przyklady = ', '.join('%s (%d)' % kv for kv in wpis['wartosci'].most_common(MAKS_PRZYKLADOW))
        if len(wpis['wartosci']) > MAKS_PRZYKLADOW:
            przyklady += ' … (%d wartości)' % len(wpis['wartosci'])
        linie.append('| %s | %s | %s | %s | %d | %s | %s |' % (
            komorka(identyfikator), komorka(nazwa), komorka(wpis['typ']),
            komorka(', '.join(sorted(wpis['kontekst']))), wpis['produkty'],
            komorka(', '.join('%s:%d' % kv for kv in wpis['ukryty'].items())), komorka(przyklady)))
    return '\n'.join(linie) + '\n'


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    oferta = os.path.abspath(sys.argv[1])
    wyjscie = sys.argv[2] if len(sys.argv) == 3 else os.path.join(
        os.path.dirname(oferta), 'parametry_%s.md' % os.path.splitext(os.path.basename(oferta))[0])
    dane = analizuj(oferta)
    with open(wyjscie, 'w', encoding='utf-8') as plik:
        plik.write(raport(dane, oferta))
    print('Produktów: %d, parametrów: %d' % (dane['statystyki']['produkty'], len(dane['parametry'])))
    print('Zapisano: %s' % wyjscie)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
