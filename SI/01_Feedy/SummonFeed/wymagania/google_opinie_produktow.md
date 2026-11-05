# Google — opinie o produktach — wymagania feedu
- Źródła: https://developers.google.com/product-review-feeds/schema?hl=pl
- Data przeglądu: 2026-10-27
- Format: własny XML (schemat XSD v2.4: `http://www.google.com/shopping/reviews/schema/product/2.4/product_reviews.xsd`), akceptuje format Google: nie (to nie jest feed produktowy RSS `g:*`)
- Szablon bazowy: inny — nowa struktura `<feed>/<reviews>/<review>`; Google.xml może posłużyć wyłącznie jako źródło identyfikatorów produktu

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| feed/version | stała wartość `2.4` | 1 |
| feed/publisher/name | nazwa wydawcy opinii, niepusta | 1 |
| reviews/review | jedna lub więcej opinii | bez limitu |
| review/review_id | trwały, unikalny identyfikator opinii w systemie wydawcy | — |
| review/reviewer/name | imię lub pseudonim; atrybut opcjonalny `is_anonymous` (boolean) | — |
| review/review_timestamp | `xs:dateTime`, np. `2014-04-21T00:00:00Z`, dozwolone przesunięcie strefy | — |
| review/content | treść opinii, niepusta | — |
| review/review_url | URL http z wymaganym atrybutem `type`: `singleton` (sama opinia) lub `group` (strona z wieloma opiniami) | — |
| review/ratings/overall | liczba dziesiętna z wymaganymi atrybutami całkowitymi `min` i `max` (`max` > `min`; `min` to najniższa ocena, nie „brak oceny”) | dokładnie 1 |
| review/products/product | jeden lub więcej produktów, których dotyczy opinia | — |
| product/product_url | URL strony produktu (może być taki sam jak review_url) | — |
| product_ids/gtins/gtin | wymagany, jeśli produkt ma znany GTIN (UPC, EAN, ISBN, JAN…) | — |
| product_ids/mpns/mpn | wymagany, jeśli znany; dopasowanie MPN działa tylko z marką | — |
| product_ids/skus/sku | wymagany, jeśli znany; zwykle równy `id` z feedu produktowego | — |
| product_ids/brands/brand | wymagany, jeśli znany; niezbędny przy dopasowaniu po MPN | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| feed/aggregator/name | nazwa agregatora opinii | 0–1 |
| feed/publisher/favicon | URL ikony 16×16 px, GIF/JPG/PNG | 0–1 |
| review/reviewer/reviewer_id | trwały identyfikator autora | — |
| review/is_verified_purchase | boolean | — |
| review/is_incentivized_review | boolean | — |
| review/title | tytuł opinii | — |
| review/review_language | tag językowy BCP 47 (np. `pl`) | — |
| review/review_country | kod kraju ISO 3166-1 autora | — |
| review/pros/pro, review/cons/con | zalety i wady w kolejności wyświetlania, bez etykiet typu „Zalety:” | 1..n |
| review/reviewer_images/reviewer_image/url | URL zdjęcia od klienta (nie musi kończyć się rozszerzeniem) | 1..n |
| review/is_spam | boolean, oznaczenie spamu przez wydawcę | — |
| review/collection_method | `unsolicited` lub `post_fulfillment` | — |
| review/transaction_id | trwały identyfikator transakcji | — |
| product/product_name | nazwa produktu | — |
| product_ids/asins/asin | 10 znaków alfanumerycznych | — |

## Limity i formaty
- Plik XML zgodny z XSD v2.4; typy z przestrzeni `http://www.w3.org/2001/XMLSchema`.
- Feed zawsze pełny: opinie nieobecne w kolejnym pliku są usuwane.
- Jedna opinia dotycząca kilku produktów — wpisana raz, z wieloma `<product>`.
- Dopasowanie do produktów głównie po GTIN; bez GTIN skuteczność spada.
- Strona nie podaje: przestrzeni nazw docelowej, maksymalnego rozmiaru pliku, kodowania, limitów długości tekstów ani liczby opinii.

## Różnice względem szablonu Google.xml
- Zupełnie inna struktura (brak RSS/`channel`/`item`, brak `g:*`); feed opisuje opinie, nie oferty.
- Z szablonu można przenieść tylko identyfikatory: `g:id` → `sku`, `g:gtin` → `gtin`, `g:mpn` → `mpn`, `g:brand` → `brand`, `link` → `product_url`, `title` → `product_name`.
- Eksport ofert IdoSell (IOF) nie zawiera treści opinii — potrzebne osobne źródło danych z opiniami (z ID opinii, autorem, datą, oceną).

## Uwagi
- Strona wczytana poprawnie. Ograniczenia unikalności elementów w XSD są wspomniane, ale nieopisane szczegółowo.
