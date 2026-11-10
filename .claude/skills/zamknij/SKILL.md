---
name: zamknij
description: Zamknięcie ukończonego projektu — commit i push gałęzi projektu, a następnie merge do main z wygenerowanym opisem i push main. Używaj, gdy użytkownik wywołuje /zamknij, mówi „zamknij projekt”, „scal do main”, „projekt gotowy, merguj”. Tylko na wyraźne polecenie użytkownika — nigdy automatycznie.
---

# /zamknij — commit, push i merge do main

Repo: `C:\Users\Admin\Desktop\Domino`, remote `origin`.

## 1. Sprawdź gałąź
- `git branch --show-current` → zapamiętaj jako `<galaz>`.
- Jeśli to **`main`**: nie ma czego scalać. Informuję i kończę (zapis na `main` robi użytkownik — podaję listę plików do commita).
- **Worktree zadania?** `git rev-parse --path-format=absolute --git-dir` różne od `--git-common-dir` (folder `Domino\.worktrees\<temat>`) → tryb worktree: kroki 3–5 robię w głównym folderze `Domino` przez `git -C C:\Users\Admin\Desktop\Domino …` (opis niżej). W worktree nie przełączam gałęzi: `main` jest wyciągnięty w `Domino`, więc `git switch main` się tu nie uda.

## 1a. Przebieg kontrolny sterowników (gdy projekt dotyczył feedów/sterowników IdoSell)
Cel: upewnić się, że w wyniku błędu sterownik nie trafił do dwóch serwisów ani do niewłaściwego. Procedura: `SI/02_Serwisy/IdoSell/Zmiany_sterownikow/_narzedzia/historia_sterownikow/README.md`.
- Zrzut `koniec` **wszystkich** sklepów klienta (nie tylko tych, w których pracowaliśmy), potem `python historia.py kontrola --klient <klient>`.
- Kod 0 → wynik „OK” do podsumowania, idę dalej.
- Kod 1 → **nie robię merge**. Pokazuję listę problemów i przechodzę do procedury incydentu (spisanie, przywrócenie stanu z `_historia/kopie/`, zgłoszenie do IdoSell tylko gdy wygląda na ich błąd). Merge dopiero po wyjaśnieniu i ponownej kontroli.
- Panel wylogowany → proszę o zalogowanie. Bez kontroli zamykam tylko na wyraźną decyzję użytkownika i odnotowuję to w opisie merge.
- Pliki zrzutów i dziennika wchodzą do commita z kroku 2.

## 2. Zapisz gałąź
Wykonaj kroki 2–4 skilla `/zapisz` (`.claude/skills/zapisz/SKILL.md`): wybór plików projektu, kontrola > 50 MB, commit z opisem, push — z tą różnicą, że **tytuł nie ma dopisku `(WIP)`**, a zamiast `Dalej:` piszę `Stan: ukończone`.

## 3. Przygotuj main
- `git fetch origin`.
- `git switch main`. Zmiany użytkownika w drzewie roboczym przechodzą razem z przełączeniem — **nie stashuję, nie resetuję i nie commituję ich**. Jeśli przełączenie się nie uda (konflikt z lokalnymi zmianami) — wracam na `<galaz>`, zgłaszam pliki i kończę.
- `git pull --ff-only`. Niepowodzenie (lokalny main rozjechany z origin) → zatrzymaj się i zgłoś, bez rebase main.
- **Tryb worktree:** zamiast `switch` sprawdzam `git -C <Domino> branch --show-current`.
  - To musi być `main`. Jeśli nie, zatrzymuję się i zgłaszam: użytkownik ma tam inną gałąź, a ja jej nie przełączam.
  - Potem `git -C <Domino> fetch origin` i `git -C <Domino> pull --ff-only`.
  - Zmiany użytkownika w `Domino` zostają nietknięte.

## 4. Merge z opisem
- Opis generuję po polsku z `git log --oneline main..<galaz>` i `git diff --stat main...<galaz>`:
  - **Tytuł**: `Merge <galaz>: <projekt w kilku słowach>`
  - **Treść**: co projekt dostarcza (3–8 punktów: nowe narzędzia/skille, kluczowe pliki, jak uruchomić), lista commitów gałęzi, linia attribution z system-remindera.
- `git merge --no-ff <galaz> -F "<scratchpad>/merge_msg.txt"`.
- Konflikt → `git merge --abort`, powrót na `<galaz>`, zgłoszenie plików w konflikcie. Konfliktów nie rozwiązuję bez zgody użytkownika.
- Merge zablokowany przez niezacommitowane zmiany użytkownika → zgłaszam te pliki, bez stashowania.
- **Tryb worktree:** te same polecenia z `git -C <Domino>`, czyli `log`, `diff --stat` i `merge --no-ff <galaz> -F …`. Konflikt → `git -C <Domino> merge --abort` i zgłoszenie.

## 5. Push main i sprzątanie
- `git push` (bez `--force`).
- Lokalną gałąź usuwam bezpiecznie: `git branch -d <galaz>` (tylko po udanym pushu main). Gałąź na `origin` zostawiam — usuwam ją wyłącznie na prośbę.
- Zostaję na `main` (użytkownik pracuje na `main` w VS Code).
- **Tryb worktree:**
  - `git -C <Domino> push`.
  - Gałęzi lokalnej **nie** usuwam, bo jest wyciągnięta w tym worktree. Folderu też nie usuwam, bo działa w nim ta sesja.
  - Na koniec piszę: „Zamknij okno VS Code tego zadania. Worktree usunie następne /zadanie (albo `run_worktree.bat usun <temat>` z Domino).”

## 6. Podsumowanie (krótko)
Gałąź, commit zapisu, hash merge commita, liczba commitów i plików scalonych, wynik pushu, pominięte pliki.
