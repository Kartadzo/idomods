# -*- coding: utf-8 -*-
"""
Porównanie sterownika XSLT z panelu IdoSell z plikiem lokalnym w xslt/.

Krok stały każdej zmiany sterownika: zanim zmienię plik lokalny, sprawdzam,
czy odpowiada wersji z panelu. Panel czytam przez schowek (Claude in Chrome
zaznacza textarea[name=driver_body] i kopiuje Ctrl+C), a skrypt robi resztę:
normalizacja, werdykt, diff, a po potwierdzeniu przeniesienie starego pliku
do <kraj>/old/<nazwa>_<RRRR-MM-DD>.xml i zapis wersji z panelu.

Uruchomienie bez argumentów (dwuklik run_porownaj.bat) prowadzi przez menu:
klient -> plik lokalny -> źródło tekstu z panelu -> folder na diff -> podmiana.

Argumenty (wszystkie opcjonalne, pomijają odpowiednie pytanie):
  --lokalny <ścieżka>        plik lokalny sterownika
  --panel <ścieżka>          tekst z panelu z pliku (domyślnie: schowek)
  --folder-zadania <ścieżka> gdzie zapisać porownanie_*.diff (i .html)
  --zastap                   przy różnicy podmień bez pytania
  --bez-zmian                tylko porównanie, nigdy nie podmieniaj
  --html                     dodatkowo podgląd różnic w HTML
  --auto                     bez pytań (wymaga --lokalny; diff do wyniki/)

Kody wyjścia: 0 = zgodne (także poza białymi znakami), 1 = różne,
2 = błąd wejścia (brak pliku, w schowku nie ma sterownika).
"""

import argparse
import datetime
import difflib
import hashlib
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KATALOG_SKRYPTU = os.path.dirname(os.path.abspath(__file__))
ROZSZERZENIA = (".xml", ".xsl", ".xslt")
POMIJANE_W_XSLT = {"szablony", "backup", "iaiDownloader", "old"}
LIMIT_LINII_DIFFU_NA_EKRANIE = 60

ZGODNE = "ZGODNE"
ZGODNE_BIALE = "ZGODNE poza białymi znakami"
ROZNE = "RÓŻNE"


# ---------------------------------------------------------------- ścieżki

def znajdz_repo():
    """Katalog Domino: pierwszy przodek, który ma podfoldery xslt i SI."""
    sciezka = KATALOG_SKRYPTU
    while True:
        if os.path.isdir(os.path.join(sciezka, "xslt")) and os.path.isdir(os.path.join(sciezka, "SI")):
            return sciezka
        rodzic = os.path.dirname(sciezka)
        if rodzic == sciezka:
            return None
        sciezka = rodzic


def katalog_zmian_sterownikow():
    """SI/02_Serwisy/IdoSell/Zmiany_sterownikow (dwa poziomy nad skryptem)."""
    return os.path.dirname(os.path.dirname(KATALOG_SKRYPTU))


# ---------------------------------------------------------------- wejście

def czytaj_plik(sciezka):
    """Zwraca (tekst, bajty). Tekst bez dekodowania BOM-u (BOM usuwa normalizacja)."""
    with open(sciezka, "rb") as plik:
        surowe = plik.read()
    return surowe.decode("utf-8", errors="replace"), surowe


def czytaj_schowek():
    """Tekst ze schowka: najpierw tkinter, awaryjnie PowerShell Get-Clipboard."""
    try:
        import tkinter
        okno = tkinter.Tk()
        okno.withdraw()
        try:
            tekst = okno.clipboard_get()
        finally:
            okno.destroy()
        if tekst:
            return tekst
    except Exception:
        pass
    try:
        polecenie = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "Get-Clipboard -Raw"
        )
        wynik = subprocess.run(
            ["powershell", "-NoProfile", "-Command", polecenie],
            capture_output=True, timeout=30,
        )
        return wynik.stdout.decode("utf-8", errors="replace")
    except Exception:
        return ""


def wyglada_na_xslt(tekst):
    return "xsl:stylesheet" in tekst or "xsl:transform" in tekst


# ---------------------------------------------------------------- porównanie

def normalizuj(tekst, biale_znaki=True):
    """
    Lista linii do porównania: bez BOM, końce linii LF.
    biale_znaki=True dodatkowo obcina spacje/tabulatory na końcach linii
    i końcowe puste linie (tryb podstawowy, odporny na kopiowanie z panelu).
    """
    tekst = tekst.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    linie = tekst.split("\n")
    if biale_znaki:
        linie = [linia.rstrip(" \t") for linia in linie]
        while linie and linie[-1] == "":
            linie.pop()
    return linie


def skrot(linie):
    """SHA-256 znormalizowanego tekstu (linie złączone LF) — ten sam w JS panelu."""
    return hashlib.sha256("\n".join(linie).encode("utf-8")).hexdigest()


def porownaj(tekst_panel, tekst_lokalny):
    """Zwraca (werdykt, linie_panel, linie_lokalne) po normalizacji."""
    panel = normalizuj(tekst_panel)
    lokalny = normalizuj(tekst_lokalny)
    if panel == lokalny:
        surowe_rowne = normalizuj(tekst_panel, False) == normalizuj(tekst_lokalny, False)
        return (ZGODNE if surowe_rowne else ZGODNE_BIALE), panel, lokalny
    return ROZNE, panel, lokalny


def policz_zmiany(diff):
    dodane = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    usuniete = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    return dodane, usuniete


def koniec_linii(surowe):
    return "\r\n" if b"\r\n" in surowe else "\n"


# ---------------------------------------------------------------- menu

def wybierz(pytanie, pozycje, opis=lambda x: str(x)):
    """Numerowane menu, Enter = 1, jedna pozycja = bez pytania."""
    if not pozycje:
        return None
    if len(pozycje) == 1:
        print(f"{pytanie} {opis(pozycje[0])}")
        return pozycje[0]
    print(pytanie)
    for i, pozycja in enumerate(pozycje, 1):
        print(f"  {i:>3}. {opis(pozycja)}")
    while True:
        odpowiedz = input(f"Wybierz 1-{len(pozycje)} (Enter = 1): ").strip()
        if not odpowiedz:
            return pozycje[0]
        if odpowiedz.isdigit() and 1 <= int(odpowiedz) <= len(pozycje):
            return pozycje[int(odpowiedz) - 1]
        print("  Nieprawidłowy wybór.")


def tak_nie(pytanie, domyslnie=True):
    podpowiedz = "[T/n]" if domyslnie else "[t/N]"
    odpowiedz = input(f"{pytanie} {podpowiedz}: ").strip().lower()
    if not odpowiedz:
        return domyslnie
    return odpowiedz in ("t", "tak", "y", "yes")


def klienci_xslt(repo):
    """Foldery klientów: xslt/<grupa liter>/<klient>/."""
    wynik = []
    katalog = os.path.join(repo, "xslt")
    for grupa in sorted(os.listdir(katalog)):
        sciezka_grupy = os.path.join(katalog, grupa)
        if grupa in POMIJANE_W_XSLT or not os.path.isdir(sciezka_grupy):
            continue
        for klient in sorted(os.listdir(sciezka_grupy)):
            sciezka = os.path.join(sciezka_grupy, klient)
            if os.path.isdir(sciezka) and klient not in POMIJANE_W_XSLT:
                wynik.append(sciezka)
    return wynik


def pliki_sterownikow(katalog_klienta):
    """Pliki .xml/.xsl/.xslt klienta (rekurencyjnie), bez folderów old/."""
    wynik = []
    for korzen, katalogi, pliki in os.walk(katalog_klienta):
        katalogi[:] = sorted(k for k in katalogi if k not in POMIJANE_W_XSLT)
        for nazwa in sorted(pliki):
            sciezka = os.path.join(korzen, nazwa)
            if nazwa.lower().endswith(ROZSZERZENIA) and jest_sterownikiem(sciezka):
                wynik.append(sciezka)
    return wynik


def jest_sterownikiem(sciezka):
    """Odsiewa eksporty IOF i inne XML-e: XSLT w pierwszych 64 KB pliku."""
    try:
        with open(sciezka, "rb") as plik:
            poczatek = plik.read(65536).decode("utf-8", errors="replace")
    except OSError:
        return False
    return wyglada_na_xslt(poczatek)


def wybierz_plik_lokalny(repo):
    klienci = klienci_xslt(repo)
    while True:
        fraza = input("Fragment nazwy klienta (folder w xslt/, Enter = wszyscy): ").strip().lower()
        pasujacy = [k for k in klienci if fraza in os.path.basename(k).lower()]
        if pasujacy:
            break
        print("  Brak klienta pasującego do tej frazy.")
    klient = wybierz("Klient:", pasujacy, lambda k: os.path.relpath(k, os.path.join(repo, "xslt")))
    pliki = pliki_sterownikow(klient)
    if not pliki:
        print("Brak plików sterowników u tego klienta.")
        return None
    return wybierz("Plik lokalny:", pliki, lambda p: os.path.relpath(p, klient))


def wybierz_folder_zadania(sciezka_lokalna):
    """Podfoldery zadań klienta w Zmiany_sterownikow/<klient>/ (najnowsze najpierw) albo wyniki/."""
    klient = os.path.basename(os.path.dirname(os.path.dirname(sciezka_lokalna)))
    kandydaci = []
    for nazwa in (klient, os.path.basename(os.path.dirname(sciezka_lokalna))):
        katalog = os.path.join(katalog_zmian_sterownikow(), nazwa)
        if os.path.isdir(katalog):
            podfoldery = [os.path.join(katalog, p) for p in os.listdir(katalog)
                          if os.path.isdir(os.path.join(katalog, p))]
            kandydaci = sorted(podfoldery, key=os.path.getmtime, reverse=True)
            break
    kandydaci.append(os.path.join(KATALOG_SKRYPTU, "wyniki"))
    return wybierz("Gdzie zapisać diff:", kandydaci,
                   lambda p: os.path.relpath(p, katalog_zmian_sterownikow()))


# ---------------------------------------------------------------- zapis

def nazwa_w_old(sciezka_lokalna, data):
    katalog_old = os.path.join(os.path.dirname(sciezka_lokalna), "old")
    baza, rozszerzenie = os.path.splitext(os.path.basename(sciezka_lokalna))
    kandydat = os.path.join(katalog_old, f"{baza}_{data}{rozszerzenie}")
    numer = 2
    while os.path.exists(kandydat):
        kandydat = os.path.join(katalog_old, f"{baza}_{data}_{numer}{rozszerzenie}")
        numer += 1
    return kandydat


def zapisz_diff(folder, sciezka_lokalna, data, diff, linie_lokalne, linie_panel, html):
    os.makedirs(folder, exist_ok=True)
    baza = os.path.splitext(os.path.basename(sciezka_lokalna))[0]
    sciezka_diff = os.path.join(folder, f"porownanie_{baza}_{data}.diff")
    with open(sciezka_diff, "w", encoding="utf-8", newline="\n") as plik:
        plik.write("\n".join(diff) + "\n")
    sciezka_html = None
    if html:
        sciezka_html = os.path.join(folder, f"porownanie_{baza}_{data}.html")
        tresc = difflib.HtmlDiff(wrapcolumn=120).make_file(
            linie_lokalne, linie_panel, "lokalny", "panel", context=True, numlines=3)
        tresc = tresc.replace('charset=ISO-8859-1', 'charset=utf-8')
        with open(sciezka_html, "w", encoding="utf-8") as plik:
            plik.write(tresc)
    return sciezka_diff, sciezka_html


def podmien(sciezka_lokalna, tekst_panel, surowe_lokalne, data):
    """Stary plik -> old/<nazwa>_<data>.xml, wersja z panelu pod nazwą lokalną."""
    cel_old = nazwa_w_old(sciezka_lokalna, data)
    os.makedirs(os.path.dirname(cel_old), exist_ok=True)
    os.replace(sciezka_lokalna, cel_old)
    eol = koniec_linii(surowe_lokalne)
    linie = normalizuj(tekst_panel, biale_znaki=False)
    with open(sciezka_lokalna, "w", encoding="utf-8", newline="") as plik:
        plik.write(eol.join(linie))
    return cel_old


# ---------------------------------------------------------------- główna

def main():
    parser = argparse.ArgumentParser(description="Porównanie sterownika z panelu z plikiem lokalnym.")
    parser.add_argument("--lokalny")
    parser.add_argument("--panel")
    parser.add_argument("--folder-zadania")
    grupa = parser.add_mutually_exclusive_group()
    grupa.add_argument("--zastap", action="store_true")
    grupa.add_argument("--bez-zmian", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--auto", action="store_true")
    args = parser.parse_args()

    repo = znajdz_repo()
    if repo is None:
        print("BŁĄD: nie znaleziono katalogu repo (z folderami xslt i SI).")
        return 2

    # 1. Plik lokalny
    if args.lokalny:
        sciezka_lokalna = os.path.abspath(args.lokalny)
    elif args.auto:
        print("BŁĄD: tryb --auto wymaga --lokalny.")
        return 2
    else:
        sciezka_lokalna = wybierz_plik_lokalny(repo)
    if not sciezka_lokalna or not os.path.isfile(sciezka_lokalna):
        print(f"BŁĄD: brak pliku lokalnego: {sciezka_lokalna}")
        return 2

    # 2. Tekst z panelu
    if args.panel:
        if not os.path.isfile(args.panel):
            print(f"BŁĄD: brak pliku z tekstem panelu: {args.panel}")
            return 2
        tekst_panel, _ = czytaj_plik(args.panel)
        zrodlo = os.path.basename(args.panel)
    else:
        if not args.auto:
            input("Skopiuj sterownik z panelu do schowka i naciśnij Enter...")
        tekst_panel = czytaj_schowek()
        zrodlo = "schowek"
    if not wyglada_na_xslt(tekst_panel):
        print(f"BŁĄD: w źródle ({zrodlo}) nie ma sterownika XSLT (brak xsl:stylesheet).")
        return 2

    tekst_lokalny, surowe_lokalne = czytaj_plik(sciezka_lokalna)
    werdykt, linie_panel, linie_lokalne = porownaj(tekst_panel, tekst_lokalny)

    print()
    print(f"Plik lokalny: {os.path.relpath(sciezka_lokalna, repo)}")
    print(f"Panel:        {zrodlo}")
    print(f"SHA-256 panel:    {skrot(linie_panel)}  ({len(linie_panel)} linii)")
    print(f"SHA-256 lokalny:  {skrot(linie_lokalne)}  ({len(linie_lokalne)} linii)")
    print(f"Werdykt: {werdykt}")
    if werdykt != ROZNE:
        return 0

    # 3. Diff
    diff = list(difflib.unified_diff(linie_lokalne, linie_panel, "lokalny", "panel", lineterm=""))
    dodane, usuniete = policz_zmiany(diff)
    print(f"Różnice (panel względem lokalnego): +{dodane} / -{usuniete} linii")
    for linia in diff[:LIMIT_LINII_DIFFU_NA_EKRANIE]:
        print("  " + linia[:200])
    if len(diff) > LIMIT_LINII_DIFFU_NA_EKRANIE:
        print(f"  ... ({len(diff) - LIMIT_LINII_DIFFU_NA_EKRANIE} linii więcej w pliku .diff)")

    data = datetime.date.today().isoformat()
    if args.folder_zadania:
        folder = os.path.abspath(args.folder_zadania)
    elif args.auto:
        folder = os.path.join(KATALOG_SKRYPTU, "wyniki")
    else:
        folder = wybierz_folder_zadania(sciezka_lokalna)
    html = args.html or (not args.auto and tak_nie("Podgląd różnic w HTML?", False))
    sciezka_diff, sciezka_html = zapisz_diff(folder, sciezka_lokalna, data, diff,
                                             linie_lokalne, linie_panel, html)
    print(f"Diff: {sciezka_diff}")
    if sciezka_html:
        print(f"HTML: {sciezka_html}")

    # 4. Podmiana
    if args.bez_zmian:
        decyzja = False
    elif args.zastap:
        decyzja = True
    elif args.auto:
        decyzja = False
    else:
        decyzja = tak_nie("Przenieść plik lokalny do old/ i zapisać wersję z panelu?", True)
    if decyzja:
        cel_old = podmien(sciezka_lokalna, tekst_panel, surowe_lokalne, data)
        print(f"Stary plik: {os.path.relpath(cel_old, repo)}")
        print(f"Zapisano wersję z panelu: {os.path.relpath(sciezka_lokalna, repo)}")
    else:
        print("Plik lokalny bez zmian.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nPrzerwano.")
        sys.exit(2)
