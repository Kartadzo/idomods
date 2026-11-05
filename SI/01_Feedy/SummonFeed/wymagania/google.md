# Google Merchant Center — wymagania feedu
- Źródła:
  - https://support.google.com/merchants/answer/7052112?hl=pl (specyfikacja danych produktów)
  - https://support.google.com/merchants/answer/14819809?hl=en (specyfikacja danych asortymentu lokalnego)
  - https://support.google.com/merchants/answer/6324436?hl=pl (atrybut google_product_category)
  - https://developers.google.com/hotels/hotel-prices/dev-guide/country-codes (kody krajów, pomocniczy)
- Data przeglądu: 2026-10-27
- Format: Google RSS 2.0 z elementami `g:*` (natywny), akceptuje format Google: tak
- Szablon bazowy: Google.xml

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| id | unikalny, stały identyfikator (najlepiej SKU), niezmienny między aktualizacjami, krajami i językami | 50 znaków |
| title (lub structured_title) | czysty tekst; w structured_title podpole `content` + opcjonalne `digital_source_type` (`default` / `trained_algorithmic_media`) | 150 znaków |
| description (lub structured_description) | czysty tekst, analogiczna wersja strukturalna | 5000 znaków |
| link | http/https, zweryfikowana domena, URL zakodowany wg RFC 2396/1738 | — |
| image_link | http/https, dostępny dla googlebot i googlebot-image | — |
| availability | `in_stock`, `out_of_stock`, `preorder`, `backorder` | — |
| availability_date | wymagane przy `preorder`, zalecane przy `backorder`; ISO 8601, maks. rok w przód | 25 znaków |
| price | liczba + kod ISO 4217, kropka dziesiętna; 0 tylko dla telefonów na abonament i subskrypcji | — |
| brand | wymagane dla nowych produktów (poza filmami, książkami, muzyką); bez wartości typu „N/A”, „generic” | 70 znaków |
| gtin | wymagany, gdy produkt ma GTIN nadany przez producenta; bez spacji i myślników, poprawna cyfra kontrolna; prefiksy 02, 04, 2, 98–99 nieakceptowane; UPC-12, EAN-13, JAN, ISBN-13, ITF-14 | 14 cyfr na wartość, łącznie 50 |
| mpn | wymagany dla nowych produktów bez GTIN; tylko kod producenta | 70 znaków |
| condition | wymagane, gdy produkt jest używany lub odnowiony: `new`, `refurbished`, `used` | — |
| adult | wymagane przy treściach dla dorosłych: `yes`/`no` | — |
| item_group_id | wymagane dla wariantów (w wybranych krajach i w bezpłatnych informacjach); ta sama wartość dla całej grupy, nie zmieniać | 50 znaków |
| color / size / gender / age_group | wymagane dla odzieży w wybranych krajach (BR, FR, JP, DE, US, UK) oraz zawsze w bezpłatnych informacjach o odzieży (kat. 166); `size` także dla każdego produktu wielorozmiarowego; Polska nie jest na liście krajów | patrz tabela niżej |
| material / pattern | wymagane, gdy odróżniają warianty | 200 / 100 znaków |
| multipack / is_bundle | wymagane dla multipaków i zestawów w wybranych krajach i bezpłatnych informacjach | — |
| certification | wymagane dla produktów z unijną etykietą energetyczną (UE, EFTA, UK): `EC:EPREL:<kod>` | — |
| shipping | wymagane w części krajów i typów informacji lub z mocy prawa; podpole `country` obowiązkowe | cena do 1000 USD |
| warranty | wymagane tam, gdzie wymaga tego prawo (np. Quebec); `czas:jednostka` | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| additional_image_link | dodatkowe zdjęcia, te same zasady co image_link | do 10 wartości, 2000 znaków |
| mobile_link | wersja mobilna strony, wymagania jak dla link | 2000 znaków |
| sale_price | liczba + ISO 4217, zgodna ze stroną i koszykiem | — |
| sale_price_effective_date | dwie daty ISO 8601 rozdzielone `/`, początek przed końcem | 51 znaków |
| cost_of_goods_sold, auto_pricing_min_price | liczba + ISO 4217 | — |
| unit_pricing_measure | liczba dodatnia + jednostka: oz, lb, mg, g, kg, floz, pt, qt, gal, ml, cl, l, cbm, in, ft, yd, cm, m, sqft, sqm, ct; w części krajów wymagane | — |
| unit_pricing_base_measure | liczba całkowita (1, 10, 100, 2, 4, 8 lub 75cl, 750ml, 50kg, 1000kg) + ta sama jednostka | — |
| installment, subscription_cost, loyalty_program | raty, subskrypcja (`month:12:35.00PLN`), program lojalnościowy (PL nie jest na liście krajów) | — |
| google_product_category | ID liczbowe (zalecane) albo pełna ścieżka, nie oba; jedna kategoria; w XML `>` jako `&gt;` | — |
| product_type | własna ścieżka kategorii `A > B > C`; do grupowania kampanii używana tylko pierwsza wartość | 750 znaków |
| identifier_exists | `yes` (domyślnie) / `no`, tylko gdy brak GTIN, MPN i marki | — |
| item_group_title | wspólny tytuł grupy wariantów | 150 znaków |
| color | kilka kolorów rozdzielonych `/`; bez cyfr, pojedynczych liter, słów niebędących kolorem | 100 znaków łącznie, 40 na kolor |
| size | `one_size`/`OS` dla rozmiaru uniwersalnego; liczby sztuk w `multipack`, nie w `size` | 100 znaków |
| size_type | `regular`, `petite`, `maternity`, `big`, `tall`, `plus` | maks. 2 wartości |
| size_system | US, UK, EU, DE, FR, JP, CN, IT, BR, MEX, AU; domyślnie kraj docelowy | — |
| gender | `male`, `female`, `unisex` | — |
| age_group | `newborn`, `infant`, `toddler`, `kids`, `adult` | — |
| material | do 3 wartości rozdzielonych `/` | 200 znaków |
| multipack | liczba całkowita; pomijać, gdy multipak tworzy producent | — |
| is_bundle | `yes`/`no` | — |
| product_detail | podpola `section_name` (140), `attribute_name` (140), `attribute_value` (1000) | do 100 wpisów |
| product_highlight | krótkie wyróżniki produktu | 2–100 wpisów, 150 znaków każdy |
| product_length/width/height | liczba + `cm` lub `in`, zakres 1–3000, ta sama jednostka | — |
| product_weight | liczba + `lb`, `oz`, `g`, `kg`, zakres 0–2000 | — |
| document_link | linki do PDF | do 5, 2000 znaków |
| energy_efficiency_class (+ min/max) | A+++ do G, tylko CH, NO, UK | — |
| popularity_rank | liczba 0–100.0 | — |
| question_and_answer | grupa `question` + `answer` (po 1000 znaków), bez powielania innych pól | do 30, łącznie 10 000 znaków |
| related_product | `relationship_type` (part_of_set, required_part, often_bought_with, substitute, different_brand, accessory), `identifier_type` (gtin/id), `identifier`; każdy powiązany osobno | do 30 |
| variant_option | grupa `name` + `value` (po 250 znaków) | do 30, 5000 znaków |
| ads_redirect | URL w tej samej domenie co link | 2000 znaków |
| custom_label_0–4 | dowolne etykiety do kampanii | 100 znaków, do 1000 unikalnych wartości na etykietę |
| promotion_id | bez spacji i symboli, wielkość liter ma znaczenie | 50 znaków, do 10 na produkt |
| lifestyle_image_link | zdjęcie aranżacyjne, http/https | 2000 znaków |
| short_title | tylko kampanie Demand Gen | 150 znaków (zalecane 5–65) |
| excluded_destination / included_destination | Shopping_ads, Buy_on_Google_listings, Display_ads, Local_inventory_ads, Free_listings, Free_local_listings, YouTube_Shopping | — |
| shopping_ads_excluded_country, ships_from_country | kod ISO 3166-1 alfa-2 | 2 znaki |
| pause | `ads`, maks. 14 dni | — |
| shipping | podpola: country (wymagane), region, postal_code, location_id, location_group_name, service, price, min/max_handling_time, min/max_transit_time, loyalty_program_label, loyalty_tier_label | cena ≤ 1000 USD |
| carrier_shipping, handling_cutoff_time, minimum_order_value, free_shipping_threshold | rozbudowane reguły dostawy (stawki przewoźnika, godzina odcięcia, minimalne zamówienie, próg darmowej dostawy) | — |
| shipping_label | etykieta dla reguł dostawy, niewidoczna dla klienta | 100 znaków |
| shipping_weight | 0–2000 lb lub 0–1000 kg; jednostki lb, oz, g, kg; wymagane przy stawkach przewoźnika | — |
| shipping_length/width/height | 1–150 in lub 1–400 cm; podawać wszystkie trzy w tej samej jednostce | — |
| min/max_handling_time | dni robocze, liczba ≥ 0 | — |
| return, return_policy_label | zasady zwrotów na poziomie produktu (country, item_condition, method, window_type/window_days, shipping_fee itd.) | etykieta 100 znaków |
| external_seller_id | wymagany na kontach wielu sprzedawców | 1–50 znaków |

### Asortyment lokalny (osobny plik, answer 14819809)
| pole | opis/format | limit |
|---|---|---|
| id | wymagany, zgodny z id w feedzie produktowym | 50 znaków |
| store_code | wymagany, zgodny z kodem sklepu w Profilu Firmy, rozróżnia wielkość liter | 64 znaki |
| availability | wymagany: `in_stock`, `limited_availability`, `on_display_to_order`, `out_of_stock` | — |
| price / sale_price / sale_price_effective_date | opcjonalne, nadpisują cenę z feedu dla danego sklepu | — |
| quantity | liczba sztuk; 3+ = w magazynie, 1–2 = ograniczona, 0 = brak | — |
| pickup_method / pickup_sla / pickup_cost | odbiór w sklepie (`buy`, `reserve`, `ship to store`, `not supported`; `same day` … `multi-week`); od 30.09.2026 koszt odbioru wymagany w UK/UE/EFTA, jeśli sklep go pobiera | pickup_cost 0–1000 USD |
| local_shipping_label | etykieta dostawy tego samego dnia | 100 znaków |

## Limity i formaty
- Tytuł: 150 znaków; opis: 5000 znaków; czysty tekst.
- Zdjęcia: min. 500 × 500 px (egzekwowane od 31.01.2027); JPEG, WebP, PNG, nieanimowany GIF, BMP, TIFF; bez powiększania miniatur, napisów promocyjnych, znaków wodnych, ramek i obrazów zastępczych. Grafiki AI muszą zachować metadane IPTC `DigitalSourceType`.
- Waluta: ISO 4217 (np. PLN), kropka jako separator dziesiętny; poza USA/Kanadą ceny brutto z VAT.
- Nazwy atrybutów i wartości słownikowe po angielsku, z podkreślnikami; teksty swobodne w jednym języku w całym feedzie.
- Kody krajów: dwuliterowe, wielkimi literami (PL, DE, CZ, SK, AT, GB, UA, US, FR, IT, ES, NL, LT, RO, HU). Wielka Brytania to `GB`, nie `UK` (lista pomocnicza nazywa je kodami CLDR; `ZZ` i kody regionów nieobsługiwane). W polach Merchant Center (`shopping_ads_excluded_country`, `ships_from_country`) Google wskazuje ISO 3166-1 alfa-2.
- google_product_category: tylko z oficjalnej taksonomii (pliki Excel i tekst UTF-8); gdy brak tłumaczenia — angielska ścieżka lub ID; wersje po sierpniu 2011 są konwertowane do najnowszej.
- Kodowanie i maksymalny rozmiar pliku: strony tego nie podają (jedyny limit rozmiaru to 15 MB dla modelu 3D w `virtual_model_link`).

## Różnice względem szablonu Google.xml
- Szablon jest natywnym formatem tego serwisu — przenosi się w całości.
- `video_link`, `display_ads_link` i `tax` nie występują w przejrzanej specyfikacji (strona 7052112); Google może je zignorować — nie usuwać bez potrzeby, ale nie traktować jako pól wspieranych przez tę specyfikację.
- Brakuje w szablonie (warte rozważenia): `identifier_exists`, `availability_date` (przy preorder/backorder), `sale_price_effective_date`, `unit_pricing_base_measure` (gdy jest `unit_pricing_measure`), `size_type`, `size_system`, `pattern`, `item_group_title`, `product_weight`/wymiary, `shipping_label`, `custom_label_4`, `lifestyle_image_link`, `product_length/width/height`, `return_policy_label`, `free_shipping_threshold`.
- Kontrola wartości: `availability` z podkreślnikami (`in_stock`), kolory przez `/`, `material` maks. 3 wartości przez `/`, `>` w `google_product_category`/`product_type` jako `&gt;`.

## Uwagi
- Strona 7052112 ma ok. 144 tys. znaków; przeczytana w dwóch częściach. Narzędzie streszczające mogło pominąć pojedyncze atrybuty z sekcji kampanii/marketplace’ów.
- Strona 14819809 dotyczy asortymentu lokalnego (osobny feed sklepów stacjonarnych), nie głównego feedu produktowego.
- Strona 6324436 dotyczy wyłącznie `google_product_category` (kategorie alkoholu 499676/3577, zestawy — kategoria produktu głównego, telefony na abonament 267, karty podarunkowe 53, oprogramowanie 313).
