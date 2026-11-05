import os
import sys
import unittest
from unittest import mock

from wt import wspolne


class TestKatalogProgramu(unittest.TestCase):
    def test_w_zrodlach_folder_nad_pakietem(self):
        self.assertEqual(wspolne.katalog_programu(),
                         os.path.dirname(os.path.dirname(os.path.abspath(wspolne.__file__))))

    def test_w_exe_folder_pliku_exe(self):
        # PyInstaller rozpakowuje moduły do katalogu tymczasowego - wyniki muszą trafiać obok .exe.
        exe = os.path.join("C:\\", "Programy", "Wiadomosci", "Wiadomości transakcyjne.exe")
        with mock.patch.object(sys, "frozen", True, create=True), mock.patch.object(sys, "executable", exe):
            self.assertEqual(wspolne.katalog_programu(), os.path.dirname(exe))


class TestFolderPobierania(unittest.TestCase):
    def test_folder_z_windows_istnieje(self):
        self.assertTrue(os.path.isdir(wspolne.folder_pobierania()))

    def test_awaryjnie_downloads_w_profilu(self):
        with mock.patch.object(wspolne, "_folder_pobierania_windows", side_effect=OSError("brak API")):
            self.assertEqual(wspolne.folder_pobierania(), os.path.join(os.path.expanduser("~"), "Downloads"))


@unittest.skipUnless(os.name == "nt", "ścieżki rozszerzone dotyczą Windows")
class TestDlugaSciezka(unittest.TestCase):
    def test_przedrostek_i_pokaz(self):
        sciezka = wspolne.dluga_sciezka("C:\\Programy\\Wiadomosci")
        self.assertEqual(sciezka, "\\\\?\\C:\\Programy\\Wiadomosci")
        self.assertEqual(wspolne.dluga_sciezka(sciezka), sciezka)   # bez podwójnego przedrostka
        self.assertEqual(wspolne.pokaz("Plan: " + sciezka), "Plan: C:\\Programy\\Wiadomosci")

    def test_udzial_sieciowy(self):
        sciezka = wspolne.dluga_sciezka("\\\\serwer\\dane\\WT")
        self.assertEqual(sciezka, "\\\\?\\UNC\\serwer\\dane\\WT")
        self.assertEqual(wspolne.pokaz(sciezka), "\\\\serwer\\dane\\WT")

    def test_katalog_glowny_rozszerzony(self):
        self.assertTrue(wspolne.KATALOG_GLOWNY.startswith(wspolne.PRZEDROSTEK_DLUGI))


if __name__ == "__main__":
    unittest.main()
