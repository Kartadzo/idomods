# -*- coding: utf-8 -*-
"""Test scalonego matfel_Ceneo.xml: kompilacja + przebieg na probce produktow."""
import io, os, sys
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
IAIEXT = "http://www.iai-shop.com/developers/iof/extensions.phtml"

def produkt(pid, typ, iai_id, cat_name, menu, cp, code, producer, params,
            nazwa=u"Testowa ksiazka", cena="39.90", stan="5"):
    p = u"".join(u'<parameter name="%s" hide="n"><value name="%s"/></parameter>' % (k, v)
                 for k, v in params)
    items = u"".join(u'<iaiext:item textid="%s"/>' % m for m in menu)
    iai = u'<iai_category id="%s"/>' % iai_id if iai_id else u""
    dostepnosc = u'available="available"' if typ == "virtual" else u''
    return u"""<product id="%s" type="%s" producer_code_standard="ISBN13">
      <producer name="%s"/>
      <category id="1" name="%s"/>
      %s
      <card url="https://sklep.pl/%s"/>
      <description><name>%s</name><short_desc>Krotki opis testowy produktu.</short_desc><long_desc/></description>
      <price gross="%s"/>
      <images><large><image url="https://sklep.pl/%s.jpg" iaiext:priority="1"/></large></images>
      <sizes><size code="%s" code_producer="%s" weight="500" %s>
        <stock id="1" available_stock_quantity="%s"/>
      </size></sizes>
      <parameters>%s</parameters>
      <iaiext:navigation><iaiext:site><iaiext:menu id="1">%s</iaiext:menu></iaiext:site></iaiext:navigation>
    </product>""" % (pid, typ, producer, cat_name, iai, pid, nazwa, cena, pid,
                     code, cp, dostepnosc, stan, p, items)

PRZYPADKI = [
    (u"1. ksiazka papierowa (iai 5771 kryminal)", produkt(
        "196293", "product_item", "5771", u"ASI/Kryminał", [u"Książki\\Kryminał"],
        "9788375822083", "KS-001", u"Złote Myśli",
        [(u"Rok wydania", "2008"), (u"Oprawa", u"broszurowa"), (u"Strony", "214"),
         (u"Elementy", "214"), (u"Autorzy", u"Piotr Surdel"), (u"Język", u"polski"),
         (u"Format", u"15x21 cm"), (u"Stan", u"Nowy"), (u"Kampania", u"Walentynki"),
         (u"Waga", u"0,35kg"), (u"Seria", u"Forex")])),
    (u"2. ebook wirtualny (_3, bez iai)", produkt(
        "196296", "virtual", None, u"*Kategoria tymczasowa", [u"Ebooki\\Poradniki"],
        "8374832975_3", "EB-003", u"Złote Myśli",
        [(u"Oprawa", u"Inna"), (u"Elementy", "49"), (u"Redakcja", u"Anna Nowak"),
         (u"Format pliku", u"pdf")],
        nazwa=u"Rada pracowników (Wersja elektroniczna (PDF))")),
    (u"3. wielotom (lista kodow, iai 5704)", produkt(
        "300001", "product_item", "5704", u"ASI/Dla dzieci", [u"Książki\\Dla dzieci"],
        "9788327107183_9788327107190", "KS-002", u"Znak",
        [(u"Oprawa", u"Twarda"), (u"Strony", "512"), (u"Autorzy", u"Jan Kowalski")])),
    (u"4. zabawka (iai 2085, poza Ksiegarnia)", produkt(
        "300004", "product_item", "2085", u"Zabawki/Plastyczne", [u"Zabawki\\Kreatywne"],
        "5907758708675", "ZA-004", u"Alexander",
        [(u"Materiał", u"drewno"), (u"Minimalny wiek", u"3+")],
        nazwa=u"Zestaw kreatywny")),
]

xml = u'<offer xmlns:iaiext="%s"><products>%s</products></offer>' % (
    IAIEXT, u"".join(p for _, p in PRZYPADKI))

try:
    tr = etree.XSLT(etree.parse(os.path.join(BASE, "matfel_Ceneo.xml")))
except (etree.XSLTParseError, etree.XMLSyntaxError) as e:
    print("BLAD KOMPILACJI:")
    print(e)
    sys.exit(1)

print("Kompilacja scalonego matfel_Ceneo.xml: OK\n")
out = tr(etree.fromstring(xml.encode("utf-8")))
for log in tr.error_log:
    print("  ostrzezenie:", log)

for (tytul, _), o in zip(PRZYPADKI, out.getroot()):
    print("=" * 72)
    print(tytul)
    print(u"   <cat> = %s" % (o.findtext("cat") or u"").strip())
    for a in o.iter("a"):
        print(u"   %-24s = %s" % (a.get("name"), (a.text or u"").strip()))
