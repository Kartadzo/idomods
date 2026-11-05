import os
import subprocess
import sys
import unittest
import urllib.parse

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRYPT = os.path.join(KATALOG, "przegladarka", "zbuduj_bookmarklet.py")


class TestBookmarklet(unittest.TestCase):
    def test_budowanie(self):
        r = subprocess.run([sys.executable, SKRYPT], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(KATALOG, "przegladarka", "bookmarklet.txt"), encoding="utf-8") as p:
            zakladka = p.read().strip()
        self.assertTrue(zakladka.startswith("javascript:"))
        kod = urllib.parse.unquote(zakladka[len("javascript:"):])
        self.assertIn("WT.eksportuj", kod)
        self.assertIn("WTUI.pokaz()", kod)
        self.assertNotIn("module.exports = WT;\n  else", kod.replace("\r", ""))   # wariant przeglądarkowy
        with open(os.path.join(KATALOG, "przegladarka", "konsola.js"), encoding="utf-8") as p:
            self.assertIn("WTUI.pokaz()", p.read())
        node = subprocess.run(["node", "--check", os.path.join(KATALOG, "przegladarka", "konsola.js")],
                              capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stderr)


if __name__ == "__main__":
    unittest.main()
