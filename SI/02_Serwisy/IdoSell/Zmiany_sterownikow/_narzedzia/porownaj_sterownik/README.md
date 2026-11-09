# porownaj_sterownik — sterownik z panelu IdoSell vs plik lokalny

Krok stały przed każdą zmianą sterownika XSLT (zasada nr 9 w `SI/README.md`).
Analiza i decyzje: `../../ANALIZA_porownanie_sterownikow.md`.

## Użycie
1. W panelu: „Serwisy porównywarek” → serwis → „Wybierz → Ustawienia”, zaznacz `textarea` ze sterownikiem i skopiuj (Ctrl+A, Ctrl+C). Claude in Chrome robi to przez `ta.focus(); ta.select()` i `ctrl+c`.
2. Dwuklik `run_porownaj.bat` → fragment nazwy klienta → plik lokalny → Enter (schowek) → folder na diff → podmiana `[T/n]`.

Werdykty: `ZGODNE`, `ZGODNE poza białymi znakami` (BOM, CRLF/LF, spacje na końcach linii — bez podmiany), `RÓŻNE` (+/− linii, diff w `porownanie_<plik>_<data>.diff`, opcjonalnie `.html`).
Przy podmianie: stary plik → `<kraj>/old/<nazwa>_<RRRR-MM-DD>.xml` (zajęta nazwa → `_2`, `_3`), wersja z panelu zapisana w UTF-8 bez BOM z końcami linii jak w starym pliku.

## Z sesji Claude (bez pytań)
```
python porownaj_sterownik.py --auto --lokalny xslt/E/ezebra/PL/ezebrapl_WP.xml --folder-zadania <folder zadania> [--zastap] [--html]
```
`--panel <plik>` zamiast schowka. Kody wyjścia: 0 zgodne, 1 różne, 2 błąd wejścia (np. w schowku nie ma XSLT).
Skrypt wypisuje SHA-256 znormalizowanego tekstu (linie złączone LF, bez końcowych spacji i pustych linii) — do porównań hashy liczonych w panelu.

Pliki `porownanie_*` zawierają kod klienta i są w `.gitignore`.
