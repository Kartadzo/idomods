# Zadania ClickUp — skill `/zadanie`

Link do zadania ClickUp → krótka analiza i propozycja realizacji → po akceptacji folder projektu w SI ze wstępną analizą → nowe okno terminala z Claude Code pracującym w tym folderze.

Status: gotowe (2026-11-05), czeka na pierwsze prawdziwe zadanie.

## Uruchamianie

- W sesji Claude: `/zadanie <link do zadania ClickUp>`.
- Dwuklik: `Zadanie_ClickUp.bat` — pyta o link i uruchamia Claude w folderze `Domino` z `/zadanie <link>`.

## Pliki

| Plik | Do czego |
|---|---|
| `Domino/.claude/skills/zadanie/SKILL.md` | treść skilla (kroki, zasady, git) |
| `ANALIZA_skill_zadanie_clickup.md` | specyfikacja, porównanie wariantów agentowych, decyzje |
| `Zadanie_ClickUp.bat` | start z pulpitu/eksploratora |
| `uruchom_sesje.bat "<folder>" "<prompt>" ["<tytuł>"]` | otwiera nowe okno `cmd` z `claude "<prompt>"` w folderze; `ZADANIE_KOMENDA` podmienia `claude` do testów |

## Najważniejsze zasady

- ClickUp tylko do odczytu; komentarz przygotowuje sesja realizująca w `komentarz_clickup.txt`, wkleja użytkownik.
- Zadania FB / GMC / feed XSLT / wiadomości transakcyjne → od razu nowe okno z dedykowanym skillem.
- Git:
  - przy pracy w ramach skilla sesja sama robi `/zapisz` i `/zamknij`, ale tylko dla wniosków z procesu, bez danych klientów;
  - przy nowym problemie przełączamy na nową gałąź, a commity robi użytkownik.
- Jedna sesja w Claude in Chrome naraz.
- Sesja realizująca otwiera się domyślnie jako nowa karta Claude w VS Code, przez link `vscode://anthropic.claude-code/open?prompt=…`. Karta startuje w `Domino`, więc prompt podaje folder zadania. Zapasowo działa okno `cmd` przez `uruchom_sesje.bat`.
- Pierwsze prawdziwe zadanie: [MegaDron.pl gAds - Test zdarzeń na nowym OSCOP](https://app.clickup.com/t/1ammhmkcgn4) (2026-11-05) → `02_Serwisy/IdoSell/Test_zdarzen_OSCOP`.
