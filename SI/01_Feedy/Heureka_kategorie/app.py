# -*- coding: utf-8 -*-
"""
Mapowanie kategorii na kategorie Heureka (Heureka.cz / Heureka.sk).

Obsługiwane są dwa źródła kategorii:
  1. taksonomia Google Shopping   -- plik taxonomy-with-ids.<lang>.xls
  2. eksport kategorii z IdoSell  -- plik products_export*.csv
     (kolumny @id, /category@id, /category@name[<jezyk>])

Uruchomienie bez argumentów prowadzi przez trzy pytania: który plik Heureki,
które źródło kategorii, który plik źródłowy. Zakładamy, że plik Heureki i plik
źródłowy są w tym samym języku.

Wejście (szukane w katalogu skryptu):
  - plik kategorii Heureka      -- CSV (segment, ID, kategoria, povinný název, przykład)
  - plik źródła kategorii       -- taksonomia Google (.xls) albo eksport IdoSell (.csv)
  - segment_map_<zrodlo>_<lang>.csv -- kotwica: top-level źródła -> dozwolone segmenty
                                   Heureki; generowana automatycznie, do ręcznej korekty

Wyjście (dwa pliki, nazwy zawierają tryb i język):
  - raport_<zrodlo>_<lang>.csv         -- pełne mapowanie: score, metoda, flaga do przeglądu
  - <zrodlo>_to_heureka_<lang>.xslt    -- XSLT 1.0, named template z xsl:choose (ID -> ID)
Statystyki pokrycia trafiają na ekran.

Argumenty (wszystkie opcjonalne -- brakujące dane skrypt dopyta):
  --zrodlo google|idosell   pomija pytanie o źródło kategorii
  --auto                    bez pytań; bierze pierwszy pasujący plik każdego rodzaju
  --tylko-pewne             do XSLT trafiają wyłącznie dopasowania fuzzy_high
  --z-wezlami               do XSLT trafiają także węzły pośrednie drzewa kategorii

Metoda: dopasowanie rozmyte ograniczone do segmentów dopuszczonych kotwicą,
scoring = 0.7 * nazwa liścia + 0.3 * kontekst pełnej ścieżki, preferencja kategorii
ogólniejszej przy zbliżonym wyniku, test zgodności rzeczownika głównego, a na koniec
dwa fallbacki dla węzłów bez dopasowania: dziedziczenie po pewnym przodku w drzewie
oraz dopasowanie nazwy przodka wprost ze ścieżki.
"""

import csv
import glob
import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Polskie i czeskie znaki w menu -- konsola Windows domyślnie nie jest w UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WZORCE_GOOGLE = ("*.xls", "*.xlsx")
WZORZEC_CSV = "*.csv"

# Progi wiarygodności (score 0-100)
PROG_WYSOKI = 85.0   # >= : dopasowanie automatyczne
PROG_SREDNI = 65.0   # >= : dopasowanie przyjęte, ale oznaczone do przeglądu
OKNO_OGOLNOSCI = 4.0  # przy różnicy score <= tej wartości wybierz kategorię ogólniejszą
MAKS_DZIEDZICZENIA = 2  # ile poziomów w górę drzewa wolno szukać przodka

WAGA_LISCIA = 0.7
WAGA_SCIEZKI = 0.3

PROG_KOTWICY = 70.0  # próg auto-propozycji kotwicy dla eksportu IdoSell

# Kotwica dla taksonomii Google: top-level Google -> dozwolone segmenty Heureka (nazwy CZ).
# Dla Heureki SK nazwy segmentów są tłumaczone tabelą SEGMENTY_CZ_SK.
KOTWICA_GOOGLE = {
    "Chovatelství": ["Chovatelské potřeby"],
    "Děti a kojenci": ["Dětské zboží"],
    "Dům a zahrada": ["Bydlení a doplňky", "Dílna, stavba, zahrada",
                      "Domácí a osobní spotřebiče", "Velké spotřebiče", "Drogerie"],
    "Elektronika": ["Elektronika", "Gaming", "Domácí a osobní spotřebiče"],
    "Foto, video a optika": ["Elektronika"],
    "Hračky a hry": ["Hračky", "Gaming", "Hobby"],
    "Jídlo, pití a tabák": ["Jídlo a nápoje"],
    "Kancelářské potřeby": ["Kancelář a papírnictví"],
    "Kutilství a řemeslo": ["Dílna, stavba, zahrada", "Hobby"],
    "Média": ["Filmy, knihy, hry"],
    "Nábytek": ["Bydlení a doplňky"],
    "Náboženské a obřadní zboží": ["Hobby", "Bydlení a doplňky"],
    "Obchod a průmysl": ["Dílna, stavba, zahrada", "Kancelář a papírnictví", "Hobby"],
    "Oblečení a doplňky": ["Oblečení, obuv a doplňky"],
    "Pro dospělé": ["Erotické pomůcky"],
    "Software": ["Elektronika", "Gaming"],
    "Sportovní potřeby": ["Sport a outdoor"],
    "Tašky a zavazadla": ["Oblečení, obuv a doplňky", "Sport a outdoor"],
    "Umění a zábava": ["Hobby", "Filmy, knihy, hry", "Hračky"],
    "Vozidla a náhradní díly": ["Auto-moto"],
    "Zdraví a krása": ["Kosmetika a parfémy", "Zdraví", "Drogerie", "Erotické pomůcky"],
}

# Nazwy segmentów Heureki: czeskie -> słowackie. Fuzzy tu nie wystarcza,
# bo część nazw jest różna słowotwórczo (Dětské zboží / Detský tovar).
SEGMENTY_CZ_SK = {
    "Auto-moto": "Auto-moto",
    "Bydlení a doplňky": "Bývanie a doplnky",
    "Chovatelské potřeby": "Chovateľské potreby",
    "Domácí a osobní spotřebiče": "Domáce a osobné spotrebiče",
    "Drogerie": "Drogéria",
    "Dílna, stavba, zahrada": "Dielňa, stavba, záhrada",
    "Dětské zboží": "Detský tovar",
    "Elektronika": "Elektronika",
    "Erotické pomůcky": "Erotické pomôcky",
    "Filmy, knihy, hry": "Filmy, knihy, hry",
    "Gaming": "Gaming",
    "Hobby": "Hobby",
    "Hračky": "Hračky",
    "Jídlo a nápoje": "Jedlo a nápoje",
    "Kancelář a papírnictví": "Kancelária a papiernictvo",
    "Kosmetika a parfémy": "Kozmetika a parfumy",
    "Oblečení, obuv a doplňky": "Oblečenie, obuv a doplnky",
    "Sport a outdoor": "Šport a outdoor",
    "Velké spotřebiče": "Veľké spotrebiče",
    "Zdraví": "Zdravie",
}


def sciezka(nazwa):
    return os.path.join(BASE_DIR, nazwa)


def znajdz(wzorce):
    """Pliki pasujące do wzorca (lub wzorców) w katalogu skryptu."""
    if isinstance(wzorce, str):
        wzorce = (wzorce,)
    znalezione = []
    for wzorzec in wzorce:
        znalezione += sorted(glob.glob(sciezka(wzorzec)))
    return znalezione


def zgodna_glowa(nazwa_a, nazwa_b):
    """Czy obie nazwy dotyczą tego samego przedmiotu, a nie tylko podobnie brzmią?

    W czeskim i słowackim rzeczownik główny frazy stoi na końcu ("Sportovní dresy"),
    dlatego porównanie ostatnich tokenów odsiewa pary zgodne wyłącznie znakowo:
    Šortky/Šátky, Toaletní sedátka/Toaletní stolky, Plynové plotny/Plynové konvektory.
    """
    tokeny_a, tokeny_b = nazwa_a.split(), nazwa_b.split()
    if not tokeny_a or not tokeny_b:
        return False
    glowa_a, glowa_b = tokeny_a[-1], tokeny_b[-1]
    if fuzz.ratio(glowa_a, glowa_b) >= 80:
        return True
    # wspólny rdzeń (odmiana / liczba mnoga): pralka/pralki, vrtacka/vrtacky
    return len(os.path.commonprefix([glowa_a, glowa_b])) >= 4


def normalizuj(tekst):
    """Do porównań: bez diakrytyków, małe litery, tylko alfanumeryki i pojedyncze spacje."""
    tekst = unicodedata.normalize("NFKD", str(tekst))
    tekst = tekst.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", tekst)).strip()


def zbuduj_drzewo(df):
    """Uzupełnia DataFrame (gid, poziomy) o path, top, leaf, parent_gid, is_leaf."""
    df["path"] = df.poziomy.map(lambda p: " > ".join(p))
    df["top"] = df.poziomy.map(lambda p: p[0] if p else "")
    df["leaf"] = df.poziomy.map(lambda p: p[-1] if p else "")

    gid_po_sciezce = dict(zip(df.path, df.gid))
    df["parent_gid"] = df.poziomy.map(
        lambda p: gid_po_sciezce.get(" > ".join(p[:-1]), "") if len(p) > 1 else ""
    )

    # liść = ścieżka, która nie jest prefiksem żadnej innej ścieżki
    prefiksy = set()
    for poziomy in df.poziomy:
        for i in range(1, len(poziomy)):
            prefiksy.add(" > ".join(poziomy[:i]))
    df["is_leaf"] = ~df.path.isin(prefiksy)
    return df


def wczytaj_google(plik):
    """Taksonomia Google: kol. 0 = ID, kol. 1..7 = poziomy hierarchii."""
    surowe = pd.read_excel(plik, dtype=str, header=None)
    if surowe.shape[1] < 2:
        sys.exit(f"BŁĄD: {os.path.basename(plik)} ma {surowe.shape[1]} kolumn, "
                 "to nie wygląda na taksonomię Google")

    poziomy = surowe.iloc[:, 1:].apply(
        lambda w: [v.strip() for v in w if isinstance(v, str) and v.strip()], axis=1
    )
    df = pd.DataFrame({"gid": surowe[0].astype(str).str.strip(), "poziomy": poziomy})
    df = df[df.gid.str.fullmatch(r"\d+") & df.poziomy.map(bool)].reset_index(drop=True)
    return zbuduj_drzewo(df)


def wczytaj_idosell(plik):
    """Eksport IdoSell: kolumny /category@id oraz /category@name[<jezyk>].

    Eksport jest listą produktów, więc kategorie deduplikujemy. Ścieżka kategorii
    jest w jednej komórce, rozdzielona ukośnikami.
    """
    surowe = pd.read_csv(plik, dtype=str, keep_default_na=False, encoding="utf-8")

    kol_id = next((k for k in surowe.columns if "category@id" in k.lower()), None)
    kol_nazwa = next((k for k in surowe.columns if "category@name" in k.lower()), None)
    if not kol_id or not kol_nazwa:
        sys.exit(f"BŁĄD: {os.path.basename(plik)} nie ma kolumn /category@id "
                 f"i /category@name[...]; znalezione kolumny: {list(surowe.columns)}")

    jezyk = re.search(r"\[(\w+)\]", kol_nazwa)
    print(f"  IdoSell: kolumna kategorii '{kol_nazwa}'"
          f"{f' (jezyk {jezyk.group(1)})' if jezyk else ''}, produktów: {len(surowe)}")

    kat = surowe[[kol_id, kol_nazwa]].copy()
    kat.columns = ["gid", "sciezka_kat"]
    kat["gid"] = kat.gid.str.strip()
    kat["sciezka_kat"] = kat.sciezka_kat.str.strip()
    kat = kat[(kat.gid != "") & (kat.sciezka_kat != "")]
    kat = kat.drop_duplicates(subset=["gid"]).reset_index(drop=True)

    kat["poziomy"] = kat.sciezka_kat.map(
        lambda s: [c.strip() for c in s.split("/") if c.strip()]
    )
    kat = kat[kat.poziomy.map(bool)].reset_index(drop=True)
    return zbuduj_drzewo(kat[["gid", "poziomy"]].copy())


def wczytaj_heureke(plik):
    """Kategorie Heureka -> DataFrame: hid, segment, kategorie, povinny."""
    df = pd.read_csv(plik, dtype=str, keep_default_na=False, encoding="utf-8")
    if df.shape[1] < 4:
        sys.exit(f"BŁĄD: {os.path.basename(plik)} ma {df.shape[1]} kolumn, "
                 "oczekiwano co najmniej 4 (segment, ID, kategoria, povinný název)")

    df = df.iloc[:, :5].copy()
    df.columns = ["segment", "hid", "kategorie", "povinny", "priklad"][:df.shape[1]]
    for kol in df.columns:
        df[kol] = df[kol].astype(str).str.strip()

    # odsiew wierszy technicznych (#N/A, puste ID, resztki po wielolinijkowych polach)
    przed = len(df)
    df = df[df.hid.str.fullmatch(r"\d+") & (df.kategorie != "")].copy()
    df = df.drop_duplicates(subset=["hid"]).reset_index(drop=True)
    if przed - len(df):
        print(f"  Heureka: odrzucono {przed - len(df)} wierszy bez poprawnego ID/nazwy")
    return df


def domyslna_kotwica(tryb, topy, segmenty, jezyk):
    """Kotwica startowa: wbudowana dla Google, auto-proponowana dla eksportu IdoSell."""
    if tryb == "google":
        if jezyk == "SK":
            return {top: [SEGMENTY_CZ_SK.get(s, s) for s in segs]
                    for top, segs in KOTWICA_GOOGLE.items()}
        return dict(KOTWICA_GOOGLE)

    # Kategorie sklepu są dowolne, więc proponujemy segmenty po podobieństwie nazwy.
    # Puste = bez ograniczenia (wszystkie segmenty) -- do ręcznego zawężenia.
    propozycja = {}
    segmenty = list(segmenty)
    n_segmenty = [normalizuj(s) for s in segmenty]
    for top in topy:
        n_top = normalizuj(top)
        wyniki = [fuzz.token_set_ratio(n_top, n_seg) for n_seg in n_segmenty]
        pasujace = [segmenty[i] for i, w in enumerate(wyniki) if w >= PROG_KOTWICY]
        propozycja[top] = pasujace
    return propozycja


def wczytaj_kotwice(plik_kotwicy, tryb, topy, segmenty, jezyk):
    """Kotwica segmentów z pliku; przy braku pliku zapisuje wersję startową."""
    plik = sciezka(plik_kotwicy)

    if not os.path.exists(plik):
        startowa = domyslna_kotwica(tryb, topy, segmenty, jezyk)
        with open(plik, "w", encoding="utf-8", newline="") as fh:
            zapis = csv.writer(fh, delimiter=";")
            zapis.writerow([f"{tryb}_top_level", "heureka_segmenty (oddzielone |)"])
            for top in sorted(startowa):
                zapis.writerow([top, "|".join(startowa[top])])
        rodzaj = "wbudowana" if tryb == "google" else "auto-propozycja"
        print(f"  Utworzono {plik_kotwicy} ({rodzaj}) -- warto sprawdzić i uruchomić ponownie")

    kotwica = {}
    with open(plik, encoding="utf-8", newline="") as fh:
        czyt = csv.reader(fh, delimiter=";")
        next(czyt, None)
        for wiersz in czyt:
            if not wiersz or not wiersz[0].strip():
                continue
            kolumna = wiersz[1] if len(wiersz) > 1 else ""
            kotwica[wiersz[0].strip()] = [s.strip() for s in kolumna.split("|") if s.strip()]

    # kontrola spójności z danymi
    for top in sorted(set(topy) - set(kotwica)):
        print(f"  UWAGA: gałąź źródła bez wpisu w kotwicy (pomijana): {top}")
    puste = sorted(t for t in kotwica if not kotwica[t] and t in set(topy))
    for top in puste:
        print(f"  UWAGA: gałąź bez zawężenia segmentów (dopuszczone wszystkie): {top}")
    nieznane = {s for segs in kotwica.values() for s in segs} - set(segmenty)
    for seg in sorted(nieznane):
        print(f"  UWAGA: segment z kotwicy nie występuje w danych Heureka: {seg}")
    return kotwica


def przygotuj_heureke(heureka):
    heureka = heureka.assign(
        n_kat=heureka.kategorie.map(normalizuj),
        n_kontekst=(heureka.segment + " " + heureka.kategorie).map(normalizuj),
    )
    heureka["tokeny"] = heureka.n_kat.str.count(" ") + 1
    return heureka


def kandydaci_dla(heureka, kotwica, top):
    """Kategorie Heureki dopuszczone dla danej gałęzi źródła."""
    if top not in kotwica:
        return heureka.iloc[0:0]
    segmenty = kotwica[top]
    if not segmenty:  # puste = brak zawężenia
        return heureka
    return heureka[heureka.segment.isin(segmenty)]


def dopasuj(zrodlo, heureka, kotwica):
    """Dopasowanie rozmyte w obrębie dozwolonych segmentów."""
    heureka = przygotuj_heureke(heureka)
    zrodlo = zrodlo.assign(
        n_leaf=zrodlo.leaf.map(normalizuj),
        n_path=zrodlo.path.map(normalizuj),
    )

    hid = pd.Series("", index=zrodlo.index, dtype=object)
    hkat = pd.Series("", index=zrodlo.index, dtype=object)
    score = pd.Series(0.0, index=zrodlo.index, dtype=float)

    for top, grupa in zrodlo.groupby("top", sort=False):
        kandydaci = kandydaci_dla(heureka, kotwica, top)
        if kandydaci.empty:
            continue

        # macierze podobieństwa: nazwa liścia oraz kontekst pełnej ścieżki
        m_leaf = process.cdist(grupa.n_leaf.tolist(), kandydaci.n_kat.tolist(),
                               scorer=fuzz.token_sort_ratio, workers=-1)
        m_path = process.cdist(grupa.n_path.tolist(), kandydaci.n_kontekst.tolist(),
                               scorer=fuzz.token_set_ratio, workers=-1)
        razem = WAGA_LISCIA * m_leaf + WAGA_SCIEZKI * m_path

        tokeny = kandydaci.tokeny.to_numpy()
        ids = kandydaci.hid.to_numpy()
        nazwy = kandydaci.kategorie.to_numpy()

        for poz_wiersza, idx in enumerate(grupa.index):
            wyniki = razem[poz_wiersza]
            najlepszy = wyniki.max()
            # w oknie tolerancji preferuj kategorię ogólniejszą (mniej tokenów),
            # by "Kávovary" nie trafiło do "Pákové kávovary"
            bliscy = np.flatnonzero(wyniki >= najlepszy - OKNO_OGOLNOSCI)
            wybor = bliscy[np.lexsort((-wyniki[bliscy], tokeny[bliscy]))[0]]

            hid.at[idx] = ids[wybor]
            hkat.at[idx] = nazwy[wybor]
            score.at[idx] = round(float(wyniki[wybor]), 1)

    zrodlo["heureka_id"] = hid
    zrodlo["heureka_kategorie"] = hkat
    zrodlo["score"] = score
    zrodlo["metoda"] = np.where(
        zrodlo.score >= PROG_WYSOKI, "fuzzy_high",
        np.where(zrodlo.score >= PROG_SREDNI, "fuzzy_review", "brak"),
    )

    # Dopasowania z przedziału średniego przyjmujemy tylko wtedy, gdy zgadza się
    # rzeczownik główny -- inaczej wpadają tu pary podobne wyłącznie literowo.
    srednie = zrodlo.metoda == "fuzzy_review"
    zgodne = [
        zgodna_glowa(normalizuj(l), normalizuj(k))
        for l, k in zip(zrodlo.loc[srednie, "leaf"], zrodlo.loc[srednie, "heureka_kategorie"])
    ]
    zrodlo.loc[srednie, "metoda"] = np.where(zgodne, "fuzzy_review", "brak")

    zrodlo.loc[zrodlo.metoda == "brak", ["heureka_id", "heureka_kategorie"]] = ""
    zrodlo.loc[zrodlo.metoda == "brak", "score"] = 0.0
    return zrodlo


def dopasuj_nazwy_przodkow(df, heureka, kotwica):
    """Fallback: dla węzłów bez dopasowania spróbuj nazwy przodka wprost ze ścieżki.

    Potrzebny zwłaszcza dla eksportu IdoSell, gdzie kategorie pośrednie zwykle nie
    występują jako osobne wiersze, więc dziedziczenie po przodku nie ma czego przejąć.
    """
    heureka = przygotuj_heureke(heureka)

    for idx in df.index[df.metoda == "brak"]:
        poziomy = df.at[idx, "poziomy"]
        kandydaci = kandydaci_dla(heureka, kotwica, df.at[idx, "top"])
        if kandydaci.empty or len(poziomy) < 2:
            continue

        # od najgłębszego przodka w górę, z pominięciem samego liścia
        for poziom in reversed(poziomy[:-1]):
            n_poziom = normalizuj(poziom)
            wyniki = np.array([fuzz.token_sort_ratio(n_poziom, n) for n in kandydaci.n_kat])
            najlepszy = wyniki.max()
            if najlepszy < PROG_WYSOKI:
                continue
            bliscy = np.flatnonzero(wyniki >= najlepszy - OKNO_OGOLNOSCI)
            tokeny = kandydaci.tokeny.to_numpy()
            wybor = bliscy[np.lexsort((-wyniki[bliscy], tokeny[bliscy]))[0]]
            nazwa = kandydaci.kategorie.iloc[wybor]
            if not zgodna_glowa(n_poziom, normalizuj(nazwa)):
                continue
            df.at[idx, "heureka_id"] = kandydaci.hid.iloc[wybor]
            df.at[idx, "heureka_kategorie"] = nazwa
            df.at[idx, "score"] = round(float(wyniki[wybor]), 1)
            df.at[idx, "metoda"] = "nazwa_przodka"
            break
    return df


def odziedzicz_po_przodkach(df, maks_poziomow=MAKS_DZIEDZICZENIA):
    """Węzły bez dopasowania przejmują mapowanie bliskiego, pewnego przodka.

    Dziedziczymy wyłącznie po przodkach z metodą fuzzy_high i najwyżej o
    `maks_poziomow` w górę -- inaczej jedna fałszywka rozlewa się na całą gałąź.
    """
    po_gid = df.set_index("gid")
    rodzic = po_gid.parent_gid.to_dict()
    mapowanie = {
        g: (r.heureka_id, r.heureka_kategorie)
        for g, r in po_gid.iterrows() if r.metoda == "fuzzy_high"
    }

    for idx in df.index[df.metoda == "brak"]:
        biezacy = rodzic.get(df.at[idx, "gid"], "")
        krokow = 0
        while biezacy and krokow < maks_poziomow:
            if biezacy in mapowanie:
                df.at[idx, "heureka_id"], df.at[idx, "heureka_kategorie"] = mapowanie[biezacy]
                df.at[idx, "metoda"] = "inherited"
                break
            biezacy = rodzic.get(biezacy, "")
            krokow += 1
    return df


DO_PRZEGLADU = ("fuzzy_review", "inherited", "nazwa_przodka")


def zapisz_raport(df, plik):
    """Raport CSV: pełne mapowanie z wynikiem, metodą i flagą do przeglądu."""
    kolumny = ["gid", "path", "leaf", "top", "is_leaf", "heureka_id", "heureka_kategorie",
               "score", "metoda", "do_przegladu"]
    wynik = df.copy()
    wynik["do_przegladu"] = np.where(wynik.metoda.isin(DO_PRZEGLADU), "1", "")
    wynik = wynik[kolumny].rename(columns={
        "gid": "source_id", "path": "source_path", "leaf": "source_leaf",
        "top": "source_top_level",
    })
    wynik.to_csv(sciezka(plik), index=False, sep=";", encoding="utf-8-sig")
    return wynik


def zapisz_xslt(df, plik, tryb, jezyk, tylko_pewne=False, z_wezlami=False):
    """XSLT 1.0: named template z xsl:choose, ID kategorii źródła -> ID kategorii Heureka.

    Domyślnie eksportujemy tylko liście drzewa źródłowego -- feed produktowy podaje
    najgłębszą kategorię, a Heureka jest listą liści, więc dopasowanie węzła
    pośredniego (np. "Hudební nástroje") do wąskiej kategorii Heureki byłoby błędne.
    """
    zmapowane = df[df.heureka_id != ""].copy()
    if tylko_pewne:
        zmapowane = zmapowane[zmapowane.metoda == "fuzzy_high"]
    if not z_wezlami:
        zmapowane = zmapowane[zmapowane.is_leaf]
    zmapowane = zmapowane.copy()
    zmapowane["klucz"] = pd.to_numeric(zmapowane.gid, errors="coerce")
    zmapowane = zmapowane.sort_values(["klucz", "gid"])

    nazwa_szablonu = "google-to-heureka" if tryb == "google" else "category-to-heureka"
    nazwa_parametru = "google_id" if tryb == "google" else "category_id"
    zrodlo_opis = ("ID kategorii Google Shopping" if tryb == "google"
                   else "ID kategorii sklepu IdoSell")

    licznik = df.metoda.value_counts()
    rozbicie = ", ".join(
        f"{metoda}: {int(licznik.get(metoda, 0))}"
        for metoda in ("fuzzy_high", "fuzzy_review", "nazwa_przodka", "inherited")
        if licznik.get(metoda, 0)
    )

    linie = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!--",
        f"  Mapowanie: {zrodlo_opis} -> ID kategorii Heureka ({jezyk})",
        "  Plik wygenerowany skryptem app.py. Nie edytować ręcznie.",
        f"  Wpisów: {len(zmapowane)} z {len(df)} kategorii źródłowych.",
        f"  Metody dopasowania: {rozbicie}.",
        "  Szczegóły i wpisy do przeglądu: patrz raport CSV obok tego pliku.",
        "",
        "  Użycie:",
        f'    <xsl:call-template name="{nazwa_szablonu}">',
        f'      <xsl:with-param name="{nazwa_parametru}" select="..."/>',
        "    </xsl:call-template>",
        "-->",
        '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">',
        "",
        f'  <xsl:template name="{nazwa_szablonu}">',
        f'    <xsl:param name="{nazwa_parametru}"/>',
        "    <xsl:choose>",
    ]
    for _, wiersz in zmapowane.iterrows():
        komentarz = f"{wiersz.leaf} -> {wiersz.heureka_kategorie}".replace("--", "-")
        linie.append(
            f"      <xsl:when test=\"${nazwa_parametru} = '{wiersz.gid}'\">"
            f"{wiersz.heureka_id}</xsl:when><!-- {komentarz} -->"
        )
    linie += [
        "      <xsl:otherwise/><!-- brak odpowiednika w taksonomii Heureka -->",
        "    </xsl:choose>",
        "  </xsl:template>",
        "",
        "</xsl:stylesheet>",
    ]
    with open(sciezka(plik), "w", encoding="utf-8") as fh:
        fh.write("\n".join(linie) + "\n")
    return len(zmapowane)


def zestawienie(wynik, liczba_xslt, tryb, jezyk):
    """Statystyki pokrycia -- wypisywane na ekran po zakończeniu pracy."""
    licznik = wynik.metoda.value_counts()
    razem = len(wynik)
    liscie = wynik[wynik.is_leaf]
    linie = [
        f"PODSUMOWANIE MAPOWANIA {tryb} -> Heureka {jezyk}",
        "=" * 56,
        f"Kategorii źródłowych:        {razem} (liści: {len(liscie)}, "
        f"węzłów pośrednich: {razem - len(liscie)})",
        f"Zmapowanych (razem):         {(wynik.heureka_id != '').sum()} "
        f"({(wynik.heureka_id != '').mean():.1%})",
        f"Zmapowanych liści:           {(liscie.heureka_id != '').sum()} "
        f"({(liscie.heureka_id != '').mean():.1%})",
        f"Wpisów w XSLT:               {liczba_xslt}",
        "",
        "Wg metody:",
    ]
    for metoda in ("fuzzy_high", "fuzzy_review", "nazwa_przodka", "inherited", "brak"):
        ile = int(licznik.get(metoda, 0))
        linie.append(f"  {metoda:14s} {ile:5d}  ({ile / razem:5.1%})")
    linie += [
        "",
        f"Do przeglądu (do_przegladu=1): {(wynik.do_przegladu == '1').sum()}",
        "",
        "Pokrycie wg gałęzi źródła:",
    ]
    for top, grupa in wynik.groupby("source_top_level"):
        pokrycie = (grupa.heureka_id != "").mean()
        wysokie = (grupa.metoda == "fuzzy_high").sum()
        linie.append(f"  {top[:30]:32s} {len(grupa):5d} kat.  pokrycie {pokrycie:5.1%}  "
                     f"pewnych {wysokie:4d}")

    return "\n".join(linie)


def argument(nazwa, dozwolone):
    """Wartość argumentu --nazwa z listy dozwolonych (bez rozróżniania wielkości)."""
    if nazwa not in sys.argv:
        return None
    poz = sys.argv.index(nazwa) + 1
    if poz >= len(sys.argv):
        sys.exit(f"BŁĄD: {nazwa} wymaga wartości: {'|'.join(dozwolone)}")
    wartosc = sys.argv[poz]
    dopasowane = next((d for d in dozwolone if d.lower() == wartosc.lower()), None)
    if not dopasowane:
        sys.exit(f"BŁĄD: {nazwa}={wartosc}; dozwolone: {'|'.join(dozwolone)}")
    return dopasowane


def zapytaj_z_listy(pytanie, pozycje, opisy=None, auto=False):
    """Numerowane menu wyboru. Enter przyjmuje pozycję 1; --auto nie pyta wcale."""
    if not pozycje:
        sys.exit(f"BŁĄD: brak plików do wyboru ({pytanie})")
    if len(pozycje) == 1 or auto:
        return pozycje[0]

    print()
    print(pytanie)
    for numer, pozycja in enumerate(pozycje, 1):
        opis = f"  [{opisy[numer - 1]}]" if opisy else ""
        print(f"  {numer}. {pozycja}{opis}")

    while True:
        try:
            odpowiedz = input(f"Wybierz 1-{len(pozycje)} (Enter = 1): ").strip()
        except EOFError:
            sys.exit("\nPrzerwano: brak wejścia z klawiatury (użyj --auto lub --zrodlo).")
        if not odpowiedz:
            return pozycje[0]
        if odpowiedz.isdigit() and 1 <= int(odpowiedz) <= len(pozycje):
            return pozycje[int(odpowiedz) - 1]
        print(f"  Podaj liczbę 1-{len(pozycje)}.")


def wyglada_na_heureke(plik):
    """Czy CSV ma układ listy kategorii Heureki (segment, ID, kategoria, ...)?"""
    try:
        probka = pd.read_csv(plik, dtype=str, keep_default_na=False, nrows=20)
    except Exception:
        return False
    if probka.shape[1] < 4 or probka.empty:
        return False
    return probka.iloc[:, 1].str.strip().str.fullmatch(r"\d+").mean() >= 0.8


def wyglada_na_idosell(plik):
    """Czy CSV ma kolumny eksportu kategorii z IdoSell?"""
    try:
        naglowek = pd.read_csv(plik, dtype=str, nrows=0)
    except Exception:
        return False
    kolumny = " ".join(naglowek.columns).lower()
    return "category@id" in kolumny and "category@name" in kolumny


def kandydaci_zrodla(tryb, wszystkie_csv, plik_heureki=None):
    """Pliki mogące być źródłem kategorii dla wybranego trybu."""
    if tryb == "google":
        znalezione = znajdz(WZORCE_GOOGLE)
        if not znalezione:
            sys.exit(f"BŁĄD: brak pliku .xls/.xlsx z taksonomią Google w {BASE_DIR}")
        return znalezione

    inne_csv = [p for p in wszystkie_csv if p != plik_heureki]
    znalezione = [p for p in inne_csv if wyglada_na_idosell(p)] or inne_csv
    if not znalezione:
        sys.exit(f"BŁĄD: brak pliku CSV z eksportem kategorii IdoSell w {BASE_DIR}")
    return znalezione


def dobierz_heureke_auto(kandydaci, plik_zrodla):
    """Tryb --auto: plik Heureki dobrany po kodzie kraju w nazwie pliku źródłowego."""
    nazwa_zrodla = os.path.basename(plik_zrodla).lower()
    kody = set(re.findall(r"[a-z]{2}", nazwa_zrodla))
    for kod in ("sk", "cz"):
        if kod not in kody:
            continue
        pasujace = [p for p in kandydaci
                    if re.search(rf"\b{kod}\b", os.path.basename(p), re.IGNORECASE)]
        if pasujace:
            print(f"  --auto: wybrano {os.path.basename(pasujace[0])} "
                  f"(kod '{kod}' w nazwie pliku źródłowego)")
            return pasujace[0]
    return kandydaci[0]


def wykryj_jezyk(segmenty):
    """Język pliku Heureki rozpoznany po nazwach segmentów, nie po nazwie pliku."""
    obecne = set(segmenty)
    trafien_cz = len(obecne & set(SEGMENTY_CZ_SK))
    trafien_sk = len(obecne & set(SEGMENTY_CZ_SK.values()))
    return "SK" if trafien_sk > trafien_cz else "CZ"


def main():
    tylko_pewne = "--tylko-pewne" in sys.argv
    z_wezlami = "--z-wezlami" in sys.argv
    auto = "--auto" in sys.argv

    print("=" * 60)
    print(" Mapowanie kategorii -> kategorie Heureka")
    print("=" * 60)

    wszystkie_csv = znajdz(WZORZEC_CSV)
    kandydaci_h = [p for p in wszystkie_csv if wyglada_na_heureke(p)] or wszystkie_csv
    if not kandydaci_h:
        sys.exit(f"BŁĄD: w {BASE_DIR} nie ma żadnego pliku CSV")
    tryb = argument("--zrodlo", ("google", "idosell"))

    if auto:
        # bez pytań: tryb z dostępnych plików, a plik Heureki dobrany do źródła
        if not tryb:
            tryb = "google" if znajdz(WZORCE_GOOGLE) else "idosell"
        plik_zrodla = kandydaci_zrodla(tryb, wszystkie_csv)[0]
        plik_heureki = dobierz_heureke_auto(kandydaci_h, plik_zrodla)
    else:
        # 1. plik kategorii Heureki
        plik_heureki = sciezka(zapytaj_z_listy(
            "1/3. Który plik zawiera kategorie Heureki?",
            [os.path.basename(p) for p in kandydaci_h]))

        # 2. źródło kategorii
        if not tryb:
            etykiety = ["taksonomia Google Shopping (.xls)",
                        "eksport kategorii z IdoSell (.csv)"]
            wybor = zapytaj_z_listy("2/3. Do czego dopasować kategorie Heureki?", etykiety)
            tryb = "google" if wybor == etykiety[0] else "idosell"

        # 3. plik źródłowy
        plik_zrodla = sciezka(zapytaj_z_listy(
            f"3/3. Który plik zawiera kategorie źródłowe ({tryb})?",
            [os.path.basename(p) for p in kandydaci_zrodla(tryb, wszystkie_csv, plik_heureki)]))

    print()
    print(f"Kategorie Heureka: {os.path.basename(plik_heureki)}")
    print(f"Źródło kategorii:  {tryb} -- {os.path.basename(plik_zrodla)}")
    if tylko_pewne:
        print("Tryb --tylko-pewne: XSLT obejmie wyłącznie dopasowania fuzzy_high")
    if z_wezlami:
        print("Tryb --z-wezlami: XSLT obejmie także węzły pośrednie drzewa kategorii")

    print("Wczytywanie danych...")
    zrodlo = wczytaj_google(plik_zrodla) if tryb == "google" else wczytaj_idosell(plik_zrodla)
    heureka = wczytaj_heureke(plik_heureki)
    jezyk = wykryj_jezyk(heureka.segment.unique())
    print(f"  Źródło:  {len(zrodlo)} kategorii, {zrodlo.top.nunique()} gałęzi top-level")
    print(f"  Heureka: {len(heureka)} kategorii, {heureka.segment.nunique()} segmentów"
          f", język {jezyk}")

    plik_kotwicy = f"segment_map_{tryb}_{jezyk}.csv"
    out_raport = f"raport_{tryb}_{jezyk}.csv"
    out_xslt = f"{tryb}_to_heureka_{jezyk}.xslt"

    kotwica = wczytaj_kotwice(plik_kotwicy, tryb, zrodlo.top.unique(),
                              heureka.segment.unique(), jezyk)

    print("Dopasowywanie...")
    wynik = dopasuj(zrodlo, heureka, kotwica)
    wynik = odziedzicz_po_przodkach(wynik)
    wynik = dopasuj_nazwy_przodkow(wynik, heureka, kotwica)

    tabela = zapisz_raport(wynik, out_raport)
    liczba_xslt = zapisz_xslt(wynik, out_xslt, tryb, jezyk, tylko_pewne, z_wezlami)

    print()
    print(zestawienie(tabela, liczba_xslt, tryb, jezyk))
    print()
    print("Zapisano dwa pliki:")
    print(f"  raport: {out_raport}")
    print(f"  XSLT:   {out_xslt}")


if __name__ == "__main__":
    main()
