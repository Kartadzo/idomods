# -*- coding: utf-8 -*-
"""
Zrzut ekranu okna Chrome do pliku PNG (zapas, gdy zrzut z rozszerzenia Claude in Chrome nie działa).

Użycie:
    python zrzut.py <fragment_tytułu_okna> <plik_wyjściowy.png> [--obszar strona] [--gora N]

- Okno szukane po fragmencie tytułu (bez rozróżniania wielkości liter). Najpewniej: przed zrzutem
  ustawić w karcie document.title = '[CLAUDE] ' + document.title i szukać fragmentu "[claude]".
- PrintWindow z flagą PW_RENDERFULLCONTENT — działa także, gdy okno jest zasłonięte (nie może być zminimalizowane).
- "--obszar strona" przycina pasek kart i adresu (górne ~ 88 px przy skali 100%).
- "--gora N" dodatkowo ucina N px od góry (pasek zakładek + baner „Klient Claude rozpoczął debugowanie”),
  domyślnie 98 przy "--obszar strona".
"""

import ctypes
import ctypes.wintypes as wt
import sys
from pathlib import Path

from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
user32.SetProcessDPIAware()

PW_RENDERFULLCONTENT = 2


def znajdz_okno(fragment):
    """Zwraca uchwyt pierwszego widocznego okna Chrome, którego tytuł zawiera fragment."""
    fragment = fragment.lower()
    wynik = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        dlugosc = user32.GetWindowTextLengthW(hwnd)
        bufor = ctypes.create_unicode_buffer(dlugosc + 1)
        user32.GetWindowTextW(hwnd, bufor, dlugosc + 1)
        tytul = bufor.value
        if "chrome" in tytul.lower() and fragment in tytul.lower():
            wynik.append((hwnd, tytul))
        return True

    user32.EnumWindows(callback, 0)
    return wynik[0] if wynik else (None, None)


def zrzut_okna(hwnd):
    prostokat = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(prostokat))
    szer = prostokat.right - prostokat.left
    wys = prostokat.bottom - prostokat.top

    hdc_okna = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_okna)
    bitmapa = gdi32.CreateCompatibleBitmap(hdc_okna, szer, wys)
    gdi32.SelectObject(hdc_mem, bitmapa)
    user32.PrintWindow(hwnd, hdc_mem, PW_RENDERFULLCONTENT)

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
            ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
            ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
            ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
        ]

    naglowek = BITMAPINFOHEADER()
    naglowek.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    naglowek.biWidth = szer
    naglowek.biHeight = -wys  # top-down
    naglowek.biPlanes = 1
    naglowek.biBitCount = 32
    bufor = ctypes.create_string_buffer(szer * wys * 4)
    gdi32.GetDIBits(hdc_mem, bitmapa, 0, wys, bufor, ctypes.byref(naglowek), 0)

    gdi32.DeleteObject(bitmapa)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_okna)
    return Image.frombuffer("RGB", (szer, wys), bufor, "raw", "BGRX", 0, 1)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    fragment, wyjscie = sys.argv[1], Path(sys.argv[2])
    tylko_strona = "--obszar" in sys.argv and sys.argv[sys.argv.index("--obszar") + 1] == "strona"
    gora_dodatkowo = int(sys.argv[sys.argv.index("--gora") + 1]) if "--gora" in sys.argv else (98 if tylko_strona else 0)

    hwnd, tytul = znajdz_okno(fragment)
    if not hwnd:
        print(f"Nie znaleziono okna Chrome z tytułem zawierającym: {fragment}")
        sys.exit(2)
    if user32.IsIconic(hwnd):
        print("Okno jest zminimalizowane — przywróć je i spróbuj ponownie.")
        sys.exit(3)

    obraz = zrzut_okna(hwnd)
    if tylko_strona:
        skala = user32.GetDpiForWindow(hwnd) / 96
        gora = int(88 * skala)
        ramka = int(8 * skala)
        obraz = obraz.crop((ramka, gora, obraz.width - ramka, obraz.height - ramka))
    if gora_dodatkowo:
        obraz = obraz.crop((0, gora_dodatkowo, obraz.width, obraz.height))

    wyjscie.parent.mkdir(parents=True, exist_ok=True)
    obraz.save(wyjscie)
    print(f"Zapisano: {wyjscie} ({obraz.width}x{obraz.height}) z okna: {tytul}")


if __name__ == "__main__":
    main()
