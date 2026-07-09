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

1. **Wybór struktury** - Wybierz jeden z dostępnych feedów (Google, Facebook, Samba)
2. **Filtrowanie parametrów** - Aplikacja automatycznie pokaże tylko parametry obsługiwane dla wybranej struktury
3. **Wybór parametrów** - Dla każdego kontekstu (product, size, feed) wybierz jakie parametry wstawić
4. **Uzupełnienie configVars** - Jeśli parametr wymaga zmiennych konfiguracyjnych, generator zapyta o nie raz
5. **Generowanie** - Aplikacja wygeneruje plik XSLT z wybranymi parametrami
6. **Zapisanie** - Wynik zostanie zapisany w głównym folderze `summonFeed/` z datą i czasem

## Struktura projektu

```
summonFeed/
├── summonFeed_generator.py          # Główna aplikacja
├── structure_templates/             # Szablony struktur feedów (szkielety)
│   ├── google.json / google.xsl
│   ├── facebook.json / facebook.xsl
│   └── samba.json / samba.xsl
├── parameters_templates/            # Szablony parametrów produktu (sama emisja)
│   ├── title.json / title.xsl
│   ├── price.json / price.xsl
│   ├── size.json / size.xsl
│   └── ... (wiele więcej)
├── variables/                       # Zmienne obliczeniowe i globalne (1 plik = 1 zmienna)
│   ├── _registry.json               #   rejestr: order, uses, scope
│   ├── avail_perProduct.xsl
│   ├── upperLetters.xsl             #   (scope: global)
│   └── ...
└── helpers/                         # Biblioteka helperów (1 plik = 1 named template)
    ├── _registry.json               #   rejestr: uses (domknięcie), globals
    ├── wordFormat.xsl
    └── ...
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
  "description": "Buduje g:color z wartości ...",  // Opis widoczny w menu wyboru
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

Jeśli parametr ma tablicę `configVars`, generator zapyta o każdą wartość raz (krok 4 przepływu). Każdy wpis: `name`, `default`, opcjonalny `delimeter`. Formatowanie wpisanej wartości zależy od `delimeter`:

- brak `delimeter` → wartość wstawiana bez zmian (np. `399.00`),
- jeden wyraz → otoczony separatorem (`kolor` + `|` → `|kolor|`),
- wiele wyrazów (spacja) → separator między i na końcach (`kolor rozmiar` + `|` → `|kolor|rozmiar|`).

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

Aby dodać nowy parametr:

1. Utwórz `parameters_templates/nazwa.json` (opis) i `nazwa.xsl` (sama emisja).
2. Zmienne obliczeniowe wynieś do `variables/nazwa_zmiennej.xsl` i dodaj wpis do `variables/_registry.json` (`order`, `uses`); wymień je w `createVars` parametru.
3. Jeśli parametr używa helpera → dodaj go do `helpers: [...]`; nowy helper to plik w `helpers/` + wpis w `helpers/_registry.json`.
4. Stałe globalne → plik w `variables/` z `"scope": "global"` w rejestrze.
5. Aplikacja wykryje wszystko automatycznie (po nazwach i rejestrach).

Aby dodać nową strukturę:

1. Utwórz plik JSON w `structure_templates/` z definicją (`insertionPoints`).
2. Utwórz plik XSLT w `structure_templates/` z pustymi szablonami.
3. Aplikacja automatycznie je wykryje.
