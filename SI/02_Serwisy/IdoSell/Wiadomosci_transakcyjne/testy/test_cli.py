import os
import subprocess
import sys
import tempfile
import unittest

from testy import fixtures

SKRYPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiadomosci.py")


def uruchom(katalog, *argumenty):
    env = dict(os.environ, WT_KATALOG=katalog, WT_POBIERANIE=os.path.join(katalog, "Downloads"), PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, SKRYPT] + list(argumenty), capture_output=True, text=True,
                          encoding="utf-8", env=env, stdin=subprocess.DEVNULL)


class TestCli(unittest.TestCase):
    def test_pelny_przebieg(self):
        with tempfile.TemporaryDirectory() as k:
            m = fixtures.manifest(jezyki=("pol", "eng"))
            w = m["wiadomosci"][0]
            zip_ = os.path.join(k, "eksport.zip")
            fixtures.zbuduj_zip(zip_, m, {w["pliki"][j]: fixtures.icf_xml(jezyk=j) for j in ("pol", "eng")})

            r = uruchom(k, "rozpakuj", zip_)
            self.assertEqual(r.returncode, 0, r.stderr)
            katalog = os.path.join(k, "Eksport i Import Treści", "zooart6_shop1", "2026-10-13_130509")
            self.assertTrue(os.path.exists(os.path.join(katalog, "manifest.json")))

            r = uruchom(k, "status", katalog)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(k, "Status", "zooart6_shop1", "status_2026-10-13_130509.md")))

            r = uruchom(k, "konfiguracja", katalog)
            self.assertEqual(r.returncode, 0, r.stderr)
            csv_ = os.path.join(k, "Edycja Działania", "zooart6_shop1", "konfiguracja_2026-10-13_130509.csv")
            with open(csv_, encoding="utf-8-sig") as p:
                tekst = p.read()
            with open(csv_, "w", encoding="utf-8-sig") as p:
                p.write(tekst.replace("tak;tak;nie", "tak;nie;nie", 1))
            r = uruchom(k, "zmiany", katalog, "--tak")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("mail eng: tak -> nie", r.stdout)

            with open(os.path.join(katalog, "order_confirmation", "eng_sms.txt"), "w", encoding="utf-8") as p:
                p.write("Nowy SMS")
            r = uruchom(k, "tresci", katalog, "--tak")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("plan_importu.json", r.stdout)
            self.assertNotIn("\\\\?\\", r.stdout)   # komunikaty bez przedrostka ścieżki rozszerzonej

            # ZIP sprzed zmian jako „stan po” - weryfikacja wykaże problem, ale ma zapisać raport i nie zostawiać po\.
            plan = [os.path.join(katalog, n) for n in os.listdir(katalog) if n.startswith("do_importu_")][0]
            r = uruchom(k, "weryfikuj", plan, zip_)
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("Raport weryfikacji", r.stdout)
            self.assertFalse(os.path.exists(os.path.join(plan, "po")))
            self.assertTrue(any(n.endswith(".md") for n in os.listdir(plan)))

    def test_zip_z_folderu_pobierania_przeniesiony_do_archiwum(self):
        with tempfile.TemporaryDirectory() as k:
            m = fixtures.manifest(jezyki=("pol",))
            pobieranie = os.path.join(k, "Downloads")
            os.makedirs(pobieranie)
            nazwa = "eksport_zooart6_shop1_20261013-130509.zip"
            fixtures.zbuduj_zip(os.path.join(pobieranie, nazwa), m, {m["wiadomosci"][0]["pliki"]["pol"]: fixtures.icf_xml()})
            obcy = os.path.join(pobieranie, "faktura.zip")
            with open(obcy, "wb") as p:
                p.write(b"x")
            r = uruchom(k, "rozpakuj", os.path.join(pobieranie, nazwa))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(os.path.exists(os.path.join(pobieranie, nazwa)))
            self.assertTrue(os.path.exists(os.path.join(k, "_pobrane", nazwa)))
            self.assertTrue(os.path.exists(obcy))   # inne pliki z Pobranych nietknięte

    def test_exe_nie_zamyka_okna_po_bledzie(self):
        sys.path.insert(0, os.path.dirname(SKRYPT))
        import wiadomosci
        from unittest import mock
        with mock.patch.object(sys, "frozen", True, create=True), \
                mock.patch.object(wiadomosci, "main", side_effect=RuntimeError("coś poszło nie tak")), \
                mock.patch("builtins.input", return_value="") as czekaj:
            self.assertEqual(wiadomosci.main_exe([]), 1)
        czekaj.assert_called_once()

    def test_zle_argumenty(self):
        with tempfile.TemporaryDirectory() as k:
            self.assertEqual(uruchom(k, "nieznane").returncode, 2)
            self.assertEqual(uruchom(k, "status", os.path.join(k, "brak")).returncode, 1)


if __name__ == "__main__":
    unittest.main()
