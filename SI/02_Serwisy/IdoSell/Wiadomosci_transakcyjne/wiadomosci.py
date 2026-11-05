"""Wiadomości transakcyjne IdoSell - praca na plikach eksportu.

Uruchom bez argumentów (albo dwuklikiem run_wiadomosci.bat), żeby dostać menu.
Skróty: rozpakuj <zip>... | status <katalog> | konfiguracja <katalog> | zmiany <katalog> [csv]
        | tresci <katalog> | weryfikuj <katalog_planu> <zip>     (+ --tak = bez pytań o potwierdzenie)
"""

import glob
import os
import sys
import tempfile

from wt import eksport, icf, konfiguracja, status, tresci, weryfikacja, wspolne

POTWIERDZAJ = "--tak" not in sys.argv


class BladUzycia(Exception):
    pass


def pytaj_tak(pytanie: str) -> bool:
    if not POTWIERDZAJ:
        return True
    return input(pytanie + " [t/N]: ").strip().lower() in ("t", "tak", "y")


def wybierz(opcje, opis, wiele=False):
    if not opcje:
        print("Brak: " + opis)
        return [] if wiele else None
    for nr, (etykieta, _) in enumerate(opcje, start=1):
        print("  %d) %s" % (nr, etykieta))
    odp = input("%s (numer%s, Enter = anuluj): " % (opis, "y po przecinku" if wiele else "")).strip()
    try:
        numery = [int(x) for x in odp.split(",") if x.strip()]
        wybrane = [opcje[n - 1][1] for n in numery if 1 <= n <= len(opcje)]
    except ValueError:
        wybrane = []
    if wiele:
        return wybrane
    return wybrane[0] if wybrane else None


def eksporty():
    pliki = sorted(glob.glob(os.path.join(wspolne.FOLDER_TRESCI, "*", "*", "manifest.json")), reverse=True)
    return [(os.path.relpath(os.path.dirname(p), wspolne.FOLDER_TRESCI), os.path.dirname(p)) for p in pliki]


def zipy(przedrostek):
    """ZIP-y narzędzia: najpierw nowe z folderu pobierania Chrome, potem archiwum _pobrane w projekcie."""
    wynik = []
    for folder, etykieta in ((wspolne.FOLDER_POBIERANIE, "Pobrane"), (wspolne.FOLDER_POBRANE, "archiwum")):
        pliki = sorted(glob.glob(os.path.join(folder, przedrostek + "*.zip")), key=os.path.getmtime, reverse=True)
        wynik += [("[%s] %s" % (etykieta, os.path.basename(p)), p) for p in pliki]
    return wynik


def _manifest(katalog):
    if not os.path.exists(os.path.join(katalog, "manifest.json")):
        raise BladUzycia("W %s nie ma manifest.json - to nie jest rozpakowany eksport." % katalog)
    return eksport.wczytaj_eksport(katalog)


def cmd_rozpakuj(sciezki):
    for s in sciezki:
        eksport.wczytaj_zip(s)   # najpierw sprawdź, czy to eksport narzędzia - dopiero potem przenoś
    sciezki = [wspolne.przejmij(s) for s in sciezki]
    katalog, manifest = eksport.rozpakuj(sciezki)
    bledy = sum(len(w.get("bledy", [])) for w in manifest["wiadomosci"])
    print("[OK] Rozpakowano %d wiadomości do: %s" % (len(manifest["wiadomosci"]), wspolne.pokaz(katalog)))
    if bledy:
        print("[!] Błędów eksportu: %d - szczegóły w raporcie Status." % bledy)
    if manifest.get("niekompletny"):
        print("[!] Eksport niekompletny (brakuje %d wiadomości) - uruchom eksport ponownie i rozpakuj oba ZIP-y razem."
              % len(manifest["pozostale"]))
    return katalog


def cmd_status(katalog):
    manifest = _manifest(katalog)
    sciezka, sciezka_csv = status.zapisz_raport(manifest, katalog)
    problemy = status.kontrola(manifest, katalog)
    print("[OK] Raport Status: %s" % wspolne.pokaz(sciezka))
    print("     Tabela do Excela: %s" % wspolne.pokaz(sciezka_csv))
    print("     Wiadomości: %d, problemy kontroli jakości: %d" % (len(manifest["wiadomosci"]), len(problemy)))


def cmd_konfiguracja(katalog):
    manifest = _manifest(katalog)
    sciezka = konfiguracja.sciezka_csv(manifest)
    if os.path.exists(sciezka) and not pytaj_tak("Plik %s istnieje (może z Twoimi zmianami). Nadpisać?" % wspolne.pokaz(sciezka)):
        print("Anulowano.")
        return
    konfiguracja.zapisz_csv(manifest, sciezka)
    print("[OK] CSV konfiguracji: %s" % wspolne.pokaz(sciezka))
    print("     Zmień wartości tak/nie, zapisz (CSV UTF-8, średnik) i wybierz 'Zmiany konfiguracji'.")


def cmd_zmiany(katalog, sciezka_csv=None):
    manifest = _manifest(katalog)
    sciezka_csv = sciezka_csv or konfiguracja.sciezka_csv(manifest)
    zmiany, bledy = konfiguracja.roznice(manifest, sciezka_csv)
    for b in bledy:
        print("[!] " + b)
    if not zmiany:
        print("Brak zmian do wprowadzenia.")
        return 1 if bledy else 0
    stan = {w["template"]: w["formularz"] for w in manifest["wiadomosci"] if w.get("formularz")}
    print("Zmiany (%d wiadomości):" % len(zmiany))
    for z in zmiany:
        opisy = ["mail %s: %s -> %s" % (j, "tak" if stan[z["template"]]["mail"].get(j) == "y" else "nie",
                                        "tak" if f == "y" else "nie") for j, f in sorted(z["mail"].items())]
        if z["sms"] is not None:
            opisy.append("sms: %s -> %s" % ("tak" if stan[z["template"]]["sms"] == "y" else "nie", "tak" if z["sms"] == "y" else "nie"))
        if z["reset"]:
            opisy.append("RESET do treści domyślnej (krok ręczny w panelu)")
        print("  - %s (%s): %s" % (z["nazwa"], z["template"], "; ".join(opisy)))
    if bledy and not pytaj_tak("Są błędy w CSV (powyżej) - wiersze z błędami zostaną pominięte. Kontynuować?"):
        return 1
    if not pytaj_tak("Przygotować plan zmian?"):
        print("Anulowano.")
        return 0
    katalog_planu = os.path.join(wspolne.FOLDER_EDYCJA, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                                 "zmiany_" + wspolne.znacznik_daty(wspolne.teraz_iso()))
    sciezka = konfiguracja.zapisz_plan(manifest, katalog, zmiany, katalog_planu)
    print("[OK] Plan: %s" % wspolne.pokaz(sciezka))
    print("     Bookmarklet -> 'Zastosuj plan' -> wskaż folder %s" % wspolne.pokaz(katalog_planu))
    return 0


def cmd_tresci(katalog):
    manifest = _manifest(katalog)
    roznice = tresci.roznice_tresci(katalog, manifest)
    if not roznice:
        print("Brak zmian w plikach treści.")
        return
    print("Zmienione treści (%d):" % len(roznice))
    for r in roznice:
        print("  - %s (%s), %s: %s" % (r["nazwa"], r["template"], r["jezyk"], ", ".join(sorted(r["pola"]))))
    if not pytaj_tak("Złożyć ICF do importu?"):
        print("Anulowano.")
        return
    katalog_planu = os.path.join(katalog, "do_importu_" + wspolne.znacznik_daty(wspolne.teraz_iso()))
    sciezka = tresci.zloz(manifest, roznice, katalog_planu)
    print("[OK] Plan: %s" % wspolne.pokaz(sciezka))
    print("     Bookmarklet -> 'Zastosuj plan' -> wskaż folder %s" % wspolne.pokaz(katalog_planu))


def cmd_weryfikuj(katalog_planu, sciezka_zip):
    plany = [p for p in ("plan_importu.json", "plan_konfiguracji.json") if os.path.exists(os.path.join(katalog_planu, p))]
    if not plany:
        raise BladUzycia("W %s nie ma plan_importu.json ani plan_konfiguracji.json." % katalog_planu)
    plan = wspolne.czytaj_json(os.path.join(katalog_planu, plany[0]))
    eksport.wczytaj_zip(sciezka_zip)
    sciezka_zip = wspolne.przejmij(sciezka_zip)
    # Stan „po” tylko do porównania - w folderze tymczasowym, bo pod folderem planu ścieżki przekraczały 260 znaków.
    with tempfile.TemporaryDirectory(prefix="wt_po_", ignore_cleanup_errors=True) as tymczasowy:
        katalog_po, manifest_po = eksport.rozpakuj([sciezka_zip], wspolne.dluga_sciezka(tymczasowy), nadpisz=True)
        wyniki = weryfikacja.weryfikuj(plan, manifest_po, katalog_po)
    sciezka = os.path.join(katalog_planu, weryfikacja.nazwa_raportu(plan))
    wspolne.zapisz_tekst(sciezka, weryfikacja.raport(plan, wyniki))
    problemy = [w for w in wyniki if w["wynik"] != weryfikacja.OK]
    print("[OK] Raport weryfikacji: %s" % wspolne.pokaz(sciezka))
    print("     OK: %d, problemy: %d" % (len(wyniki) - len(problemy), len(problemy)))
    for w in problemy:
        print("  [!] %s (%s) %s %s: %s %s" % (w["nazwa"], w["template"], w["jezyk"], w["co"], w["wynik"], w["szczegoly"]))
    return 1 if problemy else 0


def cmd_edytor():
    import edytor_tresci   # tkinter ładowany dopiero na żądanie
    print("Otwieram edytor treści w osobnym oknie - menu wróci po jego zamknięciu.")
    edytor_tresci.main()


def plany():
    wzory = [os.path.join(wspolne.FOLDER_EDYCJA, "*", "zmiany_*"), os.path.join(wspolne.FOLDER_TRESCI, "*", "*", "do_importu_*")]
    katalogi = sorted([k for w in wzory for k in glob.glob(w) if os.path.isdir(k)], key=os.path.getmtime, reverse=True)
    return [(os.path.relpath(k, wspolne.KATALOG_GLOWNY), k) for k in katalogi]


class _Anulowano(Exception):
    pass


def _anuluj():
    raise _Anulowano()


def ostrzez_o_glebokim_folderze():
    katalog = wspolne.pokaz(wspolne.KATALOG_GLOWNY)
    if len(katalog) > wspolne.LIMIT_KATALOGU:
        print("[!] Folder programu leży głęboko (%d znaków): %s" % (len(katalog), katalog))
        print("    Program działa, ale przy sklepach z długimi nazwami wiadomości ścieżki plików mogą przekroczyć")
        print("    260 znaków i Notatnik, Eksplorator albo Chrome mogą ich nie otworzyć.")
        print("    Najlepiej przenieś cały folder bliżej dysku, np. do C:\\Wiadomosci_transakcyjne")


def menu():
    pozycje = [
        ("Rozpakuj eksport (z Pobranych)", lambda: cmd_rozpakuj(wybierz(zipy("eksport_"), "Które ZIP-y (części jednego eksportu)", wiele=True) or _anuluj())),
        ("Raport Status", lambda: cmd_status(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Edycja działania: utwórz CSV ze stanu", lambda: cmd_konfiguracja(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Edycja działania: różnice i plan zmian", lambda: cmd_zmiany(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Treści: różnice i ICF do importu", lambda: cmd_tresci(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Weryfikacja po wykonaniu planu", lambda: cmd_weryfikuj(wybierz(plany(), "Który plan") or _anuluj(),
                                                                 wybierz(zipy("weryfikacja_"), "Który ZIP weryfikacji") or _anuluj())),
        ("Edytor treści (okno: tytuły i treść maili, podgląd, usuwanie z importu)", cmd_edytor),
    ]
    ostrzez_o_glebokim_folderze()
    while True:
        print("\n=== Wiadomości transakcyjne IdoSell ===")
        for nr, (etykieta, _) in enumerate(pozycje, start=1):
            print("  %d) %s" % (nr, etykieta))
        print("  0) Wyjście")
        odp = input("Wybór: ").strip()
        if odp in ("0", ""):
            return
        if not odp.isdigit() or not 1 <= int(odp) <= len(pozycje):
            continue
        try:
            pozycje[int(odp) - 1][1]()
        except _Anulowano:
            print("Anulowano.")
        except (BladUzycia, eksport.BladEksportu, konfiguracja.BladKonfiguracji, icf.BladIcf, OSError) as blad:
            print("[BŁĄD] %s" % wspolne.pokaz(blad))


POLECENIA = {
    "rozpakuj": (lambda a: cmd_rozpakuj(a), 1, None),
    "status": (lambda a: cmd_status(a[0]), 1, 1),
    "konfiguracja": (lambda a: cmd_konfiguracja(a[0]), 1, 1),
    "zmiany": (lambda a: cmd_zmiany(a[0], a[1] if len(a) > 1 else None), 1, 2),
    "tresci": (lambda a: cmd_tresci(a[0]), 1, 1),
    "weryfikuj": (lambda a: cmd_weryfikuj(a[0], a[1]), 2, 2),
}


def main(argv):
    argumenty = [a for a in argv if a != "--tak"]
    if not argumenty:
        menu()
        return 0
    nazwa, reszta = argumenty[0], [wspolne.dluga_sciezka(a) for a in argumenty[1:]]   # wszystkie argumenty to ścieżki
    if nazwa not in POLECENIA:
        print(__doc__)
        return 2
    funkcja, minimum, maksimum = POLECENIA[nazwa]
    if len(reszta) < minimum or (maksimum is not None and len(reszta) > maksimum):
        print(__doc__)
        return 2
    try:
        wynik = funkcja(reszta)
        return wynik if isinstance(wynik, int) else 0
    except (BladUzycia, eksport.BladEksportu, konfiguracja.BladKonfiguracji, icf.BladIcf, OSError) as blad:
        print("[BŁĄD] %s" % wspolne.pokaz(blad))
        return 1


def main_exe(argv):
    """Jak main, ale w wersji .exe okno nie znika przy błędzie - użytkownik musi zobaczyć komunikat."""
    try:
        kod = main(argv)
    except Exception as blad:   # ostatnia linia obrony: nieoczekiwany błąd ma być widoczny, nie zamknąć okno
        print("[BŁĄD] Nieoczekiwany błąd programu: %s" % wspolne.pokaz(blad))
        kod = 1
    if getattr(sys, "frozen", False) and kod != 0:
        input("\nNaciśnij Enter, aby zamknąć okno...")
    return kod


if __name__ == "__main__":
    sys.exit(main_exe(sys.argv[1:]))
