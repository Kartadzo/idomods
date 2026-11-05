import os
import tempfile
import unittest

from testy import fixtures
from wt import edytor, eksport, tresci, wspolne


class TestEdytor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        m = fixtures.manifest(jezyki=("pol", "eng"))
        w = m["wiadomosci"][0]
        zip_ = os.path.join(self.tmp.name, "e.zip")
        fixtures.zbuduj_zip(zip_, m, {w["pliki"][j]: fixtures.icf_xml(jezyk=j) for j in ("pol", "eng")})
        katalog, _ = eksport.rozpakuj([zip_], os.path.join(self.tmp.name, "e"))
        self.e = edytor.Eksport(katalog)
        self.w = self.e.wiadomosci()[0]

    def tearDown(self):
        self.tmp.cleanup()

    def test_lista_i_jezyki(self):
        self.assertEqual([w["template"] for w in self.e.wiadomosci()], ["order_confirmation"])
        self.assertEqual(self.e.jezyki(self.w), ["pol", "eng"])
        self.assertFalse(self.e.zmieniony(self.w, "eng"))
        self.assertEqual(self.e.liczba_zmian(), 0)

    def test_zapis_trafia_do_importu(self):
        self.e.zapisz(self.w, "eng", "Your order [iai:order_sn]", "<p>Thank you [iai:order_sn]</p>")
        self.assertTrue(self.e.zmieniony(self.w, "eng"))
        self.assertEqual(self.e.tresc(self.w, "eng"), ("Your order [iai:order_sn]", "<p>Thank you [iai:order_sn]</p>"))
        roznice = tresci.roznice_tresci(self.e.katalog, self.e.manifest)
        self.assertEqual([(r["jezyk"], sorted(r["pola"])) for r in roznice], [("eng", ["mail.text_main_0", "mail.title"])])

    def test_cofnij(self):
        self.e.zapisz(self.w, "eng", "X", "<p>Y</p>")
        self.e.cofnij(self.w, "eng")
        self.assertFalse(self.e.zmieniony(self.w, "eng"))
        self.assertEqual(tresci.roznice_tresci(self.e.katalog, self.e.manifest), [])

    def test_usun_i_przywroc(self):
        self.e.zapisz(self.w, "eng", "Zmieniony", "<p>Zmieniony</p>")
        self.e.wyklucz(self.w, "eng")
        folder = self.e.folder(self.w)
        self.assertTrue(self.e.wykluczony(self.w, "eng"))
        self.assertTrue(os.path.exists(os.path.join(folder, "eng.icf")))       # oryginał zostaje
        self.assertFalse(os.path.exists(os.path.join(folder, "eng_mail.html")))
        self.assertTrue(os.path.exists(os.path.join(self.e.katalog, "_usuniete", "order_confirmation", "eng_mail.html")))
        self.assertEqual(tresci.roznice_tresci(self.e.katalog, self.e.manifest), [])   # nie trafi do „Zastosuj plan”
        self.assertEqual(self.e.liczba_zmian(), 0)
        self.e.przywroc(self.w, "eng")
        self.assertFalse(self.e.wykluczony(self.w, "eng"))
        self.assertEqual(self.e.tresc(self.w, "eng")[1], "<p>Zmieniony</p>")   # zmiany wracają razem z plikiem
        self.assertEqual(len(tresci.roznice_tresci(self.e.katalog, self.e.manifest)), 1)

    def test_przygotuj_paczke(self):
        self.assertEqual(self.e.przygotuj_paczke(), (None, []))
        self.e.zapisz(self.w, "pol", "Nowy tytuł", self.e.tresc(self.w, "pol")[1])
        katalog_planu, roznice = self.e.przygotuj_paczke()
        self.assertTrue(os.path.exists(os.path.join(katalog_planu, "plan_importu.json")))
        self.assertEqual(roznice[0]["pola"], {"mail.title": "Nowy tytuł"})

    def test_pusty_w_sklepie(self):
        # Przypadek alpha-teile: <contents message_type="mail"></contents> - mail nigdy niewypełniony w panelu.
        import re
        sciezka = os.path.join(self.e.folder(self.w), "eng.icf")
        xml = re.sub(r'(<contents message_type="mail">).*?(</contents>)', r"\1\2", wspolne.czytaj_tekst(sciezka), flags=re.S)
        wspolne.zapisz_tekst(sciezka, xml)
        self.e.zapisz(self.w, "eng", "", "")   # tak rozpakowuje się pusty mail z panelu
        e = edytor.Eksport(self.e.katalog)
        self.assertTrue(e.pusty_w_sklepie(self.w, "eng"))
        self.assertFalse(e.pusty_w_sklepie(self.w, "pol"))
        self.assertEqual(tresci.roznice_tresci(e.katalog, e.manifest), [])
        wspolne.zapisz_tekst(os.path.join(e.folder(self.w), "eng_mail.html"), "<p>Nowa treść</p>")
        with self.assertRaisesRegex(edytor.icf.BladIcf, "w sklepie pusty"):
            tresci.roznice_tresci(e.katalog, e.manifest)

    def test_roznica_zmiennych(self):
        self.assertEqual(edytor.roznica_zmiennych("Nr [iai:order_sn] [iai:shop_name]", "Nr [iai:order_sn] [iai:nowa]"),
                         (["[iai:shop_name]"], ["[iai:nowa]"]))

    def test_podglad(self):
        sciezka = edytor.plik_podgladu("Temat <1>", '<p>Nr [iai:order_sn]</p><img src="[iai:logo]">', "Test (polski)")
        strona = wspolne.czytaj_tekst(sciezka)
        self.assertIn("Temat &lt;1&gt;", strona)
        self.assertIn('<span style="background:#fff3b0;color:#7a5b00">[iai:order_sn]</span>', strona)
        self.assertIn('src="[iai:logo]"', strona)   # zmienna w atrybucie nietknięta
        self.assertIn('charset="utf-8"', strona)


if __name__ == "__main__":
    unittest.main()
