# -*- coding: utf-8 -*-
"""Budowa pliku wykonywalnego dla urządzeń bez Pythona.

    python build_exe.py

Efektem jest katalog `dystrybucja/` gotowy do skopiowania na pendrive: plik
`.exe`, katalog `structures/` (żeby dało się dodać własną strukturę bez
przebudowy) oraz instrukcja. Profile, ustawienia i sesja powstaną obok `.exe`
przy pierwszym uruchomieniu.

Wymaga PyInstallera:  pip install pyinstaller
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP_NAME = u"Edycja eksportu IdoSell"
ICON = os.path.join(HERE, "app.ico")
DIST = os.path.join(HERE, "dystrybucja")
WORK = os.path.join(HERE, "build")
SPEC = os.path.join(HERE, "build")

INSTRUKCJA = u"""EDYCJA EKSPORTU PRODUKTÓW IDOSELL
=================================

Uruchomienie
------------
Dwuklik w "{app}.exe". Python nie jest potrzebny - wszystko jest w środku.

Pierwsze uruchomienie trwa kilka sekund dłużej, bo program rozpakowuje się do
katalogu tymczasowego. Windows albo antywirus może zapytać, czy na pewno
uruchomić plik pobrany z innego komputera - to normalne dla programów bez
podpisu cyfrowego.

Co tu jest
----------
{app}.exe    sama aplikacja
structures\\           definicje struktur wyjściowych (pliki JSON)
README.md             pełna instrukcja obsługi

Co powstanie samo
-----------------
settings.json         ostatnio używany katalog i ustawienia okna
last_session.json     ustawienia z ostatniego zamknięcia - program pyta przy
                      starcie, czy je wczytać
profiles\\             zapisane profile (Plik > Zapisz profil)

Wszystkie te pliki tworzą się OBOK pliku .exe, więc trzymaj go w katalogu,
w którym masz prawo zapisu - nie w "Program Files".

Własne struktury
----------------
Katalog "structures" można edytować: każdy plik JSON to jedna pozycja na liście
struktur wyjściowych. Aplikacja czyta ten katalog przy starcie. Gdy go usuniesz,
program użyje kompletu wbudowanego w .exe.
""".format(app=APP_NAME)


def main():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "Brak PyInstallera. Zainstaluj go poleceniem:\n\n"
            "    pip install pyinstaller\n\n")
        return 2

    if not os.path.isfile(ICON):
        sys.stderr.write("Brak pliku app.ico obok build_exe.py.\n")
        return 2

    separator = ";" if os.name == "nt" else ":"
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile",                      # jeden plik do przeniesienia
        "--windowed",                     # bez okna konsoli
        "--name", APP_NAME,
        "--icon", ICON,
        # Ścieżki muszą być pełne: przy własnym --specpath PyInstaller liczy
        # względne od katalogu ze specem, nie od katalogu projektu.
        "--add-data", "%s%s." % (ICON, separator),
        "--add-data", "%s%sstructures" % (os.path.join(HERE, "structures"), separator),
        "--distpath", DIST,
        "--workpath", WORK,
        "--specpath", SPEC,
        os.path.join(HERE, "app.py"),
    ]
    print(u"Buduję %s.exe - to potrwa kilkadziesiąt sekund…" % APP_NAME)
    result = subprocess.call(command, cwd=HERE)
    if result != 0:
        sys.stderr.write("PyInstaller zakonczyl sie bledem %d.\n" % result)
        return result

    _copy_extras()
    exe = os.path.join(DIST, APP_NAME + ".exe")
    size = os.path.getsize(exe) / (1024.0 * 1024.0) if os.path.isfile(exe) else 0
    print(u"\nGotowe: %s  (%.1f MB)" % (exe, size))
    print(u"Cały katalog „dystrybucja” jest tym, co przenosisz na inne urządzenie.")
    return 0


def _copy_extras():
    """Do katalogu wynikowego trafia to, co ma być edytowalne albo czytane."""
    target = os.path.join(DIST, "structures")
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.copytree(os.path.join(HERE, "structures"), target,
                    ignore=shutil.ignore_patterns("__pycache__"))

    readme = os.path.join(HERE, "README.md")
    if os.path.isfile(readme):
        shutil.copy2(readme, os.path.join(DIST, "README.md"))

    with open(os.path.join(DIST, "JAK URUCHOMIC.txt"), "w",
              encoding="utf-8-sig") as handle:
        handle.write(INSTRUKCJA)


if __name__ == "__main__":
    sys.exit(main())
