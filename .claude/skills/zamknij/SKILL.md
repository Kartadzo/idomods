---
name: zamknij
description: Zamknięcie ukończonego projektu — commit i push gałęzi projektu, a następnie merge do main z wygenerowanym opisem i push main. Używaj, gdy użytkownik wywołuje /zamknij, mówi „zamknij projekt”, „scal do main”, „projekt gotowy, merguj”. Tylko na wyraźne polecenie użytkownika — nigdy automatycznie.
---

# /zamknij — commit, push i merge do main

Repo: `C:\Users\Admin\Desktop\Domino`, remote `origin`.

## 1. Sprawdź gałąź
- `git branch --show-current` → zapamiętaj jako `<galaz>`.
- Jeśli to **`main`**: nie ma czego scalać. Informuję i kończę (zapis na `main` robi użytkownik — podaję listę plików do commita).

## 2. Zapisz gałąź
Wykonaj kroki 2–4 skilla `/zapisz` (`.claude/skills/zapisz/SKILL.md`): wybór plików projektu, kontrola > 50 MB, commit z opisem, push — z tą różnicą, że **tytuł nie ma dopisku `(WIP)`**, a zamiast `Dalej:` piszę `Stan: ukończone`.

## 3. Przygotuj main
- `git fetch origin`.
- `git switch main`. Zmiany użytkownika w drzewie roboczym przechodzą razem z przełączeniem — **nie stashuję, nie resetuję i nie commituję ich**. Jeśli przełączenie się nie uda (konflikt z lokalnymi zmianami) — wracam na `<galaz>`, zgłaszam pliki i kończę.
- `git pull --ff-only`. Niepowodzenie (lokalny main rozjechany z origin) → zatrzymaj się i zgłoś, bez rebase main.

## 4. Merge z opisem
- Opis generuję po polsku z `git log --oneline main..<galaz>` i `git diff --stat main...<galaz>`:
  - **Tytuł**: `Merge <galaz>: <projekt w kilku słowach>`
  - **Treść**: co projekt dostarcza (3–8 punktów: nowe narzędzia/skille, kluczowe pliki, jak uruchomić), lista commitów gałęzi, linia attribution z system-remindera.
- `git merge --no-ff <galaz> -F "<scratchpad>/merge_msg.txt"`.
- Konflikt → `git merge --abort`, powrót na `<galaz>`, zgłoszenie plików w konflikcie. Konfliktów nie rozwiązuję bez zgody użytkownika.
- Merge zablokowany przez niezacommitowane zmiany użytkownika → zgłaszam te pliki, bez stashowania.

## 5. Push main i sprzątanie
- `git push` (bez `--force`).
- Lokalną gałąź usuwam bezpiecznie: `git branch -d <galaz>` (tylko po udanym pushu main). Gałąź na `origin` zostawiam — usuwam ją wyłącznie na prośbę.
- Zostaję na `main` (użytkownik pracuje na `main` w VS Code).

## 6. Podsumowanie (krótko)
Gałąź, commit zapisu, hash merge commita, liczba commitów i plików scalonych, wynik pushu, pominięte pliki.
