"""Wspólne pomocnicze: foldery trybów, identyfikator sklepu, zapis plików bez zmiany końców linii."""

import datetime
import json
import os
import re
import shutil
import sys
from typing import Any


def katalog_programu() -> str:
    """Folder narzędzia: obok pliku .exe (PyInstaller rozpakowuje moduły do katalogu tymczasowego) albo nad pakietem wt."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _folder_pobierania_windows() -> str:
    """Rzeczywisty folder Pobrane z Windows (Known Folder) - bywa przeniesiony, np. do OneDrive."""
    import ctypes
    from ctypes import wintypes
    import uuid

    class GUID(ctypes.Structure):
        _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

    u = uuid.UUID("{374DE290-123F-4565-9164-39C4925E467B}")   # FOLDERID_Downloads
    guid = GUID(u.time_low, u.time_mid, u.time_hi_version, (ctypes.c_ubyte * 8).from_buffer_copy(u.bytes[8:]))
    wskaznik = ctypes.c_wchar_p()
    if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(wskaznik)) != 0:
        raise OSError("SHGetKnownFolderPath nie zwrócił folderu Pobrane")
    try:
        return wskaznik.value
    finally:
        ctypes.windll.ole32.CoTaskMemFree(wskaznik)


def folder_pobierania() -> str:
    try:
        return _folder_pobierania_windows()
    except (OSError, AttributeError, ImportError):
        return os.path.join(os.path.expanduser("~"), "Downloads")


PRZEDROSTEK_DLUGI = "\\\\?\\"
# Powyżej tej długości folderu programu pliki eksportu sklepów z długimi nazwami wiadomości przekraczają
# 260 znaków - program sobie poradzi, ale Notatnik, Eksplorator i Chrome mogą ich nie otworzyć.
LIMIT_KATALOGU = 100


def dluga_sciezka(sciezka: str) -> str:
    r"""Ścieżka rozszerzona Windows (\\?\C:\...) - zapis i odczyt nie podlegają limitowi 260 znaków (WinError 206)."""
    if os.name != "nt":
        return sciezka
    pelna = os.path.abspath(sciezka)
    if pelna.startswith(PRZEDROSTEK_DLUGI):
        return pelna
    if pelna.startswith("\\\\"):
        return PRZEDROSTEK_DLUGI + "UNC\\" + pelna[2:]
    return PRZEDROSTEK_DLUGI + pelna


def pokaz(tekst: str) -> str:
    """Usuwa przedrostek ścieżki rozszerzonej z komunikatu dla użytkownika."""
    return str(tekst).replace(PRZEDROSTEK_DLUGI + "UNC\\", "\\\\").replace(PRZEDROSTEK_DLUGI, "")


# WT_KATALOG / WT_POBIERANIE pozwalają testom podmienić katalog roboczy i folder pobierania.
KATALOG_GLOWNY = dluga_sciezka(os.environ.get("WT_KATALOG") or katalog_programu())
# Folder pobierania Chrome - użytkownik nie musi zmieniać ustawień przeglądarki.
FOLDER_POBIERANIE = os.environ.get("WT_POBIERANIE") or folder_pobierania()
# Archiwum eksportów w projekcie - tu trafiają ZIP-y zabrane z folderu pobierania.
FOLDER_POBRANE = os.path.join(KATALOG_GLOWNY, "_pobrane")
FOLDER_STATUS = os.path.join(KATALOG_GLOWNY, "Status")
FOLDER_EDYCJA = os.path.join(KATALOG_GLOWNY, "Edycja Działania")
FOLDER_TRESCI = os.path.join(KATALOG_GLOWNY, "Eksport i Import Treści")


# Kody języków panelu IdoSell -> nazwy dla użytkownika (raport CSV, edytor treści).
NAZWY_JEZYKOW = {
    "pol": "polski", "eng": "angielski", "ger": "niemiecki", "cze": "czeski", "slo": "słowacki", "ukr": "ukraiński",
    "fre": "francuski", "ita": "włoski", "spa": "hiszpański", "rum": "rumuński", "hun": "węgierski", "lit": "litewski",
    "lav": "łotewski", "est": "estoński", "dut": "niderlandzki", "por": "portugalski", "swe": "szwedzki", "dan": "duński",
    "nor": "norweski", "fin": "fiński", "rus": "rosyjski", "bul": "bułgarski", "gre": "grecki", "scr": "chorwacki",
    "slv": "słoweński",
}


def nazwa_jezyka(kod: str) -> str:
    return NAZWY_JEZYKOW.get(kod, kod)


def id_sklepu(domena: str, shop_id: int) -> str:
    """'zooart6.yourtechnicaldomain.com', 1 -> 'zooart6_shop1'."""
    pierwszy = domena.strip().lower().split(".")[0]
    return re.sub(r"[^a-z0-9_-]", "_", pierwszy) + "_shop" + str(shop_id)


def znacznik_daty(iso: str) -> str:
    """'2026-10-13T13:05:09' -> '2026-10-13_130509' (bezpieczne w nazwach folderów)."""
    data, _, czas = iso.partition("T")
    return data + "_" + czas.replace(":", "")[:6]


def teraz_iso() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def przejmij(sciezka: str) -> str:
    """ZIP narzędzia leżący w folderze pobierania przenosi do archiwum projektu; inne ścieżki zwraca bez zmian."""
    nazwa = os.path.basename(sciezka)
    w_pobieraniu = (os.path.normcase(pokaz(os.path.dirname(os.path.abspath(sciezka))))
                    == os.path.normcase(pokaz(os.path.abspath(FOLDER_POBIERANIE))))
    if not w_pobieraniu or not re.match(r"^(eksport|weryfikacja)_.*\.zip$", nazwa):
        return sciezka
    os.makedirs(FOLDER_POBRANE, exist_ok=True)
    rdzen, rozszerzenie = os.path.splitext(nazwa)
    cel, nr = os.path.join(FOLDER_POBRANE, nazwa), 2
    while os.path.exists(cel):
        cel = os.path.join(FOLDER_POBRANE, "%s_%d%s" % (rdzen, nr, rozszerzenie))
        nr += 1
    shutil.move(sciezka, cel)
    return cel


def czytaj_tekst(sciezka: str) -> str:
    with open(sciezka, encoding="utf-8", newline="") as plik:
        return plik.read()


def zapisz_tekst(sciezka: str, tresc: str) -> None:
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8", newline="") as plik:
        plik.write(tresc)


def czytaj_json(sciezka: str) -> Any:
    # utf-8-sig: meta.json mógł zostać zapisany przez edytor „UTF-8 z BOM”.
    with open(sciezka, encoding="utf-8-sig") as plik:
        return json.load(plik)


def zapisz_json(sciezka: str, dane: Any) -> None:
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as plik:
        json.dump(dane, plik, ensure_ascii=False, indent=2)
