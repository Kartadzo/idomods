# Meta (Facebook) — wymagania feedu
- Źródła:
  - https://www.facebook.com/business/help/120325381656392?id=725943027795860 (specyfikacje danych produktów do katalogów w Menedżerze sprzedaży)
  - https://www.facebook.com/business/help/609872007120910 (dodawanie dodatkowego zestawienia/źródła danych do katalogu)
  - https://mypresta.eu/en/art/know-how/facebook-list-of-local-language-codes.html (kody języków, pomocniczy)
- Data przeglądu: 2026-10-27
- Format: nie ustalono ze źródeł (strony Meta niedostępne), akceptuje format Google: nie ustalono ze źródeł
- Szablon bazowy: Facebook.xml (istniejący szablon w repozytorium; wybór na podstawie nazwy, nie treści specyfikacji)

## Pola wymagane
Nie ustalono — strona specyfikacji Meta nie zwróciła treści (patrz Uwagi).

| pole | opis/format | limit |
|---|---|---|
| — | brak danych ze źródła | — |

## Pola zalecane / opcjonalne istotne
Nie ustalono — brak danych ze źródła.

| pole | opis/format | limit |
|---|---|---|
| — | brak danych ze źródła | — |

## Limity i formaty
- Długości tytułu/opisu, wymagania zdjęć, waluta, rozmiar pliku: nie ustalono (strony Meta niedostępne).
- Kody języków (źródło pomocnicze mypresta.eu): format `jj_KK` — mała litera języka, podkreślnik, wielka litera kraju. Przykłady: `pl_PL`, `en_US`, `en_GB`, `de_DE`, `cs_CZ`, `sk_SK`, `uk_UA`, `fr_FR`, `fr_CA`, `es_ES`, `es_LA`, `es_MX`, `it_IT`, `nl_NL`, `nl_BE`, `lt_LT`, `ro_RO`, `hu_HU`. Uwaga: ukraiński to `uk_UA` (nie `ua_UA`), czeski `cs_CZ` (nie `cz_CZ`). Lista ma charakter pomocniczy (strona zewnętrzna, nie Meta) i przydaje się przy zestawieniach językowych/krajowych katalogu.

## Różnice względem szablonu Google.xml
- Nie ustalono ze źródeł Meta. Do weryfikacji po ręcznym odczycie strony: obsługiwane formaty (XML RSS/ATOM, CSV, TSV, Arkusze Google), zgodność z prefiksem `g:`, wartości `availability` i `condition`, limity tytułu/opisu, pola specyficzne Meta (np. `rich_text_description`, `fb_product_category`, `quantity_to_sell_on_facebook`) — wymienione tu wyłącznie jako lista kontrolna, nie potwierdzone treścią źródła.

## Uwagi
- Obie strony facebook.com/business/help zwróciły przez WebFetch wyłącznie tytuł (treść ładowana dynamicznie/za JavaScriptem). Ponowna próba bez parametru `?id=` dała ten sam wynik. Treści nie zgadywano.
- Tytuł strony 120325381656392: „Specyfikacje danych produktów do katalogów w Menedżerze sprzedaży”.
- Tytuł strony 609872007120910 dotyczy dodawania dodatkowego zestawienia (źródła danych) do katalogu w Menedżerze sprzedaży.
- Aby uzupełnić plik: otworzyć strony w przeglądarce (np. Claude in Chrome) lub wkleić ich treść.
