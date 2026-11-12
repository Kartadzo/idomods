# -*- coding: utf-8 -*-
"""
Porównanie i walidacja pliku szablonu Amazon (.xlsm, arkusz „Szablon”).

Porównuje naszą wersję pliku z wersją odesłaną przez klienta i sprawdza
wersję klienta względem pustego szablonu Amazon (definicje pól, listy
dozwolonych wartości) oraz wymagań GPSR dla zabawek.

Użycie:
    python porownaj_amazon.py --nasz NASZ.xlsm --klient KLIENT.xlsm
        [--szablon SZABLON.xlsm] [--wyjscie FOLDER] [--data RRRR-MM-DD]

Bez argumentów pyta o ścieżki (Enter = wartość domyślna).

Wynik (w folderze --wyjscie):
    weryfikacja_<data>.md   podsumowanie
    zmiany_klientki.csv     różnice komórka po komórce (SKU, kolumna, nasza, klienta, typ)
    uwagi_per_sku.csv       błędy walidacji, ostrzeżenia i braki GPSR

Wymaga: openpyxl.
"""

import argparse
import csv
import datetime
import hashlib
import os
import re
import sys
import warnings
import zipfile
from collections import Counter, OrderedDict
from urllib.parse import parse_qs

try:
    import openpyxl
except ImportError:
    print("Brak biblioteki openpyxl. Zainstaluj: python -m pip install openpyxl")
    sys.exit(1)

warnings.filterwarnings("ignore")

ARKUSZ = "Szablon"

# Limity długości (Amazon PL, wartości ostrożne)
LIMITY = {
    "item_name": 200,
    "bullet_point": 500,
    "product_description": 2000,
    "generic_keyword": 250,
}

# Słowa pisane wielkimi literami dopuszczalne w tekstach (marki, skróty)
WIELKIE_DOZWOLONE = {"MAGNICREATIX", "KIDIBOTS", "LED", "ABS", "MABS", "USB", "AAA", "AA", "XL", "XXL", "3D", "DIY",
                     "STEM", "STEAM", "GPSR", "UE", "EU", "BPA", "EN71", "ASTM", "CPSC", "CE", "PVC"}

# Kraje UE (nazwy jak w liście Amazon) – poza nimi wymagana osoba odpowiedzialna w UE
KRAJE_UE = {"Austria", "Belgia", "Bułgaria", "Chorwacja", "Cypr", "Czechy", "Dania", "Estonia", "Finlandia",
            "Francja", "Grecja", "Hiszpania", "Holandia", "Irlandia", "Litwa", "Luksemburg", "Łotwa", "Malta",
            "Niemcy", "Polska", "Portugalia", "Rumunia", "Słowacja", "Słowenia", "Szwecja", "Węgry", "Włochy"}

# Kolumny liczbowe sprawdzane pod kątem wartości zastępczych (ta sama wartość, przeciągnięta seria)
KOLUMNY_LICZBOWE = ("item_weight", "item_package_weight", "item_dimensions", "item_package_dimensions")

# Słowa w tytule wskazujące na produkt z bateriami
SLOWA_BATERIE = ("robot", "kidibots", "świec", "swiec", "led", "bateri", "akumul")

# Punkty GPSR: (numer, nazwa, lista prefiksów atrybutów)
GPSR = [
    ("1", "Wiek", ["manufacturer_minimum_age", "compliance_recommended_age",
                   "eu_toys_safety_directive_age_warning", "age_range_description"]),
    ("2", "Ostrzeżenia", ["eu_toys_safety_directive_warning", "safety_warning",
                          "eu_toys_safety_directive_language"]),
    ("3", "Materiał", ["material["]),
    ("4", "Producent", ["manufacturer[", "gpsr_manufacturer_reference"]),
    ("5", "Osoba odpowiedzialna w UE", ["dsa_responsible_party_address"]),
    ("6", "Baterie", ["batteries_required", "batteries_included", "num_batteries",
                      "contains_battery_or_cell", "battery["]),
    ("7", "Waga i wymiary", ["item_package_dimensions", "item_package_weight",
                             "item_weight", "item_dimensions"]),
    ("+", "Kraj pochodzenia", ["country_of_origin"]),
    ("+", "Atest bezpieczeństwa GPSR", ["gpsr_safety_attestation"]),
]


# ---------------------------------------------------------------- odczyt

class PlikAmazon:
    """Arkusz „Szablon” jednego pliku: nagłówki, wiersze danych, ustawienia."""

    def __init__(self, sciezka):
        self.sciezka = sciezka
        wb = openpyxl.load_workbook(sciezka, read_only=True, data_only=True)
        self.arkusze = wb.sheetnames
        if ARKUSZ not in self.arkusze:
            raise ValueError("Brak arkusza „%s” w %s" % (ARKUSZ, sciezka))
        wiersze = [list(r) for r in wb[ARKUSZ].iter_rows(values_only=True)]
        self.ustawienia = self._ustawienia(wiersze[0][0] if wiersze and wiersze[0] else "")
        self.wiersz_etykiet = int(self.ustawienia.get("labelRow", 4))
        self.wiersz_atrybutow = int(self.ustawienia.get("attributeRow", 5))
        self.wiersz_danych = int(self.ustawienia.get("dataRow", 7))
        self.szerokosc = max((len(r) for r in wiersze), default=0)
        self.wiersze = [r + [None] * (self.szerokosc - len(r)) for r in wiersze]
        self.naglowki = self.wiersze[:self.wiersz_danych - 1]
        self.etykiety = self.wiersze[self.wiersz_etykiet - 1]
        self.atrybuty = self.wiersze[self.wiersz_atrybutow - 1]
        self.dane = [r for r in self.wiersze[self.wiersz_danych - 1:] if any(v not in (None, "") for v in r)]
        self.wb = wb

    @staticmethod
    def _ustawienia(tekst):
        tekst = str(tekst or "")
        if not tekst.startswith("settings="):
            return {}
        q = parse_qs(tekst[len("settings="):])
        return {k: v[0] for k, v in q.items()}

    def wg_sku(self):
        wynik = OrderedDict()
        for nr, r in enumerate(self.dane):
            sku = tekst(r[0])
            if sku:
                wynik[sku] = (self.wiersz_danych + nr, r)
        return wynik


def tekst(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def rowne(a, b):
    ta, tb = tekst(a), tekst(b)
    if ta == tb:
        return True
    try:
        return abs(float(ta.replace(",", ".")) - float(tb.replace(",", "."))) < 1e-9
    except ValueError:
        return False


def czytaj_definicje(wb):
    """Słownik atrybut -> stopień wymagalności z arkusza „Definicje danych”."""
    wynik = {}
    if "Definicje danych" not in wb.sheetnames:
        return wynik
    for r in wb["Definicje danych"].iter_rows(values_only=True):
        if len(r) >= 6 and r[1] and r[1] != "Nazwa pola":
            wynik[str(r[1])] = tekst(r[5])
    return wynik


def czytaj_listy(wb):
    """Słownik atrybut -> zbiór dozwolonych wartości z arkusza „Dropdown Lists”."""
    wynik = {}
    if "Dropdown Lists" not in wb.sheetnames:
        return wynik
    dl = [list(r) for r in wb["Dropdown Lists"].iter_rows(values_only=True)]
    if len(dl) < 4:
        return wynik
    szer = max(len(r) for r in dl)
    for j in range(szer):
        atr = dl[2][j] if j < len(dl[2]) else None
        if not atr:
            continue
        wart = {tekst(r[j]) for r in dl[3:] if j < len(r) and tekst(r[j])}
        if wart:
            wynik.setdefault(str(atr), set()).update(wart)
    return wynik


def info_pliku(sciezka):
    """Rozmiar, lista części zip i skrót makr (vbaProject.bin)."""
    info = {"rozmiar": os.path.getsize(sciezka), "vba": None, "czesci": []}
    with zipfile.ZipFile(sciezka) as z:
        info["czesci"] = sorted(z.namelist())
        for n in info["czesci"]:
            if n.endswith("vbaProject.bin"):
                info["vba"] = hashlib.sha1(z.read(n)).hexdigest()
    return info


# ---------------------------------------------------------------- walidacja

def ean_ok(kod):
    if not re.fullmatch(r"\d{13}", kod):
        return False
    suma = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(kod[:12]))
    return (10 - suma % 10) % 10 == int(kod[12])


def baza_atrybutu(atr):
    return re.split(r"[\[#]", str(atr or ""), 1)[0]


def slowa_wielkie(t):
    slowa = re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9]+", t)
    return [s for s in slowa if len(s) >= 3 and s.isupper() and any(c.isalpha() for c in s)
            and s not in WIELKIE_DOZWOLONE]


def waliduj(plik, kanon, definicje, listy):
    """Lista uwag: (wiersz, sku, poziom, kolumna, atrybut, opis)."""
    uwagi = []
    wg_sku = plik.wg_sku()
    kol = {a: j for j, a in enumerate(kanon) if a}

    def wartosc(r, atr):
        j = kol.get(atr)
        return tekst(r[j]) if j is not None and j < len(r) else ""

    def dodaj(nr, sku, poziom, j, opis):
        uwagi.append((nr, sku, poziom, j + 1 if j is not None else "", kanon[j] if j is not None else "", opis))

    # Duplikaty SKU
    licz = Counter(tekst(r[0]) for r in plik.dane)
    for sku, n in licz.items():
        if sku and n > 1:
            dodaj("", sku, "BŁĄD", 0, "SKU występuje %d razy" % n)

    rodzice = {sku for sku, (_, r) in wg_sku.items()
               if wartosc(r, "parentage_level[marketplace_id=A1C3SOZRARQ6R3]#1.value") == "Rodzic"}

    for sku, (nr, r) in wg_sku.items():
        akcja = wartosc(r, "::record_action")
        pelna = not akcja or akcja.startswith("Utwórz") or akcja.startswith("(Domyślnie)")
        for j, atr in enumerate(kanon):
            if not atr:
                continue
            v = tekst(r[j]) if j < len(r) else ""
            baza = baza_atrybutu(atr)
            # wymagane
            if not v and pelna and definicje.get(atr) == "Wymagane":
                dodaj(nr, sku, "BŁĄD", j, "brak wartości w polu wymaganym (akcja: %s)" % (akcja or "domyślna"))
            if not v:
                continue
            # listy wartości
            dozw = listy.get(atr)
            if dozw and v not in dozw:
                dodaj(nr, sku, "BŁĄD", j, "wartość spoza listy dozwolonych: „%s”" % v[:80])
            # liczby i jednostki
            if atr.endswith(".value") and any(baza.startswith(p) for p in ("item_weight", "item_package_weight", "item_dimensions", "item_package_dimensions", "item_length")):
                try:
                    if float(v.replace(",", ".")) <= 0:
                        dodaj(nr, sku, "BŁĄD", j, "wartość musi być większa od zera: %s" % v)
                except ValueError:
                    dodaj(nr, sku, "BŁĄD", j, "wartość nie jest liczbą: „%s”" % v)
                jedn = atr[:-len(".value")] + ".unit"
                if jedn in kol and not wartosc(r, jedn):
                    dodaj(nr, sku, "BŁĄD", j, "brak jednostki (%s)" % jedn)
            if atr.endswith(".unit") and atr[:-len(".unit")] + ".value" in kol and not wartosc(r, atr[:-len(".unit")] + ".value"):
                dodaj(nr, sku, "UWAGA", j, "jednostka bez wartości")
            if baza in ("manufacturer_minimum_age", "manufacturer_maximum_age"):
                if not re.fullmatch(r"\d+", v):
                    dodaj(nr, sku, "BŁĄD", j, "wiek w miesiącach musi być liczbą całkowitą: „%s”" % v)
            # długości
            if baza in LIMITY and len(v) > LIMITY[baza]:
                dodaj(nr, sku, "BŁĄD", j, "za długie: %d znaków (limit %d)" % (len(v), LIMITY[baza]))
            # wielkie litery
            if baza in ("item_name", "bullet_point", "product_description"):
                wk = slowa_wielkie(v)
                if wk:
                    dodaj(nr, sku, "UWAGA", j, "słowa wielkimi literami: %s" % ", ".join(sorted(set(wk))[:10]))
        # EAN
        typ = wartosc(r, "amzn1.volt.ca.product_id_type")
        kod = wartosc(r, "amzn1.volt.ca.product_id_value")
        jk = kol.get("amzn1.volt.ca.product_id_value")
        if typ == "EAN" and kod and not ean_ok(kod):
            dodaj(nr, sku, "BŁĄD", jk, "nieprawidłowy EAN: %s" % kod)
        # rodzic–wariant
        poziom = wartosc(r, "parentage_level[marketplace_id=A1C3SOZRARQ6R3]#1.value")
        rodzic = wartosc(r, "child_parent_sku_relationship[marketplace_id=A1C3SOZRARQ6R3]#1.parent_sku")
        if poziom == "Dziecko":
            if not rodzic:
                dodaj(nr, sku, "BŁĄD", kol.get("child_parent_sku_relationship[marketplace_id=A1C3SOZRARQ6R3]#1.parent_sku"), "wariant bez SKU rodzica")
            elif rodzic not in rodzice:
                dodaj(nr, sku, "UWAGA", kol.get("child_parent_sku_relationship[marketplace_id=A1C3SOZRARQ6R3]#1.parent_sku"), "rodzica %s nie ma w pliku" % rodzic)
        if poziom and not wartosc(r, "variation_theme#1.name"):
            dodaj(nr, sku, "BŁĄD", kol.get("variation_theme#1.name"), "brak motywu wariantu przy poziomie „%s”" % poziom)
        # baterie
        tytul = wartosc(r, "item_name[marketplace_id=A1C3SOZRARQ6R3][language_tag=pl_PL]#1.value").lower()
        wym = wartosc(r, "batteries_required[marketplace_id=A1C3SOZRARQ6R3]#1.value")
        if any(s in tytul for s in SLOWA_BATERIE) and not wym:
            dodaj(nr, sku, "GPSR", kol.get("batteries_required[marketplace_id=A1C3SOZRARQ6R3]#1.value"), "produkt prawdopodobnie z bateriami, brak informacji o bateriach")
        if wym == "Tak" and not wartosc(r, "num_batteries[marketplace_id=A1C3SOZRARQ6R3]#1.type"):
            dodaj(nr, sku, "BŁĄD", kol.get("num_batteries[marketplace_id=A1C3SOZRARQ6R3]#1.type"), "baterie wymagane, brak rodzaju i liczby baterii")
        # produkt a opakowanie
        M = "[marketplace_id=A1C3SOZRARQ6R3]#1."
        wp = [liczba(wartosc(r, "item_dimensions%s%s.value" % (M, o))) for o in ("length", "width", "height")]
        wo = [liczba(wartosc(r, "item_package_dimensions%s%s.value" % (M, o))) for o in ("length", "width", "height")]
        if None not in wp and None not in wo and any(p > o + 1e-9 for p, o in zip(sorted(wp), sorted(wo))):
            dodaj(nr, sku, "BŁĄD", kol.get("item_dimensions%slength.value" % M),
                  "wymiary produktu %s większe niż opakowania %s" % ("×".join(tekst(x) for x in wp), "×".join(tekst(x) for x in wo)))
        mp = waga_kg(wartosc(r, "item_weight%svalue" % M), wartosc(r, "item_weight%sunit" % M))
        mo = waga_kg(wartosc(r, "item_package_weight%svalue" % M), wartosc(r, "item_package_weight%sunit" % M))
        if mp is not None and mo is not None and mp > mo + 1e-9:
            dodaj(nr, sku, "BŁĄD", kol.get("item_weight%svalue" % M), "waga produktu %s kg większa niż opakowania %s kg" % (tekst(mp), tekst(mo)))
        # kraj spoza UE bez osoby odpowiedzialnej
        kraj = wartosc(r, "country_of_origin%svalue" % M)
        if kraj and kraj not in KRAJE_UE and not wartosc(r, "dsa_responsible_party_address%svalue" % M):
            dodaj(nr, sku, "GPSR", kol.get("dsa_responsible_party_address%svalue" % M),
                  "kraj pochodzenia %s (spoza UE), brak osoby odpowiedzialnej w UE" % kraj)

    # wartości zastępcze w kolumnach liczbowych
    wiersze = list(wg_sku.items())
    for j, atr in enumerate(kanon):
        if not atr or not str(atr).endswith(".value") or baza_atrybutu(atr) not in KOLUMNY_LICZBOWE:
            continue
        vals = [(sku, nr, liczba(tekst(r[j]))) for sku, (nr, r) in wiersze]
        pelne = [v for v in vals if v[2] is not None]
        if len(pelne) >= 5:
            c = Counter(v[2] for v in pelne)
            wart, ile = c.most_common(1)[0]
            if ile >= 6:
                for sku, nr, v in pelne:
                    if v == wart:
                        dodaj(nr, sku, "UWAGA", j, "ta sama wartość %s w %d z %d wierszy (wartość zastępcza?)" % (tekst(v), ile, len(pelne)))
        # przeciągnięta seria: >= 4 kolejne wiersze ze stałym niezerowym krokiem
        i = 0
        while i < len(vals) - 3:
            if None in (vals[i][2], vals[i + 1][2]):
                i += 1
                continue
            krok = round(vals[i + 1][2] - vals[i][2], 9)
            k = i + 1
            while k + 1 < len(vals) and vals[k + 1][2] is not None and round(vals[k + 1][2] - vals[k][2], 9) == krok:
                k += 1
            if krok != 0 and k - i + 1 >= 4:
                for sku, nr, v in vals[i:k + 1]:
                    dodaj(nr, sku, "UWAGA", j, "seria %s, %s … co %s (przeciągnięta w Excelu?)" % (tekst(vals[i][2]), tekst(vals[i + 1][2]), tekst(krok)))
                i = k + 1
            else:
                i += 1
    return uwagi


def liczba(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def waga_kg(v, jedn):
    x = liczba(v)
    if x is None:
        return None
    mnoz = {"Kilogramy": 1, "Gramy": 0.001, "Miligramy": 0.000001, "Funty": 0.45359237, "Uncje": 0.028349523,
            "Setne funta": 0.0045359237, "Tony": 1000}.get(jedn)
    return round(x * mnoz, 6) if mnoz else None


def kontrola_gpsr(plik, kanon):
    """Dla każdego punktu GPSR: kolumny, liczba wypełnionych SKU, rozkład wartości, braki."""
    wg_sku = plik.wg_sku()
    wynik = []
    for nr, nazwa, prefiksy in GPSR:
        kolumny = [j for j, a in enumerate(kanon) if a and any(str(a).startswith(p) for p in prefiksy)]
        wypelnione, braki = [], []
        wartosci = OrderedDict()
        for sku, (_, r) in wg_sku.items():
            vals = [(kanon[j], tekst(r[j])) for j in kolumny if tekst(r[j])]
            if vals:
                wypelnione.append(sku)
                for a, v in vals:
                    wartosci.setdefault(baza_atrybutu(a), Counter())[v] += 1
            else:
                braki.append(sku)
        wynik.append({"nr": nr, "nazwa": nazwa, "kolumny": kolumny, "wypelnione": wypelnione,
                      "braki": braki, "wartosci": wartosci})
    return wynik


# ---------------------------------------------------------------- porównanie

def porownaj_naglowki(nasz, klient, kanon):
    """Różnice w wierszach nagłówków (1 .. dataRow-1), po pozycji kolumny."""
    roznice = []
    szer = max(nasz.szerokosc, klient.szerokosc)
    for i in range(min(len(nasz.naglowki), len(klient.naglowki))):
        if i == 0:
            continue  # wiersz ustawień porównywany osobno
        a = nasz.naglowki[i] + [None] * (szer - nasz.szerokosc)
        k = klient.naglowki[i] + [None] * (szer - klient.szerokosc)
        for j in range(szer):
            if not rowne(a[j], k[j]):
                roznice.append((i + 1, j + 1, kanon[j] if j < len(kanon) else "", tekst(a[j]), tekst(k[j])))
    return roznice


def porownaj_dane(nasz, klient, kanon):
    """Różnice komórka po komórce, wiersze po SKU, kolumny po pozycji."""
    zmiany = []
    a, k = nasz.wg_sku(), klient.wg_sku()
    szer = max(nasz.szerokosc, klient.szerokosc, len(kanon))
    etyk = nasz.etykiety + [None] * (szer - nasz.szerokosc)
    for sku in a:
        if sku not in k:
            zmiany.append((sku, "", "", "", "", "", "wiersz usunięty"))
    for sku in k:
        if sku not in a:
            zmiany.append((sku, "", "", "", "", "", "wiersz dodany"))
    for sku, (_, ra) in a.items():
        if sku not in k:
            continue
        rk = k[sku][1]
        ra = ra + [None] * (szer - len(ra))
        rk = rk + [None] * (szer - len(rk))
        for j in range(szer):
            if rowne(ra[j], rk[j]):
                continue
            va, vk = tekst(ra[j]), tekst(rk[j])
            typ = "dopisane" if not va else ("usunięte" if not vk else "nadpisane")
            atr = kanon[j] if j < len(kanon) else "(kolumna spoza szablonu)"
            zmiany.append((sku, j + 1, tekst(etyk[j]), atr, va, vk, typ))
    return zmiany


# ---------------------------------------------------------------- raport

def litera_kolumny(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def zapisz_csv(sciezka, naglowek, wiersze):
    with open(sciezka, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(naglowek)
        w.writerows(wiersze)


def raport_md(sciezka, data, nasz, klient, szablon, kanon, inf_a, inf_k, nagl, zmiany, uwagi, gpsr):
    L = []
    p = L.append
    p("# Weryfikacja pliku Amazon (%s)" % data)
    p("")
    p("Wygenerowano narzędziem `porownaj_amazon.py`. Plik nasz: `%s` · plik klienta: `%s` · szablon: `%s`."
      % (os.path.basename(nasz.sciezka), os.path.basename(klient.sciezka), os.path.basename(szablon.sciezka)))
    p("")
    # Struktura
    p("## Struktura pliku")
    p("")
    p("| | nasz | klienta |")
    p("|---|---|---|")
    p("| rozmiar (B) | %d | %d |" % (inf_a["rozmiar"], inf_k["rozmiar"]))
    p("| arkusze | %d | %d |" % (len(nasz.arkusze), len(klient.arkusze)))
    p("| kolumny w „Szablon” | %d | %d |" % (nasz.szerokosc, klient.szerokosc))
    p("| wiersze danych (SKU) | %d | %d |" % (len(nasz.dane), len(klient.dane)))
    p("| makra (vbaProject.bin) | %s | %s |" % ("tak" if inf_a["vba"] else "brak", "tak" if inf_k["vba"] else "brak"))
    p("")
    if nasz.arkusze != klient.arkusze:
        p("- Arkusze różnią się: nasz %s, klienta %s." % (nasz.arkusze, klient.arkusze))
    if inf_a["vba"] != inf_k["vba"]:
        p("- Makra różnią się (inny skrót vbaProject.bin). Informacyjnie: Amazon przy wgrywaniu czyta tylko dane.")
    if nasz.ustawienia != klient.ustawienia:
        p("- **Wiersz ustawień (A1) różni się.** Amazon używa go do rozpoznania szablonu.")
    p("")
    # Nagłówki
    p("## Nagłówki kolumn (wiersze 1–%d)" % (nasz.wiersz_danych - 1))
    p("")
    if not nagl:
        p("Bez zmian.")
    else:
        krytyczne = [n for n in nagl if n[0] == nasz.wiersz_atrybutow]
        if krytyczne:
            p("**BŁĄD KRYTYCZNY:** zmieniony wiersz %d z technicznymi nazwami atrybutów. Amazon nie rozpozna tych kolumn "
              "(dane z nich zostaną pominięte albo plik zostanie odrzucony)." % nasz.wiersz_atrybutow)
            p("")
        p("| wiersz | kolumna | atrybut (szablon) | nasze | klienta |")
        p("|---|---|---|---|---|")
        for w, j, atr, va, vk in nagl:
            p("| %d | %s (%d) | `%s` | %s | %s |" % (w, litera_kolumny(j), j, atr, va[:60], vk[:60]))
    p("")
    # Zmiany w danych
    licz = Counter(z[6] for z in zmiany)
    p("## Zmiany klienta w danych")
    p("")
    p("Razem: %d (%s). Szczegóły: `zmiany_klientki.csv`." % (len(zmiany), ", ".join("%s: %d" % kv for kv in licz.items()) or "brak"))
    p("")
    po_kol = OrderedDict()
    for z in zmiany:
        if z[1] == "":
            continue
        klucz = (z[1], z[2], z[3])
        po_kol.setdefault(klucz, Counter())[z[6]] += 1
    if po_kol:
        p("| kolumna | etykieta | atrybut | dopisane | nadpisane | usunięte | przykład wartości klienta |")
        p("|---|---|---|---|---|---|---|")
        for (j, et, atr), c in po_kol.items():
            przyklad = Counter(z[5] for z in zmiany if z[1] == j and z[5]).most_common(1)
            przyklad = przyklad[0][0][:60] if przyklad else ""
            p("| %s (%d) | %s | `%s` | %d | %d | %d | %s |" % (litera_kolumny(j), j, et[:40], baza_atrybutu(atr),
                                                          c["dopisane"], c["nadpisane"], c["usunięte"], przyklad))
    wiersze_zm = [z for z in zmiany if z[1] == ""]
    for z in wiersze_zm:
        p("- %s: %s" % (z[0], z[6]))
    p("")
    # GPSR
    n = len(klient.dane)
    p("## GPSR (wersja klienta)")
    p("")
    p("| punkt | uzupełnione SKU | braki | wartości |")
    p("|---|---|---|---|")
    for g in gpsr:
        wart = []
        for atr, c in g["wartosci"].items():
            wart.append("`%s`: %s" % (atr, "; ".join("%s (%d)" % (v[:50], k) for v, k in c.most_common(4))))
        braki = ", ".join(g["braki"][:12]) + (" …" if len(g["braki"]) > 12 else "")
        p("| %s. %s | %d / %d | %s | %s |" % (g["nr"], g["nazwa"], len(g["wypelnione"]), n, braki or "—", "<br>".join(wart) or "—"))
    p("")
    # Walidacja
    lp = Counter(u[2] for u in uwagi)
    p("## Walidacja według szablonu (wersja klienta)")
    p("")
    p("Razem: %s. Szczegóły: `uwagi_per_sku.csv`." % (", ".join("%s: %d" % kv for kv in lp.items()) or "brak uwag"))
    p("")
    grupy = OrderedDict()
    for u in uwagi:
        opis = re.sub(r"„.*”", "„…”", u[5]) if "spoza listy" not in u[5] else u[5]
        opis = re.sub(r": [A-ZĄĆĘŁŃÓŚŹŻ0-9, ]+$", "", opis) if "wielkimi" in opis else opis
        grupy.setdefault((u[2], u[3], baza_atrybutu(u[4]), opis), []).append(u[1])
    if grupy:
        p("| poziom | kolumna | atrybut | opis | SKU |")
        p("|---|---|---|---|---|")
        for (poz, j, atr, opis), skus in grupy.items():
            p("| %s | %s | `%s` | %s | %s |" % (poz, j, atr, opis[:90], ", ".join(skus[:10]) + (" … (%d)" % len(skus) if len(skus) > 10 else "")))
    p("")
    with open(sciezka, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------- main

def zapytaj(opis, domyslna):
    try:
        odp = input("%s [%s]: " % (opis, domyslna or "")).strip().strip('"')
    except EOFError:
        odp = ""
    return odp or domyslna


def main():
    ap = argparse.ArgumentParser(description="Porównanie i walidacja pliku szablonu Amazon")
    ap.add_argument("--nasz")
    ap.add_argument("--klient")
    ap.add_argument("--szablon")
    ap.add_argument("--wyjscie")
    ap.add_argument("--data", default=datetime.date.today().isoformat())
    a = ap.parse_args()

    if not (a.nasz and a.klient):
        print("Porównanie pliku Amazon: podaj ścieżki (Enter = domyślna).")
        xlsm = sorted(f for f in os.listdir(".") if f.lower().endswith(".xlsm"))
        a.nasz = a.nasz or zapytaj("Nasz plik .xlsm", xlsm[0] if xlsm else "")
        a.klient = a.klient or zapytaj("Plik od klienta .xlsm", "")
        a.szablon = a.szablon or zapytaj("Pusty szablon Amazon .xlsm (opcjonalnie)", "")
        a.wyjscie = a.wyjscie or zapytaj("Folder wyników", os.path.join(os.path.dirname(os.path.abspath(a.klient)), "weryfikacja_" + a.data))

    for s in (a.nasz, a.klient):
        if not s or not os.path.isfile(s):
            print("Nie znaleziono pliku: %s" % s)
            return 1
    wyjscie = a.wyjscie or "weryfikacja_" + a.data
    os.makedirs(wyjscie, exist_ok=True)

    print("Czytam pliki…")
    nasz = PlikAmazon(a.nasz)
    klient = PlikAmazon(a.klient)
    szablon = PlikAmazon(a.szablon) if a.szablon and os.path.isfile(a.szablon) else nasz
    kanon = list(szablon.atrybuty)
    definicje = czytaj_definicje(szablon.wb)
    listy = czytaj_listy(szablon.wb)

    nagl = porownaj_naglowki(nasz, klient, kanon)
    zmiany = porownaj_dane(nasz, klient, kanon)
    uwagi = waliduj(klient, kanon, definicje, listy)
    # nagłówki atrybutów klienta niezgodne z szablonem
    for j, at in enumerate(klient.atrybuty):
        oczek = kanon[j] if j < len(kanon) else None
        if tekst(at) != tekst(oczek):
            uwagi.insert(0, (klient.wiersz_atrybutow, "(nagłówek)", "BŁĄD KRYTYCZNY", j + 1, oczek or "",
                             "nazwa atrybutu w wierszu %d zmieniona na „%s”" % (klient.wiersz_atrybutow, tekst(at)[:80])))
    gpsr = kontrola_gpsr(klient, kanon)

    zapisz_csv(os.path.join(wyjscie, "zmiany_klientki.csv"),
               ["sku", "kolumna_nr", "kolumna", "etykieta", "atrybut", "nasza_wartosc", "wartosc_klienta", "typ"],
               [(z[0], z[1], litera_kolumny(z[1]) if z[1] else "", z[2], z[3], z[4], z[5], z[6]) for z in zmiany])
    gpsr_braki = []
    for g in gpsr:
        for sku in g["braki"]:
            nr = klient.wg_sku()[sku][0]
            gpsr_braki.append((nr, sku, "GPSR", "", "", "brak danych: %s. %s" % (g["nr"], g["nazwa"])))
    zmienione = {(z[0], z[1]) for z in zmiany if z[1] != ""}
    nasze_sku = nasz.wg_sku()

    def zrodlo(u):
        if u[1] not in nasze_sku or u[3] == "":
            return ""
        return "klient" if (u[1], u[3]) in zmienione else "nasza wersja"

    zapisz_csv(os.path.join(wyjscie, "uwagi_per_sku.csv"),
               ["wiersz", "sku", "poziom", "kolumna_nr", "atrybut", "opis", "zrodlo_wartosci"],
               [u + (zrodlo(u),) for u in uwagi + gpsr_braki])
    raport_md(os.path.join(wyjscie, "weryfikacja_%s.md" % a.data), a.data, nasz, klient, szablon, kanon,
              info_pliku(a.nasz), info_pliku(a.klient), nagl, zmiany, uwagi, gpsr)

    print("Zmiany w nagłówkach: %d, w danych: %d, uwagi walidacji: %d" % (len(nagl), len(zmiany), len(uwagi)))
    print("Wyniki: %s" % os.path.abspath(wyjscie))
    return 0


if __name__ == "__main__":
    sys.exit(main())
