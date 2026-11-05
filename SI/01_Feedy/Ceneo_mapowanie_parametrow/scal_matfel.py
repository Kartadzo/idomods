# -*- coding: utf-8 -*-
"""Scalenie bloku atrybutow i mapowania kategorii w matfel_Ceneo.xml.

Wejscie (z katalogu skryptu):
  matfel_Ceneo.xml          - arkusz produkcyjny (zachowane konce linii CRLF)
  szablon_atrybutu_v2.xml   - blok <attrs> (zrodlo tresci nazwanego szablonu)
  mapowanie_kategorii.xslt  - blok mapowania kategorii (wygenerowany)

Wyjscie:
  matfel_Ceneo.xml          - nadpisany (kopia w matfel_Ceneo.xml.bak)

Scalenie polega na:
  1. wyniesieniu $lowercase/$uppercase i slownikow wartosci na poziom globalny,
  2. dodaniu nazwanych szablonow ceneoAttrs i ceneoCat na koncu arkusza,
  3. podmianie obu blokow <attrs> i obu <cat> na wywolania tych szablonow.
Dzieki temu logika istnieje w jednym egzemplarzu, a nie w duplikacie dla
towarow wirtualnych i fizycznych.
"""
import io, os, re, shutil, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CEL = os.path.join(BASE, "matfel_Ceneo.xml")

def czytaj(p):
    with io.open(p, encoding="utf-8", newline="") as f:
        return f.read()

src = czytaj(CEL)
attrs_frag = czytaj(os.path.join(BASE, "szablon_atrybutu_v2.xml"))
kat_frag = czytaj(os.path.join(BASE, "mapowanie_kategorii.xslt"))

EOL = "\r\n" if "\r\n" in src else "\n"

# ---------------------------------------------------------------- 1. slowniki
# Wyjmujemy z bloku <attrs> deklaracje slownikow — w nazwanym szablonie musza
# byc globalne, bo $lowercase/$uppercase byly dotad zmiennymi lokalnymi
# wewnatrz for-each i nazwany szablon ich nie widzi.
slowniki = re.findall(r'<xsl:variable name="(?:okladka_miekka|okladka_twarda|jezyki|format_pliku)">.*?</xsl:variable>',
                      attrs_frag)
if len(slowniki) != 4:
    sys.exit("Nie znaleziono wszystkich 4 slownikow w szablon_atrybutu_v2.xml (znaleziono %d)" % len(slowniki))

# tresc <attrs> bez deklaracji slownikow i bez naglowkowego komentarza
attrs_body = attrs_frag
for s in slowniki:
    attrs_body = attrs_body.replace(s, "")
attrs_body = re.sub(r"^\s*<!--.*?-->\s*", "", attrs_body, count=1, flags=re.S)
attrs_body = attrs_body.strip()
if not attrs_body.startswith("<attrs>") or not attrs_body.endswith("</attrs>"):
    sys.exit("Nieoczekiwana struktura szablon_atrybutu_v2.xml")
attrs_body = attrs_body[len("<attrs>"):-len("</attrs>")]

# ---------------------------------------------------------------- 2. globalne
GLOBALNE = EOL.join([
    '',
    '    <!-- ==================================================================',
    '         Zmienne globalne wspolne dla obu galezi (towary wirtualne i fizyczne).',
    '         $lowercase/$uppercase byly dotad deklarowane lokalnie w for-each;',
    '         nazwane szablony na koncu arkusza wymagaja zasiegu globalnego.',
    '         ================================================================== -->',
    '    <xsl:variable name="lowercase" select="\'abcdefghijklmnopqrstuvwxyząćęłńóśżź\'" />',
    '    <xsl:variable name="uppercase" select="\'ABCDEFGHIJKLMNOPQRSTUVWXYZĄĆĘŁŃÓŚŻŹ\'" />',
] + ['    ' + s.strip() for s in slowniki] + [''])

# Najpierw usuwamy lokalne deklaracje $lowercase/$uppercase, dopiero potem
# wstawiamy globalne — inaczej ten sam wzorzec usunalby swiezo dodane globalne.
przed = src
src = re.sub(r'[ \t]*<xsl:variable name="(?:lowercase|uppercase)" select="\'[^\']+\'"[ ]*/>[ \t]*\r?\n',
             '', src)
usuniete = (przed.count('name="lowercase"') + przed.count('name="uppercase"')) - \
           (src.count('name="lowercase"') + src.count('name="uppercase"'))
if usuniete != 2:
    sys.exit("Oczekiwano usuniecia 2 lokalnych deklaracji lowercase/uppercase, usunieto %d" % usuniete)

# uwaga: arkusz ma konce linii CRLF, wiec kotwica $ nie moze byc uzyta wprost
m = re.search(r'<xsl:output\b[^>]*(?:></xsl:output>|/>)', src)
if not m:
    sys.exit("Nie znaleziono <xsl:output> w arkuszu")
src = src[:m.end()] + GLOBALNE + src[m.end():]

# ---------------------------------------------------------------- 3. <attrs>
def podmien_bloki(tekst, otw, zam, nowy_szablon):
    """Podmienia kazdy blok <otw>...</zam> na wywolanie nazwanego szablonu."""
    wynik, ile = [], 0
    i = 0
    while True:
        a = tekst.find(otw, i)
        if a < 0:
            wynik.append(tekst[i:])
            break
        b = tekst.find(zam, a)
        if b < 0:
            sys.exit("Blok %s bez domkniecia %s" % (otw, zam))
        b += len(zam)
        # wciecie linii, w ktorej otwiera sie blok
        ls = tekst.rfind("\n", 0, a) + 1
        wciecie = tekst[ls:a]
        wynik.append(tekst[i:a])
        wynik.append(nowy_szablon(wciecie))
        ile += 1
        i = b
    return "".join(wynik), ile

def nowe_attrs(wciecie):
    return (u'<attrs>' + EOL +
            wciecie + u'    <xsl:call-template name="ceneoAttrs"/>' + EOL +
            wciecie + u'</attrs>')

def nowe_cat(wciecie):
    return (u'<cat>' + EOL +
            wciecie + u'    <xsl:call-template name="ceneoCat"/>' + EOL +
            wciecie + u'</cat>')

src, n_attrs = podmien_bloki(src, "<attrs>", "</attrs>", nowe_attrs)
src, n_cat = podmien_bloki(src, "<cat>", "</cat>", nowe_cat)
if n_attrs != 2 or n_cat != 2:
    sys.exit("Oczekiwano 2 blokow <attrs> i 2 <cat>; znaleziono %d i %d" % (n_attrs, n_cat))

# ---------------------------------------------------------------- 4. szablony
def wciecie_bloku(tekst, poziom=1):
    return EOL.join(("    " * poziom + l) if l.strip() else l
                    for l in tekst.replace("\r\n", "\n").split("\n"))

SZABLONY = EOL.join([
    '',
    '    <!-- ==================================================================',
    '         Nazwane szablony feedu Ceneo — ksiegarnia.',
    '         Wygenerowane przez scal_matfel.py ze zrodel:',
    '           szablon_atrybutu_v2.xml   (blok <attrs>)',
    '           mapowanie_kategorii.xslt  (mapowanie kategorii, generator:',
    '                                      mapowanie_kategorii.py)',
    '         Zmiany nanosic w tych plikach i przegenerowac, nie edytowac tutaj.',
    '         ================================================================== -->',
    '    <xsl:template name="ceneoAttrs">',
    wciecie_bloku(attrs_body.strip(), 1),
    '    </xsl:template>',
    '',
    '    <xsl:template name="ceneoCat">',
    wciecie_bloku(kat_frag.strip(), 1),
    '        <xsl:choose>',
    '            <xsl:when test="$ceneo_cat != \'\'">',
    '                <xsl:value-of select="$ceneo_cat"/>',
    '            </xsl:when>',
    '            <xsl:otherwise>',
    '                <!-- brak mapowania: dotychczasowe zachowanie -->',
    '                <xsl:choose>',
    '                    <xsl:when test="category/@name = \'*Kategoria tymczasowa\'">',
    '                        <xsl:value-of select="translate(iaiext:navigation/iaiext:site/iaiext:menu[@id=1]/iaiext:item/@textid, \'\\\', \'/\')"/>',
    '                    </xsl:when>',
    '                    <xsl:otherwise>',
    '                        <xsl:value-of select="translate(category/@name, \'&gt;\', \'/\')"/>',
    '                    </xsl:otherwise>',
    '                </xsl:choose>',
    '            </xsl:otherwise>',
    '        </xsl:choose>',
    '    </xsl:template>',
    '',
])

k = src.rfind("</xsl:stylesheet>")
if k < 0:
    sys.exit("Nie znaleziono </xsl:stylesheet>")
src = src[:k] + SZABLONY + src[k:]

with io.open(CEL, "w", encoding="utf-8", newline="") as f:
    f.write(src)

print("Scalono: %d blokow <attrs>, %d blokow <cat>, %d slownikow wyniesionych globalnie"
      % (n_attrs, n_cat, len(slowniki)))
print("Kopia zapasowa: matfel_Ceneo.xml.bak")
