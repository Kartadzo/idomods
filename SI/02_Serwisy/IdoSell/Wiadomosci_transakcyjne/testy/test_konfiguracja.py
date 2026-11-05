import csv
import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, icf, konfiguracja as k, wspolne


def _manifest():
    return fixtures.manifest(wiadomosci=[
        fixtures.wiadomosc(template="order_confirmation", nazwa="Potwierdzenie", jezyki=("pol", "eng")),
        fixtures.wiadomosc(template="panel_only", nazwa="Z panelu", jezyki=("pol", "eng"), sms=None,
                           stan_listy={"sms": "nie dotyczy", "mail": "tak", "webpush": "nie", "braki": None}),
        fixtures.wiadomosc(template="old", nazwa="Wycofana", edytowalna=False),
    ], jezyki=("pol", "eng"))


class TestCsv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "konf.csv")
        self.m = _manifest()
        k.zapisz_csv(self.m, self.csv)

    def tearDown(self):
        self.tmp.cleanup()

    def _wiersze(self):
        with open(self.csv, encoding="utf-8-sig", newline="") as p:
            return list(csv.DictReader(p, delimiter=";"))

    def _zapisz(self, wiersze, kodowanie="utf-8-sig", sep=";"):
        with open(self.csv, "w", encoding=kodowanie, newline="") as p:
            w = csv.DictWriter(p, fieldnames=list(wiersze[0].keys()), delimiter=sep)
            w.writeheader()
            w.writerows(wiersze)

    def test_zawartosc_csv(self):
        wiersze = self._wiersze()
        self.assertEqual(list(wiersze[0].keys()), ["grupa", "template", "nazwa", "mail_pol", "mail_eng", "sms", "reset_domyslna"])
        self.assertEqual([w["template"] for w in wiersze], ["order_confirmation", "panel_only"])   # bez wycofanej
        self.assertEqual(wiersze[0]["mail_eng"], "tak")
        self.assertEqual(wiersze[0]["sms"], "nie")
        self.assertEqual(wiersze[1]["sms"], "nie dotyczy")
        with open(self.csv, "rb") as p:
            self.assertTrue(p.read().startswith(b"\xef\xbb\xbf"))   # BOM dla Excela

    def test_brak_zmian(self):
        self.assertEqual(k.roznice(self.m, self.csv), ([], []))

    def test_zmiana_maila_i_sms(self):
        w = self._wiersze()
        w[0]["mail_eng"], w[0]["sms"] = "NIE ", "tak"
        self._zapisz(w)
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(bledy, [])
        self.assertEqual(zmiany, [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "grupa": "make_order",
                                   "mail": {"eng": "n"}, "sms": "y", "reset": False}])

    def test_zmiana_nie_dotyczy_to_blad(self):
        w = self._wiersze()
        w[1]["sms"] = "tak"
        self._zapisz(w)
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(zmiany, [])
        self.assertEqual(len(bledy), 1)
        self.assertIn("wiersz 3", bledy[0])
        self.assertIn("sms", bledy[0])

    def test_pusta_lub_zla_wartosc(self):
        w = self._wiersze()
        w[0]["mail_pol"], w[0]["mail_eng"] = "", "może"
        self._zapisz(w)
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(zmiany, [])
        self.assertEqual(len(bledy), 2)
        self.assertTrue(all("dozwolone: tak / nie" in b for b in bledy))

    def test_duplikat_wiersza(self):
        w = self._wiersze()
        self._zapisz(w + [dict(w[0])])
        _, bledy = k.roznice(self.m, self.csv)
        self.assertTrue(any("powtórzona" in b for b in bledy))

    def test_nieznana_wiadomosc(self):
        w = self._wiersze()
        w[0]["template"] = "old"
        self._zapisz(w)
        _, bledy = k.roznice(self.m, self.csv)
        self.assertTrue(any("'old'" in b for b in bledy))

    def test_csv_z_przecinkiem_i_bez_bom(self):
        self._zapisz(self._wiersze(), kodowanie="utf-8", sep=",")
        with self.assertRaises(k.BladKonfiguracji) as kontekst:
            k.roznice(self.m, self.csv)
        self.assertIn("średnik", str(kontekst.exception))

    def test_csv_z_polskiego_excela_cp1250(self):
        # „CSV (rozdzielany średnikami)” w polskim Excelu zapisuje w cp1250 — polskie znaki w kolumnie nazwa.
        w = self._wiersze()
        w[0]["nazwa"], w[0]["mail_eng"] = "Potwierdzenie wpłynięcia zamówienia", "nie"
        self._zapisz(w, kodowanie="cp1250")
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(bledy, [])
        self.assertEqual(zmiany[0]["mail"], {"eng": "n"})

    def test_reset(self):
        w = self._wiersze()
        w[0]["reset_domyslna"] = "tak"
        self._zapisz(w)
        zmiany, _ = k.roznice(self.m, self.csv)
        self.assertTrue(zmiany[0]["reset"])


class TestPlan(unittest.TestCase):
    def test_plan_z_kopiami(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = _manifest()
            w = m["wiadomosci"][0]
            katalog = os.path.join(tmp, "eksport")
            for j in ("pol", "eng"):
                wspolne.zapisz_tekst(os.path.join(eksport.folder_wiadomosci(katalog, w), j + ".icf"),
                                     fixtures.icf_xml(jezyk=j))
            zmiany = [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "grupa": "make_order",
                       "mail": {"eng": "n"}, "sms": None, "reset": False}]
            sciezka = k.zapisz_plan(m, katalog, zmiany, os.path.join(tmp, "plan"))
            plan = wspolne.czytaj_json(sciezka)
            z = plan["zmiany"][0]
            self.assertEqual(plan["rodzaj"], "konfiguracja")
            self.assertEqual(z["oczekiwane"], {"mail": {"pol": "y", "eng": "n"}, "sms": "n"})
            self.assertEqual(z["kopie"]["eng"]["plik"], "order_confirmation__eng.icf")
            kopia = os.path.join(tmp, "plan", "kopie", "order_confirmation__eng.icf")
            self.assertEqual(z["kopie"]["eng"]["odcisk"], icf.odcisk(wspolne.czytaj_tekst(kopia)))

    def test_reset_bez_kopii(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = _manifest()
            zmiany = [{"template": "order_confirmation", "nazwa": "P", "grupa": "make_order",
                       "mail": {}, "sms": None, "reset": True}]
            plan = wspolne.czytaj_json(k.zapisz_plan(m, os.path.join(tmp, "e"), zmiany, os.path.join(tmp, "p")))
            self.assertEqual(plan["zmiany"][0]["kopie"], {})


if __name__ == "__main__":
    unittest.main()
