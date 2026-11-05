# ANALIZA: skill `/zadanie` — zadanie ClickUp → analiza → folder projektu → osobna sesja Claude

Data: 2026-11-05

## 1. Cel

Podajesz link do zadania ClickUp. Dostajesz krótką analizę i propozycję realizacji. Po Twojej akceptacji skill:
1. otwiera istniejący albo zakłada nowy folder projektu w SI (zgodnie z `SI/README.md`),
2. zapisuje tam wstępną analizę zadania,
3. uruchamia w tym folderze nową sesję Claude w osobnym oknie terminala, która przejmuje realizację.

## 2. Wejście i wyjście

- **Wejście:** `/zadanie <link ClickUp>` (np. `https://app.clickup.com/t/<workspace>/<id>` lub `/t/<id>`).
- **Wyjście w czacie:** analiza (do ~15 linii) + propozycja realizacji + pytania blokujące, jeśli są.
- **Wyjście na dysku (po akceptacji):** `<folder projektu>/ANALIZA_<temat>.md` (+ wpis w tabeli `SI/README.md`).
- **Wyjście „agentowe”:** nowe okno `cmd` z `claude` uruchomionym w folderze projektu i promptem startowym.

## 3. Przebieg skilla

**Krok 1. Odczyt zadania (tylko odczyt ClickUp):**
- `clickup_get_task` (opis, status, termin, osoby, pola własne, lista/folder/przestrzeń);
- komentarze (`clickup_get_task_comments`);
- podzadania i zadanie nadrzędne;
- lista załączników (bez pobierania — pobieram tylko za zgodą, jeśli są potrzebne).

**Krok 2. Rozpoznanie:**
- **klient/domena:** pierwszy człon nazwy zadania, jak w skillach FB/GMC;
- **serwis:** IdoSell, Facebook, GMC, GTM…;
- **typ pracy:** feed, weryfikacja, migracja, analiza…
- **Dopasowanie do tego, co już jest:**
  - dedykowany skill (`weryfikacja-fb`, `weryfikacja-gmc`, `summonfeed`, `wiadomosci-transakcyjne`);
  - istniejący projekt z tabeli w `SI/README.md`;
  - wcześniejsze foldery i raporty tej domeny (wyszukiwanie po domenie w `SI`);
  - notatki w pamięci o kliencie.

**Krok 3. Analiza w czacie (bez zapisu plików):**

```
Zadanie: <nazwa> (<status>, termin <data>) — <klient>
Cel: 1–2 zdania własnymi słowami
Co już mamy: projekt/skill/poprzednie raporty
Czego brakuje: dane, dostępy, decyzje klienta
Propozycja realizacji: 3–6 kroków; który skill/narzędzie; gdzie folder
Ryzyka / pytania: tylko te, które blokują start
```

Kończę pytaniem: „Realizować? (folder: `<ścieżka>`)” — i czekam.

**Krok 4. Po akceptacji — folder:**

| Sytuacja | Folder | Co zapisuję |
|---|---|---|
| Zadanie obsługuje dedykowany skill | folder tego skilla (np. `02_Serwisy/GMC/Weryfikacja_GMC/`) | nic — skill sam tworzy `raporty/<domena>_<data>/` |
| Istniejący projekt, nowy klient | `<projekt>/klienci/<domena>/` | `ANALIZA_<temat>.md` |
| Nowa praca | `SI/<obszar>/<Serwis>/<Projekt>/` wg zasad z `SI/README.md` | `ANALIZA_<temat>.md` + wiersz w tabeli „w toku” |

`ANALIZA_<temat>.md` ma układ jak w globalnym CLAUDE.md:
- link do zadania i data;
- cel;
- dane wejściowe i wyjściowe;
- plan;
- założenia;
- otwarte pytania;
- sekcja „Stan” do aktualizacji przez sesję realizującą.

**Krok 5. Uruchomienie sesji realizującej:**

```
start "<klient> - <temat>" cmd /k "cd /d <folder> && claude "<prompt startowy>""
```

- Prompt startowy dla nowej pracy:
  „Zadanie ClickUp `<link>`. Przeczytaj `ANALIZA_<temat>.md` i `SI/README.md`. Potwierdź plan albo dopytaj, potem realizuj.”
- Dla zadania z dedykowanym skillem: `claude "/weryfikacja-gmc <link>"` — tak jak robią dziś `Weryfikacja_GMC.bat` i `Weryfikacja_FB.bat`.
- Bieżąca sesja kończy na podaniu ścieżki folderu i informacji, że okno jest otwarte.

**Zasady stałe:**
- ClickUp tylko do odczytu: komentarz, zmiana statusu czy podzadania wyłącznie na Twoje polecenie.
- Bez pobierania załączników bez zgody.
- Sesja-matka niczego nie realizuje — tylko analiza, folder i start.

## 4. Sposób działania na agentach — porównanie

| Wariant | Jak | Plusy | Minusy |
|---|---|---|---|
| **A. Nowe okno terminala z `claude` w folderze** (Twoja propozycja) | `start cmd /k claude …` | pełna interakcja, osobny kontekst na zadanie, Claude in Chrome działa, CLAUDE.md i pamięć Domino ładują się (pamięć jest wspólna dla całego repo) | każde okno pyta o uprawnienia od nowa; kilka sesji naraz dzieli **jedno drzewo git** (patrz p. 5) |
| B. Subagent w tle w tej sesji (`Agent`) | bez nowego okna | zero przełączania okien, wynik wraca tutaj | brak rozmowy w trakcie; nie nadaje się do pracy w przeglądarce ani do pytań po drodze |
| C. Worktree git na zadanie | osobna kopia repo na gałęzi | pełna izolacja gałęzi | **w SI większość plików jest nieśledzona** (dane, `config.json`, `_wspolne/idosell_client.py`) — w worktree ich nie ma, narzędzia nie zadziałają |
| D. Sesja w chmurze | zdalnie | działa bez komputera | brak dostępu do lokalnych plików, Chrome i paneli klientów |

**Rekomendacja:** wariant A jako główny, z jednym dodatkiem z B. Krok 1–3 (zbieranie i analiza) może dla zadań z dużą liczbą komentarzy lub podzadań zrobić subagent w tle, żeby nie zaśmiecać tej sesji. Realizacja zawsze w nowym oknie.

## 5. Ryzyka i wątpliwości

1. **Gałęzie przy kilku oknach naraz.**
   - Problem: Twoja zasada to „gałąź na projekt”. Gdy sesja w oknie X zrobi `git switch -c <temat>`, przełączy też drzewo VS Code i wszystkich innych okien.
   - Propozycja: sesje uruchamiane przez `/zadanie` **nie przełączają gałęzi same**. Pracują na plikach, a commit robią przez `/zapisz` / `/zamknij` wywołane świadomie przez Ciebie (po jednym projekcie naraz).
   - Alternatywa (więcej roboty): `/zapisz` commituje przez tymczasowy worktree, bez ruszania drzewa roboczego.
2. **Claude in Chrome w kilku sesjach naraz** — rozszerzenie obsługuje jedną sesję jednocześnie. Dwie sesje pracujące w przeglądarce będą sobie przeszkadzać. W analizie zaznaczę, czy zadanie wymaga przeglądarki.
3. **Uprawnienia** — nowe okno pyta o zgody od zera. Można to ograniczyć wpisami w `.claude/settings.json` (skill `fewer-permission-prompts`) — poza zakresem tego zadania.
4. Uruchomienie okna przez `start` z sesji Claude działa w Windows, ale okno otwiera się poza moją kontrolą — nie widzę, co się w nim dzieje (to cecha, nie błąd).

## 6. Planowane pliki

- `Domino/.claude/skills/zadanie/SKILL.md` — skill `/zadanie` (kroki 1–5, zasady).
- `SI/02_Serwisy/ClickUp/Zadania_ClickUp/`:
  - `ANALIZA_skill_zadanie_clickup.md` (ten plik);
  - `README.md`;
  - `Zadanie_ClickUp.bat` — dwuklik: pyta o link, uruchamia `claude "/zadanie <link>"`, wzorem `Weryfikacja_FB.bat`;
  - `uruchom_sesje.bat <folder> <tytuł> <prompt>` — jedno miejsce na komendę otwierania okna (łatwo podmienić na Windows Terminal, gdy go zainstalujesz).
- Wiersz w tabeli `SI/README.md` + notatka w pamięci.

## 7. Decyzje użytkownika (2026-11-05)

1. Nazwa: `/zadanie`.
2. Git:
   - **Zadanie obsługiwane przez istniejący skill:** sesja może sama wykonać `/zapisz` i `/zamknij` dla **nowych wniosków z procesu** (poprawki skilla, wiedza, narzędzia). Danych klientów i ich serwisów nie commitujemy, chyba że są ważne jako przykład.
   - **Nowy problem:** przełączamy na nową gałąź, a `/zapisz` i `/zamknij` wykonuje użytkownik.
   - Dodatek: gałąź zakładam tylko od `main`. Jeśli drzewo jest na innej gałęzi projektu — pytam, bo przełączenie zabrałoby z dysku jej pliki.
3. Zadanie z dedykowanym skillem → od razu nowe okno z tym skillem (bez analizy w tej sesji).
4. ClickUp tylko do odczytu. Gdy zadanie tego wymaga, sesja realizująca przygotowuje `komentarz_clickup.txt`, który użytkownik wkleja sam.

Rozwiązanie techniczne: okno otwiera `uruchom_sesje.bat <folder> "<prompt>"`. Prompt jest bez polskich znaków (cmd), a szczegóły i zasady sesji są w `ANALIZA_<temat>.md` (sekcja „Zasady sesji”).

## 8. Otwarte pytania (rozstrzygnięte w p. 7)

1. **Nazwa skilla:** `/zadanie` — pasuje? (alternatywy: `/clickup`, `/zadanie-clickup`)
2. **Gałęzie przy wielu oknach:** zgoda na „sesje z `/zadanie` nie przełączają gałęzi, commit robisz Ty przez `/zapisz`/`/zamknij`” (p. 5.1)?
3. **Zadania z dedykowanym skillem** (FB, GMC, summonFeed…) — od razu uruchamiać skill w nowym oknie, czy też najpierw pokazać krótką analizę i czekać na akceptację?
4. **Komentarz w ClickUp** — czy po starcie dodawać do zadania krótki komentarz „rozpoczęto, folder: …”, czy ClickUp zostaje całkowicie tylko do odczytu?
