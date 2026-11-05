# Samba.ai — wymagania feedu
- Źródła: https://doc.samba.ai/knowledge-base/datove-feedy/?lang=en
- Data przeglądu: 2026-10-27
- Format: własny XML (`<PRODUCTS>` → `<PRODUCT>`), akceptuje format Google: nie (dokumentacja nie wspomina o formacie Google ani o CSV)
- Szablon bazowy: `samba.xml` — własna struktura wielkimi literami, zagnieżdżone warianty i parametry NAME/VALUE; szablon Google wymagałby przebudowy całej struktury.

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| PRODUCT_ID | tekst; musi być zgodny z ID używanym w feedzie zamówień | — |
| TITLE | nazwa produktu, tekst | — |
| PRICE | liczba zmiennoprzecinkowa ≥ 0; cena sprzedaży brutto (z VAT), bez kosztu dostawy | ≥ 0 |
| URL | adres karty produktu | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| IMAGE | URL zdjęcia, ok. 300×300 px; formalnie opcjonalne, ale bez niego produkt nie jest rekomendowany | — |
| DESCRIPTION | czysty tekst, bez znaczników HTML | — |
| BRAND | marka | — |
| STOCK | liczba całkowita ≥ 0, domyślnie 1 | ≥ 0 |
| PRICE_BEFORE_DISCOUNT | cena przed rabatem, musi być większa niż PRICE | > 0 |
| COST_PRICE | cena zakupu, do liczenia marży | > 0 |
| PRICES | ceny per grupa klientów (NAME, VALUE), powiązane z PRICE_CATEGORY z feedu klientów | max 1000 grup w całym feedzie |
| CATEGORYTEXT | ścieżka kategorii rozdzielana znakiem `\|` | — |
| PRODUCT_LINE | linia produktowa | — |
| VARIANT | lista zagnieżdżonych produktów-wariantów | bez limitu |
| SHOW | logiczne, domyślnie TRUE; FALSE wyklucza produkt | — |
| PARAMETER | powtarzalny (NAME, VALUE); NAME nie musi być unikalny | — |
| VAT_RATE | stawka VAT jako liczba, np. 23 | > 0 |

## Limity i formaty
- Kodowanie: strona podaje „UTF-8LE”; zakazane znaki sterujące Unicode poza CR i LF.
- Znaki `& > < \ " '` trzeba escapować albo umieścić w CDATA.
- Rekomendowane są wyłącznie produkty dostępne (STOCK > 0), z PRICE > 0 oraz z URL i IMAGE.
- Warianty: produkt spoza VARIANT jest produktem głównym; jeśli nie spełnia kryteriów (cena, stan, zdjęcie, URL), rolę głównego przejmuje pierwszy pasujący wariant. Brakujące pola wariant dziedziczy po głównym (także PRICES).
- PRICES nie są dziedziczone między polami — każda grupa musi mieć komplet używanych pól. Ceny grupowe działają obecnie tylko w mailingu, nie w rekomendacjach na stronie. Przekroczenie 1000 grup = produkty nieprzetwarzane.
- Zdjęcia cache'owane na CDN Samby do 7 dni; aby wymusić odświeżenie, trzeba zmienić nazwę pliku (URL).
- Aktualizacja raz dziennie, zawsze całość; błąd = cały feed odrzucony, ponowienia w rosnących odstępach.
- Pozostałe feedy: klienci (CUSTOMER_ID, NEWSLETTER_FREQUENCY wymagane), zamówienia (ORDER_ID, CREATED_ON, ITEMS; produkty z zamówień muszą istnieć w feedzie produktów), kategorie (opcjonalny; TITLE i URL, TITLE zgodny z CATEGORYTEXT).

## Różnice względem szablonu bazowego
- Względem `Google.xml`: inna struktura (brak RSS/`g:`), nazwy pól wielkimi literami, cena jako sama liczba bez waluty, stan liczbowy zamiast `availability`, kategoria z `|` zamiast ` > `, warianty zagnieżdżone w produkcie zamiast płaskich pozycji z `item_group_id`, atrybuty jako PARAMETER NAME/VALUE zamiast `color`/`size`/`gender`.
- Względem `samba.xml`: treści szablonu nie weryfikowano (poza zakresem folderu) — do sprawdzenia pola PRICES, COST_PRICE, VAT_RATE, SHOW, PRODUCT_LINE oraz zakaz HTML w DESCRIPTION.

## Uwagi
- Strona wczytana poprawnie. Brak osobnego artykułu wyłącznie o feedzie produktów; strona odsyła do instrukcji per platforma i artykułów o typowych problemach.
- Zapis „UTF-8LE” pochodzi ze źródła — prawdopodobnie chodzi o zwykłe UTF-8; do potwierdzenia.
