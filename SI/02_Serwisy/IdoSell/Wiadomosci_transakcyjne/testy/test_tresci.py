import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, icf, tresci, wspolne


class TestTresci(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.m = fixtures.manifest(jezyki=("pol", "eng"))
        pliki = {}
        for j in ("pol", "eng"):
            pliki[self.m["wiadomosci"][0]["pliki"][j]] = fixtures.icf_xml(jezyk=j, html="<p>A</p>\n<p>B</p>")
        zip_ = os.path.join(self.tmp.name, "e.zip")
        fixtures.zbuduj_zip(zip_, self.m, pliki)
        self.kat, self.m = eksport.rozpakuj([zip_], os.path.join(self.tmp.name, "e"))
        self.folder = os.path.join(self.kat, "order_confirmation")

    def tearDown(self):
        self.tmp.cleanup()

    def test_bez_zmian(self):
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_crlf_to_nie_zmiana(self):
        sciezka = os.path.join(self.folder, "eng_mail.html")
        wspolne.zapisz_tekst(sciezka, wspolne.czytaj_tekst(sciezka).replace("\n", "\r\n"))
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_bom_z_edytora_to_nie_zmiana(self):
        sciezka = os.path.join(self.folder, "eng_mail.html")
        wspolne.zapisz_tekst(sciezka, "﻿" + wspolne.czytaj_tekst(sciezka))
        meta = os.path.join(self.folder, "meta.json")
        with open(meta, encoding="utf-8") as p:
            tekst = p.read()
        with open(meta, "w", encoding="utf-8-sig") as p:   # Notatnik „UTF-8 z BOM”
            p.write(tekst)
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_bom_nie_trafia_do_panelu(self):
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_sms.txt"), "﻿Nowy SMS")
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m)[0]["pola"]["sms.text_main_0"], "Nowy SMS")

    def test_zmiana_tresci_tytulu_i_sms(self):
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_mail.html"), "<p>Thank you</p>\r\n")
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_sms.txt"), "Order [iai:order_id] received")
        meta = wspolne.czytaj_json(os.path.join(self.folder, "meta.json"))
        meta["tytuly"]["eng"] = "Your order [iai:order_sn]"
        wspolne.zapisz_json(os.path.join(self.folder, "meta.json"), meta)
        wynik = tresci.roznice_tresci(self.kat, self.m)
        self.assertEqual(len(wynik), 1)
        self.assertEqual(wynik[0]["jezyk"], "eng")
        self.assertEqual(wynik[0]["pola"], {"mail.text_main_0": "<p>Thank you</p>\n",
                                            "sms.text_main_0": "Order [iai:order_id] received",
                                            "mail.title": "Your order [iai:order_sn]"})
        self.assertEqual(wynik[0]["przed"]["mail.text_main_0"], "<p>A</p>\n<p>B</p>")

    def test_brak_pliku_jezyka_nie_rusza(self):
        os.remove(os.path.join(self.folder, "pol_mail.html"))
        os.remove(os.path.join(self.folder, "pol_sms.txt"))
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_kanal_nie_dotyczy_pominiety(self):
        self.m["wiadomosci"][0]["stan_listy"]["sms"] = "nie dotyczy"
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_sms.txt"), "zmiana")
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_zloz(self):
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_mail.html"), "<p>Nowa</p>")
        roznice = tresci.roznice_tresci(self.kat, self.m)
        plan_dir = os.path.join(self.tmp.name, "plan")
        plan = wspolne.czytaj_json(tresci.zloz(self.m, roznice, plan_dir))
        poz = plan["pozycje"][0]
        self.assertEqual(plan["rodzaj"], "import")
        self.assertEqual(poz["plik"], "order_confirmation__eng.icf")
        nowy = wspolne.czytaj_tekst(os.path.join(plan_dir, poz["plik"]))
        self.assertEqual(icf.wczytaj(nowy)["kanaly"]["mail"]["text_main_0"], "<p>Nowa</p>")
        self.assertEqual(icf.wczytaj(nowy)["kanaly"]["mail"]["active"], "y")   # flaga bez zmian
        oryginal = wspolne.czytaj_tekst(os.path.join(self.folder, "eng.icf"))
        self.assertEqual(poz["odcisk_oryginalu"], icf.odcisk(oryginal))
        self.assertEqual(plan["oczekiwane_flagi"]["order_confirmation"], {"mail": {"pol": "y", "eng": "y"}, "sms": "n"})


if __name__ == "__main__":
    unittest.main()
