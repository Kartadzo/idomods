# Weryfikacja GMC — footballmasters.pl — 2026-10-21 (stan bazowy)

ClickUp: [FootballMasters.pl gAds - Optymalizacja GMC](https://app.clickup.com/t/869cqamb2)
To pierwsza weryfikacja w tym trybie, więc wyniki są **stanem bazowym** do porównania za ok. 90 dni.

## Identyfikatory i konta

| Element | Wartość |
|---|---|
| Konto GMC (brands) | 121004785 „Football Masters”, CSS **BRANDS MANAGO SP. Z O.O** — konto analizowane (507 produktów) |
| Konto GMC (google) | 5758278661 — witryna zweryfikowana i zarezerwowana, **0 źródeł danych i 0 produktów**. Bezpłatne informacje są realizowane przez konto brands (metody marketingowe źródła: bezpłatne informacje, reklamy produktowe i 1 inna). |
| Witryna | footballmasters.pl — Zweryfikowana, Zarezerwowana |
| Połączone usługi | Google Ads **258-769-7247** i **884-957-0496** (oba aktywne), GA4 396575189 „Football Masters – GA4”. Profilu Firmy brak. |
| Źródło podstawowe | „FootballMasters.pl product feed [IdoMods]” (afmDataSourceId 114572663), plik URL `footballmasters.pl/data/export/feed10003_<hash>.xml`, codziennie 01:00, PL/pl, etykieta PL, 508 produktów |
| Inne źródła podstawowe | „Produkty-Wszystkie” i „Produkty Football Masters” (Arkusze Google): 0 produktów, „Wstrzymano aktualizacje” — pozostałości |
| Źródła dodatkowe | brak |
| Reguły atrybutów | brak |
| Feed w IdoSell | „Google ads [IdoMods]” (serwis 10003, sklep id 1), XSLT 96 969 zn. (summonFeed, zmiany MD 01–03.2026). Natywnego feedu Google Shopping nie używamy. |
| Wielosklep | footballmasters.pl, footballmasters-eu.iai-shop.com, .sk, .cz, controlsocks, b2b — analiza dotyczy tylko PL |

## Panel IdoSell

| Punkt | Wynik | Status |
|---|---|---|
| Google ads [IdoMods] | Aktywna, wygenerowany 2026-10-21 14:28:23; 264 towary / 427 pozycji; konwersja 0, zamówienia 0 (Ceneo: 9,23 / 12) | OK |
| Harmonogram | 00:00, co 24 h. Wszystkie serwisy zostały dodatkowo wygenerowane o 14:28 (ręcznie lub przez zmianę towarów). | OK |
| Eksport | magazyny własne i obce, pokazywane mimo niedostępności, informacja o niedostępności; IOF 3.0; ceny, nazwy i zdjęcia z własnego serwisu, a w razie braku domyślne | OK |
| Dostęp do pliku | **„bez kontroli”**, czyli bez ograniczenia IP | Info |
| Historia pobrań (6 stron, 120 wpisów, 23.08–21.10) | 60 × Google o ~01:00 (173.194 / 172.217 / 172.253 / 74.125), **60/60 dni, bez luk**, 0 nieudanych prób. Dodatkowo 60 × pobranie z **Azure/Microsoft** (52.238.x — 47, 172.184.64.190/191 — 13) o 01:15–01:45. | OK / Info |
| Cennik (profil STANDARD, PL) | InPost Kurier: przedpłata 19,00 zł, darmowa od 500 zł; pobranie 25,00 zł, darmowa od 500 zł; 2 dni. Paczkomaty 24/7: przedpłata 19,00 zł, darmowa od 500 zł; 2 dni. Sieć punktów odbioru 4: 0 zł. | Baza |

**Pobrania z Azure** pochodzą prawdopodobnie z Microsoft Merchant Center (Bing Shopping) albo innego narzędzia. Plik nie ma ograniczenia IP, więc pobrania działają. Warto zapytać klienta, czy korzysta z Microsoft Ads lub innego narzędzia.

**Różnica 508 (GMC, plik z 01:00) i 427 (IdoSell, plik z 14:28):** feed obejmuje warianty dostępne lub oznaczone jako niedostępne. W GMC liczba produktów spadała przez 28 dni z ok. 660 do 507, ze skokiem 16.10. Do obserwacji przy kolejnej weryfikacji.

### XSLT feedu — zmienne

| Zmienna | Wartość | Uwagi |
|---|---|---|
| `Koszt_dostawy` / `kwota_dla_darmowej_dostawy` | 19 / 500 | zgodne z cennikiem |
| `Czas_obsługi_zamówienia_na_magazynie` / `Czas_dostawy_zamówienia` | 0 / 1 | w feedzie handling 0–1 i transit 1–2, łącznie 1–3 dni; cennik podaje 2 dni, więc OK |
| `dlugosc_opisu` / `dlugosc_opisu_z_parametrow` / `minimalna_dlugosc_opisu_dla_parametrow` | 2400 / 1200 / 120 | — |
| `kolor_nazwa_w_panelu` | `\|kolor\|` (+ CONTEXT_COLOR) | parametr „Kolor” istnieje |
| `material_nazwa_w_panelu` | `\|materiał\|` | **w sklepie brak parametru** → `g:material` nie jest wysyłany |
| `informacje_wyroznione_nazwa_w_panelu` | `\|wyróżnione\|` | **brak parametru** → `g:product_highlight` nie jest wysyłany |
| `gender_*`, `age_group_*`, `*_id_menu`, `gender_nazwa_w_panelu` | puste | **`g:gender` i `g:age_group` nie są wysyłane** |
| `pojemnosc_nazwa_w_panelu` | `Pojemność [ml]` | **w sklepie parametr nazywa się „Pojemność”** (1 litr; 53 L; 100g; 400ml), więc warunek `@name=` nie pasuje |
| `waga_nazwa_w_panelu` | `Waga [g]` | brak takiego parametru (jest „Waga gabarytowa w gramach”) |
| `klasa_energetyczna_nazwa_w_panelu` | `klasa energetyczna` | nie dotyczy |
| Elementy wyjściowe | `g:id, title, description, google_product_category, product_type, image_link, additional_image_link, condition, brand, item_group_id, is_bundle, color, gender, age_group, energy_efficiency_class, material, unit_pricing_measure/base_measure, cost_of_goods_sold, product_highlight, product_detail (attribute_name/value), custom_label_0–3, link, display_ads_link, mobile_link, availability, gtin, mpn, size, price, sale_price, promotion_id, shipping (country, min/max handling, min/max transit, service), shipping_handling/transit_business_days, shipping_weight` | — |

Lokalna kopia `xslt/F/footballmasters/footballmastersPL_gAds.xml` ma 98 327 zn., a wersja w panelu 96 969 zn. Zmienne są zgodne; różnica wynika prawdopodobnie z końców linii. Przed zmianami trzeba porównać obie wersje.

## Merchant Center

| Punkt | Wynik | Status |
|---|---|---|
| Problemy z kontem | „Brak problemów do rozwiązania” | OK |
| Produkty (28 dni) | 507: 506 zatwierdzonych, 0 ograniczonych, 1 niezatwierdzony | OK |
| Przetwarzanie (10 wersji 12–21.10, 01:00) | 508 zaktualizowanych, 0 nowych, „Rozpoznano wszystkie”, „Nie znaleziono problemów” | OK |
| Problemy wymagające uwagi (5) | 1 × strona produktu niedostępna (odrzucony), 18 × obraz < 500×500, 15 × auto-korekta ceny, 5 × auto-korekta ceny przekreślonej, 1 × brak `unit_pricing_measure` | Uwaga |
| Znalezione przez Google | 211 produktów spoza feedu (w powiadomieniach 244) | Info |
| Ochrona produktów | WŁ, 40% | OK |
| Zasady dostawy | „Zasady dostawy 12 34”: PL, wszystkie produkty, stała stawka 19,00 zł, darmowa powyżej 500 zł, 2–30 dni roboczych | OK (czas za szeroki) |
| Kalkulator (2787-2, 209,25 zł) | 19,00 zł „z pliku danych”, zasady konta **nie mają zastosowania** | OK |
| Zasady zwrotów | Standardowy: Polska, zweryfikowany, 14 dni, 9,23 zł, 100% płatnych, metoda „W sklepie” 50% | Info |
| Przykładowy produkt | kolor Czarny, rozmiar 6, `custom_label_0` „200-500 pln”, `custom_label_1` „\|bestseller\|”, `custom_label_2/3` „sklep;” i „rękawice bramkarskie;” | Info (kosmetyka) |
| Powiadomienia | „Zaktualizuj opisy: Koszulki i topy”: 296 produktów bez „Kolor, Wzór i Materiał”; zasady dostawy i zwrotów (konkurencja: zwrot 19,3 dnia za 0 zł, dostawa 0,7 dnia za 4,28 zł); promocje; Portfel Google; automatyczna poprawa zdjęć | Info |

## Parametry vs sterownik vs atrybuty Google

Mapowanie według [specyfikacji danych produktów Google](https://support.google.com/merchants/answer/7052112?hl=pl) i ściągi `specyfikacja_google.md`.

| Parametr w panelu | Wartości | W feedzie | Atrybut Google i zasady | Propozycja |
|---|---|---|---|---|
| Kolor | 28: mieszanka PL i EN (Black/Czarny, White/Biały), łączone zapisane różnie („Czarno Złoty”, „Czarny-Złoty”, „Biały-Złoty”, „Czarny Pomarańczowy”), różna wielkość liter („złoty”, „hebanowy”) | `g:color`, do 4 wartości z `/` | `color`: kolory łączone rozdzielane `/`, ≤ 40 zn. na kolor | Sklep: ujednolicić na polskie nazwy i zapis „Czarny/Złoty”. Ewentualnie mapa w XSLT. |
| (brak) Materiał | — | `g:material` gotowy (`\|materiał\|`), bez limitu liczby wartości (obcięcie do 200 zn.) | `material` ≤ 3 wartości | Sklep: dodać parametr „Materiał” (np. poliester, bawełna). XSLT: ograniczyć do 3 wartości. |
| (brak) Wzór | — | — | `pattern`, sugestia Google dla 296 koszulek | Opcjonalnie parametr „Wzór” w sklepie + `g:pattern` w XSLT |
| Rozmiar meczówki Górnika | 15 (2XL, 3XL, 110–164…) | `g:size` z rozmiarów IdoSell | `size` | OK. Rozmiary dziecięce 110–164 uzasadniają `age_group=kids`. |
| (brak) płeć / wiek | — | `g:gender` i `g:age_group` puste | `gender`, `age_group`: zalecane dla odzieży (wymagane w DE/FR/UK/US) | XSLT: `age_group` z kategorii menu (junior → kids, reszta → adult), `gender=unisex` dla odzieży i rękawic, jeśli sklep nie rozróżnia płci. Potrzebne id kategorii junior. |
| Krój | 3 (Mixcut, Negative, Roll Finger) — krój rękawic | `g:product_detail`, jeśli parametr ma `distinction='y'` | `product_detail` (bez `section_name`, który jest opcjonalny) | Sprawdzić wyróżnienie parametru; ewentualnie dodać `section_name` „Rękawice”. |
| Rodzaj lateksu | 5 (Contact 4mm, Giga Grip 4mm, Hard Grip 3/4 mm…) | jak wyżej | `product_detail`. `material` = „lateks” tylko jako materiał, bez nazwy handlowej. | `product_detail` („Lateks” → wartość) |
| Pojemność | 4 (1 litr; 53 L; 100g; 400ml) | **nie działa**: XSLT szuka „Pojemność [ml]” | `unit_pricing_measure` + `unit_pricing_base_measure`, ta sama jednostka | XSLT: `pojemnosc_nazwa_w_panelu` → `Pojemność` i sprawdzenie parsowania „1 litr”, „53 L”, „100g”. To przyczyna 1 braku ceny jednostkowej. |
| Długość / Szerokość / Wysokość towaru w cm | po 2 | — | `product_length/width/height` (1–3000 cm, ta sama jednostka) | niska wartość, pominąć |
| Waga gabarytowa w gramach | 2 | — | `shipping_weight` (tylko przy stawkach przewoźnika) | pominąć |
| nazwa (33), Konfigurator, Koszulki_idm, Druk, Nadruk kolor, Numer na plecach, KWOTA, PROMOCJA -50, wyprzedaż, Tłumaczenia, Maksymalna liczba… | — | — | — | techniczne lub personalizacja, pominąć |

### Zgodność obecnego XSLT ze specyfikacją

- `g:adult` nie jest wysyłany, więc jest OK.
- `g:product_highlight` jest wysyłany dla każdej wartości bez minimum 2, ale parametr nie istnieje, więc obecnie nie ma problemu.
- `g:product_type`: do 9 pozycji menu, każda osobno. Google używa w kampaniach tylko pierwszej, więc jest OK.
- `custom_label_1` zawiera znaki `|` („|Bestseller|”), a `custom_label_2/3` kończą się `;`. Działa, ale warto wyczyścić, bo etykiety są niewidoczne dla klienta, a ułatwi to segmentację w Google Ads.
- `shipping`: koszt liczony od `price/@gross`. Próg 500 zł jest zgodny z cennikiem.

## Proponowane zmiany (do decyzji)

| # | Gdzie | Przed → po | Status |
|---|---|---|---|
| 1 | XSLT → `pojemnosc_nazwa_w_panelu` | `Pojemność [ml]` → `Pojemność` + test parsowania jednostek | propozycja |
| 2 | XSLT → `age_group` / `gender` | puste → `age_group` z kategorii menu (junior: kids, reszta: adult), `gender=unisex` | propozycja (potrzebne id kategorii) |
| 3 | XSLT → `g:material` | bez limitu → maks. 3 wartości | propozycja (ma znaczenie po dodaniu parametru) |
| 4 | XSLT → `custom_label_1–3` | `\|Bestseller\|`, `sklep;` → `Bestseller`, `sklep` | propozycja (kosmetyka) |
| 5 | GMC → źródła „Produkty-Wszystkie”, „Produkty Football Masters” | 2 puste arkusze → usunięcie | propozycja |
| 6 | GMC → Zasady dostawy → czas | 2–30 dni → 1–3 dni (jak w feedzie) | propozycja |
| 7 | Sklep | 18 zdjęć ≥ 500×500 (termin 31.01.2027), parametr „Materiał” (opcjonalnie „Wzór”), ujednolicenie kolorów, sprawdzenie odrzuconego produktu | do klienta |
| 8 | Klient | pobrania pliku z Azure/Microsoft — jakie narzędzie? | pytanie |

## Wnioski do skilla

- Primary feed może być feedem XSLT (`feed10003_…`) zamiast natywnego Google Shopping. Natywnego feedu nie trzeba wtedy szukać, a `?return=google_shopping` przy wielosklepie pokazuje listę stron.
- Wielosklep: `/panel/config-pricecomparers.php` najpierw pokazuje listę stron. Wybór przez `[wybierz]` przy domenie prowadzi do `?shop=<id>`.
- Historia pobrań ładuje strony AJAX-em, więc można je przejść pętlą w jednym kontekście JS (kontekst się nie resetuje).
- Pętla odczytu wersji przetwarzania w GMC dłuższa niż 45 s zawiesza `javascript_tool`. Trzeba ją uruchomić w tle (`(async()=>{…})()`) i odczytać wynik osobnym wywołaniem.
- Jeśli w GMC nie ma źródeł dodatkowych, zakładki „Źródła podstawowe / dodatkowe” w ogóle się nie pojawiają.
