---
name: zadanie
description: Zadanie ClickUp → krótka analiza i propozycja realizacji → po akceptacji folder projektu w SI ze wstępną analizą → nowe okno terminala z Claude Code pracującym w tym folderze. Zadania obsługiwane przez istniejący skill (weryfikacja-fb, weryfikacja-gmc, summonfeed, wiadomosci-transakcyjne) od razu uruchamia w nowym oknie z tym skillem. Używaj, gdy użytkownik wywołuje /zadanie <link>, wkleja link do zadania ClickUp z prośbą o analizę/propozycję/realizację, mówi „przeanalizuj zadanie”, „weź to zadanie”, „co z tym zadaniem w ClickUp”.
---

# /zadanie — zadanie ClickUp → analiza → folder → sesja realizująca

Specyfikacja i decyzje: `SI/02_Serwisy/ClickUp/Zadania_ClickUp/ANALIZA_skill_zadanie_clickup.md`. Mapa SI, tabela projektów i zasady folderów: `SI/README.md` (czytam przed krokiem 2).
Repo: `C:\Users\Admin\Desktop\Domino`. Launcher okna: `SI/02_Serwisy/ClickUp/Zadania_ClickUp/uruchom_sesje.bat`. Worktree zadań: `SI/02_Serwisy/ClickUp/Zadania_ClickUp/worktree_zadania.py` (analiza: `ANALIZA_worktree_zadanie.md`).

## Zasady (zawsze)
- **Baza wiedzy o klientach:** w kroku 2 czytam `SI/Klienci/README.md` i plik domeny (zasady, wyjątki, panel wielosklepowy) i uwzględniam je w propozycji. W prompcie sesji realizującej dopisuję: „Przeczytaj SI/Klienci/<plik>.md i przestrzegaj zasad klienta.” Nowe stałe ustalenie z zadania lub komentarzy proponuję dopisać do bazy (po zgodzie).
- **ClickUp tylko do odczytu.** Nie komentuję, nie zmieniam statusu, terminu, osób ani podzadań. Komentarz dla klienta/zespołu przygotowuje sesja realizująca jako `komentarz_clickup.txt` — użytkownik wkleja go sam.
- Załączników nie pobieram bez zgody (podaję nazwę i rozmiar, pytam).
- **Narzędzia przeglądarki** (ustalenie użytkownika 2026-11-05):
  - **Chrome DevTools MCP („webtools”, osobny profil):**
    - zamówienia testowe;
    - sprawdzanie zdarzeń na stronie sklepu: zapytania sieciowe `gtag`/`fbq`/`ttq` i inne, dataLayer, podwójne odpalenia, wartości.
  - **Claude in Chrome:** reszta, czyli panele IdoSell, Events Manager, Google Ads, TikTok i GMC, gdzie użytkownik jest zalogowany.
  - Gdy inne działanie byłoby wydajniejsze w DevTools, proponuję to i pytam, zamiast przenosić je samemu.
- **Historia sterowników:** gdy zadanie dotyczy feedów lub sterowników XSLT w panelu IdoSell, w prompcie sesji realizującej dopisuję: „Zadanie dotyczy sterowników: stosuj procedurę z SI/02_Serwisy/IdoSell/Zmiany_sterownikow/_narzedzia/historia_sterownikow/README.md (zrzut start przed pierwszą zmianą, znacznik BM-SERWIS/BM-EDYCJA w edytowanych plikach, przed wgraniem pytanie: wgrywasz Ty czy ja?, zrzuty przed/po wgraniu i dziennik).” W analizie (3B) wpisuję ten krok do planu.
- **Powtarzalne zadania → propozycja skilla:** gdy ten sam typ zadania wystąpił już 3–5 razy (licząc bieżące) i nie ma dla niego dedykowanego skilla, w analizie dodaję punkt „Propozycja skilla”. Podaję w nim nazwę, zakres i to, co z dotychczasowych realizacji da się ustandaryzować. Skill tworzę dopiero po zgodzie użytkownika.
- Ta sesja niczego nie realizuje: tylko analiza, folder i start nowego okna.
- Przed zapisem plików czekam na akceptację propozycji (wyjątek: zadanie z dedykowanym skillem — krok 3A).

## 1. Odczyt zadania
1. ID z linku: `https://app.clickup.com/t/<workspace>/<id>` lub `/t/<id>` → `<id>`. ID w postaci `ABC-123` to custom task ID — wtedy podaję je z opcją custom ID.
2. `clickup_get_task` (opis, status, termin, osoby, pola własne, lista/folder/przestrzeń, rodzic, podzadania, załączniki).
3. Komentarze: `clickup_get_task_comments`; przy wątkach `clickup_get_threaded_comments`. Zadanie nadrzędne — `clickup_get_task` rodzica, gdy opis odsyła do kontekstu wyżej.
4. Dużo komentarzy/podzadań (umownie > 30 pozycji) → kroki 1–2 może zrobić subagent w tle (`Agent`, typ `general-purpose`) z poleceniem zwrotu streszczenia w układzie z kroku 3B; w tej sesji zostaje tylko wynik.

## 2. Rozpoznanie
- **Klient/domena:** pierwszy człon nazwy zadania (np. „Pyrawinyl.pl FbAds …” → `pyrawinyl.pl`); w razie wątpliwości — nazwa listy/folderu ClickUp.
- **Serwis i typ pracy:** IdoSell, Facebook, GMC, GTM, OpenAI, Base, Shoparena, Amazon, Erli, n8n…; feed, weryfikacja, migracja, analiza, wdrożenie…
- **Dedykowany skill** (dopasowanie po nazwie zadania i opisie):
  | Wzorzec | Skill | Folder |
  |---|---|---|
  | „FbAds - Optymalizacja katalogu i API konwersji”, Meta/piksel/katalog | `/weryfikacja-fb <link>` | `SI/02_Serwisy/Facebook/Weryfikacja_FB` |
  | „gAds - Optymalizacja GMC”, Merchant Center | `/weryfikacja-gmc <link>` | `SI/02_Serwisy/GMC/Weryfikacja_GMC` |
  | sterownik/feed XSLT dla serwisu | `/summonfeed <link>` | `SI/01_Feedy/SummonFeed` |
  | wiadomości transakcyjne (maile/SMS) | `/wiadomosci-transakcyjne <link>` | `SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne` |
- **Co już jest:** wiersz w tabeli `SI/README.md`; wcześniejsze foldery/raporty domeny (`Grep` po domenie w `SI`, bez `dane/` i plików > 1 MB); notatki pamięci o kliencie.
- **Powtarzalność typu zadania:** liczę wcześniejsze realizacje tego samego typu. Źródła:
  - raporty `raporty/<domena>_<data>/` w folderze projektu;
  - wiersze tabeli `SI/README.md`;
  - pamięć;
  - opcjonalnie `clickup_search` po stałym członie nazwy zadania (np. „Test zdarzeń”), tylko do odczytu.

  Przy 3–5 wystąpieniach i braku skilla dodaję „Propozycja skilla” (zasady stałe).

## 3A. Zadanie z dedykowanym skillem → od razu nowe okno
Podaję jednym zdaniem: nazwa zadania, domena, skill, folder. Uruchamiam (krok 5) z promptem `/<skill> <link>` w folderze skilla. Bez analizy i bez czekania. Git: wariant „skill” (krok 6).

## 3B. Pozostałe zadania → analiza w czacie
```
Zadanie: <nazwa> (<status>, termin <data>) — <klient>
Cel: 1–2 zdania własnymi słowami
Co już mamy: projekt / skill / poprzednie raporty / notatki
Czego brakuje: dane, dostępy, decyzje klienta
Propozycja realizacji: 3–6 kroków; narzędzia; przeglądarka: Claude in Chrome (panele) / DevTools (zdarzenia, zamówienie testowe)
Propozycja skilla: tylko gdy typ zadania powtórzył się 3–5 razy i nie ma skilla
Folder: <ścieżka>  ·  Git: worktree .worktrees/<temat>, gałąź <temat>
Pytania blokujące: tylko te, bez których nie da się zacząć
```
Kończę: „Realizować? Folder: `<ścieżka>`”. Czekam. Poprawki użytkownika wprowadzam do propozycji przed krokiem 4.

## 4. Folder i wstępna analiza (po akceptacji)
- **Wariant „nowy problem”: najpierw worktree** (krok 6), dopiero potem folder. Folder zadania, `ANALIZA_<temat>.md` i wiersz w `SI/README.md` zapisuję **w worktree** (`C:\Users\Admin\Desktop\Domino\.worktrees\<temat>\SI\...`), nie w `Domino`. Wtedy trafiają do gałęzi zadania, a `Domino` zostaje czyste.
- Folder według `SI/README.md`:
  - istniejący projekt + nowy klient → `<projekt>/klienci/<domena>/`;
  - nowa praca → `SI/01_Feedy/<Projekt>/` albo `SI/02_Serwisy/<Serwis>/<Projekt>/` (nowy serwis = nowy podfolder);
  - nazwa folderu bez spacji i ogonków.
- `<temat>`: krótki, ASCII, `_` zamiast spacji (np. `migracja_opinii_lauramessi`).
- Zapisuję `ANALIZA_<temat>.md`:
  ```
  # ANALIZA: <tytuł>
  Zadanie ClickUp: [<nazwa>](<link>) · Klient: <domena> · Data: <dziś>
  ## Cel
  ## Dane wejściowe i wyjściowe
  ## Plan
  ## Założenia
  ## Otwarte pytania
  ## Zasady sesji
  - ClickUp tylko do odczytu; komentarz → `komentarz_clickup.txt` (wkleja użytkownik).
  - Git: <tekst wariantu z kroku 6>.
  - Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
  - Przeglądarka: <tak/nie> — jedna sesja z Claude in Chrome naraz.
  - Zamówienie testowe i sprawdzanie zdarzeń na stronie sklepu (jeśli w planie): **tylko przez Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`, osobny profil), nie przez Claude in Chrome.
    - Zamówienie: tani produkt, 1 szt., płatność „przelew zwykły”, nigdy za pobraniem (globalny CLAUDE.md).
    - Panele i platformy reklamowe zostają w Claude in Chrome.
  ## Stan
  - <dziś>: analiza wstępna (sesja /zadanie).
  ```
- Nowy projekt → wiersz w tabeli `SI/README.md` ze statusem „w toku”.

## 5. Start sesji realizującej
**Domyślnie: nowa karta Claude w VS Code** (przetestowane 2026-11-05). Użytkownik pracuje w VS Code. Rozszerzenie Claude Code obsługuje link `vscode://anthropic.claude-code/open?prompt=…`. Link otwiera kartę w edytorze z wpisanym promptem, a wysyła go Enter użytkownika.
- Karta startuje w folderze workspace okna VS Code, nie w folderze zadania. Dlatego prompt **zawsze podaje ścieżkę folderu** (względną od korzenia repo) i każe w nim zapisywać pliki. Polskie znaki są dozwolone, bo prompt idzie przez URL-encoding. Przykład:
  `Zadanie ClickUp <link> (<klient> - <temat>). Folder zadania: SI/<ścieżka>. Przeczytaj ANALIZA_<temat>.md w tym folderze oraz SI/README.md, potwierdź plan ze mną i realizuj zgodnie z sekcją Zasady sesji. Wszystkie pliki zapisuj w tym folderze.`
- **Wariant „nowy problem” → nowe okno VS Code na worktree** (decyzja 2026-11-10, przetestowane): najpierw `code -n <worktree>`, chwila na start okna, potem link. Karta otwiera się w nowym oknie, z katalogiem roboczym i gałęzią worktree. Do promptu dopisuję: „Pracujesz w worktree .worktrees/<temat> (gałąź <temat>); nie przełączaj gałęzi i nie wchodź do folderu Domino.”
- **Wariant „skill” (3A)** → karta w bieżącym oknie (`Domino`), bez `code -n`.
- Wywołanie (narzędzie **PowerShell**):
  ```powershell
  code -n 'C:\Users\Admin\Desktop\Domino\.worktrees\<temat>'; Start-Sleep -Seconds 8   # tylko „nowy problem”
  $p = '<prompt>'   # apostrof w treści podwajam: ''
  Start-Process ('vscode://anthropic.claude-code/open?prompt=' + [uri]::EscapeDataString($p))
  ```
- Zadanie z dedykowanym skillem (3A): prompt `/<skill> <link>. Folder skilla: SI/<ścieżka>.`
- **Zapas: okno `cmd`** (gdy VS Code jest zamknięte albo użytkownik o to poprosi). Prompt bez polskich znaków i bez `"`, `&`, `|`, `%`:
  `& "C:\Users\Admin\Desktop\Domino\SI\02_Serwisy\ClickUp\Zadania_ClickUp\uruchom_sesje.bat" "<folder Windows>" "<prompt>" "<domena> - <temat>"`
  Kod 0 oznacza, że okno jest otwarte, a kod 1, że brak folderu. Plik .bat wywołuję narzędziem PowerShell, bo z Git Bash `cmd` go nie znajduje.
- Zintegrowanego terminala VS Code nie da się otworzyć z zewnątrz, więc go nie proponuję.
- Zadanie wymaga przeglądarki, a w tej sesji (lub innym oknie) trwa praca w Chrome → uprzedzam, że okna będą sobie przeszkadzać.
- Kończę: ścieżka folderu + „karta otwarta, zatwierdź prompt Enterem”. Dalsza praca dzieje się w nowej karcie.

## 6. Git
- **Wariant „skill”** (krok 3A albo praca w folderze istniejącego skilla): sesja realizująca sama wykonuje `/zapisz` i `/zamknij`, ale tylko dla **nowych wniosków z procesu** (poprawki skilla, specyfikacji, narzędzi, wiedza). Dane klientów i ich serwisów (raporty, zrzuty, eksporty) nie trafiają do gita — wyjątek: plik ważny jako wzorzec, za zgodą. Gałąź `wnioski-<skill>-<domena>` zakłada dopiero, gdy jest co commitować.
- **Wariant „nowy problem” → osobny worktree** (od 2026-11-10; `Domino` nie przełącza gałęzi):
  - `python SI/02_Serwisy/ClickUp/Zadania_ClickUp/worktree_zadania.py utworz <temat>` (z `Domino`). Tworzy `.worktrees/<temat>` na nowej gałęzi `<temat>` z `origin/main`. Dołącza to, czego git nie przenosi:
    - kopie `.gitignore` i `.claude/settings.local.json`;
    - dowiązania do `SI/Klienci` i do `_historia/kopie` oraz `_robocze`;
    - twarde dowiązania do plików `config.json`.
  - Zadanie kontynuuje projekt z danymi tylko lokalnymi (np. `raporty/`, `dane/`, eksport) → dodaję `--dolacz <ścieżka>` (można powtarzać). Folder dostaje junction, a w folderze częściowo śledzonym brakujące pliki dostają twarde dowiązania. Pliki zapisane przez junction fizycznie lądują w `Domino`. Nie commituję ich z worktree, bo przy merge'u kolidowałyby z tymi samymi plikami w `Domino`. Narzędzia i analizy do gita trzymam poza dowiązanym folderem.
  - **Dane klienta od razu w `Domino`** (ustalenie użytkownika z 2026-11-12). Worktree trzyma wyłącznie to, co idzie do gita. Dane klienta ignorowane przez git (eksporty, pliki od klienta, raporty z danymi, zrzuty) trafiają na bieżąco do `Domino` pod tę samą ścieżkę względną: przez `--dolacz` (junction) albo przez przeniesienie zaraz po wygenerowaniu. Dzięki temu `usun` nie odmawia z powodu plików tylko lokalnych.
  - Kod 0 → dalej. Kod 1 (gałąź lub folder istnieje, `git status` nieczysty, błąd dowiązania) → zgłaszam i nie otwieram okna.
  - Gałąź bieżąca `Domino` nie ma znaczenia: nie pytam o nią i niczego w `Domino` nie przełączam.
  - `/zapisz` i `/zamknij` wykonuje użytkownik w oknie zadania (sesja realizująca nie commituje). `/zamknij` w worktree robi merge w `Domino` i nie usuwa folderu, w którym sam działa.
  - Tekst do „Zasad sesji”: „Git: worktree .worktrees/<temat>, gałąź <temat>; nie przełączaj gałęzi; /zapisz i /zamknij wykonuje użytkownik w tym oknie. Dane klienta (pliki ignorowane przez git: eksporty, pliki od klienta, raporty z danymi, zrzuty) zapisuj na bieżąco w Domino pod tą samą ścieżką względną (C:\Users\Admin\Desktop\Domino\<ścieżka>), nie w worktree. Gdy narzędzie zapisze je w worktree, przenieś je do Domino zaraz po wygenerowaniu. W worktree zostają tylko pliki do commita.”
- **Sprzątanie na starcie:** przed krokiem 4 uruchamiam `worktree_zadania.py lista`. Worktree „SCALONA z main” proponuję usunąć jednym zdaniem: „zamknij okno VS Code zadania <temat>, a usunę worktree”. Po zgodzie: `worktree_zadania.py usun <temat>`. Skrypt odmawia, gdy są niezapisane zmiany, gałąź jest niescalona albo są pliki tylko lokalne. `--sila` tylko na wyraźną prośbę użytkownika.
