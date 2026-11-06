# -*- coding: utf-8 -*-
"""
Eksport produktów IdoSell (XML IOF) -> szablon Amazon (flat file .xlsm).

Użycie:
    python amazon_szablon.py [folder_klienta]

Folder klienta musi zawierać:
    - products_export-*.xml   (eksport z panelu IdoSell; brany najnowszy)
    - *.xlsm                  (szablon pobrany z Seller Central)
    - konfiguracja.json       (ustawienia klienta, patrz MagniCreatix/konfiguracja.json)

Wynik (w folderze klienta):
    - Amazon_<klient>_<data>.xlsm   kopia szablonu z wierszami produktów
    - raport_<data>.csv             braki, ostrzeżenia, tytuły przed/po

Dane wpisywane są bezpośrednio do XML arkusza „Szablon”, dzięki czemu makra,
listy rozwijane i formatowanie warunkowe szablonu pozostają nietknięte.
Tylko biblioteka standardowa.
"""

import csv
import datetime
import glob
import html
import json
import os
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

IAIEXT = '{http://www.iai-shop.com/developers/iof/extensions.phtml}'
NS_MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
NS_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

KRAJE = {'PL': 'Polska', 'CN': 'Chiny', 'DE': 'Niemcy', 'CZ': 'Czechy'}

AKCJA_PELNA = 'Utwórz lub zastąp (pełna aktualizacja)'
AKCJA_CZESCIOWA = 'Edytuj (częściowa aktualizacja)'

LIMIT_TYTUL = 200
LIMIT_OPIS = 2000
LIMIT_PUNKTOR = 500
LICZBA_PUNKTOROW = 5
LICZBA_ZDJEC_DODATKOWYCH = 8
FORMATY_ZDJEC = {'jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'}


# ---------------------------------------------------------------- pomocnicze

def wypisz(tekst):
    """print odporny na konsolę Windows bez UTF-8."""
    try:
        print(tekst)
    except UnicodeEncodeError:
        print(tekst.encode('ascii', 'replace').decode('ascii'))


def html_na_tekst(fragment):
    """Usuwa znaczniki HTML, zamienia encje, scala białe znaki."""
    if not fragment:
        return ''
    t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', fragment)
    t = re.sub(r'(?i)</(h[1-6]|li)>', ' \x01 ', t)   # znacznik końca nagłówka/punktu
    t = re.sub(r'(?i)<br\s*/?>|</(p|div|tr)>', ' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t).replace('\xa0', ' ')
    t = re.sub(r'\s+', ' ', t)
    # po nagłówku/punkcie bez interpunkcji dodaj kropkę, żeby zdania się nie zlewały
    t = re.sub(r'([^\s.!?:;,])\s*\x01', r'\1.', t)
    t = re.sub(r'\s*\x01', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def wyczysc_punktor(tekst):
    tekst = tekst.strip().rstrip(',;.').strip()
    return tekst[:1].upper() + tekst[1:] if tekst else tekst


def przytnij(tekst, limit):
    """Przycina do limitu na granicy zdania, a gdy się nie da - słowa."""
    if len(tekst) <= limit:
        return tekst
    wycinek = tekst[:limit]
    koniec = max(wycinek.rfind('. '), wycinek.rfind('! '), wycinek.rfind('? '))
    if koniec > limit * 0.6:
        return wycinek[:koniec + 1].strip()
    spacja = wycinek.rfind(' ')
    return (wycinek[:spacja] if spacja > 0 else wycinek).rstrip(' ,;:-–')


def liczba(wartosc):
    """'1330' -> 1330.0; puste/0/niepoprawne -> None."""
    try:
        v = float(str(wartosc).replace(',', '.'))
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def format_liczby(v):
    return ('%.3f' % v).rstrip('0').rstrip('.')


def kolumna_litera(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


# ---------------------------------------------------------------- tytuły

def normalizuj_tytul(nazwa, konf):
    """Zasady z ANALIZA_amazon-szablon.md p. 4."""
    t = nazwa
    uwagi = []
    if re.search(r'(?i)gratis', t):
        t = re.sub(r'(?i)\s*\+\s*\d*\s*gratis!?', '', t)
        t = re.sub(r'(?i)\s*\bgratis\b!?', '', t)
        uwagi.append('usunięto GRATIS')
    lego = bool(re.search(r'(?i)\blego\b', t))
    if lego:
        t = re.sub(r'(?i)\s*kompatybilne\s+z\s+lego\s*®?', ' ', t)
        t = re.sub(r'(?i)\s*\blego\b\s*®?', ' ', t)
        uwagi.append('LEGO® przeniesione do punktora')
    t = t.replace('™', '').replace('®', '')

    marka = konf['marka']
    wyjatki = {w.upper() for w in konf.get('slowa_wielkie', [])} | {marka.upper()}

    def zamien(m):
        slowo = m.group(0)
        if slowo.upper() == marka.upper():
            return marka
        if slowo.upper() in wyjatki:
            return slowo.upper()
        if len(slowo) >= 2 and slowo.isupper():
            return slowo.lower()
        return slowo

    t = re.sub(r'[^\W\d_]+', zamien, t)
    t = re.sub(r'\s+', ' ', t).strip(' -–,')
    t = re.sub(r'\s+([,.])', r'\1', t)
    if t:
        t = t[0].upper() + t[1:]
    if len(t) > LIMIT_TYTUL:
        t = przytnij(t, LIMIT_TYTUL)
        uwagi.append('tytuł przycięty do %d znaków' % LIMIT_TYTUL)
    return t, lego, uwagi


def liczba_elementow(nazwa):
    """'68 el.' / '180el.' / '6 szt.' (+ 'N GRATIS') -> int lub None."""
    m = re.search(r'(\d+)\s*(?:el\b\.?|elementów|szt\b\.?)', nazwa, re.I)
    if not m:
        return None
    n = int(m.group(1))
    g = re.search(r'\+\s*(\d+)\s*gratis', nazwa, re.I)
    if g:
        n += int(g.group(1))
    return n


# ---------------------------------------------------------------- odczyt XML

def wczytaj_produkty(sciezka_xml):
    produkty = []
    for _, el in ET.iterparse(sciezka_xml, events=('end',)):
        if el.tag != 'product':
            continue
        produkty.append(produkt_na_slownik(el))
        el.clear()
    return produkty


def produkt_na_slownik(p):
    rozmiar = p.find('sizes/size')
    opis = p.find('description')
    parametry = {}
    for par in p.findall('parameters/parameter'):
        wartosci = [v.get('name') for v in par.findall('value')]
        parametry[par.get('name')] = wartosci[0] if wartosci else ''
    # Oryginały, bo wersje 'large' IdoSell to WebP, którego Amazon nie przyjmuje.
    zdjecia = sorted(
        p.findall('images/%soriginals/%simage' % (IAIEXT, IAIEXT)) or p.findall('images/large/image'),
        key=lambda i: int(i.get(IAIEXT + 'priority') or 999))
    urle = [i.get('url') for i in zdjecia if i.get('url')]
    zdjecia_ok = [u for u in urle if u.rsplit('.', 1)[-1].lower() in FORMATY_ZDJEC]
    long_desc = opis.findtext('long_desc') if opis is not None else ''
    gwarancja = p.find('warranty')
    return {
        'id': p.get('id'),
        'sku': rozmiar.get('code') if rozmiar is not None else '',
        'ean': (rozmiar.get('code_producer') if rozmiar is not None else None)
               or p.get('code_on_card') or '',
        'kod_zewn': rozmiar.get(IAIEXT + 'code_external') if rozmiar is not None else '',
        'liczba_rozmiarow': len(p.findall('sizes/size')),
        'nazwa': (opis.findtext('name') if opis is not None else '') or '',
        'long_desc': long_desc or '',
        'short_desc': (opis.findtext('short_desc') if opis is not None else '') or '',
        'producent': p.find('producer').get('name') if p.find('producer') is not None else '',
        'kraj': p.get(IAIEXT + 'country_of_origin') or '',
        'waga_brutto': liczba(rozmiar.get('weight')) if rozmiar is not None else None,
        'waga_netto': liczba(rozmiar.get(IAIEXT + 'weight_net')) if rozmiar is not None else None,
        'parametry': parametry,
        'zdjecia': zdjecia_ok,
        'zdjecia_odrzucone': len(urle) - len(zdjecia_ok),
        'gwarancja': gwarancja.get('name') if gwarancja is not None else '',
    }


def punktory_z_opisu(long_desc):
    wyniki = []
    for li in re.findall(r'(?is)<li\b[^>]*>(.*?)</li>', long_desc):
        tekst = wyczysc_punktor(przytnij(html_na_tekst(li), LIMIT_PUNKTOR))
        if len(tekst) >= 3 and tekst not in wyniki:
            wyniki.append(tekst)
    return wyniki


def ean_poprawny(kod):
    if not re.fullmatch(r'\d{13}', kod or ''):
        return False
    suma = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(kod[:12]))
    return (10 - suma % 10) % 10 == int(kod[12])


# ---------------------------------------------------------------- mapowanie

def zbuduj_wiersz(pr, konf):
    """Zwraca (słownik atrybut->wartość, lista uwag, tytuł po normalizacji)."""
    w = {}
    uwagi = []

    w['contribution_sku#1.value'] = pr['sku']
    w['product_type#1.value'] = konf['typ_produktu']
    czesciowa = pr['sku'] in set(konf.get('sku_czesciowa_aktualizacja', []))
    w['::record_action'] = AKCJA_CZESCIOWA if czesciowa else AKCJA_PELNA
    if not czesciowa and konf.get('pomin_oferte_dla_nowych', True):
        w['skip_offer#1.value'] = 'Tak'

    tytul, lego, u = normalizuj_tytul(pr['nazwa'], konf)
    uwagi += u
    w['item_name#1.value'] = tytul
    w['brand#1.value'] = konf['marka']
    w['manufacturer#1.value'] = konf['marka']

    if ean_poprawny(pr['ean']):
        w['amzn1.volt.ca.product_id_type'] = 'EAN'
        w['amzn1.volt.ca.product_id_value'] = pr['ean']
    else:
        uwagi.append('BRAK poprawnego EAN (%s)' % (pr['ean'] or 'pusty'))

    if pr['kod_zewn']:
        w['model_number#1.value'] = pr['kod_zewn']
        w['part_number#1.value'] = pr['kod_zewn']

    if pr['zdjecia']:
        w['main_product_image_locator#1.media_location'] = pr['zdjecia'][0]
        for i, url in enumerate(pr['zdjecia'][1:1 + LICZBA_ZDJEC_DODATKOWYCH], start=1):
            w['other_product_image_locator_%d#1.media_location' % i] = url
    else:
        uwagi.append('BRAK zdjęć w formacie JPG/PNG')
    if pr['zdjecia_odrzucone']:
        uwagi.append('pominięto %d zdjęć WebP (Amazon nie przyjmuje)' % pr['zdjecia_odrzucone'])

    opis = przytnij(html_na_tekst(pr['long_desc']) or html_na_tekst(pr['short_desc']), LIMIT_OPIS)
    if opis:
        w['product_description#1.value'] = opis
    else:
        uwagi.append('BRAK opisu')

    punktory = punktory_z_opisu(pr['long_desc'])
    if lego:
        punktory.insert(0, konf.get('punktor_lego', 'Kompatybilne z klockami LEGO®'))
    if not punktory and pr['short_desc']:
        punktory = [przytnij(html_na_tekst(pr['short_desc']), LIMIT_PUNKTOR)]
    for i, tekst in enumerate(punktory[:LICZBA_PUNKTOROW], start=1):
        w['bullet_point#%d.value' % i] = tekst
    if not punktory:
        uwagi.append('BRAK punktorów')

    kraj = KRAJE.get(pr['kraj'].upper()) if pr['kraj'] else None
    if not kraj:
        kraj = konf.get('kraj_domyslny')
        uwagi.append('kraj pochodzenia nieznany w IdoSell, przyjęto: %s' % kraj)
    w['country_of_origin#1.value'] = kraj

    if pr['id'] in set(konf.get('id_z_bateriami', [])):
        uwagi.append('BRAK „Przepisy dot. towarów niebezpiecznych” - produkt prawdopodobnie z bateriami')
    else:
        w['supplier_declared_dg_hz_regulation#1.value'] = 'Nie dotyczy'

    elementy = liczba_elementow(pr['nazwa'])
    if elementy:
        w['number_of_pieces#1.value'] = elementy
    else:
        uwagi.append('liczba elementów nieznana (brak w nazwie)')
    w['number_of_items#1.value'] = 1
    w['item_package_quantity#1.value'] = 1
    w['condition_type#1.value'] = konf.get('stan', 'Nowy nowy')
    if konf.get('rodzaj_klockow'):
        w['toy_building_block_type#1.value'] = konf['rodzaj_klockow']
    if pr['gwarancja']:
        w['warranty_description#1.value'] = pr['gwarancja']

    wymiary = konf.get('parametry_wymiarow', {})
    pelne = True
    for os_, nazwa_par in wymiary.items():
        v = liczba(pr['parametry'].get(nazwa_par))
        if v:
            w['item_package_dimensions#1.%s.value' % os_] = format_liczby(v)
            w['item_package_dimensions#1.%s.unit' % os_] = 'Centymetry'
        else:
            pelne = False
    if not pelne:
        uwagi.append('BRAK pełnych wymiarów opakowania')

    if pr['waga_brutto']:
        w['item_package_weight#1.value'] = format_liczby(pr['waga_brutto'] / 1000)
        w['item_package_weight#1.unit'] = 'Kilogramy'
    else:
        uwagi.append('BRAK wagi opakowania')
    if pr['waga_netto']:
        w['item_weight#1.value'] = format_liczby(pr['waga_netto'] / 1000)
        w['item_weight#1.unit'] = 'Kilogramy'

    if pr['liczba_rozmiarow'] != 1:
        uwagi.append('produkt ma %d rozmiary - wzięto tylko pierwszy' % pr['liczba_rozmiarow'])

    return w, uwagi, tytul


# ---------------------------------------------------------------- xlsm

def znajdz_arkusz(zf, nazwa):
    wb = ET.fromstring(zf.read('xl/workbook.xml'))
    rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    cele = {r.get('Id'): r.get('Target') for r in rels}
    for sh in wb.iter('{%s}sheet' % NS_MAIN):
        if sh.get('name') == nazwa:
            cel = cele[sh.get('{%s}id' % NS_REL)].lstrip('/')
            return cel if cel.startswith('xl/') else 'xl/' + cel
    raise SystemExit('Nie znaleziono arkusza „%s” w szablonie.' % nazwa)


def wspolne_teksty(zf):
    if 'xl/sharedStrings.xml' not in zf.namelist():
        return []
    root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    return [''.join(t.text or '' for t in si.iter('{%s}t' % NS_MAIN))
            for si in root.findall('{%s}si' % NS_MAIN)]


def odczytaj_wiersz(xml_arkusza, nr, teksty):
    """Mapa nr kolumny -> wartość dla wiersza nr (bez parsowania całego arkusza)."""
    m = re.search(r'<row [^>]*\br="%d"[^>]*>(.*?)</row>' % nr, xml_arkusza, re.S)
    if not m:
        return {}
    wynik = {}
    for c in re.finditer(r'<c r="([A-Z]+)%d"([^>]*?)(?:/>|>(.*?)</c>)' % nr, m.group(1), re.S):
        kol, atr, srodek = c.group(1), c.group(2), c.group(3) or ''
        v = re.search(r'<v>(.*?)</v>', srodek, re.S)
        if 't="s"' in atr and v:
            wart = teksty[int(v.group(1))]
        elif v:
            wart = html.unescape(v.group(1))
        else:
            wart = html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', srodek, re.S)))
        n = 0
        for ch in kol:
            n = n * 26 + ord(ch) - 64
        wynik[n] = wart
    return wynik


def klucz_atrybutu(nazwa):
    return re.sub(r'\[(marketplace_id|language_tag)=[^\]]*\]', '', nazwa)


def komorka(ref, wartosc):
    if isinstance(wartosc, (int, float)) and not isinstance(wartosc, bool):
        return '<c r="%s"><v>%s</v></c>' % (ref, wartosc)
    tekst = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', str(wartosc))
    return '<c r="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, escape(tekst))


def zapisz_xlsm(szablon, wyjscie, wiersze_danych):
    """wiersze_danych: lista słowników atrybut->wartość. Zwraca zbiór nieznanych atrybutów."""
    with zipfile.ZipFile(szablon) as zf:
        sciezka = znajdz_arkusz(zf, 'Szablon')
        xml_arkusza = zf.read(sciezka).decode('utf-8')
        teksty = wspolne_teksty(zf)
        ustawienia = odczytaj_wiersz(xml_arkusza, 1, teksty).get(1, '')

        wiersz_atr = int(re.search(r'attributeRow=(\d+)', ustawienia).group(1))
        wiersz_start = int(re.search(r'dataRow=(\d+)', ustawienia).group(1))
        atrybuty = odczytaj_wiersz(xml_arkusza, wiersz_atr, teksty)
        mapa = {klucz_atrybutu(nazwa): kol for kol, nazwa in atrybuty.items()}

        nieznane = set()
        nowe = []
        for i, dane in enumerate(wiersze_danych):
            nr = wiersz_start + i
            komorki = []
            for atr, wart in dane.items():
                if wart in (None, ''):
                    continue
                kol = mapa.get(atr)
                if kol is None:
                    nieznane.add(atr)
                    continue
                komorki.append((kol, komorka('%s%d' % (kolumna_litera(kol), nr), wart)))
            komorki.sort()
            nowe.append('<row r="%d">%s</row>' % (nr, ''.join(k for _, k in komorki)))

        if re.search(r'<row [^>]*\br="%d"' % wiersz_start, xml_arkusza):
            raise SystemExit('Szablon ma już dane od wiersza %d - użyj czystego szablonu.' % wiersz_start)
        xml_arkusza = xml_arkusza.replace('</sheetData>', ''.join(nowe) + '</sheetData>', 1)
        ostatni = wiersz_start + len(wiersze_danych) - 1
        xml_arkusza = re.sub(
            r'<dimension ref="A1:([A-Z]+)\d+"',
            lambda m: '<dimension ref="A1:%s%d"' % (m.group(1), max(ostatni, wiersz_start - 1)),
            xml_arkusza, count=1)

        with zipfile.ZipFile(wyjscie, 'w', zipfile.ZIP_DEFLATED) as out:
            for info in zf.infolist():
                dane = xml_arkusza.encode('utf-8') if info.filename == sciezka else zf.read(info.filename)
                out.writestr(info, dane)
    return nieznane


# ---------------------------------------------------------------- main

def main():
    folder = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    with open(os.path.join(folder, 'konfiguracja.json'), encoding='utf-8') as f:
        konf = json.load(f)

    xmle = sorted(glob.glob(os.path.join(folder, 'products_export-*.xml')), key=os.path.getmtime)
    if not xmle:
        raise SystemExit('Brak pliku products_export-*.xml w %s' % folder)
    sciezka_xml = xmle[-1]
    szablon = os.path.join(folder, konf['szablon'])
    if not os.path.isfile(szablon):
        raise SystemExit('Brak szablonu %s' % szablon)

    wypisz('Eksport:  %s' % os.path.basename(sciezka_xml))
    wypisz('Szablon:  %s' % os.path.basename(szablon))

    produkty = wczytaj_produkty(sciezka_xml)
    dzis = datetime.date.today().isoformat()
    wyjscie = os.path.join(folder, 'Amazon_%s_%s.xlsm' % (konf['klient'], dzis))
    raport = os.path.join(folder, 'raport_%s.csv' % dzis)

    wiersze, wiersze_raportu = [], []
    for pr in produkty:
        dane, uwagi, tytul = zbuduj_wiersz(pr, konf)
        wiersze.append(dane)
        wiersze_raportu.append({
            'id': pr['id'], 'sku': pr['sku'], 'ean': pr['ean'],
            'akcja': dane['::record_action'],
            'tytul_idosell': pr['nazwa'], 'tytul_amazon': tytul,
            'liczba_zdjec': len(pr['zdjecia']),
            'liczba_punktorow': sum(1 for k in dane if k.startswith('bullet_point')),
            'uwagi': ' | '.join(uwagi),
        })

    nieznane = zapisz_xlsm(szablon, wyjscie, wiersze)

    with open(raport, 'w', newline='', encoding='utf-8-sig') as f:
        pisz = csv.DictWriter(f, fieldnames=list(wiersze_raportu[0].keys()), delimiter=',')
        pisz.writeheader()
        pisz.writerows(wiersze_raportu)

    wypisz('Produkty: %d (pełna aktualizacja: %d, częściowa: %d)' % (
        len(wiersze),
        sum(1 for w in wiersze if w['::record_action'] == AKCJA_PELNA),
        sum(1 for w in wiersze if w['::record_action'] == AKCJA_CZESCIOWA)))
    if nieznane:
        wypisz('UWAGA: atrybuty nieobecne w szablonie (pominięte): %s' % ', '.join(sorted(nieznane)))
    wypisz('Plik:     %s' % wyjscie)
    wypisz('Raport:   %s' % raport)


if __name__ == '__main__':
    main()
