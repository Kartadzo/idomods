# -*- coding: utf-8 -*-
"""Mapowanie kategorii sklepu (IAI) -> kategorie Ceneo.

Wejscie (z katalogu skryptu):
  export_kategorii.csv - @id, /iai_category@id, /iai_category@path, menu, nazwa
  kategorie.xml        - drzewo kategorii Ceneo

Wyjscie:
  raport_kategorii.md      - pokrycie, propozycja mapowania, pozycje niezmapowane
  mapowanie_kategorii.xslt - gotowy blok XSLT 1.0 (zmienna $ceneo_cat)
"""
import csv, collections, io, os, re
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
csv.field_size_limit(10 ** 9)

# ---------- 1. drzewo Ceneo ----------
sciezka = {}      # Id -> pelna sciezka
po_nazwie = collections.defaultdict(list)

def walk(node, path):
    for c in node:
        if c.tag != "Category":
            continue
        nm, cid = c.findtext("Name"), c.findtext("Id")
        p = path + [nm]
        sciezka[cid] = " > ".join(p)
        po_nazwie[nm.lower()].append(cid)
        sub = c.find("Subcategories")
        if sub is not None:
            walk(sub, p)

walk(ET.parse(os.path.join(BASE, "kategorie.xml")).getroot(), [])

# ---------- 2. reguly mapowania ----------
# Klucz: fragment sciezki IAI (dopasowanie od najbardziej szczegolowego).
# Wartosc: Id kategorii Ceneo.
# Zrodlo decyzji: struktura galezi "Ksiegarnia" z kategorie.xml (61 lisci).
REGULY = [
    # --- nauka jezykow: IAI ma jezyk w ostatnim segmencie, Ceneo tak samo ---
    ("Książki do nauki języka obcego > Angielski",           "430"),
    ("Książki do nauki języka obcego > Francuski",           "432"),
    ("Książki do nauki języka obcego > Hiszpański",          "433"),
    ("Książki do nauki języka obcego > Niemiecki",           "434"),
    ("Książki do nauki języka obcego > Rosyjski",            "435"),
    ("Książki do nauki języka obcego > Włoski",              "436"),
    ("Książki do nauki języka obcego",                       "431"),

    # --- beletrystyka ---
    ("Literatura piękna, popularna i faktu > Kryminały",             "414"),
    ("Literatura piękna, popularna i faktu > Horrory",               "414"),
    ("Literatura piękna, popularna i faktu > Thrillery, sensacyjne", "414"),
    ("Literatura piękna, popularna i faktu > Fantasy",               "407"),
    ("Literatura piękna, popularna i faktu > Science fiction",       "407"),
    ("Literatura piękna, popularna i faktu > Romanse",               "420"),
    ("Literatura piękna, popularna i faktu > Literatura erotyczna",  "420"),
    ("Literatura piękna, popularna i faktu > Poezja",                "418"),
    ("Literatura piękna, popularna i faktu > Dramaty",               "418"),
    ("Literatura piękna, popularna i faktu > Biografie, wspomnienia","2493"),
    ("Literatura piękna, popularna i faktu > Reportaż",              "409"),
    ("Literatura piękna, popularna i faktu",                         "425"),

    # --- dzieci i mlodziez: cala galaz IAI -> jeden lisc Ceneo ---
    ("Książki dla dzieci i młodzieży",                       "403"),

    # --- nauka i popularnonauka ---
    ("Książki naukowe i popularnonaukowe > Historia, archeologia",          "409"),
    ("Książki naukowe i popularnonaukowe > Militaria",                      "409"),
    ("Książki naukowe i popularnonaukowe > Religioznawstwo",                "445"),
    ("Książki naukowe i popularnonaukowe > Informatyka",                    "398"),
    ("Książki naukowe i popularnonaukowe > Biznes, nauki ekonomiczne",      "400"),
    ("Książki naukowe i popularnonaukowe > Prawo, administracja",           "401"),
    ("Książki naukowe i popularnonaukowe > Politologia",                    "447"),
    ("Książki naukowe i popularnonaukowe > Medycyna",                       "422"),
    ("Książki naukowe i popularnonaukowe > Technika, nauki techniczne",     "413"),
    ("Książki naukowe i popularnonaukowe > Architektura, budownictwo",      "413"),
    ("Książki naukowe i popularnonaukowe > Sztuka, kultura i etnologia",    "421"),
    ("Książki naukowe i popularnonaukowe > Rolnictwo",                      "2745"),
    ("Książki naukowe i popularnonaukowe > Biologia",                       "2744"),
    ("Książki naukowe i popularnonaukowe > Chemia",                         "2744"),
    ("Książki naukowe i popularnonaukowe > Fizyka",                         "2744"),
    ("Książki naukowe i popularnonaukowe > Matematyka",                     "2744"),
    ("Książki naukowe i popularnonaukowe > Geografia",                      "2744"),
    ("Książki naukowe i popularnonaukowe > Encyklopedie",                   "405"),
    ("Książki naukowe i popularnonaukowe > Psychologia",                    "408"),
    ("Książki naukowe i popularnonaukowe > Pedagogika",                     "408"),
    ("Książki naukowe i popularnonaukowe > Filologie",                      "408"),
    ("Książki naukowe i popularnonaukowe > Filozofia",                      "408"),
    ("Książki naukowe i popularnonaukowe > Literaturoznawstwo",             "408"),
    ("Książki naukowe i popularnonaukowe > Pozostałe",                      "2746"),
    ("Książki naukowe i popularnonaukowe",                                  "2743"),

    # --- poradniki i albumy ---
    ("Poradniki i albumy > Ezoteryka",                       "406"),
    ("Poradniki i albumy > Kuchnia, potrawy",                "411"),
    ("Poradniki i albumy > Motywacja, rozwój osobisty",      "419"),
    ("Poradniki i albumy > Hobby, kolekcjonerstwo",          "417"),
    ("Poradniki i albumy > Muzyka, taniec, śpiew",           "417"),
    ("Poradniki i albumy > Sport, forma fizyczna",           "2592"),
    ("Poradniki i albumy > Motoryzacja, transport",          "453"),
    ("Poradniki i albumy > Zwierzęta domowe i hodowlane",    "424"),
    ("Poradniki i albumy > Sztuka i architektura",           "426"),
    ("Poradniki i albumy > Przyroda, krajobrazy",            "426"),
    ("Poradniki i albumy",                                   "2701"),

    # --- reszta galezi ksiazkowych ---
    ("Mapy, przewodniki, książki podróżnicze",               "399"),
    ("Podręczniki do szkół podst. i średnich",               "412"),
    ("Książki obcojęzyczne",                                 "724"),
    ("Media > Komiksy",                                      "410"),
    ("Media > Gazety i czasopisma",                          "2704"),
    ("Media > Książki",                                      "454"),
]

# Galezie spoza Ksiegarni - dopasowanie po nazwie ostatniego segmentu.
# Produkty tam trafiajace nie sa ksiazkami (ok. 1,5 tys. sztuk).
POZA_KSIEGARNIA = ("Gry i zabawki", "Artykuły biurowe", "Artykuły religijne",
                   "Torby, walizki", "Dzieci i niemowlęta", "Biznes i przemysł",
                   "Dom i ogród", "Sztuka i rozrywka", "Uroda", "Zdrowie",
                   "Sport i turystyka", "Elektronika")

def mapuj(path):
    """Zwraca (id_ceneo, zrodlo_dopasowania) albo (None, powod)."""
    for frag, cid in REGULY:
        if frag in path:
            return cid, u"reguła: %s" % frag
    # poza Ksiegarnia: sprobuj dopasowac ostatni segment po nazwie
    if path.startswith(POZA_KSIEGARNIA):
        ost = path.split(" > ")[-1].lower()
        kandydaci = po_nazwie.get(ost, [])
        if len(kandydaci) == 1:
            return kandydaci[0], u"nazwa liścia (poza Księgarnią)"
        if len(kandydaci) > 1:
            return kandydaci[0], u"nazwa liścia, %d kandydatów" % len(kandydaci)
        return None, u"poza Księgarnią, brak dopasowania nazwy"
    return None, u"brak reguły"

# --- mapowanie menu (fallback dla produktow bez iai_category) ---
# Klucz: prefiks sciezki menu (porownanie przez starts-with w XSLT).
MENU = [
    (u"Książki obcojęzyczne",                    "724"),
    (u"Książki\\Fantastyka",                     "407"),
    (u"Książki\\Science fiction",                "407"),
    (u"Książki\\Horror",                         "414"),
    (u"Książki\\Kryminał",                       "414"),
    (u"Książki\\Thriller",                       "414"),
    (u"Książki\\Sensacja",                       "414"),
    (u"Książki\\Romans",                         "420"),
    (u"Książki\\Erotyka",                        "420"),
    (u"Książki\\Poezja",                         "418"),
    (u"Książki\\Biografie",                      "2493"),
    (u"Książki\\Literatura faktu",               "409"),
    (u"Książki\\Historia",                       "409"),
    (u"Książki\\Religijne",                      "445"),
    (u"Książki\\Dla dzieci",                     "403"),
    (u"Książki\\Dla młodzieży",                  "403"),
    (u"Książki\\Komiksy",                        "410"),
    (u"Książki\\Popularnonaukowe\\Informatyka",  "398"),
    (u"Książki\\Popularnonaukowe\\Prawo",        "401"),
    (u"Książki\\Popularnonaukowe\\Medycyna",     "422"),
    (u"Książki\\Popularnonaukowe\\Psychologia",  "408"),
    (u"Książki\\Popularnonaukowe\\Filozofia",    "408"),
    (u"Książki\\Popularnonaukowe\\Językoznawstwo", "408"),
    (u"Książki\\Popularnonaukowe\\Nauka i technika", "413"),
    (u"Książki\\Popularnonaukowe",               "2743"),
    (u"Książki\\Podróże i turystyka",            "399"),
    (u"Książki\\Kultura i sztuka",               "421"),
    (u"Książki\\Zdrowie i uroda",                "2593"),
    (u"Książki\\Kulinaria",                      "411"),
    (u"Książki\\Hobby",                          "417"),
    (u"Książki\\Poradniki",                      "2701"),
    (u"Książki\\Literatura piękna",              "425"),
    (u"Podręczniki\\Szkolne",                    "412"),
    (u"Podręczniki\\Lektury",                    "412"),
    (u"Podręczniki",                             "412"),
    (u"Nauka języków obcych\\Angielski",         "430"),
    (u"Nauka języków obcych\\Francuski",         "432"),
    (u"Nauka języków obcych\\Hiszpański",        "433"),
    (u"Nauka języków obcych\\Niemiecki",         "434"),
    (u"Nauka języków obcych\\Rosyjski",          "435"),
    (u"Nauka języków obcych\\Włoski",            "436"),
    (u"Nauka języków obcych",                    "431"),
    (u"Ebooki",                                  "3451"),
    (u"Audiobooki",                              "3453"),
    (u"Książki",                                 "454"),
]

# XPath do pozycji menu głównego (id=1) — używany w wygenerowanym arkuszu
MENU_XPATH = u"iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item"

# ---------- 3. dane sklepu ----------
iai = collections.Counter()          # (id, path) -> liczba produktow
menu_bez_iai = collections.Counter()
przyklady = {}

with open(os.path.join(BASE, "export_kategorii.csv"), encoding="utf-8", newline="") as f:
    r = csv.reader(f)
    next(r)
    produkty = 0
    for row in r:
        produkty += 1
        iid, path, menu, nazwa = row[3].strip(), row[4].strip(), row[7].strip(), row[8]
        if path:
            iai[(iid, path)] += 1
            przyklady.setdefault((iid, path), nazwa[:60])
        else:
            menu_bez_iai[menu] += 1

# ---------- 4. wynik ----------
wynik = []
for (iid, path), n in iai.most_common():
    cid, how = mapuj(path)
    wynik.append((iid, path, n, cid, how))

zmapowane = [w for w in wynik if w[3]]
niezmapowane = [w for w in wynik if not w[3]]
prod_zmap = sum(w[2] for w in zmapowane)
prod_niezmap = sum(w[2] for w in niezmapowane)

def mapuj_menu(m):
    """Produkt bywa przypisany do kilku pozycji menu (w CSV rozdzielonych \\n) —
    sprawdzamy każdą, bo pierwsza bywa bezużyteczna ('Pozostałe')."""
    linie = [x.strip() for x in m.split("\n") if x.strip()]
    for pref, cid in MENU:
        for linia in linie:
            if linia.startswith(pref):
                return cid
    return None

menu_zmap = sum(n for m, n in menu_bez_iai.items() if mapuj_menu(m))
menu_niezmap = sum(n for m, n in menu_bez_iai.items() if not mapuj_menu(m))

# ---------- 5. raport ----------
with io.open(os.path.join(BASE, "raport_kategorii.md"), "w", encoding="utf-8") as o:
    w = o.write
    w(u"# Mapowanie kategorii sklepu → kategorie Ceneo\n\n")
    w(u"Produktów: **%d** · ścieżek IAI: **%d** · kategorii Ceneo w drzewie: **%d** "
      u"(w tym %d liści w gałęzi Księgarnia)\n\n"
      % (produkty, len(iai), len(sciezka),
         sum(1 for k, v in sciezka.items() if v.startswith(u"Księgarnia"))))
    w(u"## Pokrycie\n\n")
    w(u"| Źródło | Produktów | Zmapowanych | Bez mapowania |\n|---|---:|---:|---:|\n")
    w(u"| `iai_category` | %d | %d (%.1f%%) | %d |\n"
      % (prod_zmap + prod_niezmap, prod_zmap, 100.0 * prod_zmap / (prod_zmap + prod_niezmap), prod_niezmap))
    w(u"| menu (bez `iai_category`) | %d | %d (%.1f%%) | %d |\n"
      % (menu_zmap + menu_niezmap, menu_zmap,
         100.0 * menu_zmap / max(1, menu_zmap + menu_niezmap), menu_niezmap))
    razem = prod_zmap + menu_zmap
    w(u"| **razem** | **%d** | **%d (%.1f%%)** | **%d** |\n\n"
      % (produkty, razem, 100.0 * razem / produkty, produkty - razem))

    w(u"## Mapowanie ścieżek IAI\n\n")
    w(u"| Produktów | Ścieżka IAI | ID Ceneo | Kategoria Ceneo | Podstawa |\n|---:|---|---|---|---|\n")
    for iid, path, n, cid, how in wynik:
        w(u"| %d | %s | %s | %s | %s |\n"
          % (n, path, cid or u"—", sciezka.get(cid, u"—"), how))

    w(u"\n## Ścieżki bez mapowania (%d ścieżek, %d produktów)\n\n" % (len(niezmapowane), prod_niezmap))
    for iid, path, n, _, how in niezmapowane:
        w(u"- **%d** szt. — `%s` (%s) — _%s_\n" % (n, path, iid, how))

    w(u"\n## Fallback po menu — produkty bez `iai_category` (%d szt.)\n\n" % sum(menu_bez_iai.values()))
    w(u"| Produktów | Menu | ID Ceneo | Kategoria Ceneo |\n|---:|---|---|---|\n")
    for m, n in menu_bez_iai.most_common(60):
        cid = mapuj_menu(m)
        w(u"| %d | %s | %s | %s |\n" % (n, m or u"_(puste)_", cid or u"—", sciezka.get(cid, u"—")))

# ---------- 6. blok XSLT ----------
with io.open(os.path.join(BASE, "mapowanie_kategorii.xslt"), "w", encoding="utf-8") as o:
    w = o.write
    w(u"""<!--
  ============================================================================
  Mapowanie kategorii sklepu -> kategoria Ceneo.  XSLT 1.0, kontekst <product>.
  Wygenerowane przez mapowanie_kategorii.py — nie edytować ręcznie,
  zmiany nanosić w tablicach REGULY / MENU w skrypcie i przegenerować.

  Zmienna $ceneo_cat zawiera pełną ścieżkę kategorii Ceneo albo pusty łańcuch.
  Zmienna $ceneo_cat_id zawiera identyfikator kategorii Ceneo.

  Użycie w <cat> (zachowuje dotychczasowe zachowanie tam, gdzie brak mapowania):
      <cat>
        <xsl:choose>
          <xsl:when test="$ceneo_cat != ''"><xsl:value-of select="$ceneo_cat"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="translate(category/@name, '&gt;', '/')"/></xsl:otherwise>
        </xsl:choose>
      </cat>

  UWAGA: <cat> w formacie Ceneo to kategoria SKLEPU, nie pole na identyfikator
  kategorii Ceneo — podanie tu ścieżki ze słownika Ceneo tylko ułatwia serwisowi
  automatyczne dopasowanie. Właściwym odbiorcą $ceneo_cat_id jest warunkowanie
  atrybutów w bloku <attrs>, które w Ceneo są definiowane per kategoria.

  WERSJE ELEKTRONICZNE: mapowanie opiera się na kategorii sklepu, więc ebook
  dostanie kategorię książki papierowej. Jeśli w bloku <attrs> wyliczana jest
  zmienna $cp_wersja (sufiks code_producer), warto ją nałożyć przed tym blokiem:
      <xsl:variable name="ceneo_cat_id">
        <xsl:choose>
          <xsl:when test="$cp_wersja = '3'">3451</xsl:when>
          <xsl:when test="$cp_wersja = '1' or $cp_wersja = '2'">3453</xsl:when>
          ... dalej reguły poniżej ...
  gdzie 3451 = Księgarnia > E-booki > Pozostałe E-booki, 3453 = Księgarnia > Audiobooki.
  Dotyczy 202 produktów; przy większym wolumenie warto rozbić E-booki na
  podkategorie tematyczne (3439-3451) zamiast wrzucać wszystko do 3451.
  ============================================================================
-->
<xsl:variable name="iai_id" select="normalize-space(iai_category/@id)"/>
<xsl:variable name="menu_path" select="normalize-space(iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item/@textid)"/>

<xsl:variable name="ceneo_cat_id">
  <xsl:choose>
""")
    for iid, path, n, cid, how in wynik:
        if cid:
            w(u'    <xsl:when test="$iai_id = \'%s\'">%s</xsl:when>'
              u'<!-- %d szt. %s -->\n' % (iid, cid, n, path))
    w(u"    <!-- fallback: produkty bez iai_category (%d szt.) — po ścieżce menu.\n"
      u"         Predykat na <item>, bo produkt bywa w kilku pozycjach menu naraz\n"
      u"         i pierwsza z nich bywa bezużyteczna ('Pozostałe'). -->\n"
      % sum(menu_bez_iai.values()))
    for pref, cid in MENU:
        w(u'    <xsl:when test="%s[starts-with(@textid, \'%s\')]">%s</xsl:when>\n'
          % (MENU_XPATH, pref, cid))
    w(u"""  </xsl:choose>
</xsl:variable>

<xsl:variable name="ceneo_cat">
  <xsl:choose>
""")
    uzyte = sorted({cid for _, _, _, cid, _ in wynik if cid} | {c for _, c in MENU})
    for cid in uzyte:
        # separator '/' — taki sam, jakiego <cat> używa dla kategorii sklepu
        w(u'    <xsl:when test="$ceneo_cat_id = \'%s\'">%s</xsl:when>\n'
          % (cid, sciezka.get(cid, u"").replace(u" > ", u"/")))
    w(u"""  </xsl:choose>
</xsl:variable>
""")

print("Produktow: %d" % produkty)
print("iai_category: %d/%d zmapowanych (%.1f%%)" % (prod_zmap, prod_zmap + prod_niezmap,
      100.0 * prod_zmap / (prod_zmap + prod_niezmap)))
print("menu fallback: %d/%d (%.1f%%)" % (menu_zmap, menu_zmap + menu_niezmap,
      100.0 * menu_zmap / max(1, menu_zmap + menu_niezmap)))
print("RAZEM: %d/%d (%.1f%%)" % (razem, produkty, 100.0 * razem / produkty))
print("niezmapowanych sciezek IAI: %d" % len(niezmapowane))
