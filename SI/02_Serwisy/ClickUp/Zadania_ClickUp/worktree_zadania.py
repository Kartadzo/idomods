"""Worktree dla zadań z /zadanie: osobna kopia robocza gałęzi w Domino/.worktrees/<temat>.

Polecenia:
  utworz <temat>          worktree z origin/main na nowej gałęzi <temat> + pliki, których git nie przenosi
  lista                   worktree w .worktrees: gałąź, scalona z main?, zmiany, ostatni commit
  dolacz <temat> <ścieżka> [--utworz]   dowiązanie folderu z Domino do istniejącego worktree
  usun <temat> [--sila]   usuwa dowiązania, worktree i gałąź lokalną (tylko scaloną, bez zmian i bez danych lokalnych)

Bez argumentów: menu. Kody wyjścia: 0 OK, 1 odmowa/problem, 2 błąd wejścia.
Analiza i decyzje: ANALIZA_worktree_zadanie.md (ten folder).
"""
import argparse
import glob
import os
import re
import shutil
import stat
import subprocess
import sys

FOLDER_WT = ".worktrees"
# Pliki kopiowane z Domino (decyzja 2026-11-10: kopia .gitignore, nie wspólny exclude).
KOPIE = [".gitignore", os.path.join(".claude", "settings.local.json")]
# Foldery tylko lokalne, wspólne dla wszystkich kopii: dowiązanie (junction) do Domino.
DOWIAZANIA_FOLDEROW = [os.path.join("SI", "Klienci")]
DOWIAZANIA_WZORCE = [
    os.path.join("SI", "02_Serwisy", "IdoSell", "Zmiany_sterownikow", "*", "_historia", "kopie"),
    os.path.join("SI", "02_Serwisy", "IdoSell", "Zmiany_sterownikow", "*", "_historia", "_robocze"),
]
# Pliki z kluczami: twarde dowiązanie (ten sam plik, bez kopii klucza).
PLIKI_KLUCZY = "config.json"


def git(*args, cwd=None, sprawdz=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if sprawdz and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout.strip()


def korzen_repo():
    """Główny folder repozytorium (Domino), także gdy skrypt działa z worktree."""
    tu = os.path.dirname(os.path.abspath(__file__))
    wspolny = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=tu)
    return os.path.dirname(os.path.normpath(wspolny))


def jest_dowiazaniem(sciezka):
    try:
        return bool(os.lstat(sciezka).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (OSError, AttributeError):
        return False


def utworz_dowiazanie_folderu(link, cel):
    os.makedirs(os.path.dirname(link), exist_ok=True)
    try:
        import _winapi
        _winapi.CreateJunction(cel, link)
    except (ImportError, AttributeError, OSError):
        r = subprocess.run(["cmd", "/c", "mklink", "/J", link, cel], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"mklink /J {link}: {r.stderr.strip() or r.stdout.strip()}")


def sprawdz_temat(temat):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,60}", temat or ""):
        raise ValueError("temat: ASCII, cyfry, _ . -, bez spacji (np. migracja_opinii_lauramessi)")


def lista_dolaczen(korzen, wt):
    """(link w worktree, cel w Domino, rodzaj) dla wszystkiego, czego git nie przenosi."""
    wynik = []
    for p in KOPIE:
        if os.path.isfile(os.path.join(korzen, p)):
            wynik.append((os.path.join(wt, p), os.path.join(korzen, p), "kopia"))
    for p in DOWIAZANIA_FOLDEROW:
        if os.path.isdir(os.path.join(korzen, p)):
            wynik.append((os.path.join(wt, p), os.path.join(korzen, p), "folder"))
    for wz in DOWIAZANIA_WZORCE:
        for cel in glob.glob(os.path.join(korzen, wz)):
            if os.path.isdir(cel):
                wzgl = os.path.relpath(cel, korzen)
                wynik.append((os.path.join(wt, wzgl), cel, "folder"))
    for cel in glob.glob(os.path.join(korzen, "SI", "**", PLIKI_KLUCZY), recursive=True):
        wzgl = os.path.relpath(cel, korzen)
        if wzgl.startswith(FOLDER_WT) or os.sep + "node_modules" + os.sep in wzgl:
            continue
        wynik.append((os.path.join(wt, wzgl), cel, "plik"))
    return wynik


def dowiazania_w(wt):
    """Wszystkie junction w worktree (bez wchodzenia do nich)."""
    wynik = []
    for katalog, podkatalogi, _ in os.walk(wt):
        for p in list(podkatalogi):
            s = os.path.join(katalog, p)
            if jest_dowiazaniem(s):
                wynik.append(s)
                podkatalogi.remove(p)
            elif p == ".git":
                podkatalogi.remove(p)
    return wynik


def utworz(temat, dolacz=()):
    sprawdz_temat(temat)
    korzen = korzen_repo()
    for p in dolacz:
        if not os.path.exists(os.path.join(korzen, p)):
            print(f"BŁĄD: --dolacz {p}: brak w Domino")
            return 2
    wt = os.path.join(korzen, FOLDER_WT, temat)
    if os.path.exists(wt):
        print(f"BŁĄD: folder już istnieje: {wt}")
        return 1
    if git("branch", "--list", temat, cwd=korzen):
        print(f"BŁĄD: gałąź {temat} już istnieje (wybierz inny temat albo usuń starą)")
        return 1
    if not os.path.isfile(os.path.join(korzen, ".gitignore")):
        print("BŁĄD: brak Domino/.gitignore - bez reguł ignorowania worktree wciągnąłby feedy i klucze")
        return 1
    git("fetch", "origin", cwd=korzen)
    lokalny = git("rev-parse", "main", cwd=korzen)
    zdalny = git("rev-parse", "origin/main", cwd=korzen)
    if lokalny != zdalny:
        print("UWAGA: lokalny main różni się od origin/main; worktree startuje z origin/main.")
    git("worktree", "add", "-b", temat, wt, "origin/main", cwd=korzen)
    git("branch", "--unset-upstream", temat, cwd=korzen, sprawdz=False)
    bledy = []
    dodatkowe = []
    for p in dolacz:
        cel = os.path.join(korzen, os.path.normpath(p))
        dodatkowe.append((os.path.join(wt, os.path.normpath(p)), cel, "folder" if os.path.isdir(cel) else "plik"))
    for link, cel, rodzaj in lista_dolaczen(korzen, wt) + dodatkowe:
        try:
            if rodzaj == "folder" and os.path.isdir(link) and not jest_dowiazaniem(link):
                # Folder częściowo śledzony (np. raporty/ z README): brakujące pliki jako twarde dowiązania.
                n = 0
                for kat, _, pliki in os.walk(cel):
                    for nazwa in pliki:
                        zrodlo = os.path.join(kat, nazwa)
                        docel = os.path.join(link, os.path.relpath(zrodlo, cel))
                        if not os.path.lexists(docel):
                            os.makedirs(os.path.dirname(docel), exist_ok=True)
                            os.link(zrodlo, docel)
                            n += 1
                print(f"Dołączono {n} plików do {os.path.relpath(link, wt)} (twarde dowiązania)")
                continue
            if os.path.lexists(link):
                bledy.append(f"{os.path.relpath(link, wt)}: już istnieje w gałęzi, pominięte")
                continue
            os.makedirs(os.path.dirname(link), exist_ok=True)
            if rodzaj == "kopia":
                shutil.copy2(cel, link)
            elif rodzaj == "folder":
                utworz_dowiazanie_folderu(link, cel)
            else:
                os.link(cel, link)
        except (OSError, RuntimeError) as e:
            bledy.append(f"{os.path.relpath(link, wt)}: {e}")
    brudne = git("status", "--porcelain", cwd=wt)
    print(f"Worktree: {wt}")
    print(f"Gałąź: {temat} (z origin/main)")
    for b in bledy:
        print(f"UWAGA: {b}")
    if brudne:
        print("BŁĄD: git status w worktree nie jest czysty (sprawdź .gitignore):")
        print(brudne)
        return 1
    print("git status: czysto")
    return 1 if bledy else 0


def dolacz_pozniej(temat, sciezka, utworz_w_domino=False):
    """Dołącza folder z Domino do istniejącego worktree (np. _historia/kopie nowego klienta)."""
    sprawdz_temat(temat)
    korzen = korzen_repo()
    wt = os.path.join(korzen, FOLDER_WT, temat)
    if os.path.normcase(os.path.normpath(wt)) not in {os.path.normcase(s) for s, _ in worktree_zadan(korzen)}:
        print(f"BŁĄD: {wt} nie jest zarejestrowanym worktree")
        return 1
    cel = os.path.join(korzen, os.path.normpath(sciezka))
    link = os.path.join(wt, os.path.normpath(sciezka))
    if not os.path.isdir(cel):
        if not utworz_w_domino:
            print(f"BŁĄD: brak folderu w Domino: {cel} (dodaj --utworz)")
            return 1
        os.makedirs(cel)
    if jest_dowiazaniem(link):
        print(f"Już dołączone: {sciezka}")
        return 0
    if os.path.isdir(link):
        if os.listdir(link):
            print(f"ODMOWA: {link} istnieje i nie jest pusty; przenieś pliki do {cel} i powtórz")
            return 1
        os.rmdir(link)
    utworz_dowiazanie_folderu(link, cel)
    print(f"Dołączono {sciezka} → {cel}")
    return 0


def worktree_zadan(korzen):
    """Lista (ścieżka, gałąź) worktree w .worktrees."""
    wynik, sciezka = [], None
    for linia in git("worktree", "list", "--porcelain", cwd=korzen).splitlines():
        if linia.startswith("worktree "):
            sciezka = os.path.normpath(linia[9:])
        elif linia.startswith("branch ") and sciezka:
            galaz = linia[7:].replace("refs/heads/", "")
            if os.path.normpath(os.path.join(korzen, FOLDER_WT)) in sciezka:
                wynik.append((sciezka, galaz))
    return wynik


def scalona(korzen, galaz):
    git("fetch", "origin", cwd=korzen, sprawdz=False)
    r = subprocess.run(["git", "merge-base", "--is-ancestor", galaz, "origin/main"], cwd=korzen)
    return r.returncode == 0


def lista():
    korzen = korzen_repo()
    wt = worktree_zadan(korzen)
    if not wt:
        print("Brak worktree zadań w .worktrees.")
        return 0
    for sciezka, galaz in wt:
        zmiany = git("status", "--porcelain", cwd=sciezka, sprawdz=False)
        ostatni = git("log", "-1", "--format=%cd %s", "--date=format:%Y-%m-%d %H:%M", galaz, cwd=korzen)
        if git("rev-parse", galaz, cwd=korzen) == git("rev-parse", "origin/main", cwd=korzen):
            stan = "bez commitów (praca nie zaczęta albo niezapisana)"
        elif scalona(korzen, galaz):
            stan = "SCALONA z main (do usunięcia)"
        else:
            stan = "niescalona"
        print(f"{galaz}: {stan}; zmiany: {len(zmiany.splitlines()) if zmiany else 0}; ostatni commit: {ostatni}")
        print(f"   {sciezka}")
    return 0


def dane_lokalne(korzen, wt):
    """Ignorowane pliki w worktree poza dołączonymi z Domino (np. wyniki/ powstałe w zadaniu).
    Dołączone = junction (cały folder) albo plik z twardym dowiązaniem lub skopiowany z KOPIE."""
    junction = [os.path.normcase(j) for j in dowiazania_w(wt)]
    kopie = {os.path.normcase(os.path.join(wt, p)) for p in KOPIE}
    wynik = []
    for linia in git("status", "--porcelain", "--ignored", "--untracked-files=all", cwd=wt).splitlines():
        if not linia.startswith("!! "):
            continue
        sciezka = os.path.normpath(os.path.join(wt, linia[3:].strip().strip('"')))
        klucz = os.path.normcase(sciezka.rstrip(os.sep))
        if klucz in kopie or any(klucz == j or klucz.startswith(j + os.sep) for j in junction):
            continue
        if "__pycache__" in sciezka or os.path.basename(sciezka) == "node_modules":
            continue
        try:
            if os.path.isfile(sciezka) and os.stat(sciezka).st_nlink > 1:
                continue
        except OSError:
            pass
        wynik.append(os.path.relpath(sciezka, wt))
    return wynik


def usun(temat, sila=False):
    sprawdz_temat(temat)
    korzen = korzen_repo()
    wt = os.path.join(korzen, FOLDER_WT, temat)
    zarejestrowane = {os.path.normcase(s) for s, _ in worktree_zadan(korzen)}
    if os.path.normcase(os.path.normpath(wt)) not in zarejestrowane:
        # Zwykły folder bez worktree: git -C trafiłby do repozytorium Domino.
        print(f"BŁĄD: {wt} nie jest zarejestrowanym worktree (git worktree list); nic nie robię")
        return 1
    if os.path.normcase(os.getcwd()).startswith(os.path.normcase(wt)):
        print("BŁĄD: uruchom z Domino, nie z folderu usuwanego worktree")
        return 1
    zmiany = git("status", "--porcelain", cwd=wt)
    if zmiany:
        print("ODMOWA: w worktree są niezapisane zmiany (najpierw /zapisz albo /zamknij):")
        print(zmiany)
        return 1
    if not scalona(korzen, temat) and not sila:
        print(f"ODMOWA: gałąź {temat} nie jest scalona z origin/main (najpierw /zamknij; --sila tylko świadomie)")
        return 1
    lokalne = dane_lokalne(korzen, wt)
    if lokalne and not sila:
        print("ODMOWA: w worktree są pliki tylko lokalne (ignorowane), zniknęłyby razem z folderem:")
        for p in lokalne[:30]:
            print(f"   {p}")
        print("Przenieś je do Domino albo uruchom z --sila.")
        return 1
    # Najpierw wszystkie junction: usunięcie worktree z --force nie może wejść do folderów Domino.
    # Twarde dowiązania plików są bezpieczne (usunięcie kasuje tylko dowiązanie).
    for link in dowiazania_w(wt):
        try:
            os.rmdir(link)
        except OSError as e:
            print(f"BŁĄD: nie udało się usunąć dowiązania {link}: {e}; przerwane")
            return 1
    if dowiazania_w(wt):
        print("BŁĄD: w worktree zostały dowiązania; przerwane")
        return 1
    try:
        git("worktree", "remove", "--force", wt, cwd=korzen)
    except RuntimeError as e:
        print(f"BŁĄD: {e}")
        print("Najczęściej folder jest otwarty: zamknij okno VS Code / terminal tego zadania i powtórz.")
        return 1
    tryb = "-D" if sila else "-d"
    r = subprocess.run(["git", "branch", tryb, temat], cwd=korzen, capture_output=True, text=True)
    print(f"Usunięto worktree {wt}")
    print(f"Gałąź lokalna {temat}: {'usunięta' if r.returncode == 0 else r.stderr.strip()} (origin bez zmian)")
    return 0


def menu():
    print("Worktree zadań /zadanie\n  1 lista\n  2 utwórz\n  3 usuń\n")
    wybor = input("Wybór: ").strip()
    if wybor == "1":
        return lista()
    if wybor in ("2", "3"):
        temat = input("Temat (nazwa gałęzi): ").strip()
        return utworz(temat) if wybor == "2" else usun(temat)
    print("Nieznany wybór.")
    return 2


def main():
    if len(sys.argv) == 1:
        return menu()
    p = argparse.ArgumentParser(description="Worktree dla zadań z /zadanie")
    sp = p.add_subparsers(dest="cmd", required=True)
    ut = sp.add_parser("utworz")
    ut.add_argument("temat")
    ut.add_argument("--dolacz", action="append", default=[], metavar="ŚCIEŻKA",
                    help="dane lokalne projektu z Domino (folder → junction, plik → twarde dowiązanie); można powtarzać")
    sp.add_parser("lista")
    d = sp.add_parser("dolacz")
    d.add_argument("temat")
    d.add_argument("sciezka")
    d.add_argument("--utworz", action="store_true", help="załóż folder w Domino, jeśli go nie ma")
    u = sp.add_parser("usun")
    u.add_argument("temat")
    u.add_argument("--sila", action="store_true", help="także niescalona gałąź / pliki tylko lokalne")
    a = p.parse_args()
    try:
        if a.cmd == "utworz":
            return utworz(a.temat, a.dolacz)
        if a.cmd == "lista":
            return lista()
        if a.cmd == "dolacz":
            return dolacz_pozniej(a.temat, a.sciezka, a.utworz)
        return usun(a.temat, a.sila)
    except ValueError as e:
        print(f"BŁĄD: {e}")
        return 2
    except RuntimeError as e:
        print(f"BŁĄD: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
