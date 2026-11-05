# Doofinder — wymagania feedu
- Źródła: https://support.doofinder.com/managing-data/the-product-data-feed , https://support.doofinder.com/managing-data/field-name-mapping , https://support.doofinder.com/managing-data/grouping-product-variants
- Data przeglądu: 2026-10-27
- Format: XML (w tym Google Shopping), CSV/TXT, JSONL, także spakowane (zip, gz, bz2, tgz), akceptuje format Google: tak
- Szablon bazowy: `Google.xml` — Doofinder przyjmuje feed Google Shopping wprost (link z GMC); nazwy pól można dopasować aliasami w panelu.

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| id | unikalny; liczba lub tekst | ok. 3 KB |
| title | nazwa | ok. 3 KB |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| image_link | URL, najlepiej JPEG (zalecane) | — |
| price | liczba dziesiętna, np. `15.0` (zalecane) | — |
| sale_price | cena promocyjna; pusta, gdy brak rabatu (zalecane) | — |
| category | hierarchia z `>`, od ogólnej; wiele drzew rozdzielone `%%` (zalecane) | — |
| group_id | wspólna wartość = warianty jednego produktu (zalecane) | — |
| group_leader | `true` dla reprezentanta grupy, `false` dla pozostałych (zalecane) | — |
| df_variants_information | tylko u lidera; lista cech różnicujących, np. `color%%size` | — |
| link | URL produktu (opcjonalne, ale wyświetlane w wynikach) | — |
| description, availability (`in stock`/`out of stock`), condition (`new`/`used`/`refurbished`), gtin | opcjonalne | — |
| multiprice | ceny per rynek/waluta, np. `EUR_price=…/EUR_sale_price=…` | — |
| atrybuty dodatkowe (color, size, brand…) | dowolne, do wyszukiwania i filtrów; wiele wartości rozdzielone `/` | — |
| stock_quantity, best_price, purchase_price | stan liczbowy; cena netto i zakupu → wyliczanie marży | — |

## Limity i formaty
- Plik do 625 MB; limit liczby pozycji niepodany. Kodowanie nieokreślone.
- Każdy atrybut ok. 3 KB (≈3000 znaków); dłuższe wartości są obcinane, reszta feedu przetwarza się normalnie.
- XML poprawnie sformowany, jeden korzeń, znaki zastrzeżone escapowane lub w CDATA.
- CSV: separator tab, `|`, `;` lub `,` (spójnie w całym pliku), pola z separatorem/nowym wierszem/cudzysłowem w cudzysłowach.
- JSONL: tylko jeden obiekt JSON na linię; zwykły `.json` z tablicą nie przejdzie.
- Separatory wartości: `/` (wiele wartości; dosłowny ukośnik podwojony `//`), `>` (hierarchia kategorii), `%%` (wiele drzew kategorii, lista cech wariantów). Pole zbiorcze `attributes`: pary `nazwa=wartość` rozdzielone `/` (escape ukośnika niejednoznaczny w dokumentacji — przetestować).
- URL musi być dostępny serwer–serwer w limicie czasu; dopuścić user-agent `Doofinder/4.0` i IP Doofindera w firewallu/WAF/CDN; tryb serwisowy lub logowanie blokują pobranie (dane logowania można osadzić w URL).
- Nazwy pól mapowane w panelu (Field Name Mapping: pole znormalizowane ↔ aliasy z feedu); zmiana działa od następnego indeksowania.

## Różnice względem szablonu bazowego
- Warianty: Doofinder grupuje po `group_id` (dokumentacja nie opisuje wbudowanego odpowiednika `g:item_group_id` — wymagany alias albo dodatkowe pole `group_id`). Do dodania `group_leader` (np. pierwszy rozmiar produktu = `true`) i `df_variants_information` u lidera.
- Ceny: przykłady to same liczby (`15.0`), Google ma `99.00 PLN` — sprawdzić, czy Doofinder poprawnie parsuje walutę z feedu Google, lub emitować liczbę.
- `sale_price` musi być pusty bez promocji — szablon nie powinien wpisywać ceny regularnej do `sale_price`.
- Kategoria: Doofinder oczekuje `category` (alias dla `g:product_type`); wiele ścieżek łączyć `%%`.
- Pola reklamowe (`shipping`, `custom_label_*`, `google_product_category`, `age_group`) zbędne; przydatne dodatkowe: `stock_quantity`, `best_price`, `purchase_price`.

## Uwagi
- Strony wczytane poprawnie. Strona mapowania pól mówi, że nazwy w feedzie Google nie muszą się zgadzać ze specyfikacją, bo dopasowuje się je aliasami; konkretnego mapowania pól `g:*` nie publikuje.
