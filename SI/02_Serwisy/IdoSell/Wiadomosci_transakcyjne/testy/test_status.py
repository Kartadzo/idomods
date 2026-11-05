import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, status


def _eksport(tmp, icf_per_jezyk, wiadomosc=None, jezyki=("pol", "eng", "ukr")):
    w = wiadomosc or fixtures.wiadomosc(jezyki=jezyki)
    m = fixtures.manifest(wiadomosci=[w, fixtures.wiadomosc(template="old", edytowalna=False)], jezyki=jezyki)
    pliki = {w["pliki"][j]: xml for j, xml in icf_per_jezyk.items()}
    zip_ = os.path.join(tmp, "e.zip")
    fixtures.zbuduj_zip(zip_, m, pliki)
    return eksport.rozpakuj([zip_], os.path.join(tmp, "e"))


class TestFunkcje(unittest.TestCase):
    def test_zmienne(self):
        self.assertEqual(status.zmienne("Nr [iai:order_sn] [iai:if_prepaid-begin]x[iai:if_prepaid-end]"),
                         {"[iai:order_sn]", "[iai:if_prepaid-begin]", "[iai:if_prepaid-end]"})

    def test_dlugosc_sms(self):
        self.assertEqual(status.dlugosc_sms("a" * 10, "n"), (10, 160))
        self.assertEqual(status.dlugosc_sms("zażółć", "n"), (6, 70))
        self.assertEqual(status.dlugosc_sms("zażółć łódź", "y"), (11, 160))   # panel konwertuje do ASCII

    def test_dlugosc_sms_bez_zmiennych(self):
        # Zmienne panel podmienia przed wysyłką - ich nawiasy nie mogą wymuszać limitu 70 ani liczyć się do długości.
        self.assertEqual(status.dlugosc_sms("Zamówienie [iai:order_id] przyjęte", "y"), (20, 160))


class TestKontrola(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _problemy(self, icf_per_jezyk, **kw):
        katalog, m = _eksport(self.tmp.name, icf_per_jezyk, **kw)
        return status.kontrola(m, katalog)

    def test_kopia_tytulu_z_pol(self):
        p = self._problemy({
            "pol": fixtures.icf_xml(jezyk="pol"),
            "eng": fixtures.icf_xml(jezyk="eng", tytul="Order [iai:order_sn]", html="<p>Thanks [iai:order_sn]</p>",
                                    sms="Order [iai:order_id] [iai:shop_name]"),
            "ukr": fixtures.icf_xml(jezyk="ukr", html="<p>Дякуємо [iai:order_sn]</p>", sms="Замовлення [iai:order_id] [iai:shop_name]"),
        })
        kopie = [x for x in p if x["rodzaj"] == "kopia"]
        self.assertEqual(len(kopie), 1)
        self.assertEqual(kopie[0]["jezyk"], "ukr")
        self.assertIn("tytuł maila", kopie[0]["opis"])
        self.assertIn("pol", kopie[0]["opis"])

    def test_pol_identyczny_z_eng_zglaszany_raz_przy_eng(self):
        xml = fixtures.icf_xml()
        p = self._problemy({"pol": xml, "eng": xml.replace('value="pol"', 'value="eng"')}, jezyki=("pol", "eng"),
                           wiadomosc=fixtures.wiadomosc(jezyki=("pol", "eng")))
        self.assertEqual({x["jezyk"] for x in p if x["rodzaj"] == "kopia"}, {"eng"})

    def test_brakujaca_zmienna(self):
        p = self._problemy({"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Order",
                                                                              html="<p>x [iai:order_sn]</p>", sms="x [iai:order_id] [iai:shop_name]")},
                           jezyki=("pol", "eng"), wiadomosc=fixtures.wiadomosc(jezyki=("pol", "eng")))
        zm = [x for x in p if x["rodzaj"] == "zmienne"]
        self.assertEqual(len(zm), 1)
        self.assertIn("[iai:order_sn]", zm[0]["opis"])
        self.assertIn("tytuł", zm[0]["opis"])

    def test_pusta_tresc_przy_wlaczonej_wysylce(self):
        p = self._problemy({"pol": fixtures.icf_xml(html="")}, jezyki=("pol",), wiadomosc=fixtures.wiadomosc(jezyki=("pol",)))
        self.assertTrue(any(x["rodzaj"] == "pusta" and "treść maila" in x["opis"] for x in p))

    def test_dlugi_sms(self):
        w = fixtures.wiadomosc(jezyki=("pol",), sms="y")
        p = self._problemy({"pol": fixtures.icf_xml(sms="ą" * 80, only_ascii="n")}, jezyki=("pol",), wiadomosc=w)
        self.assertTrue(any(x["rodzaj"] == "sms" and "80 znaków > 70" in x["opis"] for x in p))

    def test_dlugi_sms_wylaczony_nie_zglaszany(self):
        w = fixtures.wiadomosc(jezyki=("pol",), sms="n")
        p = self._problemy({"pol": fixtures.icf_xml(sms="ą" * 80, only_ascii="n")}, jezyki=("pol",), wiadomosc=w)
        self.assertFalse(any(x["rodzaj"] == "sms" for x in p))

    def test_opis_kopii_poprawny_gramatycznie(self):
        xml = fixtures.icf_xml()
        p = self._problemy({"pol": xml, "eng": xml.replace('value="pol"', 'value="eng"')}, jezyki=("pol", "eng"),
                           wiadomosc=fixtures.wiadomosc(jezyki=("pol", "eng")))
        opisy = [x["opis"] for x in p if x["rodzaj"] == "kopia"]
        self.assertIn("tytuł maila: identyczny z pol", opisy)
        self.assertIn("treść maila: identyczna z pol", opisy)


class TestRaport(unittest.TestCase):
    def test_raport(self):
        with tempfile.TemporaryDirectory() as tmp:
            katalog, m = _eksport(tmp, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng"),
                                        "ukr": fixtures.icf_xml(jezyk="ukr")})
            m["wiadomosci"][0]["nazwa"] = "Nazwa | z kreską"
            tekst = status.raport(m, katalog)
            self.assertIn("# Status wiadomości transakcyjnych — zooart6.yourtechnicaldomain.com, sklep 1", tekst)
            self.assertIn("| Wiadomości ogółem | 2 |", tekst)
            self.assertIn("| Wycofywane (tylko podgląd) | 1 |", tekst)
            self.assertIn("| Mail włączony — pol | 1 |", tekst)
            self.assertIn("Nazwa \\| z kreską", tekst)
            self.assertIn("2026-07-17 12:10:52 (Jan Testowy)", tekst)
            self.assertIn("## Kontrola jakości", tekst)

    def test_csv_dwie_czesci(self):
        import csv
        import io
        with tempfile.TemporaryDirectory() as tmp:
            katalog, m = _eksport(tmp, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng"),
                                        "ukr": fixtures.icf_xml(jezyk="ukr")})
            tekst = status.raport_csv(m, katalog)
            self.assertTrue(tekst.startswith("﻿"))   # Excel z polskimi znakami
            wiersze = list(csv.reader(io.StringIO(tekst.lstrip("﻿")), delimiter=";"))
            ogolny = wiersze.index(["STATUS OGÓLNY (wg grup)"])
            self.assertEqual(wiersze[ogolny + 1][:7], ["Grupa", "Wiadomości", "Edytowalne", "Wycofywane",
                                                       "Mail polski włączony", "Mail angielski włączony",
                                                       "Mail ukraiński włączony"])
            self.assertEqual(wiersze[ogolny + 2][:5], ["Złożenie zamówienia", "2", "1", "1", "1"])
            self.assertEqual(wiersze[ogolny + 3][0], "RAZEM")
            szczegoly = wiersze.index(["WIADOMOŚCI"])
            self.assertGreater(szczegoly, ogolny)
            naglowek, pierwsza = wiersze[szczegoly + 1], wiersze[szczegoly + 2]
            rekord = dict(zip(naglowek, pierwsza))
            self.assertEqual(rekord["Wiadomość"], "Potwierdzenie wpłynięcia zamówienia")
            self.assertEqual(rekord["Mail polski"], "tak")
            self.assertEqual(rekord["Kto edytował"], "Jan Testowy")
            self.assertEqual(rekord["Kod wiadomości"], "order_confirmation")
            self.assertIn("angielski: tytuł maila: identyczny jak w wersji: polski", rekord["Problemy (opis)"])

    def test_zapisuje_md_i_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            katalog, m = _eksport(tmp, {"pol": fixtures.icf_xml()}, jezyki=("pol",))
            from unittest import mock
            with mock.patch.object(status.wspolne, "FOLDER_STATUS", os.path.join(tmp, "Status")):
                md, csv_ = status.zapisz_raport(m, katalog)
            self.assertTrue(md.endswith(".md") and os.path.exists(md))
            self.assertTrue(csv_.endswith(".csv") and os.path.exists(csv_))


if __name__ == "__main__":
    unittest.main()
