import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, icf, weryfikacja as wer


def _po(tmp, xml_per_jezyk, mail=None, sms="n", jezyki=("pol", "eng")):
    w = fixtures.wiadomosc(jezyki=jezyki, mail=mail, sms=sms)
    m = fixtures.manifest(wiadomosci=[w], jezyki=jezyki)
    m["rodzaj"] = "weryfikacja"
    zip_ = os.path.join(tmp, "w.zip")
    fixtures.zbuduj_zip(zip_, m, {w["pliki"][j]: x for j, x in xml_per_jezyk.items()})
    return eksport.rozpakuj([zip_], os.path.join(tmp, "po"))


def _plan_importu(oczekiwane, przed, flagi=None):
    return {"wersja": 1, "rodzaj": "import", "domena": "zooart6.yourtechnicaldomain.com", "shop_id": 1,
            "data_eksportu": "2026-10-13T13:05:09",
            "pozycje": [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "jezyk": "eng",
                         "plik": "order_confirmation__eng.icf", "odcisk_oryginalu": "x",
                         "oczekiwane": oczekiwane, "przed": przed}],
            "oczekiwane_flagi": {"order_confirmation": flagi or {"mail": {"pol": "y", "eng": "y"}, "sms": "n"}}}


class TestImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_ok(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Nowy")})
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        self.assertEqual([w["wynik"] for w in wyniki], [wer.OK])

    def test_nie_zmienilo_sie_i_inaczej(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Stary", sms="Inny")})
        plan = _plan_importu({"mail.title": "Nowy", "sms.text_main_0": "Nowy SMS"}, {"mail.title": "Stary", "sms.text_main_0": "Stary SMS"})
        wyniki = {w["co"]: w["wynik"] for w in wer.weryfikuj(plan, m, katalog)}
        self.assertEqual(wyniki["mail.title"], wer.BEZ_ZMIAN)
        self.assertEqual(wyniki["sms.text_main_0"], wer.INACZEJ)

    def test_import_wylaczyl_wysylke(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Nowy")},
                         mail={"pol": "y", "eng": "n"})
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        flagi = [w for w in wyniki if w["co"] == "flaga mail eng"]
        self.assertEqual(flagi[0]["wynik"], wer.INACZEJ)

    def test_flagi_porownywane_ze_stanem_sprzed_importu(self):
        # Eksport mówił eng=n, ale tuż przed importem panel miał eng=y (zmiana po eksporcie / inny sklep).
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Nowy")},
                         mail={"pol": "y", "eng": "n"})
        m["flagi_przed_importem"] = {"order_confirmation": {"mail": {"pol": "y", "eng": "y"}, "sms": "n"}}
        plan = _plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}, flagi={"mail": {"pol": "y", "eng": "n"}, "sms": "n"})
        flagi = {w["co"]: w["wynik"] for w in wer.weryfikuj(plan, m, katalog) if w["co"].startswith("flaga")}
        self.assertEqual(flagi["flaga mail eng"], wer.INACZEJ)

    def test_migracja_bez_odczytu_flag_nie_daje_falszywego_ok(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Nowy")})
        m["domena"] = "inny.iai-shop.com"
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        self.assertTrue(any(w["co"] == "flagi" and w["wynik"] == wer.BRAK for w in wyniki))

    def test_brak_w_eksporcie(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml()})
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        self.assertEqual(wyniki[0]["wynik"], wer.BRAK)


class TestKonfiguracja(unittest.TestCase):
    def test_flagi_i_kopie(self):
        with tempfile.TemporaryDirectory() as tmp:
            xml_pol, xml_eng = fixtures.icf_xml(), fixtures.icf_xml(jezyk="eng")
            katalog, m = _po(tmp, {"pol": xml_pol, "eng": fixtures.icf_xml(jezyk="eng", html="<p>przepisane</p>")},
                             mail={"pol": "y", "eng": "n"})
            plan = {"wersja": 1, "rodzaj": "konfiguracja", "domena": "zooart6.yourtechnicaldomain.com", "shop_id": 1,
                    "data_eksportu": "2026-10-13T13:05:09",
                    "zmiany": [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "grupa": "make_order",
                                "mail": {"eng": "n"}, "sms": None, "reset": False,
                                "oczekiwane": {"mail": {"pol": "y", "eng": "n"}, "sms": "n"},
                                "kopie": {"pol": {"plik": "a", "odcisk": icf.odcisk(xml_pol)},
                                          "eng": {"plik": "b", "odcisk": icf.odcisk(xml_eng)}}}]}
            wyniki = {(w["co"], w["jezyk"]): w["wynik"] for w in wer.weryfikuj(plan, m, katalog)}
            self.assertEqual(wyniki[("flaga mail eng", "eng")], wer.OK)
            self.assertEqual(wyniki[("flaga mail pol", "pol")], wer.OK)
            self.assertEqual(wyniki[("treść", "pol")], wer.OK)
            self.assertEqual(wyniki[("treść", "eng")], wer.INACZEJ)


class TestRaport(unittest.TestCase):
    def test_raport(self):
        plan = _plan_importu({}, {})
        wyniki = [{"template": "t", "nazwa": "N", "jezyk": "eng", "co": "mail.title", "wynik": wer.OK, "szczegoly": ""},
                  {"template": "t", "nazwa": "N", "jezyk": "eng", "co": "sms.text_main_0", "wynik": wer.INACZEJ, "szczegoly": "jest: x"}]
        tekst = wer.raport(plan, wyniki)
        self.assertIn("OK: 1", tekst)
        self.assertIn("Problemy: 1", tekst)
        self.assertTrue(wer.nazwa_raportu(plan).startswith("import_"))


if __name__ == "__main__":
    unittest.main()
