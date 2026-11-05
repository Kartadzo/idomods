#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kopiowanie szablonu sterownika XSLT i podmiana wartości zmiennych globalnych.

Użycie:
    python konfiguruj.py zmienne <szablon>
        wypisuje zmienne globalne szablonu (nazwa, forma zapisu, wartość) jako JSON
    python konfiguruj.py utworz <konfiguracja.json>
        kopiuje szablon do folderu konfiguracji i podmienia zmienne oraz teksty

<szablon> to nazwa pliku z xslt/szablony/ (np. Google.xml) albo ścieżka.

Szablon źródłowy jest tylko czytany. Logika sterownika nie jest zmieniana:
podmieniane są wyłącznie wartości zmiennych najwyższego poziomu
(dzieci xsl:stylesheet) oraz dosłowne teksty z sekcji "teksty".
"""

import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

from lxml import etree

# Katalog repozytorium Domino: pierwszy folder w górę drzewa, który zawiera xslt/szablony.
KATALOG_REPO = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(KATALOG_REPO, 'xslt', 'szablony')) and os.path.dirname(KATALOG_REPO) != KATALOG_REPO:
    KATALOG_REPO = os.path.dirname(KATALOG_REPO)
KATALOG_SZABLONOW = os.path.join(KATALOG_REPO, 'xslt', 'szablony')
XSL_NS = 'http://www.w3.org/1999/XSL/Transform'

# <xsl:variable name='X'>wartość</xsl:variable>  |  <xsl:variable name="X" select="..." />
WZORZEC_ZMIENNEJ = re.compile(
    r'<xsl:variable\s+name\s*=\s*(["\'])(?P<nazwa>[^"\']+)\1\s*'
    r'(?:'
    r'select\s*=\s*"(?P<select>[^"]*)"\s*/>'
    r'|'
    r'>(?P<tresc>.*?)</xsl:variable>'
    r')',
    re.S)


def sciezka_szablonu(szablon):
    if os.path.isfile(szablon):
        return os.path.abspath(szablon)
    sciezka = os.path.join(KATALOG_SZABLONOW, szablon)
    if os.path.isfile(sciezka):
        return sciezka
    raise SystemExit('Nie znaleziono szablonu: %s' % szablon)


def wczytaj(sciezka):
    # newline='' zachowuje oryginalne końce linii (CRLF/LF)
    with open(sciezka, 'r', encoding='utf-8', newline='') as plik:
        return plik.read()


def zmienne_globalne(tekst):
    """Zwraca listę zmiennych najwyższego poziomu z pozycją dopasowania w tekście."""
    try:
        korzen = etree.fromstring(tekst.encode('utf-8'))
    except etree.XMLSyntaxError as blad:
        raise SystemExit('Szablon nie jest poprawnym XML — popraw go przed użyciem: %s' % blad)

    # lxml podaje linię końca znacznika otwierającego, więc dla zmiennej
    # zapisanej w kilku liniach bierzemy ostatnie dopasowanie zaczynające się nie później
    kandydaci = {}
    for kandydat in WZORZEC_ZMIENNEJ.finditer(tekst):
        linia = tekst.count('\n', 0, kandydat.start()) + 1
        kandydaci.setdefault(kandydat.group('nazwa'), []).append((linia, kandydat))

    wynik = []
    for element in korzen:
        if element.tag != '{%s}variable' % XSL_NS:
            continue
        nazwa = element.get('name')
        dopasowanie = None
        for linia, kandydat in kandydaci.get(nazwa, []):
            if linia <= element.sourceline:
                dopasowanie = kandydat
        if dopasowanie is None:
            raise SystemExit('Nie udało się odnaleźć zmiennej %s (linia %s)' % (nazwa, element.sourceline))
        if dopasowanie.group('select') is not None:
            select = dopasowanie.group('select')
            if len(select) >= 2 and select[0] == "'" and select[-1] == "'":
                forma, wartosc = 'select_tekst', select[1:-1]
            else:
                forma, wartosc = 'select_wyrazenie', select
        elif len(element):
            # zmienna z elementami potomnymi (np. xsl:choose) — nie podmieniamy
            forma, wartosc = 'zlozona', None
        else:
            forma, wartosc = 'tresc', dopasowanie.group('tresc')
        wynik.append({
            'nazwa': nazwa,
            'linia': element.sourceline,
            'forma': forma,
            'wartosc': wartosc,
            'span': dopasowanie.span(),
            'dopasowanie': dopasowanie,
        })
    return wynik


def nowy_zapis(zmienna, wartosc):
    dopasowanie = zmienna['dopasowanie']
    stary = dopasowanie.group(0)
    if zmienna['forma'] == 'tresc':
        if '<' in wartosc or '&' in wartosc:
            wartosc = wartosc.replace('&', '&amp;').replace('<', '&lt;')
        poczatek = stary[:stary.index('>') + 1]
        return poczatek + wartosc + '</xsl:variable>'
    if zmienna['forma'] == 'select_tekst':
        if "'" in wartosc or '"' in wartosc:
            raise SystemExit('Zmienna %s: wartość w select nie może zawierać cudzysłowów' % zmienna['nazwa'])
        nowy_select = "'" + wartosc + "'"
    else:
        nowy_select = wartosc
    return stary.replace('select="%s"' % dopasowanie.group('select'), 'select="%s"' % nowy_select, 1)


def opis_wersji(sciezka):
    with open(sciezka, 'rb') as plik:
        skrot = hashlib.sha256(plik.read()).hexdigest()[:12]
    zmodyfikowano = datetime.datetime.fromtimestamp(os.path.getmtime(sciezka)).strftime('%Y-%m-%d %H:%M')
    try:
        commit = subprocess.run(
            ['git', 'log', '-1', '--format=%h %cs', '--', sciezka],
            cwd=KATALOG_REPO, capture_output=True, text=True, encoding='utf-8').stdout.strip()
        zmiany_lokalne = subprocess.run(
            ['git', 'status', '--porcelain', '--', sciezka],
            cwd=KATALOG_REPO, capture_output=True, text=True, encoding='utf-8').stdout.strip()
    except OSError:
        commit, zmiany_lokalne = '', ''
    return {
        'plik': os.path.relpath(sciezka, KATALOG_REPO).replace('\\', '/'),
        'sha256': skrot,
        'zmodyfikowano': zmodyfikowano,
        'commit': commit or 'brak',
        'niezatwierdzone_zmiany': bool(zmiany_lokalne),
    }


def polecenie_zmienne(szablon):
    sciezka = sciezka_szablonu(szablon)
    zmienne = zmienne_globalne(wczytaj(sciezka))
    wynik = {
        'szablon': opis_wersji(sciezka),
        'zmienne': [{k: z[k] for k in ('nazwa', 'linia', 'forma', 'wartosc')} for z in zmienne],
    }
    print(json.dumps(wynik, ensure_ascii=False, indent=2))


def polecenie_utworz(sciezka_konfiguracji):
    sciezka_konfiguracji = os.path.abspath(sciezka_konfiguracji)
    katalog = os.path.dirname(sciezka_konfiguracji)
    with open(sciezka_konfiguracji, 'r', encoding='utf-8') as plik:
        konfiguracja = json.load(plik)

    sciezka = sciezka_szablonu(konfiguracja['szablon'])
    tekst = wczytaj(sciezka)
    zmienne = {z['nazwa']: z for z in zmienne_globalne(tekst)}

    bledy = []
    podmiany = []
    raport = []
    for nazwa, wartosc in konfiguracja.get('zmienne', {}).items():
        wartosc = '' if wartosc is None else str(wartosc)
        if nazwa not in zmienne:
            bledy.append('Brak zmiennej w szablonie: %s' % nazwa)
            continue
        zmienna = zmienne[nazwa]
        if zmienna['forma'] == 'zlozona':
            bledy.append('Zmienna %s ma złożoną treść — zmień ją ręcznie w kopii' % nazwa)
            continue
        if '|' in wartosc and re.search(r'(?<![!<>])=\s*\$%s(?![\w.\-])' % re.escape(nazwa), tekst):
            # szablon porównuje zmienną jako pojedynczą wartość (@name = $X / @id = $X),
            # więc lista |id|nazwa| nie zostanie dopasowana
            bledy.append('Zmienna %s: ta wersja szablonu porównuje ją jako jedną wartość (= $%s) — '
                         'lista "%s" nie zadziała; podaj pojedyncze ID albo nazwę' % (nazwa, nazwa, wartosc))
            continue
        if zmienna['wartosc'] == wartosc:
            raport.append((nazwa, zmienna['wartosc'], wartosc, 'bez zmian'))
            continue
        podmiany.append((zmienna['span'], nowy_zapis(zmienna, wartosc)))
        raport.append((nazwa, zmienna['wartosc'], wartosc, 'zmieniono'))

    if bledy:
        raise SystemExit('\n'.join(bledy))

    # podmiana od końca, żeby nie przesuwać pozycji wcześniejszych dopasowań
    for (start, koniec), nowy in sorted(podmiany, key=lambda p: p[0][0], reverse=True):
        tekst = tekst[:start] + nowy + tekst[koniec:]

    raport_tekstow = []
    for zamiana in konfiguracja.get('teksty', []):
        stary, nowy = zamiana['z'], zamiana['na']
        oczekiwane = zamiana.get('ile')
        liczba = tekst.count(stary)
        if liczba == 0 or (oczekiwane is not None and liczba != oczekiwane):
            raise SystemExit('Tekst "%s": znaleziono %d wystąpień, oczekiwano %s' % (stary, liczba, oczekiwane or '≥1'))
        tekst = tekst.replace(stary, nowy)
        raport_tekstow.append((stary, nowy, liczba))

    # kontrola: wynik nadal jest poprawnym XML
    etree.fromstring(tekst.encode('utf-8'))

    wyjscie = os.path.join(katalog, konfiguracja['wyjscie'])
    with open(wyjscie, 'w', encoding='utf-8', newline='') as plik:
        plik.write(tekst)

    wersja = opis_wersji(sciezka)
    linie = [
        '# Raport konfiguracji — %s' % konfiguracja['wyjscie'],
        '',
        '- Wygenerowano: %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        '- Szablon: `%s` (commit %s, zmodyfikowano %s, sha256 %s%s)' % (
            wersja['plik'], wersja['commit'], wersja['zmodyfikowano'], wersja['sha256'],
            ', z niezatwierdzonymi zmianami' if wersja['niezatwierdzone_zmiany'] else ''),
        '',
        '## Zmienne',
        '',
        '| Zmienna | Szablon | Sterownik | Status |',
        '|---|---|---|---|',
    ]
    for nazwa, stara, nowa, status in raport:
        linie.append('| `%s` | `%s` | `%s` | %s |' % (nazwa, stara, nowa, status))
    if raport_tekstow:
        linie += ['', '## Teksty', '', '| Z | Na | Wystąpień |', '|---|---|---|']
        for stary, nowy, liczba in raport_tekstow:
            linie.append('| `%s` | `%s` | %d |' % (stary, nowy, liczba))
    with open(os.path.join(katalog, 'raport_konfiguracji.md'), 'w', encoding='utf-8') as plik:
        plik.write('\n'.join(linie) + '\n')

    zmienione = sum(1 for r in raport if r[3] == 'zmieniono')
    print('Zapisano: %s' % wyjscie)
    print('Zmienne: %d zmienionych, %d bez zmian; teksty: %d' % (zmienione, len(raport) - zmienione, len(raport_tekstow)))


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('zmienne', 'utworz'):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == 'zmienne':
        polecenie_zmienne(sys.argv[2])
    else:
        polecenie_utworz(sys.argv[2])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
