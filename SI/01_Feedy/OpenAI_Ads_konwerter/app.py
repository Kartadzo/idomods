#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Konwerter feedu XML (Google Shopping / IdoSell) na feed produktowy OpenAI Ads.

Wejscie : adres URL feedu XML albo lokalny plik XML.
Wyjscie : natywny feed OpenAI w formacie CSV oraz JSONL (folder `katalog/`).

Skrypt jest interaktywny - uruchamiany bez argumentow pyta o wszystko w konsoli.
Argumenty CLI sluza wylacznie jako skrot dla powtarzalnych uruchomien.

Specyfikacja: https://developers.openai.com/commerce/specs/file-upload/products
"""

import argparse
import csv
import gzip
import html
import json
import math
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "katalog")
DOWNLOAD_DIR = os.path.join(OUTPUT_DIR, "_pobrane")

USER_AGENT = "OpenAI-Ads-Feed-Converter/1.0 (+IdoMods)"

# Kolejnosc kolumn w pliku CSV (natywny schemat OpenAI).
CSV_COLUMNS = [
    "item_id",
    "title",
    "description",
    "url",
    "brand",
    "image_url",
    "additional_image_urls",
    "price",
    "sale_price",
    "availability",
    "seller_name",
    "seller_url",
    "return_policy",
    "accepts_returns",
    "return_deadline_in_days",
    "target_countries",
    "store_country",
    "gtin",
    "mpn",
    "condition",
    "product_category",
    "color",
    "material",
    "size",
    "weight",
    "item_weight_unit",
    "group_id",
    "listing_has_variations",
    "variant_dict",
    "is_eligible_search",
    "is_eligible_checkout",
    "is_ads_eligible",
]

# Pola wymagane przez OpenAI w kazdym wierszu - brak oznacza odrzucenie produktu.
REQUIRED_FIELDS = [
    "item_id",
    "title",
    "description",
    "url",
    "brand",
    "seller_name",
    "image_url",
    "availability",
    "price",
]

# Pola zapisywane w JSONL jako wartosci logiczne, a nie tekst.
BOOLEAN_FIELDS = {
    "accepts_returns",
    "listing_has_variations",
    "is_eligible_search",
    "is_eligible_checkout",
    "is_ads_eligible",
}

MAX_TITLE = 150
MAX_DESCRIPTION = 5000
MAX_ADDITIONAL_IMAGES = 10

AVAILABILITY_MAP = {
    "in stock": "in_stock",
    "in_stock": "in_stock",
    "available": "in_stock",
    "out of stock": "out_of_stock",
    "out_of_stock": "out_of_stock",
    "preorder": "pre_order",
    "pre order": "pre_order",
    "pre-order": "pre_order",
    "pre_order": "pre_order",
    "backorder": "backorder",
    "back order": "backorder",
    "back_order": "backorder",
}

CONDITION_MAP = {
    "new": "new",
    "nowy": "new",
    "refurbished": "refurbished",
    "odnowiony": "refurbished",
    "used": "used",
    "uzywany": "used",
    "używany": "used",
}

WEIGHT_UNITS = {
    "g": "g",
    "gr": "g",
    "kg": "kg",
    "oz": "oz",
    "lb": "lb",
    "lbs": "lb",
}

# Wartosci rozmiaru, ktore nie niosa informacji i nie powinny trafic do feedu.
EMPTY_SIZES = {"uniwersalny", "uniwersalna", "uniwersalne", "uniw", "one size", "-"}

DEFAULT_SHOP_CONFIG = {
    "feed_url": "",
    "seller_name": "",
    "seller_url": "",
    "return_policy": "",
    "accepts_returns": "",
    "return_deadline_in_days": "",
    "target_countries": "PL",
    "store_country": "PL",
    "waluta": "PLN",
    "is_eligible_search": True,
    "is_eligible_checkout": False,
    "is_ads_eligible": True,
}

# Ustawienia techniczne wspolne dla wszystkich sklepow (sekcja "ustawienia" w config.json).
DEFAULT_SETTINGS = {
    # Ads Manager przyjmuje pliki CSV/TXT do 20 MB - wieksze dzielimy na czesci.
    "limit_mb": 20,
    # Dodatkowo zapisuje wersje .gz (OpenAI akceptuje .csv.gz / .jsonl.gz).
    "gzip": True,
    # Przycinanie opisu; 5000 to maksimum dopuszczone przez OpenAI.
    "max_opisu": MAX_DESCRIPTION,
}


# --------------------------------------------------------------------------- #
# Konfiguracja
# --------------------------------------------------------------------------- #

def wczytaj_config() -> Dict[str, Any]:
    """Zwraca zawartosc config.json; przy braku pliku - pusta strukture."""
    if not os.path.exists(CONFIG_PATH):
        return {"sklepy": {}}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as plik:
            dane = json.load(plik)
    except (OSError, ValueError) as blad:
        print("! Nie udalo sie wczytac %s: %s" % (CONFIG_PATH, blad))
        print("  Kontynuuje z pusta konfiguracja (plik nie zostanie nadpisany bez pytania).")
        return {"sklepy": {}}
    dane.setdefault("sklepy", {})
    return dane


def zapisz_config(config: Dict[str, Any]) -> None:
    """Zapisuje config.json w UTF-8 z zachowaniem polskich znakow."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as plik:
            json.dump(config, plik, ensure_ascii=False, indent=2)
        print("  Zapisano konfiguracje: %s" % CONFIG_PATH)
    except OSError as blad:
        print("! Nie udalo sie zapisac konfiguracji: %s" % blad)


# --------------------------------------------------------------------------- #
# Pomocnicze - tekst, ceny, identyfikatory
# --------------------------------------------------------------------------- #

def tekst(element: Optional[ET.Element]) -> str:
    """Zwraca oczyszczony tekst elementu XML (bez encji HTML i zbednych spacji)."""
    if element is None or element.text is None:
        return ""
    return oczysc_tekst(element.text)


def oczysc_tekst(wartosc: str) -> str:
    """Usuwa znaczniki HTML, rozwija encje i skleja biale znaki w pojedyncze spacje."""
    if not wartosc:
        return ""
    wynik = html.unescape(wartosc)
    if "<" in wynik and ">" in wynik:
        wynik = re.sub(r"<br\s*/?>", " ", wynik, flags=re.IGNORECASE)
        wynik = re.sub(r"</(p|li|div|tr|h[1-6])>", " ", wynik, flags=re.IGNORECASE)
        wynik = re.sub(r"<[^>]+>", "", wynik)
        wynik = html.unescape(wynik)
    wynik = wynik.replace("\xa0", " ")
    wynik = re.sub(r"\s+", " ", wynik)
    return wynik.strip()


def przytnij(wartosc: str, limit: int) -> str:
    """Skraca tekst do limitu znakow, ucinajac na granicy slowa."""
    if len(wartosc) <= limit:
        return wartosc
    skrocone = wartosc[:limit].rstrip()
    spacja = skrocone.rfind(" ")
    if spacja > limit * 0.6:
        skrocone = skrocone[:spacja]
    return skrocone.rstrip(" ,;.-")


def normalizuj_cene(wartosc: str, waluta_domyslna: str) -> Tuple[str, str]:
    """Zamienia cene z feedu na format OpenAI `kwota WALUTA`.

    Zwraca krotke (cena, waluta). Przy niepowodzeniu - ("", "").
    """
    if not wartosc:
        return "", ""
    surowa = wartosc.replace("\xa0", " ").strip()
    dopasowanie = re.match(r"^([0-9][0-9\s.,]*)\s*([A-Za-z]{3})?$", surowa)
    if not dopasowanie:
        dopasowanie = re.match(r"^([A-Za-z]{3})\s*([0-9][0-9\s.,]*)$", surowa)
        if not dopasowanie:
            return "", ""
        waluta, kwota_txt = dopasowanie.group(1), dopasowanie.group(2)
    else:
        kwota_txt, waluta = dopasowanie.group(1), dopasowanie.group(2)

    kwota_txt = kwota_txt.replace(" ", "")
    if "," in kwota_txt and "." in kwota_txt:
        kwota_txt = kwota_txt.replace(",", "")
    else:
        kwota_txt = kwota_txt.replace(",", ".")
    try:
        kwota = float(kwota_txt)
    except ValueError:
        return "", ""
    if kwota <= 0:
        return "", ""

    waluta = (waluta or waluta_domyslna or "").upper()
    if len(waluta) != 3:
        return "", ""
    return "%.2f %s" % (kwota, waluta), waluta


def kwota_z_ceny(cena: str) -> Optional[float]:
    """Wyciaga liczbe z ceny w formacie `kwota WALUTA`."""
    if not cena:
        return None
    try:
        return float(cena.split(" ")[0])
    except (ValueError, IndexError):
        return None


def poprawny_gtin(wartosc: str) -> bool:
    """Sprawdza dlugosc (8/12/13/14 cyfr) i cyfre kontrolna GTIN."""
    if not wartosc.isdigit() or len(wartosc) not in (8, 12, 13, 14):
        return False
    cyfry = [int(znak) for znak in wartosc][::-1]
    suma = sum(cyfra * (3 if indeks % 2 == 0 else 1) for indeks, cyfra in enumerate(cyfry[1:]))
    return (10 - (suma % 10)) % 10 == cyfry[0]


def oczysc_etykiete(wartosc: str) -> str:
    """Czysci custom_label z separatorow IdoSell (`|Bestseller|`, `Koty;`)."""
    if not wartosc:
        return ""
    czesci = [czesc.strip() for czesc in re.split(r"[|;]", wartosc) if czesc.strip()]
    return ", ".join(czesci)


def rozbij_wage(wartosc: str) -> Tuple[str, str]:
    """Rozbija zapis typu `0.25 kg` na (wartosc, jednostka) akceptowane przez OpenAI."""
    if not wartosc:
        return "", ""
    dopasowanie = re.match(r"^([0-9]+(?:[.,][0-9]+)?)\s*([A-Za-z]+)$", wartosc.strip())
    if not dopasowanie:
        return "", ""
    liczba = dopasowanie.group(1).replace(",", ".")
    jednostka = WEIGHT_UNITS.get(dopasowanie.group(2).lower())
    if not jednostka:
        return "", ""
    try:
        if float(liczba) <= 0:
            return "", ""
    except ValueError:
        return "", ""
    return liczba, jednostka


def zakoduj_url_obrazka(adres: str) -> str:
    """Zabezpiecza URL przed rozbiciem listy - przecinek zamieniany na %2C."""
    return adres.strip().replace(",", "%2C")


def slug_z_url(adres: str) -> str:
    """Buduje nazwe sklepu (klucz konfiguracji) z adresu feedu."""
    dopasowanie = re.match(r"^https?://([^/]+)", adres.strip(), flags=re.IGNORECASE)
    host = dopasowanie.group(1).lower() if dopasowanie else os.path.basename(adres)
    return host[4:] if host.startswith("www.") else host


def nazwa_pliku(wartosc: str) -> str:
    """Zamienia dowolny tekst na bezpieczna nazwe pliku."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", wartosc).strip("_") or "feed"


# --------------------------------------------------------------------------- #
# Pobieranie feedu
# --------------------------------------------------------------------------- #

def pobierz_feed(adres: str, sciezka_docelowa: str) -> str:
    """Pobiera feed XML do pliku lokalnego, raportujac postep."""
    os.makedirs(os.path.dirname(sciezka_docelowa), exist_ok=True)
    zapytanie = urllib.request.Request(adres, headers={"User-Agent": USER_AGENT})
    print("  Pobieram: %s" % adres)
    start = time.time()
    pobrane = 0
    nastepny_raport = 5 * 1024 * 1024
    try:
        with urllib.request.urlopen(zapytanie, timeout=120) as odpowiedz:
            calosc = odpowiedz.headers.get("Content-Length")
            calosc_mb = (int(calosc) / 1048576.0) if calosc and calosc.isdigit() else None
            with open(sciezka_docelowa, "wb") as plik:
                while True:
                    fragment = odpowiedz.read(262144)
                    if not fragment:
                        break
                    plik.write(fragment)
                    pobrane += len(fragment)
                    if pobrane >= nastepny_raport:
                        nastepny_raport += 5 * 1024 * 1024
                        if calosc_mb:
                            print("    %.1f / %.1f MB" % (pobrane / 1048576.0, calosc_mb))
                        else:
                            print("    %.1f MB" % (pobrane / 1048576.0))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as blad:
        raise RuntimeError("Nie udalo sie pobrac feedu: %s" % blad)
    print("    Gotowe: %.1f MB w %.1f s" % (pobrane / 1048576.0, time.time() - start))
    return sciezka_docelowa


# --------------------------------------------------------------------------- #
# Parsowanie XML
# --------------------------------------------------------------------------- #

def nazwa_taga(element: ET.Element) -> str:
    """Zwraca nazwe znacznika bez przestrzeni nazw."""
    tag = element.tag
    return tag.split("}")[-1] if isinstance(tag, str) and "}" in tag else str(tag)


def iteruj_produkty(sciezka: str):
    """Strumieniowo zwraca slowniki {pole: [wartosci]} dla kazdego <item>/<product>."""
    kontekst = ET.iterparse(sciezka, events=("end",))
    for _, element in kontekst:
        nazwa = nazwa_taga(element)
        if nazwa not in ("item", "entry"):
            continue
        produkt: Dict[str, List[str]] = {}
        for dziecko in element:
            klucz = nazwa_taga(dziecko)
            wartosc = tekst(dziecko)
            if klucz == "product_detail":
                nazwa_atrybutu = ""
                wartosc_atrybutu = ""
                for wnuk in dziecko:
                    if nazwa_taga(wnuk) == "attribute_name":
                        nazwa_atrybutu = tekst(wnuk)
                    elif nazwa_taga(wnuk) == "attribute_value":
                        wartosc_atrybutu = tekst(wnuk)
                if nazwa_atrybutu:
                    produkt.setdefault("product_detail", []).append(
                        "%s: %s" % (nazwa_atrybutu, wartosc_atrybutu)
                    )
                continue
            if not wartosc:
                continue
            produkt.setdefault(klucz, []).append(wartosc)
        yield produkt
        element.clear()


def odczytaj_dane_kanalu(sciezka: str) -> Dict[str, str]:
    """Zwraca tytul i adres sklepu z naglowka <channel> feedu."""
    dane = {"title": "", "link": ""}
    try:
        kontekst = ET.iterparse(sciezka, events=("start", "end"))
        for zdarzenie, element in kontekst:
            nazwa = nazwa_taga(element)
            if zdarzenie == "end" and nazwa in ("title", "link") and not dane[nazwa]:
                dane[nazwa] = tekst(element)
            if zdarzenie == "start" and nazwa in ("item", "entry"):
                break
            if dane["title"] and dane["link"]:
                break
    except ET.ParseError:
        pass
    return dane


def policz_grupy(sciezka: str) -> Counter:
    """Zlicza wystapienia item_group_id - group_id ma sens tylko dla realnych wariantow."""
    licznik: Counter = Counter()
    for produkt in iteruj_produkty(sciezka):
        grupa = pierwsza(produkt, "item_group_id", "group_id")
        if grupa:
            licznik[grupa] += 1
    return licznik


def pierwsza(produkt: Dict[str, List[str]], *klucze: str) -> str:
    """Zwraca pierwsza niepusta wartosc dla pierwszego istniejacego klucza."""
    for klucz in klucze:
        wartosci = produkt.get(klucz)
        if wartosci:
            return wartosci[0]
    return ""


# --------------------------------------------------------------------------- #
# Mapowanie produktu na schemat OpenAI
# --------------------------------------------------------------------------- #

def zmapuj_produkt(
    produkt: Dict[str, List[str]],
    sklep: Dict[str, Any],
    grupy: Counter,
    statystyki: Counter,
    max_opisu: int = MAX_DESCRIPTION,
) -> Optional[Dict[str, Any]]:
    """Przeksztalca jeden produkt feedu na wiersz natywnego feedu OpenAI.

    Zwraca None, gdy brakuje pola wymaganego przez OpenAI (produkt pomijany).
    """
    waluta_domyslna = str(sklep.get("waluta") or "").upper()
    wiersz: Dict[str, Any] = {kolumna: "" for kolumna in CSV_COLUMNS}

    wiersz["item_id"] = pierwsza(produkt, "id", "item_id", "sku", "g:id")
    wiersz["title"] = przytnij(pierwsza(produkt, "title"), MAX_TITLE)
    wiersz["description"] = przytnij(pierwsza(produkt, "description"), max_opisu)
    wiersz["url"] = pierwsza(produkt, "link", "url", "mobile_link")
    wiersz["brand"] = pierwsza(produkt, "brand")
    wiersz["image_url"] = pierwsza(produkt, "image_link", "image_url")

    dodatkowe = [
        zakoduj_url_obrazka(adres)
        for adres in produkt.get("additional_image_link", produkt.get("additional_image_urls", []))
        if adres.startswith("http")
    ]
    wiersz["additional_image_urls"] = ",".join(dodatkowe[:MAX_ADDITIONAL_IMAGES])

    cena, waluta = normalizuj_cene(pierwsza(produkt, "price"), waluta_domyslna)
    wiersz["price"] = cena
    if cena and waluta_domyslna and waluta != waluta_domyslna:
        statystyki["ostrzezenie_waluta"] += 1

    cena_promocyjna, _ = normalizuj_cene(pierwsza(produkt, "sale_price"), waluta_domyslna)
    kwota_bazowa = kwota_z_ceny(cena)
    kwota_promocyjna = kwota_z_ceny(cena_promocyjna)
    if cena_promocyjna and kwota_bazowa is not None and kwota_promocyjna is not None:
        if 0 < kwota_promocyjna < kwota_bazowa:
            wiersz["sale_price"] = cena_promocyjna
        else:
            statystyki["pominieto_sale_price"] += 1

    dostepnosc = pierwsza(produkt, "availability").lower()
    wiersz["availability"] = AVAILABILITY_MAP.get(dostepnosc, "unknown" if dostepnosc else "")
    if dostepnosc and dostepnosc not in AVAILABILITY_MAP:
        statystyki["dostepnosc_unknown"] += 1

    gtin = pierwsza(produkt, "gtin", "ean").strip().replace("-", "").replace(" ", "")
    if gtin:
        if poprawny_gtin(gtin):
            wiersz["gtin"] = gtin
        else:
            statystyki["gtin_odrzucony"] += 1
    wiersz["mpn"] = pierwsza(produkt, "mpn")
    if not wiersz["gtin"] and wiersz["mpn"] and poprawny_gtin(wiersz["mpn"]):
        # Sklepy czesto wpisuja EAN w pole mpn - jesli przechodzi walidacje GTIN, uzywamy go.
        wiersz["gtin"] = wiersz["mpn"]
        statystyki["gtin_z_mpn"] += 1

    wiersz["condition"] = CONDITION_MAP.get(pierwsza(produkt, "condition").lower(), "new")
    wiersz["product_category"] = pierwsza(produkt, "product_type", "product_category")
    wiersz["color"] = pierwsza(produkt, "color")
    wiersz["material"] = pierwsza(produkt, "material")

    rozmiar = pierwsza(produkt, "size")
    if rozmiar.lower() in EMPTY_SIZES:
        rozmiar = ""
    wiersz["size"] = rozmiar

    waga, jednostka = rozbij_wage(pierwsza(produkt, "unit_pricing_measure"))
    if not waga:
        waga, jednostka = rozbij_wage(pierwsza(produkt, "shipping_weight"))
    wiersz["weight"] = waga
    wiersz["item_weight_unit"] = jednostka

    grupa = pierwsza(produkt, "item_group_id", "group_id")
    if grupa and grupy.get(grupa, 0) > 1 and grupa != wiersz["item_id"]:
        wiersz["group_id"] = grupa
        wiersz["listing_has_variations"] = "true"
        warianty = {}
        if rozmiar:
            warianty["size"] = rozmiar
        if wiersz["color"]:
            warianty["color"] = wiersz["color"]
        if warianty:
            wiersz["variant_dict"] = json.dumps(warianty, ensure_ascii=False)
        statystyki["warianty"] += 1

    for indeks in range(5):
        wiersz["custom_label_%d" % indeks] = oczysc_etykiete(
            pierwsza(produkt, "custom_label_%d" % indeks)
        )

    wiersz["seller_name"] = str(sklep.get("seller_name") or "")
    wiersz["seller_url"] = str(sklep.get("seller_url") or "")
    wiersz["return_policy"] = str(sklep.get("return_policy") or "")
    wiersz["target_countries"] = str(sklep.get("target_countries") or "")
    wiersz["store_country"] = str(sklep.get("store_country") or "")

    zwroty = sklep.get("accepts_returns")
    if isinstance(zwroty, bool):
        wiersz["accepts_returns"] = "true" if zwroty else "false"
    termin = sklep.get("return_deadline_in_days")
    if isinstance(termin, int) and termin > 0:
        wiersz["return_deadline_in_days"] = str(termin)

    for pole in ("is_eligible_search", "is_eligible_checkout", "is_ads_eligible"):
        wartosc = sklep.get(pole)
        if isinstance(wartosc, bool):
            wiersz[pole] = "true" if wartosc else "false"

    for pole in REQUIRED_FIELDS:
        if not wiersz.get(pole):
            statystyki["brak_%s" % pole] += 1
            return None

    if not wiersz["url"].lower().startswith("http") or not wiersz["image_url"].lower().startswith("http"):
        statystyki["brak_poprawnego_url"] += 1
        return None

    return wiersz


def wiersz_do_jsonl(wiersz: Dict[str, Any]) -> Dict[str, Any]:
    """Zamienia wiersz CSV na obiekt JSONL (tablice, obiekty i wartosci logiczne)."""
    rekord: Dict[str, Any] = {}
    for kolumna, wartosc in wiersz.items():
        if wartosc == "" or wartosc is None:
            continue
        if kolumna == "additional_image_urls":
            rekord[kolumna] = [adres.replace("%2C", ",") for adres in wartosc.split(",")]
        elif kolumna == "variant_dict":
            try:
                rekord[kolumna] = json.loads(wartosc)
            except ValueError:
                continue
        elif kolumna == "target_countries":
            rekord[kolumna] = [kraj.strip() for kraj in wartosc.split(",") if kraj.strip()]
        elif kolumna == "return_deadline_in_days":
            rekord[kolumna] = int(wartosc)
        elif kolumna in BOOLEAN_FIELDS:
            rekord[kolumna] = wartosc == "true"
        else:
            rekord[kolumna] = wartosc
    return rekord


# --------------------------------------------------------------------------- #
# Dopasowanie plikow do limitu Ads Managera (gzip + podzial na czesci)
# --------------------------------------------------------------------------- #

def spakuj_gzip(sciezka: str) -> str:
    """Tworzy obok pliku jego wersje .gz i zwraca sciezke do archiwum."""
    sciezka_gz = sciezka + ".gz"
    with open(sciezka, "rb") as zrodlo, gzip.open(sciezka_gz, "wb", compresslevel=9) as cel:
        shutil.copyfileobj(zrodlo, cel, length=1048576)
    return sciezka_gz


def podziel_csv(sciezka: str, liczba_czesci: int) -> List[str]:
    """Dzieli plik CSV na czesci, powtarzajac wiersz naglowka w kazdej z nich."""
    baza, rozszerzenie = os.path.splitext(sciezka)
    with open(sciezka, encoding="utf-8", newline="") as plik:
        czytnik = csv.reader(plik)
        naglowek = next(czytnik)
        wszystkie = sum(1 for _ in czytnik)

    na_czesc = int(math.ceil(wszystkie / float(liczba_czesci)))
    czesci: List[str] = []
    with open(sciezka, encoding="utf-8", newline="") as plik:
        czytnik = csv.reader(plik)
        next(czytnik)
        numer = 0
        zapis = None
        plik_wy = None
        for indeks, wiersz in enumerate(czytnik):
            if indeks % na_czesc == 0:
                if plik_wy:
                    plik_wy.close()
                numer += 1
                sciezka_czesci = "%s_czesc%dz%d%s" % (baza, numer, liczba_czesci, rozszerzenie)
                plik_wy = open(sciezka_czesci, "w", encoding="utf-8", newline="")
                zapis = csv.writer(plik_wy)
                zapis.writerow(naglowek)
                czesci.append(sciezka_czesci)
            zapis.writerow(wiersz)
        if plik_wy:
            plik_wy.close()
    return czesci


def podziel_jsonl(sciezka: str, liczba_czesci: int) -> List[str]:
    """Dzieli plik JSONL na czesci - kazdy wiersz jest niezaleznym rekordem."""
    baza, rozszerzenie = os.path.splitext(sciezka)
    with open(sciezka, encoding="utf-8") as plik:
        wszystkie = sum(1 for _ in plik)

    na_czesc = int(math.ceil(wszystkie / float(liczba_czesci)))
    czesci: List[str] = []
    with open(sciezka, encoding="utf-8") as plik:
        numer = 0
        plik_wy = None
        for indeks, linia in enumerate(plik):
            if indeks % na_czesc == 0:
                if plik_wy:
                    plik_wy.close()
                numer += 1
                sciezka_czesci = "%s_czesc%dz%d%s" % (baza, numer, liczba_czesci, rozszerzenie)
                plik_wy = open(sciezka_czesci, "w", encoding="utf-8", newline="\n")
                czesci.append(sciezka_czesci)
            plik_wy.write(linia)
        if plik_wy:
            plik_wy.close()
    return czesci


def dopasuj_do_limitu(sciezka: str, limit_mb: float, kompresja: bool) -> List[str]:
    """Przygotowuje pliki do wysylki tak, by kazdy miescil sie w limicie.

    Najpierw probuje gzip (OpenAI przyjmuje .csv.gz / .jsonl.gz), a gdy to nie
    wystarczy - dzieli katalog na czesci. Kazdy produkt trafia dokladnie do
    jednej czesci, zgodnie z wymogiem OpenAI dla katalogu dzielonego na pliki.
    Zwraca liste plikow gotowych do wyslania.
    """
    limit_bajtow = limit_mb * 1048576.0
    jest_csv = sciezka.lower().endswith(".csv")

    if kompresja:
        # Rozmiar archiwum jest tez podstawa szacunku liczby czesci przy podziale.
        gotowy = spakuj_gzip(sciezka)
        rozmiar = os.path.getsize(gotowy)
        if rozmiar <= limit_bajtow:
            return [gotowy]
        os.remove(gotowy)
    else:
        rozmiar = os.path.getsize(sciezka)
        if rozmiar <= limit_bajtow:
            return [sciezka]

    czesci: List[str] = []
    liczba_czesci = max(2, int(math.ceil(rozmiar / (limit_bajtow * 0.9))))
    for _ in range(4):
        for stary in czesci:
            usun_plik(stary)
        czesci = podziel_csv(sciezka, liczba_czesci) if jest_csv \
            else podziel_jsonl(sciezka, liczba_czesci)
        if kompresja:
            spakowane = [spakuj_gzip(czesc) for czesc in czesci]
            for czesc in czesci:
                usun_plik(czesc)
            czesci = spakowane
        if all(os.path.getsize(czesc) <= limit_bajtow for czesc in czesci):
            return czesci
        liczba_czesci += max(1, liczba_czesci // 2)

    print("! Nie udalo sie zejsc ponizej %.0f MB - zmniejsz max_opisu w config.json." % limit_mb)
    return czesci


def usun_plik(sciezka: str) -> None:
    """Kasuje plik, ignorujac brak pliku (uzywane przy ponownym dzieleniu)."""
    try:
        os.remove(sciezka)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Konwersja
# --------------------------------------------------------------------------- #

def konwertuj(
    sciezka_xml: str,
    sklep: Dict[str, Any],
    prefiks: str,
    ustawienia: Dict[str, Any],
) -> Dict[str, Any]:
    """Przetwarza feed XML na pliki CSV i JSONL. Zwraca podsumowanie konwersji."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    max_opisu = int(ustawienia.get("max_opisu") or MAX_DESCRIPTION)
    limit_mb = float(ustawienia.get("limit_mb") or 0)
    kompresja = bool(ustawienia.get("gzip"))
    znacznik = datetime.now().strftime("%Y%m%d_%H%M")
    sciezka_csv = os.path.join(OUTPUT_DIR, "%s_openai_%s.csv" % (prefiks, znacznik))
    sciezka_jsonl = os.path.join(OUTPUT_DIR, "%s_openai_%s.jsonl" % (prefiks, znacznik))

    print("\n[1/3] Licze warianty (item_group_id)...")
    grupy = policz_grupy(sciezka_xml)
    realne_grupy = sum(1 for licznik in grupy.values() if licznik > 1)
    print("      Grup z wiecej niz jednym wariantem: %d (z %d)" % (realne_grupy, len(grupy)))

    print("[2/3] Konwertuje produkty...")
    statystyki: Counter = Counter()
    wejscie = 0
    zapisane = 0
    identyfikatory = set()

    with open(sciezka_csv, "w", encoding="utf-8", newline="") as plik_csv, \
            open(sciezka_jsonl, "w", encoding="utf-8", newline="\n") as plik_jsonl:
        zapis = csv.DictWriter(plik_csv, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        zapis.writeheader()
        for produkt in iteruj_produkty(sciezka_xml):
            wejscie += 1
            wiersz = zmapuj_produkt(produkt, sklep, grupy, statystyki, max_opisu)
            if wiersz is None:
                continue
            if wiersz["item_id"] in identyfikatory:
                statystyki["duplikat_item_id"] += 1
                continue
            identyfikatory.add(wiersz["item_id"])
            zapis.writerow(wiersz)
            plik_jsonl.write(json.dumps(wiersz_do_jsonl(wiersz), ensure_ascii=False) + "\n")
            zapisane += 1
            if zapisane % 2000 == 0:
                print("      %d produktow..." % zapisane)

    print("[3/3] Przygotowuje pliki do wysylki (limit %.0f MB%s)..."
          % (limit_mb, ", gzip" if kompresja else ""))
    if limit_mb > 0:
        do_wyslania = {
            "csv": dopasuj_do_limitu(sciezka_csv, limit_mb, kompresja),
            "jsonl": dopasuj_do_limitu(sciezka_jsonl, limit_mb, kompresja),
        }
    else:
        do_wyslania = {"csv": [sciezka_csv], "jsonl": [sciezka_jsonl]}

    return {
        "wejscie": wejscie,
        "zapisane": zapisane,
        "statystyki": statystyki,
        "csv": sciezka_csv,
        "jsonl": sciezka_jsonl,
        "do_wyslania": do_wyslania,
        "limit_mb": limit_mb,
    }


# --------------------------------------------------------------------------- #
# Interfejs konsolowy
# --------------------------------------------------------------------------- #

def zapytaj(pytanie: str, domyslna: str = "") -> str:
    """Pobiera odpowiedz z konsoli; Enter zatwierdza wartosc domyslna."""
    etykieta = "%s [%s]: " % (pytanie, domyslna) if domyslna else "%s: " % pytanie
    try:
        odpowiedz = input(etykieta).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nPrzerwano.")
        sys.exit(1)
    return odpowiedz or domyslna


def zapytaj_tak_nie(pytanie: str, domyslnie_tak: bool = True) -> bool:
    """Pyta o potwierdzenie (T/n)."""
    domyslna = "T" if domyslnie_tak else "N"
    odpowiedz = zapytaj("%s (T/N)" % pytanie, domyslna).lower()
    return odpowiedz.startswith(("t", "y"))


def wybierz_sklep(config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Pozwala wybrac zapisany sklep albo zdefiniowac nowy."""
    sklepy = config["sklepy"]
    klucze = sorted(sklepy)
    print("\n--- Sklepy ---")
    for indeks, klucz in enumerate(klucze, start=1):
        print("  %d. %s (%s)" % (indeks, klucz, sklepy[klucz].get("seller_name") or "?"))
    print("  %d. [nowy sklep]" % (len(klucze) + 1))

    domyslny = "1" if klucze else str(len(klucze) + 1)
    while True:
        wybor = zapytaj("Wybor", domyslny)
        if wybor.isdigit():
            numer = int(wybor)
            if 1 <= numer <= len(klucze):
                klucz = klucze[numer - 1]
                return klucz, dict(DEFAULT_SHOP_CONFIG, **sklepy[klucz])
            if numer == len(klucze) + 1:
                return "", dict(DEFAULT_SHOP_CONFIG)
        print("! Nieprawidlowy wybor.")


def uzupelnij_dane_sklepu(
    sklep: Dict[str, Any],
    dane_kanalu: Dict[str, str],
    wymus_pytania: bool,
) -> Dict[str, Any]:
    """Uzupelnia dane sprzedawcy - z konfiguracji albo z autodetekcji naglowka feedu."""
    if not wymus_pytania and sklep.get("seller_name"):
        return sklep

    print("\n--- Dane sprzedawcy (wymagane przez OpenAI) ---")
    domyslna_nazwa = sklep.get("seller_name") or (dane_kanalu.get("title") or "").strip()
    domyslny_adres = sklep.get("seller_url") or (dane_kanalu.get("link") or "").rstrip("/")

    sklep["seller_name"] = zapytaj("seller_name (nazwa sprzedawcy)", domyslna_nazwa)
    sklep["seller_url"] = zapytaj("seller_url (adres sklepu)", domyslny_adres)
    sklep["return_policy"] = zapytaj("return_policy (URL regulaminu zwrotow, moze byc puste)",
                                     sklep.get("return_policy", ""))
    sklep["waluta"] = zapytaj("waluta (kod ISO)", sklep.get("waluta", "PLN")).upper()
    sklep["store_country"] = zapytaj("store_country (kraj sklepu)",
                                     sklep.get("store_country", "PL")).upper()
    sklep["target_countries"] = zapytaj("target_countries (kraje docelowe, po przecinku)",
                                        sklep.get("target_countries", "PL")).upper()

    termin = zapytaj("return_deadline_in_days (dni na zwrot, puste = pomin)",
                     str(sklep.get("return_deadline_in_days") or ""))
    if termin.isdigit() and int(termin) > 0:
        sklep["return_deadline_in_days"] = int(termin)
        sklep["accepts_returns"] = True
    else:
        sklep["return_deadline_in_days"] = ""
        sklep["accepts_returns"] = ""

    print("\n  Flagi kwalifikacji (is_eligible_checkout i is_ads_eligible wymagaja")
    print("  wczesniejszej konfiguracji po stronie OpenAI):")
    sklep["is_eligible_search"] = zapytaj_tak_nie("  is_eligible_search", True)
    sklep["is_eligible_checkout"] = zapytaj_tak_nie("  is_eligible_checkout", False)
    sklep["is_ads_eligible"] = zapytaj_tak_nie("  is_ads_eligible", True)
    return sklep


def pokaz_podsumowanie(wynik: Dict[str, Any]) -> None:
    """Wypisuje raport z konwersji wraz z powodami pominiec."""
    statystyki: Counter = wynik["statystyki"]
    pominiete = wynik["wejscie"] - wynik["zapisane"]

    print("\n" + "=" * 62)
    print("PODSUMOWANIE")
    print("=" * 62)
    print("  Produktow w feedzie XML : %d" % wynik["wejscie"])
    print("  Zapisanych wierszy      : %d" % wynik["zapisane"])
    print("  Pominietych             : %d" % pominiete)

    powody = {klucz: wartosc for klucz, wartosc in statystyki.items()
              if klucz.startswith("brak_") or klucz == "duplikat_item_id"}
    if powody:
        print("\n  Powody pominiec:")
        for klucz, wartosc in sorted(powody.items(), key=lambda para: -para[1]):
            print("    - %-28s %d" % (klucz, wartosc))

    uwagi = {
        "gtin_odrzucony": "GTIN odrzucony (zla dlugosc lub cyfra kontrolna)",
        "gtin_z_mpn": "GTIN uzupelniony z pola mpn (poprawna cyfra kontrolna)",
        "pominieto_sale_price": "sale_price pominiete (nie jest nizsze od price)",
        "dostepnosc_unknown": "availability zamienione na 'unknown'",
        "ostrzezenie_waluta": "waluta w feedzie inna niz w konfiguracji",
        "warianty": "wierszy oznaczonych jako warianty (group_id)",
    }
    aktywne = [(opis, statystyki[klucz]) for klucz, opis in uwagi.items() if statystyki[klucz]]
    if aktywne:
        print("\n  Uwagi:")
        for opis, wartosc in aktywne:
            print("    - %-52s %d" % (opis, wartosc))

    print("\n  Pliki pelne (robocze, bez limitu rozmiaru):")
    for sciezka in (wynik["csv"], wynik["jsonl"]):
        print("    %s  (%.1f MB)" % (sciezka, os.path.getsize(sciezka) / 1048576.0))

    do_wyslania = wynik.get("do_wyslania") or {}
    if do_wyslania:
        limit_mb = wynik.get("limit_mb") or 0
        print("\n  Do wyslania do OpenAI (limit %.0f MB na plik):" % limit_mb)
        for format_pliku in ("csv", "jsonl"):
            pliki = do_wyslania.get(format_pliku) or []
            if len(pliki) > 1:
                print("    %s - katalog podzielony na %d czesci:"
                      % (format_pliku.upper(), len(pliki)))
            for sciezka in pliki:
                rozmiar = os.path.getsize(sciezka) / 1048576.0
                znacznik = "  <<< PRZEKRACZA LIMIT" if limit_mb and rozmiar > limit_mb else ""
                print("      %s  (%.1f MB)%s" % (os.path.basename(sciezka), rozmiar, znacznik))
    print("=" * 62)


def main() -> int:
    """Uruchamia interaktywna konwersje feedu XML na feed OpenAI Ads."""
    parser = argparse.ArgumentParser(
        description="Konwerter feedu XML na feed produktowy OpenAI Ads (CSV + JSONL)."
    )
    parser.add_argument("--url", help="adres feedu XML (skrot, pomija pytanie)")
    parser.add_argument("--plik", help="lokalny plik XML zamiast pobierania")
    parser.add_argument("--sklep", help="klucz sklepu z config.json")
    argumenty = parser.parse_args()

    print("=" * 62)
    print("  Konwerter feedu XML -> OpenAI Ads (ChatGPT Ads)")
    print("  Wyjscie: natywny CSV + JSONL w folderze katalog/")
    print("=" * 62)

    config = wczytaj_config()
    ustawienia = dict(DEFAULT_SETTINGS, **config.get("ustawienia", {}))
    config["ustawienia"] = ustawienia

    klucz_sklepu = ""
    sklep: Dict[str, Any] = dict(DEFAULT_SHOP_CONFIG)
    if argumenty.sklep:
        if argumenty.sklep in config["sklepy"]:
            klucz_sklepu = argumenty.sklep
            sklep = dict(DEFAULT_SHOP_CONFIG, **config["sklepy"][klucz_sklepu])
        else:
            print("! Sklep '%s' nie istnieje w config.json." % argumenty.sklep)
    elif not (argumenty.url or argumenty.plik):
        klucz_sklepu, sklep = wybierz_sklep(config)

    sciezka_xml = argumenty.plik or ""
    if sciezka_xml and not os.path.exists(sciezka_xml):
        print("! Nie znaleziono pliku: %s" % sciezka_xml)
        return 1

    if not sciezka_xml:
        adres = argumenty.url or ""
        if not adres:
            adres = zapytaj("\nAdres URL feedu XML", sklep.get("feed_url", ""))
        if not adres:
            print("! Nie podano adresu feedu.")
            return 1

        if not klucz_sklepu:
            klucz_sklepu = slug_z_url(adres)
            if klucz_sklepu in config["sklepy"]:
                sklep = dict(DEFAULT_SHOP_CONFIG, **config["sklepy"][klucz_sklepu])
        sklep["feed_url"] = adres

        sciezka_xml = os.path.join(DOWNLOAD_DIR, "%s.xml" % nazwa_pliku(klucz_sklepu))
        if os.path.exists(sciezka_xml):
            wiek = (time.time() - os.path.getmtime(sciezka_xml)) / 3600.0
            rozmiar = os.path.getsize(sciezka_xml) / 1048576.0
            print("\n  Na dysku jest juz kopia feedu (%.1f MB, sprzed %.1f h)." % (rozmiar, wiek))
            if zapytaj_tak_nie("  Pobrac feed na nowo?", True):
                pobierz_feed(adres, sciezka_xml)
        else:
            try:
                pobierz_feed(adres, sciezka_xml)
            except RuntimeError as blad:
                print("! %s" % blad)
                return 1
    else:
        if not klucz_sklepu:
            klucz_sklepu = nazwa_pliku(os.path.splitext(os.path.basename(sciezka_xml))[0])
            if klucz_sklepu in config["sklepy"]:
                sklep = dict(DEFAULT_SHOP_CONFIG, **config["sklepy"][klucz_sklepu])

    dane_kanalu = odczytaj_dane_kanalu(sciezka_xml)
    if dane_kanalu.get("title"):
        print("\n  Sklep wg naglowka feedu: %s (%s)"
              % (dane_kanalu["title"], dane_kanalu.get("link", "")))

    sklep = uzupelnij_dane_sklepu(sklep, dane_kanalu, wymus_pytania=False)
    if not sklep.get("seller_name"):
        print("! seller_name jest wymagane przez OpenAI w kazdym wierszu.")
        return 1

    print("\n--- Konfiguracja konwersji ---")
    print("  sklep              : %s" % klucz_sklepu)
    print("  seller_name        : %s" % sklep["seller_name"])
    print("  seller_url         : %s" % (sklep.get("seller_url") or "(puste)"))
    print("  return_policy      : %s" % (sklep.get("return_policy") or "(puste)"))
    print("  waluta / kraj      : %s / %s" % (sklep.get("waluta"), sklep.get("store_country")))
    print("  target_countries   : %s" % sklep.get("target_countries"))
    print("  flagi search/checkout/ads: %s / %s / %s"
          % (sklep.get("is_eligible_search"), sklep.get("is_eligible_checkout"),
             sklep.get("is_ads_eligible")))
    print("  limit pliku / gzip : %s MB / %s"
          % (ustawienia.get("limit_mb"), "tak" if ustawienia.get("gzip") else "nie"))
    print("  max dlugosc opisu  : %s znakow" % ustawienia.get("max_opisu"))
    if not zapytaj_tak_nie("\nKonwertowac z tymi ustawieniami?", True):
        sklep = uzupelnij_dane_sklepu(sklep, dane_kanalu, wymus_pytania=True)

    config["sklepy"][klucz_sklepu] = sklep
    zapisz_config(config)

    start = time.time()
    try:
        wynik = konwertuj(sciezka_xml, sklep, nazwa_pliku(klucz_sklepu), ustawienia)
    except (ET.ParseError, OSError) as blad:
        print("! Blad podczas konwersji: %s" % blad)
        return 1

    pokaz_podsumowanie(wynik)
    print("\nCzas: %.1f s" % (time.time() - start))
    return 0


if __name__ == "__main__":
    try:
        KOD = main()
    except KeyboardInterrupt:
        print("\nPrzerwano.")
        KOD = 1
    sys.exit(KOD)
