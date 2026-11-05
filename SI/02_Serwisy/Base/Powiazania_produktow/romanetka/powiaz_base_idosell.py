"""Plik powiązań Base: produkty katalogu „Domyślny” -> towary IdoSell (Romanetka.pl).

Wejście (folder źródło/): katalog Base (Base__Products__default*.csv), powiązania Base
(Base__Products_powi*.csv), eksport towarów IdoSell (products_export*.csv) i opcjonalnie
lista od klienta (do powiązania*.csv). Reguły: ANALIZA_powiazanie_base_idosell_romanetka.md.

Do pliku importu trafiają tylko pewne pary: EAN oraz pełne SKU z kodu producenta IdoSell,
każdy klucz dokładnie raz po obu stronach i bez sprzeczności wymiarów z nazw.
SKU z wartości grupy + wymiar to tylko kandydaci w raporcie dla klienta.

Wyjście (ten folder): powiazania_base_idosell_romanetka.csv (do wczytania w Base,
integracja „IdoS Romanetka”) oraz powiazania_raport.csv (dla klienta).
"""

import csv
import glob
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

FOLDER_ZRODLA = "źródło"
ID_INTEGRACJI = "3026512"
PLIK_WYNIKU = "powiazania_base_idosell_romanetka.csv"
PLIK_RAPORTU = "powiazania_raport.csv"
WYMIAR = re.compile(r"(\d{2,3})\s*(?:cm)?\s*[x/×X]\s*(\d{2,3})")
MAX_KANDYDATOW = 10
TYPY_ZRODEL = {"allegro", "erli_connector", "shop", "temupl", "inpsa", "accounting", "otomoto"}

Wymiar = Tuple[int, int]


def najnowszy(wzorzec: str, wymagany: bool = True) -> Optional[str]:
    """Zwraca najnowszy plik w folderze źródła pasujący do wzorca."""
    pliki = sorted(glob.glob(os.path.join(FOLDER_ZRODLA, wzorzec)), key=os.path.getmtime, reverse=True)
    if not pliki and wymagany:
        raise FileNotFoundError(f"brak pliku {FOLDER_ZRODLA}/{wzorzec}")
    return pliki[0] if pliki else None


def wymiary(nazwa: str) -> Set[Wymiar]:
    """Wymiary z nazwy, bez kolejności (300x160 = 160x300)."""
    return {tuple(sorted((int(a), int(b)))) for a, b in WYMIAR.findall(nazwa)}


def liczba(tekst: str) -> Optional[int]:
    """Wymiar z wartości grupy IdoSell (`140`, `140.0`) albo None."""
    try:
        return int(float(tekst.replace(",", ".")))
    except ValueError:
        return None


def kandydaci_tekst(ids: List[str]) -> str:
    """Lista ID BL do raportu, skrócona do MAX_KANDYDATOW."""
    return " ".join(ids[:MAX_KANDYDATOW]) + (" …" if len(ids) > MAX_KANDYDATOW else "")


def zgodne(nazwa_bl: str, nazwa_ido: str) -> bool:
    """Para jest spójna, gdy któraś nazwa nie ma wymiaru albo mają wspólny wymiar."""
    a, b = wymiary(nazwa_bl), wymiary(nazwa_ido)
    return not a or not b or bool(a & b)


def wczytaj_base(sciezka: str) -> Dict[str, dict]:
    """Katalog Base: ID BL -> nazwa, SKU (bez białych znaków), EAN."""
    katalog = {}
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        for w in csv.DictReader(plik, delimiter=";"):
            katalog[w["product_id"]] = {
                "id": w["product_id"], "nazwa": w["product_name"].strip(),
                "sku": w["product_sku"].strip(), "ean": w["product_ean"].strip(),
            }
    return katalog


def wczytaj_powiazania(sciezka: str) -> Dict[str, str]:
    """Obecne powiązania z IdoSell: ID BL -> ID towaru.

    Base dokleja kolejne powiązania z błędnym cudzysłowem (wariant_id zlewa się z typem
    następnego), więc grupy mają po 5 pól i zaczynają się od typu źródła.
    """
    obecne = {}
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        next(plik)
        for linia in plik:
            pola = [p.strip('"') for p in linia.rstrip("\r\n").split(";")]
            reszta = pola[6:]
            i = 0
            while i < len(reszta) and reszta[i] in TYPY_ZRODEL:
                grupa = reszta[i:i + 5]
                if grupa[0] == "shop" and len(grupa) == 5 and grupa[1] == ID_INTEGRACJI:
                    obecne[pola[0]] = grupa[4]
                i += 5
    return obecne


def wczytaj_idosell(sciezka: str) -> List[dict]:
    """Towary IdoSell: ID, nazwa, widoczność, EAN rozmiaru, kod producenta, SKU i wymiar z grupy."""
    towary = []
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        czytnik = csv.DictReader(plik)
        for w in czytnik:
            nazwy = [s.strip() for s in w["/group/group_by_parameter@name[pol]"].split("\\")]
            wartosci = [s.strip() for s in w["/group/group_by_parameter/product_value@name[pol]"].split("\\")]
            grupa = dict(zip(nazwy, wartosci)) if len(nazwy) == len(wartosci) else {}
            wys, szer = liczba(grupa.get("Wysokość produktu", "")), liczba(grupa.get("Szerokość produktu", ""))
            towary.append({
                "id": w["@id"], "nazwa": w["/description/name[pol]"].strip(),
                "widoczny": w["/visibility/site@visible"],
                "ean": w["/sizes/size@code_producer"].strip(),
                "kod": w["@code_producer"].strip(),
                "sku_grupy": next((v for k, v in grupa.items() if k.startswith("SKU")), ""),
                "wymiar": tuple(sorted((wys, szer))) if wys and szer else None,
            })
    return towary


def wczytaj_liste(sciezka: Optional[str]) -> List[str]:
    """ID BL z listy od klienta (pierwsza kolumna)."""
    if not sciezka:
        return []
    with open(sciezka, encoding="utf-8-sig", errors="replace") as plik:
        return [l.split(";")[0].strip() for l in plik if l.strip()]


def main() -> int:
    """Dopasowuje towary IdoSell do produktów Base i zapisuje plik importu oraz raport."""
    csv.field_size_limit(2**31 - 1)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        katalog = wczytaj_base(najnowszy("Base__Products__default*.csv"))
        obecne = wczytaj_powiazania(najnowszy("Base__Products_powi*.csv"))
        towary = wczytaj_idosell(najnowszy("products_export*.csv"))
        lista = wczytaj_liste(najnowszy("do powiązania*.csv", wymagany=False))
    except (FileNotFoundError, KeyError) as blad:
        print(f"Błąd danych wejściowych: {blad}")
        return 1
    print(f"Base: {len(katalog)} produktów, IdoSell: {len(towary)} towarów, "
          f"obecne powiązania IdoSell: {len(obecne)}, lista klienta: {len(lista)}")

    ean_bl, sku_bl = defaultdict(list), defaultdict(list)
    for p in katalog.values():
        if p["ean"]:
            ean_bl[p["ean"]].append(p["id"])
        if p["sku"]:
            sku_bl[p["sku"]].append(p["id"])
    ean_ido = Counter(t["ean"] for t in towary if t["ean"])
    kod_ido = Counter(t["kod"] for t in towary if t["kod"])

    pary: Dict[str, Tuple[str, str]] = {}  # ID IdoSell -> (ID BL, metoda)
    uzyte_bl: Set[str] = set()
    uwagi: Dict[str, Tuple[str, str, str]] = {}  # ID IdoSell -> (status, ID BL, uwaga)

    def sprobuj(t: dict, klucz: str, indeks_bl: dict, licznik_ido: Counter, metoda: str) -> None:
        """Paruje towar po kluczu, jeśli jest on jednoznaczny po obu stronach i wymiary się zgadzają."""
        if t["id"] in pary or not klucz or klucz not in indeks_bl:
            return
        kandydaci = [b for b in indeks_bl[klucz] if b not in uzyte_bl]
        if len(indeks_bl[klucz]) > 1 or licznik_ido[klucz] > 1:
            uwagi.setdefault(t["id"], ("do sprawdzenia", kandydaci_tekst(indeks_bl[klucz]),
                                       f"{metoda} występuje wielokrotnie ({len(indeks_bl[klucz])} produktów Base)"))
        elif kandydaci and not zgodne(katalog[kandydaci[0]]["nazwa"], t["nazwa"]):
            uwagi.setdefault(t["id"], ("do sprawdzenia", kandydaci[0], f"{metoda} zgodny, wymiar w nazwie inny"))
        elif kandydaci:
            pary[t["id"]] = (kandydaci[0], metoda)
            uzyte_bl.add(kandydaci[0])
            uwagi.pop(t["id"], None)

    for t in towary:
        sprobuj(t, t["ean"], ean_bl, ean_ido, "EAN")
    for t in towary:
        sprobuj(t, t["kod"], sku_bl, kod_ido, "SKU")

    # Kandydaci SKU z grupy + wymiar — tylko do raportu.
    sku_wymiar = defaultdict(list)
    for p in katalog.values():
        if p["id"] not in uzyte_bl:
            for w in wymiary(p["nazwa"]):
                sku_wymiar[(p["sku"], w)].append(p["id"])
    for t in towary:
        if t["id"] in pary or t["id"] in uwagi or not t["sku_grupy"] or not t["wymiar"]:
            continue
        kandydaci = sku_wymiar.get((t["sku_grupy"], t["wymiar"]), [])
        if len(kandydaci) == 1:
            uwagi[t["id"]] = ("kandydat SKU+wymiar", kandydaci[0], "SKU z grupy IdoSell i wymiar z nazwy Base")
        elif kandydaci:
            uwagi[t["id"]] = ("niejednoznaczny SKU+wymiar", kandydaci_tekst(kandydaci),
                              f"{len(kandydaci)} produkty Base z tym SKU i wymiarem")

    with open(PLIK_WYNIKU, "w", encoding="utf-8", newline="") as plik:
        for t in towary:
            if t["id"] in pary:
                p = katalog[pary[t["id"]][0]]
                plik.write(f"{p['id']};{t['id']};;{p['sku']};{p['ean']}\r\n")

    nadpisane = sum(1 for bl in obecne if bl in uzyte_bl)
    statusy = Counter()
    with open(PLIK_RAPORTU, "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.writer(plik)
        pisarz.writerow(["status", "metoda", "id_idosell", "nazwa_idosell", "widoczny_idosell", "ean_idosell",
                         "sku_idosell", "id_bl", "nazwa_bl", "sku_bl", "ean_bl", "uwagi"])
        for t in towary:
            sku_ido = t["kod"] or t["sku_grupy"]
            if t["id"] in pary:
                bl, metoda = pary[t["id"]]
                status, uwaga = "powiązany", ""
            elif t["id"] in uwagi:
                status, bl, uwaga = uwagi[t["id"]]
                metoda = ""
            else:
                status, metoda, bl, uwaga = "brak pary w Base", "", "", ""
            p = katalog.get(bl, {})
            statusy[status] += 1
            pisarz.writerow([status, metoda, t["id"], t["nazwa"], t["widoczny"], t["ean"], sku_ido,
                             bl, p.get("nazwa", ""), p.get("sku", ""), p.get("ean", ""), uwaga])
        for bl in lista:
            if bl not in uzyte_bl:
                p = katalog.get(bl, {})
                statusy["lista klienta – brak pary"] += 1
                pisarz.writerow(["lista klienta – brak pary", "", "", "", "", "", "", bl, p.get("nazwa", ""),
                                 p.get("sku", ""), p.get("ean", ""), "brak pewnego odpowiednika w IdoSell"])
        for bl, ido in obecne.items():
            if bl not in uzyte_bl:
                p = katalog.get(bl, {})
                statusy["błędne powiązanie – usunąć ręcznie"] += 1
                pisarz.writerow(["błędne powiązanie – usunąć ręcznie", "", ido, "", "", "", "", bl,
                                 p.get("nazwa", ""), p.get("sku", ""), p.get("ean", ""),
                                 "obecne powiązanie w Base bez potwierdzenia w danych"])

    metody = Counter(m for _, m in pary.values())
    print(f"\nPowiązania do importu: {len(pary)} (EAN: {metody['EAN']}, SKU: {metody['SKU']}) -> {PLIK_WYNIKU}")
    print(f"Nadpisane obecne powiązania: {nadpisane} z {len(obecne)}")
    print(f"Lista klienta powiązana: {sum(1 for bl in lista if bl in uzyte_bl)} z {len(lista)}")
    print(f"Produkty Base bez pary (tylko liczba): {len(katalog) - len(uzyte_bl)}")
    print(f"\nRaport -> {PLIK_RAPORTU}")
    for status, ile in statusy.most_common():
        print(f"  {status}: {ile}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
