# Specyfikacja danych produktów Google: ściąga do analizy parametrów

Źródło: https://support.google.com/merchants/answer/7052112?hl=pl (pobrane 21.10.2026). Jeśli w raporcie powołuję się na limit lub termin, sprawdzam go ponownie przez WebFetch, bo Google zmienia specyfikację.

## Atrybuty, na które mapuję parametry panelu

| Atrybut | Kiedy wymagany | Format i limity | Czego nie robić |
|---|---|---|---|
| `color` | Odzież w niektórych krajach; produkty wielokolorowe | ≤ 100 zn. łącznie, ≤ 40 zn. na kolor, separator `/` | Nie używać kodów hex, liczb, pojedynczych liter ani słów typu „wielokolorowy”. Wartość złożona z przecinkiem zostaje jednym kolorem. |
| `material` | Gdy warianty różnią się materiałem | ≤ 200 zn., **do 3** materiałów, główny pierwszy, separator `/` | Nie przekazywać więcej niż 3 wartości. |
| `pattern` | Gdy warianty różnią się wzorem | ≤ 100 zn. (np. paski, kratka) | — |
| `size` | Odzież i obuwie w bezpłatnych informacjach; produkty w wielu rozmiarach | ≤ 100 zn. | Liczbę sztuk podaje się w `multipack`, nie w rozmiarze. |
| `size_type` | Opcjonalny, tylko odzież | Maks. 2 wartości z listy: regular, petite, maternity, big, tall, plus | „Slim” i „Oversize” nie są poprawnymi wartościami, więc trafiają do `product_detail`. |
| `size_system` | Opcjonalny, tylko odzież | US, UK, EU, DE, FR, JP, CN, IT, BR, MEX, AU | Domyślnie przyjmowany jest kraj docelowy. |
| `gender` | Odzież w niektórych krajach | male, female, unisex | — |
| `age_group` | Odzież w niektórych krajach | newborn, infant, toddler, kids, adult | Ustawia się jedną wartość. |
| `adult` | **Tylko** produkty z nagością lub treściami seksualnymi | yes/no (domyślnie no) | Nie ustawiać `yes` dla zwykłych produktów „dla dorosłych”, bo ogranicza to wyświetlanie (SafeSearch). Do tego służy `age_group=adult`. |
| `product_detail` | Opcjonalny | Do 100 wpisów; `section_name` ≤ 140, `attribute_name` ≤ 140, `attribute_value` ≤ 1000 | Nie powtarzać innych atrybutów. Nie wpisywać cen, dostawy, promocji, słów kluczowych ani nazwy firmy. Tylko potwierdzone wartości. |
| `product_highlight` | Opcjonalny | **2–100** wpisów na produkt, każdy ≤ 150 zn. | Nie wpisywać słów kluczowych, promocji ani tekstu wielkimi literami. Nie powtarzać `product_detail` ani `description`. Produkt z jednym wyróżnikiem pomijam. |
| `custom_label_0–4` | Opcjonalne, niewidoczne dla klienta | ≤ 100 zn.; ≤ 1000 unikalnych wartości na etykietę na koncie | Najpierw sprawdzam, które etykiety są już zajęte w XSLT. |
| `product_type` | Opcjonalny | Ścieżka rozdzielona `>`, ≤ 750 zn. | Do grupowania w kampanii służy tylko pierwsza wartość. |
| `unit_pricing_measure` + `unit_pricing_base_measure` | Prawo UE: produkty sprzedawane na wagę, objętość lub długość | Miara: liczba + jednostka (`g`, `kg`, `ml`, `l`, `ct`…). Baza: 1/2/4/8/10/100 + **ta sama** jednostka. | W wariantach różniących się rozmiarem używać tej samej wartości. |
| `product_weight` / `product_length/width/height` | Opcjonalne | Waga 0–2000 (`g`, `kg`, `lb`, `oz`); wymiary 1–3000 (`cm`, `in`) | Wszystkie wymiary w tej samej jednostce. |
| `certification` | UE: etykieta energetyczna EPREL | `EC:EPREL:<kod>` | Dotyczy sprzętu RTV i AGD. W UE nie używać `energy_efficiency_class`. |
| `brand` | Nowe produkty (poza książkami, filmami i muzyką) | ≤ 70 zn. | Nie wpisywać „brak marki” ani „generic”. |
| `gtin` / `mpn` | Gdy istnieje kod producenta | gtin ≤ 14 cyfr z poprawną cyfrą kontrolną; mpn ≤ 70 zn. | Nie zgadywać kodów. `identifier_exists=no` tylko wtedy, gdy produkt nie ma żadnego identyfikatora. |
| `item_group_id` | Warianty | ≤ 50 zn., stały w czasie | — |
| `is_bundle` / `multipack` | Zestawy własne / wielopaki | yes/no; liczba całkowita | — |
| `condition` | Produkty używane lub odnowione | new, refurbished, used | — |

## Zdjęcia, dostawa i inne

- `image_link`: **od 31.01.2027 minimum 500 × 500 px**. Bez tekstu promocyjnego, znaków wodnych i ramek. Obrazy AI muszą zachować metadane IPTC. `additional_image_link`: do 10 zdjęć. `lifestyle_image_link`: opcjonalny.
- `shipping`: **wymagany w Polsce** (reklamy i bezpłatne informacje), chyba że koszt jest ustawiony w zasadach konta. Koszt mieści się w zakresie 0–1000 USD i musi zawierać kraj.
- `free_shipping_threshold`: kraj + kwota, waluta zgodna z ceną. To alternatywa dla progu zaszytego w XSLT.
- `min/max_handling_time`: dni robocze, 0 oznacza wysyłkę tego samego dnia. `handling_cutoff_time`: format 24 h.
- `shipping_weight` i wymiary przesyłki są potrzebne tylko przy stawkach przewoźnika w zasadach konta.
- `sale_price_effective_date`: ISO 8601 `start/koniec`. Ceny dla członków programu przekazuje się w `loyalty_program`, nie w `sale_price`.
- `short_title`: opcjonalny, ≤ 150 zn. (zalecane 5–65), używany w kampaniach Demand Gen.
- `pause=ads`: wstrzymuje wyświetlanie na maks. 14 dni.
- `excluded_destination` / `included_destination`, `shopping_ads_excluded_country`, `promotion_id` (do 10 na produkt) i `return_policy_label` (musi istnieć na koncie).
