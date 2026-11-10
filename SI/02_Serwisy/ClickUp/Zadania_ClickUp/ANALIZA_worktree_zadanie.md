# ANALIZA: osobne worktree dla kart z /zadanie

Data: 2026-11-10 · Dotyczy: skill `/zadanie`, `/zapisz`, `/zamknij`, `uruchom_sesje.bat`

## Cel
Karty Claude otwierane z `/zadanie` pracują dziś w jednym folderze `Domino`. Gałąź jest wspólna:
`git switch` albo `/zamknij` w jednej karcie zmienia pliki pod nogami pozostałych.
Chcemy, żeby każde zadanie „nowy problem” miało własną kopię roboczą na swojej gałęzi.
Wtedy karty mogą równolegle edytować pliki i robić commity.

Worktree rozwiązuje **tylko git i pliki**. Claude in Chrome, Chrome DevTools MCP, schowek
i port odbiornika 8765 dalej są wspólne. Zasada „jedno zadanie z przeglądarką naraz” zostaje.

## Co sprawdziłem (2026-11-10)
| Fakt | Znaczenie |
|---|---|
| `git worktree` = osobny folder z własną gałęzią, wspólne `.git` | historia (1 GB) się nie powiela; checkout plików śledzonych ≈ 72 MB na zadanie |
| W worktree są **tylko pliki śledzone** | brak `SI/Klienci/` (zasady klientów!), `config.json` z kluczami API, `dane/`, `wyniki/`, `_historia/kopie/`, `.claude/settings.local.json` (uprawnienia) i `node_modules/` |
| `.gitignore` ignoruje sam siebie (jest tylko lokalnie) | **w worktree nie ma żadnych reguł ignorowania**: `git add` wciągnąłby feedy, eksporty i tokeny. To największe ryzyko |
| `.git/info/exclude` jest wspólny dla wszystkich worktree | możliwe miejsce na reguły, ale sprzeczne z ustaleniem „reguły tylko w `Domino/.gitignore`” |
| Gałęzi `main` nie da się wyciągnąć w drugim worktree, póki jest w `Domino` | `/zamknij` w karcie zadania nie może zrobić `git switch main` |
| Claude Code 2.1.322 ma `claude -w <nazwa>` (tworzy worktree dla sesji) | działa w terminalu; link `vscode://anthropic.claude-code/open?prompt=` nie przyjmuje folderu, karta startuje w workspace |
| Pamięć Claude (`~/.claude/projects/<ścieżka>/memory`) zależy od ścieżki folderu | do sprawdzenia, czy sesja w worktree widzi pamięć `Domino`, czy dostaje pustą |

## Warianty
**A. Worktree zakładany przez `/zadanie` + uzupełnienie brakujących plików (rekomendacja)**
1. `git worktree add C:\Users\Admin\Desktop\Domino_wt\<temat> -b <temat> main`
   (folder obok `Domino`, nie w środku: inaczej `Domino` widziałby go jako nieśledzony folder).
2. Uzupełnienie tego, czego git nie przenosi:
   - `.gitignore`: kopia z `Domino` (albo twarde dowiązanie, żeby zmiana działała wszędzie);
   - `SI\Klienci`: dowiązanie folderu (`mklink /J`) do `Domino\SI\Klienci`, czyli jedna baza klientów, nie kopia;
   - `.claude\settings.local.json`: kopia;
   - `config.json` i `dane/`: tylko gdy zadanie ich potrzebuje, dowiązanie do folderu w `Domino`.
3. Start sesji w folderze worktree:
   - VS Code: `code -n <folder>` otwiera nowe okno, a w nim link z promptem (do przetestowania, czy karta trafia do nowego okna);
   - zapas: `uruchom_sesje.bat`, który już przyjmuje folder.
4. `/zapisz` w worktree działa bez zmian (commit i push gałęzi).
5. `/zamknij` w worktree: commit i push gałęzi, potem merge **w folderze `Domino`** (`git -C Domino merge --no-ff`).
   Warunek: `Domino` jest na `main`, a zmiany użytkownika nie kolidują. Po udanym pushu `git worktree remove` i usunięcie gałęzi lokalnej.

**B. `claude -w` (wbudowane w Claude Code)**
Mniej kodu, ale tylko w terminalu, nie w karcie VS Code. Brakujące pliki (`.gitignore`, `Klienci`) też trzeba uzupełnić.
Miejsce i nazwę worktree ustala Claude Code. Dobre jako zapas, gdy wariant A nie zadziała w VS Code.

**C. Bez worktree, tylko zasada**
Jedna karta naraz robi operacje git, pozostałe tylko pliki. Zero zmian, ale ryzyko zostaje i zależy od pamiętania.
Kłóci się z Twoim ustaleniem, żeby nie opierać procesu na pamiętaniu.

## Wpływ na istniejące narzędzia
- **Historia sterowników:** odbiornik zapisuje `_historia/` obok skryptu. Uruchomiony z worktree zapisałby kopie
  w folderze, który zniknie po `worktree remove`. Dlatego odbiornik zawsze uruchamiamy z `--baza` wskazującym `Domino`
  (albo zawsze z `Domino`). `dziennik_wdrozen.csv` i zrzut `.json` są śledzone, więc trafiają do commita gałęzi.
- **Skrypty z `config.json`** (`_wspolne/idosell_client.py`) szukają pliku względem `__file__`, więc w worktree potrzebne jest dowiązanie.
- **Wariant „skill” (`/weryfikacja-*`, `/summonfeed`)** zostaje w `Domino`: commituje rzadko i tylko wnioski. Worktree tylko dla „nowego problemu”.
- **Długie ścieżki:** `Domino_wt\<temat>` jest krótsze niż typowe ścieżki w `xslt/`, ale trzeba sprawdzić `core.longpaths` przy checkout.
- **Sprzątanie:** `git worktree list` w `/zamknij` i przy `/zadanie`; osierocone worktree (zamknięta karta bez `/zamknij`) zgłaszam, nie usuwam sam.

## Plan wdrożenia (po akceptacji)
1. Test ręczny na gałęzi testowej:
   - worktree, dowiązania;
   - `git status` z `.gitignore` (czy nie widać śmieci);
   - pamięć Claude w worktree;
   - `code -n` + link z promptem;
   - `/zapisz`, merge w `Domino`, `worktree remove`.
2. Skrypt `nowy_worktree.bat` / `.py` w `Zadania_ClickUp/`: krok 1–2 wariantu A, kod wyjścia, bez polskich znaków w `.bat`.
3. Zmiany skilli:
   - `/zadanie`: krok 6 „nowy problem” zakłada worktree zamiast `git switch -c`;
   - `/zamknij`: wykrywa worktree (`git rev-parse --git-common-dir`), robi merge w `Domino`, potem sprzątanie;
   - `/zapisz`: kontrola, że `.gitignore` jest w worktree.
4. Wpis w `SI/README.md` (zasada 10) i w `historia_sterownikow/README.md` (`--baza`).

## Założenia
- `Domino` zostaje na `main`, użytkownik pracuje tam w VS Code.
- Worktree tylko dla zadań „nowy problem”; zadania ze skillem zostają w `Domino`.
- Baza klientów jest jedna (dowiązanie), nie kopiujemy jej do worktree.

## Otwarte pytania
1. Reguły ignorowania w worktree: kopia `.gitignore` przy zakładaniu (zostaje zasada „tylko `Domino/.gitignore`”),
   czy przeniesienie ich do wspólnego `.git/info/exclude`? Rekomenduję kopię (twarde dowiązanie): nic nie zmienia w obecnej zasadzie.
2. Gdzie trzymać worktree: `C:\Users\Admin\Desktop\Domino_wt\` (obok projektu)? To poza folderem `Domino`,
   więc wymaga wyjątku w globalnej zasadzie „tylko w folderze projektu”. Alternatywa w środku: `Domino\.worktrees\` dopisane do `.gitignore`.
3. Czy nowe okno VS Code na zadanie Ci odpowiada (zamiast karty w obecnym oknie)?

## Decyzje (2026-11-10, użytkownik)
1. Reguły ignorowania: **kopia `.gitignore`** przy zakładaniu worktree (zasada „reguły tylko w `Domino/.gitignore`” zostaje; kopia odświeżana przy każdym zakładaniu).
2. Miejsce: **w środku, `Domino\.worktrees\<temat>`**, `.worktrees/` dopisane do `Domino/.gitignore` (dopisane). Bez wyjątku od zasady „tylko w folderze projektu”.
3. **Nowe okno VS Code** na każde zadanie „nowy problem”.

## Test ręczny (2026-11-10, gałąź `test_wt`, bez pushu)
| Krok | Wynik |
|---|---|
| `git worktree add .worktrees/test_wt -b test_wt main` | OK, 1105 plików |
| kopia `.gitignore` i `.claude/settings.local.json`, `New-Item -ItemType Junction SI\Klienci` | OK (`mklink` z Git Bash psuje ścieżki → dowiązanie robić w PowerShell) |
| `git status` w worktree / w `Domino` | worktree czysty; `Domino` nie widzi `.worktrees/` |
| `SI/Klienci` przez dowiązanie | pliki widoczne, nadal ignorowane (`.gitignore:146`) |
| pamięć Claude w worktree | **wspólna** z `Domino` (`C--Users-Admin-Desktop-Domino\memory`), skille `zadanie`/`zapisz`/`zamknij` widoczne |
| commit w worktree + `git merge --no-ff --no-commit test_wt` w `Domino` | merge bez konfliktu, `merge --abort` → `main` bez zmian |
| `code -n <worktree>` + link `vscode://…/open?prompt=` | karta otwiera się w **nowym oknie** worktree, katalog roboczy i gałąź `test_wt` |

Wniosek: wariant A działa w całości. `core.longpaths` nie jest ustawione, a checkout przeszedł bez błędów; ustawiamy dopiero przy pierwszym problemie.

## Wdrożenie (2026-11-10, gałąź `worktree_zadanie`)
- `worktree_zadania.py` + `run_worktree.bat` (dwuklik = menu) zamiast planowanego `nowy_worktree`. Polecenia:
  - `utworz <temat> [--dolacz <ścieżka>]`:
    - startuje z `origin/main`;
    - kopiuje `.gitignore` i `settings.local.json`;
    - zakłada junction do `SI/Klienci` oraz do istniejących `_historia/kopie` i `_robocze`;
    - robi twarde dowiązania do `config.json`;
    - przez `--dolacz` dołącza dane projektu; w folderze częściowo śledzonym (np. `raporty/` z README) brakujące pliki dostają twarde dowiązania;
  - `lista`: stan „bez commitów” / „SCALONA” / „niescalona”;
  - `dolacz <temat> <ścieżka> [--utworz]`: np. `_historia/kopie` nowego klienta;
  - `usun <temat> [--sila]`: najpierw usuwa wszystkie junction, potem worktree i gałąź.
- Odmowy `usun`:
  - folder, który nie jest zarejestrowanym worktree (zwykły folder → `git -C` trafiłby do `Domino`; wykryte w teście);
  - niezapisane zmiany;
  - gałąź niescalona z `origin/main`;
  - ignorowane pliki tylko lokalne (np. nowy raport w `raporty/`).
- Testy t2–t8: wszystkie powyższe scenariusze. Po każdym `usun` sprawdzone, że w `Domino` są nienaruszone `SI/Klienci`, `config.json` i `raporty/` (220 plików).
- Skille:
  - `/zadanie`: worktree w kroku 6, folder i analiza w worktree, `code -n` + link, sprzątanie scalonych na starcie;
  - `/zamknij`: tryb worktree z merge przez `git -C Domino`, bez usuwania własnego folderu;
  - `/zapisz`: kontrola `.gitignore` w worktree.
- README: `SI/README.md` (zasada 10, tabela), `Zadania_ClickUp/README.md`, `historia_sterownikow/README.md` (kopie przez `dolacz`).
- Ograniczenia bez zmian: Claude in Chrome, DevTools MCP, schowek i port 8765 są wspólne, więc zadania z przeglądarką nadal robimy po kolei.

## Stan
- 2026-11-10: wdrożone i przetestowane skryptem. Pierwsze prawdziwe zadanie „nowy problem” w worktree = test całego przepływu z `/zadanie` i `/zamknij`.
