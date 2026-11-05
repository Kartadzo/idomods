import hashlib
import unittest
import xml.etree.ElementTree as ET

from testy import fixtures
from wt import icf


class TestWczytaj(unittest.TestCase):
    def test_pola_kanalow(self):
        dane = icf.wczytaj(fixtures.icf_xml(jezyk="eng"))
        self.assertEqual(dane["template"], "order_confirmation")
        self.assertEqual(dane["jezyk"], "eng")
        self.assertEqual(dane["kanaly"]["mail"]["active"], "y")
        self.assertEqual(dane["kanaly"]["mail"]["title"], "[iai:shop_name] – Zamówienie nr [iai:order_sn]")
        self.assertEqual(dane["kanaly"]["sms"]["active"], "n")
        self.assertEqual(dane["kanaly"]["mail"]["css"], "")   # " " w panelu = puste
        self.assertEqual(dane["zalaczniki"], 1)

    def test_brak_kanalu(self):
        dane = icf.wczytaj(fixtures.icf_xml(z_sms=False))
        self.assertNotIn("sms", dane["kanaly"])
        self.assertIsNone(icf.wartosc(dane, "sms", "text_main_0"))

    def test_nie_icf(self):
        with self.assertRaises(icf.BladIcf):
            icf.wczytaj("<html><title>Logowanie użytkownika</title></html>")
        with self.assertRaises(icf.BladIcf):
            icf.wczytaj("to nie jest xml")


class TestPodmien(unittest.TestCase):
    def test_podmienia_tylko_wskazane_pole(self):
        xml = fixtures.icf_xml()
        nowy = icf.podmien(xml, "mail", "title", "Nowy tytuł")
        dane = icf.wczytaj(nowy)
        self.assertEqual(dane["kanaly"]["mail"]["title"], "Nowy tytuł")
        self.assertEqual(dane["kanaly"]["mail"]["text_main_0"], icf.wczytaj(xml)["kanaly"]["mail"]["text_main_0"])
        # reszta pliku (sms, załączniki) bajt w bajt bez zmian
        self.assertEqual(nowy[nowy.index('<contents message_type="sms">'):], xml[xml.index('<contents message_type="sms">'):])

    def test_znaki_specjalne_i_cdata(self):
        tresc = 'Cena < 100 & "rabat" ]]> koniec – żółć'
        nowy = icf.podmien(fixtures.icf_xml(), "mail", "text_main_0", tresc)
        ET.fromstring(nowy.encode("utf-8"))   # poprawny XML
        self.assertEqual(icf.wczytaj(nowy)["kanaly"]["mail"]["text_main_0"], tresc)

    def test_pusta_wartosc_jak_w_panelu(self):
        nowy = icf.podmien(fixtures.icf_xml(), "sms", "text_main_0", "")
        self.assertIn('<content type="text_main_0"> </content>', nowy)

    def test_brak_kanalu_lub_pola(self):
        with self.assertRaises(icf.BladIcf):
            icf.podmien(fixtures.icf_xml(z_sms=False), "sms", "text_main_0", "x")
        with self.assertRaises(icf.BladIcf):
            icf.podmien(fixtures.icf_xml(), "mail", "nie_ma_takiego", "x")


class TestOdcisk(unittest.TestCase):
    def test_wektor_wspolny_z_js(self):
        # Ten sam tekst i wynik sprawdza przegladarka/testy/test_core.mjs.
        self.assertEqual(icf.odcisk(WEKTOR), WEKTOR_ODCISK)

    def test_cdata_i_encje_daja_ten_sam_odcisk(self):
        # Panel po zapisie trzyma tytuł bez CDATA - to ta sama treść.
        a = fixtures.icf_xml(tytul="A & B <c>").replace("A & B <c>", "A & B <c>")
        b = a.replace("<![CDATA[A & B <c>]]>", "A &amp; B &lt;c&gt;")
        self.assertNotEqual(a, b)
        self.assertEqual(icf.odcisk(a), icf.odcisk(b))

    def test_ignoruje_ustawienia_techniczne(self):
        a = fixtures.icf_xml()
        b = a.replace('<content type="disposition"> </content>', '<content type="disposition">n</content>')
        self.assertEqual(icf.odcisk(a), icf.odcisk(b))

    def test_ignoruje_id_i_date_eksportu(self):
        a = fixtures.icf_xml(element_id="1", opis=" 2026.10.13 13:00:00")
        b = fixtures.icf_xml(element_id="2", opis=" 2026.10.14 09:00:00")
        self.assertEqual(icf.odcisk(a), icf.odcisk(b))
        self.assertNotEqual(icf.odcisk(a), icf.odcisk(fixtures.icf_xml(html="<p>inna treść</p>")))

    def test_ignoruje_flagi_wysylki(self):
        # Odcisk opisuje treść - zmiana włącznika mail/SMS nie może wyglądać jak zmiana treści.
        self.assertEqual(icf.odcisk(fixtures.icf_xml(mail_active="y", sms_active="n")),
                         icf.odcisk(fixtures.icf_xml(mail_active="n", sms_active="y")))

    def test_zmiana_tresci_sms_i_zalacznika_zmienia_odcisk(self):
        a = fixtures.icf_xml()
        self.assertNotEqual(icf.odcisk(a), icf.odcisk(fixtures.icf_xml(sms="inny SMS")))
        self.assertNotEqual(icf.odcisk(a), icf.odcisk(a.replace("iVBORw0KGgo=", "AAAA")))

    def test_to_sha256(self):
        self.assertEqual(len(icf.odcisk(fixtures.icf_xml())), len(hashlib.sha256(b"").hexdigest()))


WEKTOR = ('<contents message_type="mail"><content type="text_main_0"><![CDATA[<p>Ż & ]]]]><![CDATA[>]]></content>'
          '<content type="title">A &amp; B</content><content type="active">y</content></contents>'
          '<contents message_type="sms"><content type="text_main_0"> </content></contents>'
          '<enclosures><enclosure id="0">QUJD</enclosure></enclosures>')
WEKTOR_ODCISK = "df229c2e450ca6e63bc58fc5b6a9d8fd7bd676fe4703175521d59965cf1f7fea"


if __name__ == "__main__":
    unittest.main()
