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
4. **Generowanie** - Aplikacja wygeneruje plik XSLT z wybranymi parametrami
5. **Zapisanie** - Wynik zostanie zapisany w głównym folderze `summonFeed/` z datą i czasem

## Struktura projektu

```
summonFeed/
├── summonFeed_generator.py          # Główna aplikacja
├── structure_templates/             # Szablony struktur feedów
│   ├── google.json / google.xsl
│   ├── facebook.json / facebook.xsl
│   └── samba.json / samba.xsl
└── parameters_templates/            # Szablony parametrów produktu
    ├── title.json / title.xsl
    ├── price.json / price.xsl
    ├── size.json / size.xsl
    └── ... (wiele więcej)
```

## Jak działają pliki konfiguracji

### Structure Templates (struktura feedu)

Plik JSON definiuje strukturę całego feedu, np. `google.json`:

```json
{
  "name": "google_structure",
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

Plik JSON definiuje pojedynczy parametr, np. `title.json`:

```json
{
  "name": "title",
  "description": "Tytuł produktu",
  "structure": ["Google", "Facebook", "Samba"],  // Gdzie ten parametr jest dostępny
  "context": "product",                           // W jakim kontekście go wstawić
  "output": "g:title",                            // Nazwa elementu XML na wyjściu
  "defaultXslt": "parameters_templates/title.xsl" // Ścieżka do kodu XSLT
}
```

Odpowiadający plik XSLT zawiera fragment kodu do wstawienia.

## Wyjście aplikacji

Wygenerowany plik XSLT będzie miał nazwę:

```
{struktura}_generated_{datę_czas}.xsl
```

Na przykład:
```
google_generated_20260626_143025.xsl
```

## Rozwiązywanie problemów

### Aplikacja nie widzi plików JSON

- Sprawdź czy jesteś w głównym folderze `summonFeed/`
- Sprawdź czy katalogi `structure_templates/` i `parameters_templates/` istnieją

### Błąd kodowania znaków

- Upewnij się że pliki JSON są zapisane w kodowaniu UTF-8

### XSLT nie wstawia się prawidłowo

- Sprawdź czy nazwy szablonów w `insertionPoints` w JSON struktury odpowiadają nazwom w plikach XSLT
- Sprawdzź czy konteksty w JSON parametrów odpowiadają kontekstom w strukturze

## Rozszerzanie aplikacji

Aby dodać nowy parametr:

1. Utwórz plik JSON w `parameters_templates/` z opisem parametru
2. Utwórz plik XSLT w `parameters_templates/` z kodem
3. Aplikacja automatycznie je wykryje

Aby dodać nową strukturę:

1. Utwórz plik JSON w `structure_templates/` z definicją
2. Utwórz plik XSLT w `structure_templates/` z pusty szablonami
3. Aplikacja automatycznie je wykryje
