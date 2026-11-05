# summonFeed — edytor parametrów i struktur (projekt)

Data: 2026-07-30

## Cel

Osobna aplikacja GUI (tkinter) do **tworzenia i aktualizowania** plików bazy summonFeed:
parametrów (`parameters_templates/`), struktur (`structure_templates/`) oraz towarzyszących im
zmiennych (`variables/`) i helperów (`helpers/`) wraz z wpisami w ich rejestrach.

Dziś te pliki powstają ręcznie — łatwo o literówkę w polu `name`, deklarację zmiennej w formie,
której generator nie podmienia, albo brak wymaganego pola. Edytor pilnuje tych reguł przy zapisie.

## Moduły

| Plik | Odpowiedzialność |
|---|---|
| `summonFeed_editor.py` | GUI: 7 kroków kreatora, widżety, przyciski **Kontynuuj**/**Cofnij** w prawym górnym rogu każdego okna |
| `summonFeed_editor_model.py` | logika bez tkintera: odczyt/zapis JSON+XSL, backup, kolizje nazw, normalizacja deklaracji zmiennych, wykrywanie duplikatów, wywołanie walidatora |
| `lang/editor_pl.json`, `lang/editor_en.json` | teksty interfejsu; brak języka → angielski, brak klucza → nazwa klucza |

Rozdział GUI/logika jest po to, by całą logikę zapisu dało się przetestować headless — tak jak
testowany jest generator. Aplikacja czyta katalogi przez `SummonFeedGenerator` (lista struktur,
zmiennych globalnych, grup `exclusiveGroup`), żeby nie duplikować wiedzy o układzie repozytorium.

## Przepływ kreatora

1. **Język** — wybór z dostępnych plików `lang/editor_*.json`.
2. **Zakres operacji** — typ elementu (parametr / struktura) oraz tryb: nowy element,
   aktualizacja (wskazanie pliku `.json`), zamknij aplikację.
   Wskazany plik niepasujący do wybranego typu → monit i oczekiwanie na poprawę.
   Rozpoznanie typu: obecność `insertionPoints` → struktura; `context` ∈ {product, size, feed} → parametr.
   Wczytana konfiguracja staje się tymczasowymi wartościami domyślnymi formularza.
3. **Formularz** — zależny od typu (poniżej). Pole `name` waliduje się na bieżąco: kolizja →
   czerwona ramka, komunikat, zablokowany **Kontynuuj**. Przy aktualizacji kolizją jest wyłącznie
   zmiana nazwy na inną, już zajętą.
4. **Decyzje** — konflikty wykryte przy planowaniu zapisu (patrz niżej).
5. **Backup i zapis** — kopie do `_backup/RRRR-MM-DD_GG-MM-SS/`, potem zapis plików i rejestrów.
6. **Walidacja** — uruchomienie `validate_params.py`, pełne wyjście w oknie.
7. **Kontynuacja** — powrót do kroku 2 albo zamknięcie.

## Formularz — struktura

Edytowane: `name`, `description`, `description_pl`, `output` (domyślnie `rss/channel/item`), `notes`,
plus pole na szkielet XSL.

Pozostałe pola domyślne: `context: "feed"`, `xpathCandidates: ["/offer/products/product"]`,
`parameterContexts: []`, `configVars: []`, `helpers: []`,
`insertionPoints`: `product`/product + `productSizeMatter`/size, `defaultXslt` wyliczone z nazwy.

Szkielet XSL wkleja użytkownik. Aplikacja sprawdza, czy zawiera puste named templates zgodne
z `insertionPoints`, i ostrzega w kroku 4, gdy któregoś brak.

Nazwa pliku: `name` małymi literami (`Google` → `google.json` + `google.xsl`) — zgodnie ze stanem repo.

## Formularz — parametr

Edytowane: `name`, `description`, `description_pl`, `output` (domyślnie kopia `name`),
`structure` (checkboxy), `context` (radio: product/size/feed), `exclusiveGroup` (z podpowiedzią
istniejących grup) + `exclusiveDefaultFor` (ograniczone do zaznaczonych struktur),
`xpathCandidates`, `parameterContexts`, `configVars`, `globals`, `helpers`, `notes`,
plus pole na kod XSL parametru.

`structure` i `context` są wymagane przez generator i walidator — bez nich plik jest niepoprawny.

Nazwa pliku: dokładnie `name` (walidator wymaga `name` == nazwa pliku).

### configVars

Zestawy dorastające: po wypełnieniu `name` pojawia się kolejny pusty. Pola: `name`, `default`,
`delimeter` oraz przełącznik **wydziel do `variables/`** (domyślnie wyłączony).

Po włączeniu przełącznika dochodzą: `scope` (globalna / lokalna), `order`, `uses` oraz pole na kod
XSL zmiennej. Skutek zapisu: plik `variables/{name}.xsl`, wpis w `variables/_registry.json`
(`{"scope": "global"}` albo `{"order": N, "uses": [...]}`), a nazwa trafia do `createVars` parametru.

### helpers

Zestawy dorastające: `name`, kod szablonu, `uses`, `globals`. Skutek zapisu: plik
`helpers/{name}.xsl` oraz wpis w `helpers/_registry.json`.

### globals

Przełącznik odsłaniający listę istniejących zmiennych globalnych (nieedytowalną) do zaznaczenia.
Pole jest dokumentacyjne — generator wykrywa globalne po referencji `$nazwa`.

## Normalizacja deklaracji zmiennych

Przy zapisie każda deklaracja postaci `<xsl:variable name="x" select="'v'"/>` jest zamieniana na
`<xsl:variable name="x">v</xsl:variable>`.

Powód: ścieżka *legacy* generatora podmienia wyłącznie drugą formę. Deklaracja z `select=` jest
po cichu ignorowana, a parametr zawsze bierze wartość domyślną — dokładnie ten błąd dotknął
`corrected` w `title.xsl`.

## Konflikty (krok 4)

| Sytuacja | Zachowanie |
|---|---|
| helper/zmienna o tej nazwie istnieje, treść identyczna | pomijane bez pytania |
| helper/zmienna o tej nazwie istnieje, treść inna | pokazane obok siebie (istniejący / nowy), wybór: zostaw istniejący / nadpisz |
| szkielet struktury bez wymaganego named template | ostrzeżenie, możliwość powrotu do formularza |
| kolizja nazwy pliku głównego | blokowana wcześniej, w kroku 3 |

## Backup i zapis

Przed zapisem kopie wszystkich nadpisywanych plików trafiają do
`summonFeed/_backup/RRRR-MM-DD_GG-MM-SS/` z zachowaniem ścieżek względnych.

Wpisy w rejestrach dopisywane tekstowo (wstawienie linii przed zamykającym nawiasem), by zachować
komentarz `_comment` i istniejące formatowanie. Wpis o tej samej nazwie jest podmieniany w miejscu.

## Walidacja (krok 6)

`validate_params.py` uruchamiany jako podproces, pełne wyjście prezentowane w oknie.
Błędy nie cofają zapisu — ekran ma przycisk powrotu do formularza, a kopie z backupu pozwalają wrócić.

## Poza zakresem

Edycja `insertionPoints` i `defaultXslt` w GUI, podgląd wygenerowanego feedu, usuwanie istniejących
parametrów, edycja plików innych niż wymienione.
