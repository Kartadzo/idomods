# -*- coding: utf-8 -*-
"""Test bloku mapowania kategorii (mapowanie_kategorii.xslt) na procesorze XSLT 1.0."""
import io, os, sys
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
frag = io.open(os.path.join(BASE, "mapowanie_kategorii.xslt"), encoding="utf-8").read()

IAIEXT = "http://www.iai-shop.com/developers/iof/extensions.phtml"

xsl = u"""<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:iaiext="%s" exclude-result-prefixes="iaiext">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <offers>
      <xsl:for-each select="offer/products/product">
        <o id="{@id}">
%s
          <cat>
            <xsl:choose>
              <xsl:when test="$ceneo_cat != ''"><xsl:value-of select="$ceneo_cat"/></xsl:when>
              <xsl:otherwise><xsl:value-of select="translate(category/@name, '&gt;', '/')"/></xsl:otherwise>
            </xsl:choose>
          </cat>
          <id_ceneo><xsl:value-of select="$ceneo_cat_id"/></id_ceneo>
        </o>
      </xsl:for-each>
    </offers>
  </xsl:template>
</xsl:stylesheet>
""" % (IAIEXT, frag)

def produkt(pid, iai_id, cat_name, menu_items):
    items = u"".join(u'<iaiext:item textid="%s"/>' % m for m in menu_items)
    iai = u'<iai_category id="%s"/>' % iai_id if iai_id else u""
    return u"""<product id="%s">
      <category name="%s"/>
      %s
      <iaiext:navigation><iaiext:site><iaiext:menu id="1">%s</iaiext:menu></iaiext:site></iaiext:navigation>
    </product>""" % (pid, cat_name, iai, items)

PRZYPADKI = [
    (u"1. komiks (iai 5663)",                 produkt("1", "5663", u"ASI/Komiksy", [u"Książki\\Komiksy"])),
    (u"2. kryminal (iai 5771)",               produkt("2", "5771", u"ASI/Kryminał", [u"Książki\\Kryminał"])),
    (u"3. angielski (iai 5718)",              produkt("3", "5718", u"ASI/Języki", [])),
    (u"4. bez iai, menu Fantastyka",          produkt("4", None, u"*Kategoria tymczasowa", [u"Książki\\Fantastyka"])),
    (u"5. bez iai, menu wielopozycyjne",      produkt("5", None, u"*Kategoria tymczasowa",
                                                     [u"Pozostałe", u"Książki obcojęzyczne\\Ukraiński"])),
    (u"6. bez iai, menu 'Pozostale'",         produkt("6", None, u"Książki/Nowości", [u"Pozostałe"])),
    (u"7. zabawka (iai 2085, poza Ksieg.)",   produkt("7", "2085", u"Zabawki/Plastyczne", [u"Zabawki\\Kreatywne"])),
    (u"8. podrecznik liceum (iai 5805)",      produkt("8", "5805", u"Podręczniki/Liceum", [])),
]

xml = u'<offer xmlns:iaiext="%s"><products>%s</products></offer>' % (
    IAIEXT, u"".join(p for _, p in PRZYPADKI))

try:
    tr = etree.XSLT(etree.fromstring(xsl.encode("utf-8")))
except etree.XSLTParseError as e:
    print("BLAD KOMPILACJI XSLT:")
    print(e)
    sys.exit(1)

out = tr(etree.fromstring(xml.encode("utf-8")))
print("Kompilacja XSLT 1.0: OK\n")
for (tytul, _), o in zip(PRZYPADKI, out.getroot()):
    cat = o.findtext("cat").strip()
    cid = (o.findtext("id_ceneo") or u"").strip()
    print(u"%-38s id=%-5s  %s" % (tytul, cid or u"-", cat))
