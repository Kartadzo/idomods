# Pinterest — wymagania feedu
- Źródła:
  - https://help.pinterest.com/pl/business/article/before-you-get-started-with-catalogs
  - https://help.pinterest.com/pl/business/article/data-source-ingestion
- Data przeglądu: 2026-10-27
- Format: XML (RSS 2.0 lub ATOM 1.0), CSV, TSV, Arkusze Google; akceptuje format Google: częściowo (RSS 2.0 przyjmowany, nazwy pól zbieżne z Google, ale inne wartości i limity)
- Szablon bazowy: Google.xml

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| id | unikalny identyfikator produktu | 127 znaków |
| title | nazwa zgodna ze stroną produktu, z cechami wariantu | 500 znaków |
| description | czysty tekst, bez HTML | 10 000 znaków |
| link | URL strony produktu, bez wymogu logowania | 511 znaków |
| image_link | zdjęcie główne, min. 1000 × 1500 px, bez szablonów i obrazów zastępczych | 2000 znaków |
| price | liczba + kod ISO 4217 (przed lub po liczbie, ze spacją lub bez); bez symboli walut; nie 0; domyślnie USD | — |
| availability | `in stock`, `out of stock`, `preorder` | — |
| item_group_id | tylko dla produktów z wariantami | 127 znaków |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| additional_image_link | dodatkowe zdjęcia min. 75 × 75 px; każde tworzy osobny Pin | do 10 linków |
| sale_price | musi być niższa niż price | — |
| sale_price_effective_date | zakres dat ISO 8601 | — |
| installment, unit_pricing_measure, unit_pricing_base_measure | raty i cena jednostkowa | — |
| product_type | do pięciu poziomów rozdzielonych ` > ` | — |
| description_html | zalecane, gdy opis przekracza 200 znaków | — |
| mobile_link | wersja mobilna strony | — |
| video_link | plik .mp4, .mov lub .m4v | maks. 2 GB |
| brand | marka | 100 znaków |
| gtin | kod GTIN | — |
| mpn | kod producenta | 70 znaków |
| color, gender, age_group, material, pattern, size, size_type, size_system | atrybuty wariantów | — |
| alt_text | tekst alternatywny zdjęcia | — |
| variant_names, variant_values | nazwy i wartości wariantów | — |
| condition | `new`, `used`, `refurbished` | — |
| adult | `TRUE` / `FALSE` | — |
| tax, shipping | grupy wartości rozdzielane dwukropkiem | — |
| shipping_weight, shipping_width, shipping_height | liczba + jednostka | — |
| free_shipping_limit | próg darmowej dostawy | — |
| custom_label_0–4 | etykiety własne | 511 znaków |
| custom_number_0–4 | liczby całkowite 0–4294967295 | — |
| ad_link | link reklamowy z parametrami śledzenia | — |
| google_product_category | kategoria z taksonomii Google | — |
| excluded_destination | wykluczenie z reklam lub bezpłatnych informacji | — |

## Limity i formaty
- Tytuł: 500 znaków; opis: 10 000 znaków (czysty tekst; HTML w `description_html`).
- Zdjęcia: główne min. 1000 × 1500 px, dodatkowe min. 75 × 75 px; URL http/https do 2000 znaków; przecinki w URL zakodować lub usunąć. Zmiana zdjęcia wymaga nowego URL — inaczej aktualizacja nie zadziała.
- Waluta: ISO 4217; bez kodu przyjmowane USD; walutę domyślną wybiera się też przy dodawaniu źródła danych.
- Kodowanie: UTF-8 (wyjątek: pliki Google TSV z Excela w ISO-8859-1).
- Rozmiar: brak limitu rozmiaru pliku na stronach; do 20 mln produktów na katalog/źródło (nadwyżka ignorowana).
- Kompresja: .zip, .gz, .bz2 i inne dopuszczalne; bez archiwów szyfrowanych/z hasłem i plików z Dropboxa.
- Hosting: FTP, SFTP, WebDAV lub HTTP/HTTPS z bezpośrednim pobraniem; bez białej listy IP i kluczy SSH; port w URL tylko 80 lub 443; URL bez danych logowania (opcjonalnie osobne pola użytkownik/hasło).
- Przy dodawaniu źródła ustawia się: nazwę, URL, format pliku, kraj/region, język, domyślną walutę, domyślną dostępność, opcjonalnie harmonogram.
- Harmonogram: źródła hostowane pobierane co 24 h (zalecany codzienny pełny plik); pliki ręczne trzeba odświeżać co najmniej co 30 dni, po 90 dniach bez aktualizacji produkty wypadają z reklam. Aktualizować istniejące źródło zamiast tworzyć nowe; zduplikowane ID między źródłami zgłaszane są jako błąd.
- Wartości słownikowe w standardowym amerykańskim angielskim. CSV: wartości w cudzysłowach, stała liczba separatorów.

## Różnice względem szablonu Google.xml
- `availability`: Pinterest wymienia wartości ze spacją (`in stock`, `out of stock`, `preorder`), Google — z podkreślnikiem (`in_stock`); brak `backorder`. Do sprawdzenia, czy Pinterest akceptuje też wariant Google — strona tego nie mówi, bezpieczniej mapować.
- `adult`: `TRUE`/`FALSE` zamiast `yes`/`no`.
- Większe limity: tytuł 500 (Google 150), opis 10 000 (Google 5000), `id`/`item_group_id` 127, custom_label 511.
- Wyższe wymaganie zdjęcia głównego (1000 × 1500 px) niż w Google (500 × 500).
- Dodatkowe pola niewystępujące w szablonie: `description_html`, `alt_text`, `variant_names`/`variant_values`, `custom_number_0–4`, `ad_link`, `free_shipping_limit`, `custom_label_4`.
- Nie wymienione przez Pinterest (prawdopodobnie ignorowane): `product_highlight`, `product_detail`, `certification`, `multipack`, `is_bundle`, `display_ads_link`, `shipping` w strukturze `g:shipping` z podelementami (Pinterest opisuje grupy rozdzielane dwukropkiem — format podelementów XML niepotwierdzony).

## Uwagi
- Obie strony wczytane. Strona „data-source-ingestion” opisuje proces dodawania źródła i harmonogram, bez listy atrybutów; lista pól pochodzi ze strony „before-you-get-started-with-catalogs”.
- Strony nie podają wymagań co do formatu pliku graficznego (JPG/PNG itp.).
