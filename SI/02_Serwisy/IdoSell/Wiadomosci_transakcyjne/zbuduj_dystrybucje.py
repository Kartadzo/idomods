"""Buduje folder dystrybucyjny: 2 x .exe (program z menu + edytor treści w oknie, PyInstaller) + instrukcja + zakładka do Chrome + puste foldery na wyniki.

Uruchom: zbuduj_dystrybucje.bat (albo python zbuduj_dystrybucje.py). Wynik: dystrybucja\\Wiadomosci_transakcyjne\\
Istniejący folder dystrybucyjny jest uzupełniany (pliki programu podmieniane), nic nie jest kasowane.
"""

import os
import shutil
import subprocess
import sys

TU = os.path.dirname(os.path.abspath(__file__))
NAZWA_EXE = "Wiadomości transakcyjne"
NAZWA_EDYTORA = "Edytor treści"
CEL = os.path.join(TU, "dystrybucja", "Wiadomosci_transakcyjne")
ROBOCZY = os.path.join(TU, "dystrybucja", "_build")
FOLDERY_WYNIKOW = ("Status", "Edycja Działania", "Eksport i Import Treści", "_pobrane")


def uruchom(polecenie):
    print("> " + " ".join(polecenie))
    subprocess.run(polecenie, cwd=TU, check=True)


def main():
    uruchom([sys.executable, os.path.join("przegladarka", "zbuduj_bookmarklet.py")])
    for nazwa, tryb, skrypt in ((NAZWA_EXE, "--console", "wiadomosci.py"), (NAZWA_EDYTORA, "--windowed", "edytor_tresci.py")):
        uruchom([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", tryb, "--name", nazwa,
                 "--distpath", os.path.join(ROBOCZY, "dist"), "--workpath", os.path.join(ROBOCZY, "work", nazwa),
                 "--specpath", ROBOCZY, skrypt])
    os.makedirs(CEL, exist_ok=True)
    for nazwa in (NAZWA_EXE, NAZWA_EDYTORA):
        shutil.copy2(os.path.join(ROBOCZY, "dist", nazwa + ".exe"), os.path.join(CEL, nazwa + ".exe"))
    shutil.copy2(os.path.join(TU, "dokumentacja", "INSTRUKCJA.html"), os.path.join(CEL, "INSTRUKCJA.html"))
    shutil.copy2(os.path.join(TU, "przegladarka", "bookmarklet.txt"), os.path.join(CEL, "zakladka_do_Chrome.txt"))
    shutil.copy2(os.path.join(TU, "przegladarka", "konsola.js"), os.path.join(CEL, "konsola.js"))
    for folder in FOLDERY_WYNIKOW:
        os.makedirs(os.path.join(CEL, folder), exist_ok=True)
    print("\n[OK] Folder dystrybucyjny: %s" % CEL)
    for nazwa in sorted(os.listdir(CEL)):
        print("     " + nazwa)


if __name__ == "__main__":
    main()
