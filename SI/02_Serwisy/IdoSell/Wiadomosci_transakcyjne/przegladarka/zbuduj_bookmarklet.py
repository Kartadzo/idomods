"""Skleja panel_core.js + bookmarklet_ui.js w zakładkę (bookmarklet.txt) i wariant do konsoli (konsola.js)."""

import os
import re
import urllib.parse

TU = os.path.dirname(os.path.abspath(__file__))


def czytaj(nazwa):
    with open(os.path.join(TU, nazwa), encoding="utf-8") as plik:
        return plik.read()


def main():
    rdzen = czytaj("panel_core.js")
    # W zakładce zawsze wariant przeglądarkowy: bez gałęzi module.exports.
    rdzen = re.sub(r"if \(typeof module !== 'undefined' && module\.exports\) module\.exports = WT;\s*else root\.WT = WT;",
                   "root.WT = WT;", rdzen)
    kod = rdzen + "\n" + czytaj("bookmarklet_ui.js") + "\nWTUI.pokaz();\n"
    with open(os.path.join(TU, "konsola.js"), "w", encoding="utf-8") as plik:
        plik.write(kod)
    zakladka = "javascript:" + urllib.parse.quote("(function(){" + kod + "})();", safe="")
    with open(os.path.join(TU, "bookmarklet.txt"), "w", encoding="utf-8") as plik:
        plik.write(zakladka + "\n")
    print("[OK] bookmarklet.txt (%d znaków) i konsola.js" % len(zakladka))


if __name__ == "__main__":
    main()
