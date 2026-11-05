import os
import shutil
import tempfile
import unittest

from testy import fixtures
from wt import eksport, wspolne


def _zip_z(katalog, manifest, nazwa="e.zip", pliki=None):
    if pliki is None:
        pliki = {}
        for w in manifest["wiadomosci"]:
            for j, sc in w["pliki"].items():
                pliki[sc] = fixtures.icf_xml(template=w["template"], jezyk=j)
    sciezka = os.path.join(katalog, nazwa)
    fixtures.zbuduj_zip(sciezka, manifest, pliki)
    return sciezka


class TestRozpakuj(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.k = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_uklad_folderu(self):
        m = fixtures.manifest(jezyki=("pol", "eng"))
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m)], os.path.join(self.k, "out"))
        folder = os.path.join(cel, "order_confirmation")
        self.assertEqual(sorted(os.listdir(folder)),
                         ["eng.icf", "eng_mail.html", "eng_sms.txt", "meta.json", "pol.icf", "pol_mail.html", "pol_sms.txt"])
        self.assertEqual(wspolne.czytaj_tekst(os.path.join(folder, "pol_mail.html")),
                         "<p>Dziękujemy, zamówienie [iai:order_sn] przyjęte.</p>")
        meta = wspolne.czytaj_json(os.path.join(folder, "meta.json"))
        self.assertEqual(meta["tytuly"]["eng"], "[iai:shop_name] – Zamówienie nr [iai:order_sn]")
        self.assertEqual(meta["shop_id"], 1)
        self.assertTrue(os.path.exists(os.path.join(cel, "manifest.json")))

    def test_icf_zapisany_bez_zmian(self):
        m = fixtures.manifest(jezyki=("pol",))
        xml = fixtures.icf_xml().replace("\n", "\r\n")
        sc = m["wiadomosci"][0]["pliki"]["pol"]
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m, pliki={sc: xml})], os.path.join(self.k, "out"))
        self.assertEqual(wspolne.czytaj_tekst(os.path.join(cel, "order_confirmation", "pol.icf")), xml)

    def test_bez_sms_brak_pliku_sms(self):
        m = fixtures.manifest(jezyki=("pol",))
        sc = m["wiadomosci"][0]["pliki"]["pol"]
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m, pliki={sc: fixtures.icf_xml(z_sms=False)})], os.path.join(self.k, "o"))
        self.assertFalse(os.path.exists(os.path.join(cel, "order_confirmation", "pol_sms.txt")))

    def test_wycofywana_bez_folderu(self):
        m = fixtures.manifest(wiadomosci=[fixtures.wiadomosc(template="old", edytowalna=False)])
        cel, man = eksport.rozpakuj([_zip_z(self.k, m)], os.path.join(self.k, "out"))
        self.assertFalse(os.path.exists(os.path.join(cel, "old")))
        self.assertEqual(man["wiadomosci"][0]["template"], "old")

    def test_odmawia_nadpisania_edytowanego_eksportu(self):
        m = fixtures.manifest()
        z = _zip_z(self.k, m)
        cel = os.path.join(self.k, "out")
        eksport.rozpakuj([z], cel)
        with self.assertRaises(eksport.BladEksportu):
            eksport.rozpakuj([z], cel)
        eksport.rozpakuj([z], cel, nadpisz=True)   # świadome nadpisanie działa

    def test_brakujacy_plik_i_zly_icf_do_bledow(self):
        m = fixtures.manifest(jezyki=("pol", "eng"))
        w = m["wiadomosci"][0]
        cel, man = eksport.rozpakuj([_zip_z(self.k, m, pliki={w["pliki"]["pol"]: "<html>Logowanie</html>"})],
                                    os.path.join(self.k, "out"))
        bledy = man["wiadomosci"][0]["bledy"]
        self.assertEqual(len(bledy), 2)
        self.assertTrue(any(b.startswith("pol:") for b in bledy))
        self.assertTrue(any(b.startswith("eng:") for b in bledy))

    def test_zip_bez_manifestu(self):
        import zipfile
        z = os.path.join(self.k, "x.zip")
        with zipfile.ZipFile(z, "w") as a:
            a.writestr("cos.txt", "x")
        with self.assertRaises(eksport.BladEksportu):
            eksport.rozpakuj([z], os.path.join(self.k, "out"))

    def test_scalanie_czesciowych(self):
        w1 = fixtures.wiadomosc(template="a")
        w2 = fixtures.wiadomosc(template="b")
        m1 = fixtures.manifest(wiadomosci=[w1])
        m1["niekompletny"], m1["pozostale"] = True, ["b"]
        m2 = fixtures.manifest(wiadomosci=[w2])
        m2["data_eksportu"] = "2026-10-13T14:00:00"
        cel, man = eksport.rozpakuj([_zip_z(self.k, m1, "1.zip"), _zip_z(self.k, m2, "2.zip")], os.path.join(self.k, "o"))
        self.assertEqual([w["template"] for w in man["wiadomosci"]], ["a", "b"])
        self.assertFalse(man["niekompletny"])
        self.assertEqual(man["data_eksportu"], "2026-10-13T13:05:09")

    def test_scalanie_roznych_sklepow(self):
        m1 = fixtures.manifest()
        m2 = fixtures.manifest()
        m2["shop_id"] = 2
        with self.assertRaises(eksport.BladEksportu):
            eksport.rozpakuj([_zip_z(self.k, m1, "1.zip"), _zip_z(self.k, m2, "2.zip")], os.path.join(self.k, "o"))

    @unittest.skipUnless(os.name == "nt", "limit 260 znaków dotyczy Windows")
    def test_dluga_sciezka_bez_winerror_206(self):
        # Przypadek alpha-teile: głęboki folder programu + długi template przekraczały 260 znaków.
        baza = os.path.join(self.k, *(["folder_programu_na_pulpicie_" + str(i) for i in range(6)]))
        self.assertGreater(len(baza), 200)
        w = fixtures.wiadomosc(template="order_confirmation_request_wholesale_from_panel", jezyki=("pol",))
        m = fixtures.manifest(wiadomosci=[w], jezyki=("pol",))
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m)], wspolne.dluga_sciezka(baza))
        folder = eksport.folder_wiadomosci(cel, w)
        self.assertGreater(len(wspolne.pokaz(os.path.join(folder, "pol_mail.html"))), 260)
        self.assertTrue(os.path.exists(os.path.join(folder, "pol_mail.html")))
        # TemporaryDirectory.cleanup sam nie usunie ścieżek > 260 znaków.
        shutil.rmtree(wspolne.dluga_sciezka(os.path.join(self.k, "folder_programu_na_pulpicie_0")))

    def test_stary_uklad_folderu_nadal_czytany(self):
        m = fixtures.manifest(jezyki=("pol",))
        w = m["wiadomosci"][0]
        stary = os.path.join(self.k, "stary", "make_order__order_confirmation")
        os.makedirs(stary)
        self.assertEqual(eksport.folder_wiadomosci(os.path.join(self.k, "stary"), w), stary)
        self.assertEqual(eksport.folder_wiadomosci(os.path.join(self.k, "nowy"), w),
                         os.path.join(self.k, "nowy", "order_confirmation"))

    def test_katalog_domyslny(self):
        self.assertEqual(eksport.katalog_eksportu(fixtures.manifest()),
                         os.path.join(wspolne.FOLDER_TRESCI, "zooart6_shop1", "2026-10-13_130509"))


if __name__ == "__main__":
    unittest.main()
