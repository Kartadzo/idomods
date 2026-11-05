# edrone — wymagania feedu
- Źródła: https://help.edrone.me/en/articles/8294829-product-feed-requirements , https://help.edrone.me/pl/collections/4638275-feed-produktowy , https://help.edrone.me/pl/articles/8294829-wymagania-dotyczace-feedu-produktowego , https://help.edrone.me/en/articles/8298350-availability-indications-for-feed-in-standards-gmc-ceneo-and-idosell-iai , https://help.edrone.me/en/articles/8715817-product-feed-import-mechanism-description
- Data przeglądu: 2026-10-27
- Format: XML w jednym z trzech standardów: Google Merchant Center (zalecany), Ceneo, IAI/IdoSell, akceptuje format Google: tak
- Szablon bazowy: `Google.xml` — GMC to standard zalecany przez edrone i jedyny z automatycznym doborem pola dopasowania ID; alternatywnie natywny feed IAI ze sklepu bez XSLT.

## Pola wymagane
(nazwy w standardzie GMC)
| pole | opis/format | limit |
|---|---|---|
| g:id | identyfikator; w GMC dopasowanie może iść też po `item_group_id`, `gtin` lub `mpn` | — |
| link | URL produktu, bez spacji | — |
| g:image_link | URL zdjęcia, bez spacji | — |
| title | nazwa | — |
| g:price | cena | — |
| g:availability | dostępność — patrz Limity | — |
| g:product_type (lub product_category) | kategoria; dowolne pole z kategorią; krytyczne dla rekomendacji, cross-sellu, filtrów, Custom Flows | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| g:sale_price | cena promocyjna w elementach dynamicznych i ramkach rekomendacji | — |
| g:quantity | stan; wymagany dla scenariusza „niski stan magazynowy” | — |
| g:complementary_product_ids | produkty uzupełniające do ramek Marketing Machine | — |
| expiration_date | okres dostępności produktu | — |
| g:brand, g:gtin, g:mpn | występują w przykładzie GMC; `gtin`/`mpn` mogą służyć do dopasowania ID | — |

## Limity i formaty
- Wyłącznie XML pod URL, UTF-8, hostowany przez sklep; bez logowania, hasła i blokad geograficznych.
- Pobieranie z IP: 34.240.145.237, 52.215.244.30, 52.48.202.28 — muszą być dopuszczone.
- Adresy produktów i zdjęć nie mogą zawierać spacji.
- Dostępność uznawana za „dostępny”: GMC — `in_stock`, `preorder`, `disponível` (pisownia jak w artykule); Ceneo — `avail` 1/3/7/14/90/110; IAI — `in_stock`, `on_order`. Każda inna wartość = niedostępny.
- Import automatyczny raz na 24 h (00:00 UTC, z opóźnieniem zależnym od kolejki); ręczny po dodaniu linku lub przyciskiem odświeżania.
- Import ręczny: próbka do 100 produktów z zamówień i dodań do koszyka z 30 dni, min. 80% musi się dopasować; dla GMC system sam wybiera, które pole (`id`, `gtin`, `item_group_id`, `mpn`) najlepiej pasuje do ID z trackingu.
- Import automatyczny: jeśli > 20% nowych produktów nie ma dopasowania, feed jest dezaktywowany (błąd `TOO_MANY_UNMATCHED_PRODUCTS`).

## Różnice względem szablonu bazowego
- Kluczowe: ID w feedzie musi odpowiadać ID przesyłanemu przez tracking edrone (zwykle ID produktu IdoSell, nie wariantu). Jeśli `Google.xml` emituje pozycję per rozmiar z `g:id` = ID wariantu, dopasowanie może się oprzeć na `item_group_id` — do sprawdzenia na danych klienta.
- Wartość dostępności: edrone przyjmuje format Google (`in stock` itd.) — potwierdzone przez użytkownika 2026-10-27. Sterownik bez zmian względem Google.xml.
- Dodać `g:quantity` (dla scenariusza niskiego stanu) i ewentualnie `g:complementary_product_ids`.
- `shipping`, `custom_label_*`, `google_product_category`, `gender`, `age_group` są zbędne.

## Elementy do wygenerowania
`dozwolone: g:id,g:title,g:description,g:link,g:image_link,g:price,g:sale_price,g:availability,g:product_type,g:brand,g:gtin,g:mpn,g:item_group_id`

- `g:item_group_id`, `g:gtin`, `g:mpn` zostają, bo edrone może po nich dopasować ID z trackingu.
- Zasada (użytkownik, 2026-10-27): element obsługiwany przez serwis zostaje, jeśli jest w szablonie Google/Facebook — w wersji z tego szablonu. Stąd `g:description` zostaje.
- `g:quantity` i `g:complementary_product_ids`: brak w szablonach Google i Facebook, więc ich nie dodaję.
- Test 2026-10-27 na próbce (jeszcze bez `g:description`): sterownik 115 KB → 45 KB, wartości zachowanych elementów bez zmian.

## Uwagi
- Strona kolekcji PL zawiera tylko listę 22 artykułów; treść wymagań pobrano z artykułów EN i PL (zgodne; PL dodaje `product_category` jako alternatywę dla `product_type`).
- W kolekcji jest osobny artykuł „Jak wygenerować feed produktowy w platformie IdoSell (IAI)?” (https://help.edrone.me/pl/articles/8298345-jak-wygenerowac-feed-produktowy-w-platformie-idosell-iai) — nieprzeglądany.
- Obsługa wariantów nie jest opisana.
