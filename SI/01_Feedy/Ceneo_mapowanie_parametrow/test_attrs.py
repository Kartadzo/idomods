# -*- coding: utf-8 -*-
"""Test bloku <attrs> z szablon_atrybutu_v2.xml na przypadkach brzegowych."""
import io, sys, os
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "szablon_atrybutu_v2.xml")
frag = io.open(SRC, encoding="utf-8").read()

xsl = u"""<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
    exclude-result-prefixes="iaiext">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <offers>
      <xsl:for-each select="offer/products/product">
        <o id="{@id}">
          <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz&#261;&#263;&#281;&#322;&#324;&#243;&#347;&#380;&#378;'"/>
          <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ&#260;&#262;&#280;&#321;&#323;&#211;&#346;&#379;&#377;'"/>
%s
        </o>
      </xsl:for-each>
    </offers>
  </xsl:template>
</xsl:stylesheet>
""" % frag

def produkt(pid, code_producer, code, producer, params, nazwa=u"Testowa ksiazka"):
    p = u"".join(
        u'<parameter name="%s"><value name="%s"/></parameter>' % (k, v)
        for k, v in params
    )
    return u"""<product id="%s">
      <producer name="%s"/>
      <description><name>%s</name></description>
      <sizes><size code="%s" code_producer="%s"/></sizes>
      <parameters>%s</parameters>
    </product>""" % (pid, producer, nazwa, code, code_producer, p)

PRZYPADKI = [
    (u"1. ksiazka papierowa, Strony+Elementy razem", produkt(
        "196293", "9788375822083", "KS-001", u"Z\u0142ote My\u015bli",
        [(u"Rok wydania", "2008"), (u"Oprawa", u"broszurowa"), (u"Strony", "214"),
         (u"Elementy", "214"), (u"Autorzy", u"Piotr Surdel"), (u"J\u0119zyk", u"polski"),
         (u"Format", u"15x21 cm"), (u"Stan", u"Nowy"), (u"Kampania", u"Walentynki"),
         (u"Data premiery", "2008-05-06"), (u"Waga", u"0,35kg"), (u"Seria", u"Forex")])),
    (u"2. wielotom - lista kodow w code_producer", produkt(
        "300001", "9788327107183_9788327107190", "KS-002", u"Znak",
        [(u"Oprawa", u"Twarda"), (u"Strony", "512"), (u"Autorzy", u"Jan Kowalski")])),
    (u"3. ebook - sufiks wersji _3, ISBN-10", produkt(
        "196296", "8374832975_3", "EB-003", u"Z\u0142ote My\u015bli",
        [(u"Oprawa", u"Inna"), (u"Elementy", "49"), (u"Autorzy", u"Przemys\u0142aw Ciszek"),
         (u"Format pliku", u"pdf")],
        nazwa=u"Rada pracownik\u00f3w w firmie (Wersja elektroniczna (PDF)) - P. Ciszek")),
    (u"4. Redakcja bez Autorzy + Miekka bez ogonka", produkt(
        "300002", "9788383671338", "KS-004", u"PWN",
        [(u"Redakcja", u"Anna Nowak"), (u"Oprawa", u"Miekka"), (u"Strony", "120"),
         (u"J\u0119zyk nauczany", u"angielski")])),
    (u"5. uszkodzony kod BAD_EAN", produkt(
        "300003", "9788378890966_BAD_EAN", "KS-005", u"Helion",
        [(u"Oprawa", u"teczka"), (u"Rok wydania", u"brak")])),
    (u"6. audiobook - sufiks _1, oprawa spoza slownika", produkt(
        "300004", "9788380087590_1", "AB-006", u"Storybox",
        [(u"Oprawa", u"pude\u0142ko"), (u"J\u0119zyk", u"polski, angielski"),
         (u"No\u015bnik", u"CD")])),
    (u"7. brak code_producer, Elementy bez Strony", produkt(
        "300005", "", "KS-007", u"",
        [(u"Elementy", "97"), (u"Oprawa", u"zintegrowana"), (u"Rok wydania", "2010")])),
]

xml = u'<offer xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"><products>%s</products></offer>' \
      % u"".join(p for _, p in PRZYPADKI)

try:
    tr = etree.XSLT(etree.fromstring(xsl.encode("utf-8")))
except etree.XSLTParseError as e:
    print("BLAD KOMPILACJI XSLT:")
    print(e)
    sys.exit(1)

out = tr(etree.fromstring(xml.encode("utf-8")))
print("Kompilacja XSLT 1.0: OK\n")
for log in tr.error_log:
    print("  ostrzezenie:", log)

wyniki = out.getroot()
for (tytul, _), o in zip(PRZYPADKI, wyniki):
    print("=" * 70)
    print(tytul, " (id=%s)" % o.get("id"))
    for a in o.iter("a"):
        print(u"   %-24s = %s" % (a.get("name"), (a.text or u"").strip()))
