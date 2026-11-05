# TikTok — wymagania feedu
- Źródła: https://ads.tiktok.com/help/article/catalog-product-parameters?lang=en
- Data przeglądu: 2026-10-27
- Format: nie ustalono ze źródła (strona nie wymienia formatów plików), akceptuje format Google: nie ustalono (strona odwołuje się tylko do taksonomii Google; nazwy większości pól zbieżne z Google)
- Szablon bazowy: Google.xml

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| sku_id | unikalny identyfikator; duplikaty ignorowane; poprawny Unicode | — |
| title | poprawny Unicode, bez emoji i tekstów promocyjnych | — |
| description | krótki opis produktu | — |
| availability | `in stock`, `available for order`, `preorder`, `out of stock`, `discontinued` | — |
| condition | `new`, `refurbished`, `used` | — |
| price | np. `9.99 USD`; waluta domyślnie wg kraju docelowego katalogu | — |
| link | URL strony produktu lub zakupu | — |
| image_link | URL zdjęcia JPG lub PNG | — |
| brand | nazwa marki | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| google_product_category | taksonomia Google, do trzech poziomów | — |
| product_type | kategoria, pierwsze trzy poziomy | — |
| video_link | wideo pionowe 9:16, min. 720 × 1280, bitrate ≥ 516 kb/s, z dźwiękiem i napisami | — |
| additional_image_link | URL-e rozdzielone przecinkami w cudzysłowie; JPG/PNG | do 10 |
| age_group | Newborn, Infant, Toddler, Kids, Adult | — |
| gender | `male`, `female`, `unisex` | — |
| color, material, pattern, size | tekst dowolny | — |
| item_group_id | wspólny identyfikator wariantów | — |
| sale_price | liczba + ISO 4217, kropka dziesiętna | — |
| sale_price_effective_date | dwa znaczniki ISO 8601 rozdzielone `/` | — |
| shipping | `KRAJ:REGION:TYP_WYSYŁKI:CENA:USŁUGA`, kolejne regiony po `;` | — |
| shipping_weight | np. `0.3 lb` | — |
| gtin | UPC (12), EAN (13), JAN (8 lub 13), ISBN (13), ITF-14 (14) | — |
| mpn | kod producenta | — |
| tax | np. `0.05` | — |
| custom_label_0–4 | etykiety własne | 100 znaków |
| merchant_brand | nazwa marki sklepu | — |
| productHisEval | liczba zakupów i pozytywnych opinii rozdzielone `:` | — |
| ios_url, android_url (+ ios_app_store_id, ios_app_store_name, android_package, android_app_name) | deep linki do aplikacji; ios_url wymagany przy ponownym zaangażowaniu w aplikacji iOS | — |

## Limity i formaty
- Jedyny jawny limit znaków: 100 dla `custom_label_0–4`; długości tytułu i opisu niepodane.
- Zdjęcia: JPG lub PNG; obrazy kwadratowe (karuzela) min. 500 × 500; link musi się otwierać. Nieobsługiwane hostingi: Google Drive, Flickr, Pinterest, 500px, Imgbb, Smugmug, Dropbox.
- Waluta: domyślnie wg kraju docelowego katalogu; w `sale_price` wymagany kod ISO 4217.
- Kodowanie: poprawny Unicode w `sku_id` i `title`; formatu pliku, kodowania i rozmiaru strona nie podaje.
- Dostępność funkcji: konta zarządzane w rynkach, gdzie działa Video Shopping Ads (Catalog).

## Różnice względem szablonu Google.xml
- `g:id` → `sku_id` (inna nazwa pola wymaganego).
- `availability`: wartości ze spacją i dodatkowe `available for order`, `discontinued`; brak `backorder`; Google używa podkreślników.
- `condition` i `brand` są wymagane zawsze (w Google warunkowo).
- `google_product_category` i `product_type` — tylko do trzech poziomów.
- `shipping` jako jeden ciąg z dwukropkami zamiast podelementów `g:country`/`g:service`/`g:price`.
- `additional_image_link` jako jedna wartość z przecinkami, a nie powtarzany element.
- Brak w szablonie: `merchant_brand`, `productHisEval`, `custom_label_4`, pola aplikacji mobilnych.
- Niewymienione przez TikTok (prawdopodobnie ignorowane): `unit_pricing_measure`, `product_highlight`, `product_detail`, `certification`, `is_bundle`, `multipack`, `display_ads_link`, `mobile_link`.

## Uwagi
- Strona wczytana. Nie określa obsługiwanych formatów pliku (XML/CSV) ani tego, czy feed Google RSS z prefiksem `g:` jest przyjmowany bez zmian — wymaga weryfikacji w panelu katalogu TikTok.
