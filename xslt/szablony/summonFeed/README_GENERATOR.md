# SummonFeed XSLT Generator

Aplikacja do generowania sterowników XSLT na podstawie wybranych struktur feedu i parametrów produktu.

## Wymagania

- Python 3.7+
- Dostęp do plików w folderach `structure_templates/` i `parameters_templates/`

## Instalacja

1. Aplikacja znajduje się w głównym folderze `summonFeed/`
2. Brak zewnętrznych zależności - wszystko oparcie na bibliotece standardowej Python

## Użycie

### Uruchomienie aplikacji

```bash
python summonFeed_generator.py
```

Lub ze wskazaniem bezpośredniej ścieżki:

```bash
python c:\Users\Admin\Desktop\Domino\xslt\szablony\summonFeed\summonFeed_generator.py
```

### Przepływ aplikacji

0. **Wybór języka** - Na starcie generator pyta o język interfejsu (lista z folderu `lang/`)
1. **Wybór struktury** - Wybierz jeden z dostępnych feedów (Google, Facebook, Samba)
2. **Filtrowanie parametrów** - Aplikacja automatycznie pokaże tylko parametry obsługiwane dla wybranej struktury
3. **Wybór parametrów** - Dla każdego kontekstu (product, size, feed) wybierz jakie parametry wstawić
4. **Nazwy elementów wyjściowych** - Opcjonalnie zmień prefiks `g:` oraz nazwę elementu każdego parametru (Enter = domyślne)
5. **Uzupełnienie configVars** - Jeśli parametr wymaga zmiennych konfiguracyjnych, generator zapyta o nie raz
6. **Generowanie** - Aplikacja wygeneruje plik XSLT z wybranymi parametrami
7. **Zapisanie** - Wynik zostanie zapisany w głównym folderze `summonFeed/` z datą i czasem

## Struktura projektu

```
summonFeed/
├── summonFeed_generator.py          # Główna aplikacja
├── validate_params.py               # Walidator spójności bazy parametrów
├── structure_templates/             # Szablony struktur feedów (szkielety)
│   ├── google.json / google.xsl
│   ├── facebook.json / facebook.xsl
│   └── samba.json / samba.xsl
├── parameters_templates/            # Szablony parametrów produktu (sama emisja)
│   ├── _TEMPLATE.json / _TEMPLATE.xsl   # szkielet nowego parametru ('_' = pomijane)
│   ├── title.json / title.xsl
│   ├── price.json / price.xsl
│   ├── size.json / size.xsl
│   └── ... (wiele więcej)
├── variables/                       # Zmienne obliczeniowe i globalne (1 plik = 1 zmienna)
│   ├── _registry.json               #   rejestr: order, uses, scope
│   ├── avail_perProduct.xsl
│   ├── upperLetters.xsl             #   (scope: global)
│   └── ...
├── helpers/                         # Biblioteka helperów (1 plik = 1 named template)
│   ├── _registry.json               #   rejestr: uses (domknięcie), globals
│   ├── wordFormat.xsl
│   └── ...
└── lang/                            # Pliki językowe interfejsu (1 plik = 1 język)
    ├── pl.json                      #   kod języka = nazwa pliku; klucz "_name" = etykieta w menu
    └── en.json
```

**Zasada „1 byt = 1 plik, bez analizy kodu":** parametr (`.xsl`) zawiera tylko emisję docelowego elementu; zmienne obliczeniowe mieszkają w `variables/`, helpery w `helpers/`. Generator składa je po nazwach (z rejestrów), nie parsując kodu XSLT.

## Jak działają pliki konfiguracji

### Structure Templates (struktura feedu)

Plik JSON definiuje strukturę całego feedu, np. `google.json`:

```json
{
  "name": "Google",
  "description": "Struktura dla Google Shopping",
  "insertionPoints": [
    {
      "template": "product",      // Nazwa szablonu XSLT
      "context": "product"        // Kontekst (do jakiego elementu wstawić)
    },
    {
      "template": "productSizeMatter",
      "context": "size"
    }
  ]
}
```

Odpowiadający plik XSLT zawiera puste szablony, które aplikacja będzie wypełniać.

### Parameter Templates (elementy produktu)

Każdy parametr to para plików o **tej samej nazwie bazowej**: `nazwa.json` (opis) + `nazwa.xsl` (sama emisja). Generator paruje je po nazwie pliku.

Przykład `color.json`:

```json
{
  "name": "color",                                 // Nazwa parametru (musi być unikalna)
  "description": "Build g:color from ...",         // Opis EN (menu przy języku 'en')
  "description_pl": "Buduje g:color z ...",        // Opis PL (menu przy języku 'pl')
  "structure": ["Google", "Facebook"],             // W których strukturach parametr jest dostępny
  "context": "product",                            // Kontekst wstawienia: product / size / feed
  "output": "g:color",                             // Nazwa elementu XML na wyjściu (podsumowanie)
  "configVars": [                                  // Zmienne konfiguracyjne uzupełniane przez użytkownika
    { "name": "kolor_nazwa_w_panelu", "default": "|kolor|", "delimeter": "|" }
  ],
  "createVars": ["value", "value_tokenized"],      // Zmienne obliczeniowe z variables/ (jeśli wynoszone)
  "helpers": ["tokenize"],                         // Named templates z helpers/ do dołączenia
  "globals": ["upperLetters", "lowerLetters"],     // Informacyjne — zmienne globalne używane przez parametr
  "xpathCandidates": [ "..." ],                    // Informacyjne — źródła danych (dla człowieka)
  "parameterContexts": ["CONTEXT_COLOR"],          // Informacyjne
  "notes": "..."                                   // Informacyjne — notatki dla utrzymującego
}
```

Pola faktycznie czytane przez generator: `name`, `description`, `structure`, `context`, `configVars`, `createVars`, `helpers` (oraz `output` w podsumowaniu). Pozostałe (`globals`, `xpathCandidates`, `parameterContexts`, `notes`) są **wyłącznie dokumentacyjne** (zmienne globalne wykrywane są automatycznie po referencji — patrz niżej).

**Parametr „zmigrowany" vs „legacy":** jeśli wszystkie nazwy z `createVars` są w `variables/_registry.json`, parametr jest *zmigrowany* — jego `.xsl` to sama emisja, a zmienne i configVary wstrzykiwane są centralnie w **preambule** kontekstu (raz, zdeduplikowane). W przeciwnym razie działa ścieżka *legacy* (zmienne inline w `.xsl`, configVary podmieniane w miejscu). Oba tryby współistnieją.

Zmienne **branch-local** (deklarowane wewnątrz `<xsl:when>`/`<xsl:if>`, zależne od zmiennych tej gałęzi) zostają inline w `.xsl` parametru — nie da się ich wynieść do `variables/`.

### configVars — zmienne konfiguracyjne

Jeśli parametr ma tablicę `configVars`, generator zapyta o każdą wartość. Każdy wpis: `name`, `default`, opcjonalny `delimeter`. Sposób pytania zależy od `delimeter`:

- **brak `delimeter`** → jedno pytanie, wartość wstawiana bez zmian (Enter = `default`), np. `399.00`.
- **z `delimeter`** → tryb **fraza po frazie**: generator prosi o kolejne wartości (pusty Enter kończy), po czym otacza je separatorem. Dzięki temu **wartości wielowyrazowe** działają poprawnie:
  - wpisy `materiał dominujący`, `rodzaj skóry` → `|materiał dominujący|rodzaj skóry|`,
  - brak wpisów (od razu Enter) → wartość `default` (w JSON już otoczona separatorem, np. `|materiał|`).

W parametrze *zmigrowanym* configVar staje się deklaracją `<xsl:variable>` na górze preambułu (przed createVars, bo te często jej używają); w *legacy* podmienia istniejącą deklarację w `.xsl`.

### variables/ — zmienne obliczeniowe (rejestr)

`variables/` to zmienne wynoszone z parametrów, po jednej na plik (`nazwa.xsl` = jedna `<xsl:variable name="nazwa">`). `variables/_registry.json` opisuje każdą:

```json
"avail_perProduct": { "order": 20, "uses": ["stocksGobalCheck_perProduct"] }
```

- `order` — kolejność deklaracji w preambule (mniejsze pierwsze; zależność musi mieć `order` ≤ dependenta),
- `uses` — inne zmienne, których ta zmienna używa (generator domyka je automatycznie).

Generator dla wybranych parametrów zbiera ich `createVars`, **domyka zależności** wg `uses`, sortuje po `order`, deduplikuje i wstawia raz na górze szablonu danego kontekstu.

**Warianty nazw:** ta sama logika w różnych kontekstach danych dostaje osobne pliki z sufiksem wariantu — `_perSize` (bieżący rozmiar) vs `_perProduct` (agregat po wszystkich rozmiarach). W przyszłości kolejne `_perX`. Dzięki temu jedna nazwa = jedno ciało (bezpieczna deduplikacja).

### Zmienne globalne (feed-scope)

Stałe i zmienne wspólne dla całego arkusza (`upperLetters`, `lowerLetters`, `unitsList`, `corrected`, `Kraj_dostawy`, czasy dostawy…) leżą w `variables/` z `"scope": "global"` w rejestrze. Muszą być globalne, bo helpery (np. `wordFormat`, `extract-measure`) ich wymagają — w XSLT 1.0 named template nie widzi zmiennych lokalnych wołającego.

Generator **wstrzykuje je automatycznie**: po złożeniu arkusza skanuje go i dla każdej globalnej referowanej (`$nazwa`), a jeszcze niezadeklarowanej, wstawia jej deklarację tuż po `<xsl:output>`. Nie trzeba deklarować globali w parametrach — pole `globals` w JSON jest tylko dokumentacją.

### helpers/ — biblioteka named templates (rejestr)

`helpers/` to nazwane szablony, po jednym na plik. `helpers/_registry.json` opisuje każdy:

```json
"wordFormat": { "uses": ["has-polish-pair"], "globals": ["corrected", "upperLetters", "lowerLetters"] }
```

- `uses` — inne helpery wołane przez ten helper (**domknięcie** — generator dołączy je nawet gdy parametr ich nie wymienił),
- `globals` — zmienne globalne, których helper wymaga (dokumentacja; realnie wykrywane po referencji).

Parametr deklaruje `helpers: [...]`; generator zbiera je, **domyka wg `uses`**, deduplikuje i wstawia raz przed `</xsl:stylesheet>`. Kolejność helperów jest nieistotna (named templates).

### lang/ — języki interfejsu

Folder `lang/` zawiera po jednym pliku JSON na język (`pl.json`, `en.json`, …). Kod języka = nazwa pliku; klucz `"_name"` to etykieta w menu wyboru. Pozostałe klucze to teksty UI z miejscami `{...}` na `format()`.

Generator wczytuje wszystkie pliki z `lang/` i w kroku 0 pozwala wybrać język. Opisy parametrów pobierane są wg języka: `description_pl` dla `pl`, `description` (EN) dla `en`, z fallbackiem na drugi. **Dodanie języka = dodanie pliku** `lang/kod.json` (i opcjonalnie `description_<kod>` w parametrach) — bez zmian w kodzie.

### Nazwy elementów wyjściowych i prefiks

W kroku 4 generator pozwala:

- **zmienić prefiks** przestrzeni nazw `g:`:
  - Enter → zostaw `g:` (np. `<g:color>`),
  - inny prefiks, np. `c` → zmiana spójna w deklaracji `xmlns` i wszystkich elementach (`<c:color>`, `xmlns:c="…"`),
  - `-` → **brak prefiksu**: elementy bez `g:` (`<color>`), a nieużywana deklaracja `xmlns:g` jest usuwana; elementy trafiają do przestrzeni „bez namespace". Parametry już bez prefiksu (np. `quantity_to_sell_on_facebook`) pozostają bez zmian.
- **zmienić nazwę elementu** każdego parametru na własną (Enter = domyślna z pola `output`). Podmiana obsługuje formy `<xsl:element name="…">`, `<…>` i `</…>`; dla parametru emitującego kilka elementów zmienia element główny (`output`).

## Wyjście aplikacji

Aktualnie generator zapisuje plik pod nazwą:
```
{struktura}_generated_{data_czas}.xsl
```

Na przykład:
```
Google_generated_20260626_143025.xsl
```

Nazwa struktury pochodzi z pola `name` w JSON struktury (np. `Google`, `Facebook`, `Samba`).

> **Uwaga:** zapis pod nazwą podaną przez użytkownika (`{nazwa}.xsl`) jest planowany — nie ma go jeszcze w kodzie.

## Rozwiązywanie problemów

### Aplikacja nie widzi plików JSON

- Sprawdź czy jesteś w głównym folderze `summonFeed/`
- Sprawdź czy katalogi `structure_templates/` i `parameters_templates/` istnieją

### Błąd kodowania znaków

- Upewnij się że pliki JSON są zapisane w kodowaniu UTF-8

### XSLT nie wstawia się prawidłowo

- Sprawdź czy nazwy szablonów w `insertionPoints` w JSON struktury odpowiadają nazwom w plikach XSLT
- Sprawdzź czy konteksty w JSON parametrów odpowiadają kontekstom w strukturze

### Duplikat zmiennej / „Redefinition of variable"

- Dwa parametry deklarują tę samą zmienną top-level inline (legacy). Rozwiązanie: wynieś ją do `variables/` (dodaj do `createVars` obu i wpis w `_registry.json`) — preambuł zadeklaruje ją raz.
- Jeśli to stała wspólna dla całego arkusza — przenieś do globali (`"scope": "global"`).

### „Undefined variable" / „template not found"

- Helper woła zmienną globalną, która jest deklarowana lokalnie → przenieś ją do globali (`variables/` + `scope: global`).
- Parametr woła helper, którego nie ma w `helpers` → dodaj go (domknięcie `uses` dobierze zależne).

## Rozszerzanie aplikacji

> Pliki zaczynające się od `_` (np. `_TEMPLATE.json`, `_registry.json`) są **pomijane** przez generator.

### Szablon i walidator

- **`parameters_templates/_TEMPLATE.json` + `_TEMPLATE.xsl`** — gotowy szkielet nowego parametru z opisem wszystkich pól i zasad (co wolno trzymać w `.xsl`, a co wynieść).
- **`validate_params.py`** — sprawdza spójność bazy: `python validate_params.py` (exit 0 = OK).
  Wykrywa m.in.: helper zadeklarowany bez pliku, helper wołany w `.xsl` a niezadeklarowany, `createVar` spoza rejestru i bez deklaracji inline, brak pliku zmiennej, `output` nieobecny w `.xsl`, złą kolejność `order` względem `uses`, martwe `createVars`/`configVars`, referencje `$zmienna` bez deklaracji.

### Dodanie nowego parametru — krok po kroku

1. Skopiuj `_TEMPLATE.json` → `nazwa.json` i `_TEMPLATE.xsl` → `nazwa.xsl` (ta sama nazwa bazowa; `name` w JSON = nazwa pliku).
2. Uzupełnij `description` (EN) i `description_pl` (PL), `structure`, `context`, `output`.
3. W `.xsl` zostaw **wyłącznie emisję** elementu. Zmienne:
   - **poziom szablonu** → `variables/nazwa_zmiennej.xsl` + wpis w `variables/_registry.json` (`order`, `uses`), a nazwy wypisz w `createVars`,
   - **branch-local** (wewnątrz `<xsl:when>`/`<xsl:if>`) → zostają w `.xsl`,
   - **globalne** (np. `$upperLetters`) → nie deklaruj, są auto-wstrzykiwane.
4. Helpery: wypisz w `helpers: [...]`. Nowy helper = plik w `helpers/` + wpis w `helpers/_registry.json` (`uses`, `globals`).
5. `configVars`: przy wartościach listowych ustaw `delimeter` (generator zapyta frazami), a `default` zapisz już otoczony separatorem (`|kolor|`).
6. Uruchom **`python validate_params.py`**, a następnie wygeneruj feed i sprawdź wynik na próbce (`products_export.xml`).

### Aktualizacja istniejącego parametru z arkusza klienta

1. Wyodrębnij blok `<xsl:element name="g:…">` ze źródłowego arkusza (np. `xslt/szablony/Facebook.xml`).
2. Sprawdź, jakich **helperów** i **zmiennych globalnych** używa; brakujące dodaj do `helpers/` i `variables/` wraz z wpisami w rejestrach.
3. Jeśli wariant różni się od istniejącego (inne pola/logika), **utwórz osobny parametr** z sufiksem kanału (jak `availability_facebook`, `shipping_facebook`) zamiast nadpisywać wspólny.
4. `validate_params.py` → generacja → porównanie wyniku.

### Dodanie nowej struktury

1. Utwórz plik JSON w `structure_templates/` z definicją (`insertionPoints`).
2. Utwórz plik XSLT w `structure_templates/` z pustymi szablonami.
3. Aplikacja automatycznie je wykryje.

### Dodanie nowego języka

Dodaj `lang/kod.json` (klucz `_name` = etykieta w menu) — bez zmian w kodzie. Opcjonalnie `description_<kod>` w parametrach.
