---
name: zapisz
description: Zapis postępu nieukończonego projektu — commit i push bieżącej gałęzi projektu (nie main) z opisem wygenerowanym na podstawie zmian. Używaj, gdy użytkownik wywołuje /zapisz, mówi „zapisz”, „zapisz postęp”, „zacommituj i wypchnij gałąź”, oraz AUTOMATYCZNIE, gdy kończymy lub przerywamy sesję nad projektem prowadzonym na osobnej gałęzi, który nie jest jeszcze gotowy. Nie dotyczy pracy na gałęzi main.
---

# /zapisz — commit i push gałęzi projektu

Repo: `C:\Users\Admin\Desktop\Domino`, remote `origin`, `push.autoSetupRemote=true` (pierwszy push nie wymaga `-u`).

## 1. Sprawdź gałąź
- `git branch --show-current`.
- Jeśli to **`main`** (albo detached HEAD): **nic nie commituję ani nie pushuję**. Informuję jednym zdaniem, że na `main` zapis robi użytkownik, i podaję listę plików zmienionych w tej sesji do jego commita. Koniec.
- **Worktree zadania** (`Domino\.worktrees\<temat>`): przed `git add` sprawdzam, że w korzeniu worktree jest `.gitignore`. Bez niego git nie ignoruje feedów, eksportów ani kluczy, więc zatrzymuję się i zgłaszam to (kopię robi `worktree_zadania.py utworz`). Resztę kroków robię normalnie w worktree.
- **Worktree: dane klienta do `Domino`** (ustalenie z 2026-11-12):
  - przed commitem uruchamiam `git ls-files -o -i --exclude-standard`;
  - pomijam to, co dokłada skrypt `utworz`: kopie `.gitignore` i `.claude/settings.local.json`, dowiązania `SI/Klienci`, `config.json`, foldery z `--dolacz` i `__pycache__`;
  - pozostałe pliki tylko lokalne przenoszę do `Domino` pod tę samą ścieżkę względną; gdy plik już tam jest, nie nadpisuję go, tylko to zgłaszam;
  - listę przeniesionych plików podaję w podsumowaniu.

## 1a. Historia sterowników (gdy w sesji była praca ze sterownikami IdoSell)
- Dotyczy pracy z feedami/sterownikami w panelu (Zmiany_sterownikow, summonfeed, zadanie z feedem). Procedura: `SI/02_Serwisy/IdoSell/Zmiany_sterownikow/_narzedzia/historia_sterownikow/README.md`.
- Panel zalogowany → zrzut `zapis` wszystkich sklepów klienta (`historia.py sesja --rodzaj zapis`, `BM.zrzutSklepu` na każdym `shop=`, `historia.py zloz`). Zmiany bez wpisu w dzienniku zgłaszam w podsumowaniu.
- Wylogowany panel albo brak pracy w panelu → bez zrzutu, odnotowuję w podsumowaniu. Zrzut nie blokuje commita.
- Zrzut robię także na `main` (commit wtedy robi użytkownik — podaję mu pliki `_historia/*.json` i `dziennik_wdrozen.csv`).

## 2. Wybierz pliki
- `git status --porcelain` — przejrzyj zmiany.
- Do commita trafiają **tylko pliki należące do projektu tej gałęzi** (te, które zmienialiśmy w sesji / leżą w folderze projektu). Zmian użytkownika spoza projektu nie dodaję — wymieniam je w podsumowaniu jako pominięte.
- Nigdy `git add -A` / `git add .` w katalogu głównym. Dodaję ścieżki jawnie (`git add -- "<ścieżka>"`).
- Pliki ignorowane przez `.gitignore` (feedy, eksporty, tokeny, `config.json` z kluczami) zostają poza repo — nie używam `-f`.
- Historia sterowników klienta (`Zmiany_sterownikow/<klient>/_historia/*.json`, `dziennik_wdrozen.csv`) należy do projektu, gdy powstała w tej sesji. `kopie/` i `_robocze/` są w `.gitignore`.
- Kontrola rozmiaru: żaden plik w stage nie może przekraczać **50 MB** (GitHub odrzuca > 100 MB). Sprawdź `git diff --cached --name-only` + rozmiar plików. Jeśli jest większy — wyjmij go ze stage (`git restore --staged`) i zgłoś.
- Brak zmian projektu do zapisania → poinformuj i przejdź do kroku 4 (push, jeśli są niewypchnięte commity).

## 3. Commit z wygenerowanym opisem
Opis generuję po polsku z `git diff --cached` (nie z pamięci rozmowy):
- **Tytuł** (≤ 72 znaki): `<Projekt>: <co zrobiono>` + dopisek `(WIP)`, bo projekt nie jest ukończony.
- **Treść**: 2–6 punktów — co dodano/zmieniono i dlaczego, a na końcu linia `Dalej: …` ze stanem i kolejnym krokiem.
- Na końcu linia attribution z bieżącego system-remindera (np. `Co-Authored-By: …`).

Commit przez plik tymczasowy w scratchpadzie (UTF-8, zachowuje polskie znaki):
`git commit -F "<scratchpad>/commit_msg.txt"`.
Hooków nie pomijam (`--no-verify` zabronione) — jeśli hook odrzuci commit, naprawiam przyczynę.

## 4. Push
- `git push` (bez `--force`). Odrzucony push (remote ma nowsze commity) → `git pull --rebase`, ponownie push; konflikt → zatrzymaj się i zgłoś.

## 5. Podsumowanie (krótko)
Gałąź, hash i tytuł commita, liczba plików, wynik pushu, pliki pominięte (spoza projektu / > 50 MB).
