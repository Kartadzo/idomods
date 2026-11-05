---
name: zadanie
description: Zadanie ClickUp → krótka analiza i propozycja realizacji → po akceptacji folder projektu w SI ze wstępną analizą → nowe okno terminala z Claude Code pracującym w tym folderze. Zadania obsługiwane przez istniejący skill (weryfikacja-fb, weryfikacja-gmc, summonfeed, wiadomosci-transakcyjne) od razu uruchamia w nowym oknie z tym skillem. Używaj, gdy użytkownik wywołuje /zadanie <link>, wkleja link do zadania ClickUp z prośbą o analizę/propozycję/realizację, mówi „przeanalizuj zadanie”, „weź to zadanie”, „co z tym zadaniem w ClickUp”.
---

# /zadanie — zadanie ClickUp → analiza → folder → sesja realizująca

Specyfikacja i decyzje: `SI/02_Serwisy/ClickUp/Zadania_ClickUp/ANALIZA_skill_zadanie_clickup.md`. Mapa SI, tabela projektów i zasady folderów: `SI/README.md` (czytam przed krokiem 2).
Repo: `C:\Users\Admin\Desktop\Domino`. Launcher okna: `SI/02_Serwisy/ClickUp/Zadania_ClickUp/uruchom_sesje.bat`.

## Zasady (zawsze)
- **ClickUp tylko do odczytu.** Nie komentuję, nie zmieniam statusu, terminu, osób ani podzadań. Komentarz dla klienta/zespołu przygotowuje sesja realizująca jako `komentarz_clickup.txt` — użytkownik wkleja go sam.
- Załączników nie pobieram bez zgody (podaję nazwę i rozmiar, pytam).
- **Narzędzia przeglądarki** (ustalenie użytkownika 2026-11-05):
  - **Chrome DevTools MCP („webtools”, osobny profil):**
    - zamówienia testowe;
    - sprawdzanie zdarzeń na stronie sklepu: zapytania sieciowe `gtag`/`fbq`/`ttq` i inne, dataLayer, podwójne odpalenia, wartości.
  - **Claude in Chrome:** reszta, czyli panele IdoSell, Events Manager, Google Ads, TikTok i GMC, gdzie użytkownik jest zalogowany.
  - Gdy inne działanie byłoby wydajniejsze w DevTools, proponuję to i pytam, zamiast przenosić je samemu.
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
Folder: <ścieżka>  ·  Git: nowa gałąź <temat>
Pytania blokujące: tylko te, bez których nie da się zacząć
```
Kończę: „Realizować? Folder: `<ścieżka>`”. Czekam. Poprawki użytkownika wprowadzam do propozycji przed krokiem 4.

## 4. Folder i wstępna analiza (po akceptacji)
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
- Karta startuje w folderze workspace (`Domino`), nie w folderze zadania. Dlatego prompt **zawsze podaje ścieżkę folderu** i każe w nim zapisywać pliki. Polskie znaki są dozwolone, bo prompt idzie przez URL-encoding. Przykład:
  `Zadanie ClickUp <link> (<klient> - <temat>). Folder zadania: SI/<ścieżka>. Przeczytaj ANALIZA_<temat>.md w tym folderze oraz SI/README.md, potwierdź plan ze mną i realizuj zgodnie z sekcją Zasady sesji. Wszystkie pliki zapisuj w tym folderze.`
- Wywołanie (narzędzie **PowerShell**):
  ```powershell
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
- **Wariant „nowy problem”:** przed startem okna przełączam na nową gałąź `git switch -c <temat>`; `/zapisz` i `/zamknij` wykonuje użytkownik (sesja realizująca nie commituje).
- Gałąź zakładam tylko od `main`. Jeśli bieżąca gałąź ≠ `main` → pytam: przełączenie przeniosłoby z dysku pliki tamtej gałęzi, a drzewo jest wspólne dla wszystkich okien i VS Code.
