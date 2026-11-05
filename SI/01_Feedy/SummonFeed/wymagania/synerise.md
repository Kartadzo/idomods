# Synerise — wymagania feedu
- Źródła: https://hub.synerise.com/developers/product-feed/ (przekierowanie), https://hub.synerise.com/docs/ai-hub/item-feed/google-merchant-feed
- Data przeglądu: 2026-10-27
- Format: Google RSS 2.0 (lub Atom) z `g:*` + własna przestrzeń `c:*` na atrybuty niestandardowe, akceptuje format Google: tak
- Szablon bazowy: `Google.xml` — Synerise wprost wymaga struktury Google Merchant; trzeba dodać deklarację przestrzeni `c:`. `Synerise.xml` (starszy) warto porównać pod kątem atrybutów `c:` — treści nie weryfikowano.

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| g:id | identyfikator; musi być spójny we wszystkich integracjach (tracking, transakcje) | — |
| title | nazwa (bez prefiksu `g:`) | — |
| link | URL produktu (bez prefiksu `g:`) | — |
| g:image_link | URL zdjęcia | bez bardzo dużych plików |
| g:price | cena z walutą, np. `12 USD`; dzielona na wartość i walutę | — |
| g:availability | konwertowana do wartości logicznej | — |
| g:product_type | zapisywane jako kategoria; separator ` > ` ze spacjami; powinno odpowiadać `product:type` w tagach OG na stronie | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| g:sale_price | cena promocyjna; na jej podstawie liczone `effectivePrice`, `discount` | — |
| g:item_group_id | grupowanie wariantów (sposób przetwarzania nieopisany) | — |
| description, name | opis, dodatkowa nazwa (bez `g:`) | — |
| g:brand, g:gtin, g:mpn, g:manufacturer | identyfikacja | — |
| g:color, g:size, g:material, g:gender, g:condition | cechy | — |
| g:google_product_category | kategoria Google | — |
| g:additional_product_type | powtarzalne, dodatkowe kategorie | — |
| g:additional_image_link | dodatkowe zdjęcia | — |
| g:quantity, g:shipping, g:shipping_weight, g:online_only | stan i wysyłka | — |
| c:<nazwa> | atrybut własny → `attributes.<nazwa>`; powtórzony tag = tablica; typ cenowy dzielony na wartość i walutę | — |

## Limity i formaty
- Kodowanie UTF-8; deklaracja przestrzeni `g:` (`http://base.google.com/ns/1.0`) i `c:` (`http://base.google.com/cns/1.0`).
- Zalecane CDATA dla wartości ze znakami `< > &`.
- Separator kategorii ` > ` musi mieć spacje po obu stronach, inaczej staje się częścią nazwy.
- Maks. rozmiar pliku 5 GB; model podobieństwa wizualnego do 1 000 000 pozycji.
- Nazwy atrybutów po imporcie: bez prefiksu, snake_case → camelCase.
- Zalecany nagłówek HTTP `Last-Modified` (wykrywanie zmian, mniejszy transfer).
- Dostarczenie: URL pobierany przez silnik AI albo wgranie do katalogu w Automation Hub (z możliwością transformacji danych niezgodnych ze specyfikacją).
- Zaleca się umieszczać tylko atrybuty faktycznie wykorzystywane.

## Różnice względem szablonu bazowego
- Dodać `xmlns:c="http://base.google.com/cns/1.0"` w nagłówku i ewentualne atrybuty własne `c:*` (np. parametry IdoSell, marża, etykiety).
- `g:product_type` jest tu kluczowe (kategoria) i musi używać ` > ` ze spacjami — sprawdzić format ścieżki kategorii z IdoSell.
- `g:additional_product_type` — przydatne przy wielu kategoriach; w `Google.xml` zwykle brak.
- `custom_label_*`, `shipping` są dopuszczalne, ale zbędne, jeśli nie są używane.

## Uwagi
- Podany link `developers/product-feed/` to strona przekierowania („artykuł przeniesiony”); treść pochodzi z nowej lokalizacji.
- Brak informacji o harmonogramie importu i limitach długości pól.
