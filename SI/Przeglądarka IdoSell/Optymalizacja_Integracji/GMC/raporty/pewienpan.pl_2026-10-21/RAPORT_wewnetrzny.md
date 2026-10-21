# Weryfikacja GMC — pewienpan.pl — 2026-10-21 (stan bazowy, pilotaż skilla)

ClickUp: [PewienPan.pl gAds - Optymalizacja GMC](https://app.clickup.com/t/86939c9w4)
Pierwsza weryfikacja w tym trybie, więc to **stan bazowy** do porównania za ~90 dni.

## Identyfikatory i konta

| Element | Wartość |
|---|---|
| Konto GMC (brands) | 9465371 „PewienPan.pl Sklep męski”, CSS **BRANDS MANAGO SP. Z O.O.** |
| Konto GMC (google) | brak w opisie zadania; w przełączniku kont jest tylko 1 konto „pewien” → brak dostępu lub brak konta |
| Witryna | www.pewienpan.pl — Zweryfikowana, Zarezerwowana |
| Połączone usługi | Google Ads 787-631-0380, GA4 382839199, Profil Firmy (Łódź, Nawrot 7) — wszystkie aktywne |
| Źródło podstawowe | „Google Ads PL [IdoMods.pl] PewienPan.pl” (afmDataSourceId 10324368050), plik URL `pewienpan.pl/data/export/googleshoppingpl_<md5>.xml`, codziennie 06:00, PL/pl, etykieta PL |
| Źródło podstawowe 2 | „Merchant Center” (dodane ręcznie) — 60 produktów z XI–XII 2020, „W trakcie sprawdzania” |
| Źródła dodatkowe | „+feed pewienPan [BM]” (plik, codziennie 08:00) oraz „SUPPLEMENTAL SOURCE 2” (Arkusz Google, 00:00) |
| Reguły atrybutów | `gtin`: wyczyść, jeśli zaczyna się od „02” (+2 warunki); pozostałe: SUPPLEMENTAL SOURCE 2 → +feed [BM] → feed główny |
| Feed główny w IdoSell | natywny „Google Shopping Polska” (id serwisu 73), bez XSLT |
| Feed dodatkowy w IdoSell | „[BM] Google ads - dodatkowy feed” (id 10003), XSLT 33 078 zn. |

## Panel IdoSell

| Punkt | Wynik | Status |
|---|---|---|
| Google Shopping Polska | Aktywna, wygenerowany 2026-10-21 10:07:34; 653 produkty / 1694 pozycje; konwersja 1,75; 2290 zamówień | OK |
| Harmonogram generowania | start 06:00, co 4 h (06, 10, 14, 18, 22, 02), trwa ~7 min | Uwaga (patrz GMC) |
| Eksport | magazyny własne + obce, przedsprzedaż, pokazywane mimo niedostępności, info o niedostępności — wszystko WŁ; język PL; waga „nie przekazuj” | OK |
| Dostęp do pliku | „automatycznie ograniczony do predefiniowanych adresów IP serwisu Google Shopping Polska” [Resetuj] | OK |
| Historia pobrań (6 stron, 105 wpisów, 22.08–21.10) | 63 × pobranie przez Google (173.194/172.217/74.125/172.253), **codziennie bez luk**, 11.10 dwa razy; 42 × „Nieudana próba” z `s29.mydevil.net (85.194.240.23)` | OK / Info |
| [BM] feed dodatkowy | Aktywny, 10:07:11, 645 / 1683; pobierany przez Google codziennie o 08:00 | OK |
| Cennik (profil STANDARD, przedpłata, PL) | InPost Smile: 0 zł od 70 zł (domyślny); ORLEN Smile: 0 zł od 70 zł; DPD 16,00 zł, darmowe od 250 zł; InPost 24/7 by IAI 19,42 zł; ORLEN by IAI 15,26 zł. Pobranie: DPD 19,90; InPost 24/7 21,57 | Baza |

**mydevil.net** — prawdopodobnie stare narzędzie poprzedniej agencji lub skrypt ze starym linkiem. IdoSell go blokuje, więc nie ma wpływu na Google. Warto zapytać klienta, czy coś takiego zna.

### XSLT feedu dodatkowego — zmienne

| Zmienna | Wartość | Uwagi |
|---|---|---|
| `kolor_nazwa_w_panelu` | `\|kolor\|` | parametr „Kolor” |
| `material_nazwa_w_panelu` | `\|material\|materiał\|` | parametry „Material” (2 wart.) i „Materiał” (35) |
| `Koszt_dostawy` | 12.92 | **nieaktualne** — komentarz w XSLT „kwoty stawek wysyłek do ustalenia”; najtańsza płatna w sklepie 15,26 (ORLEN by IAI) |
| `kwota_dla_darmowej_dostawy` | 70.00 | zgodne ze Smile (InPost/ORLEN od 70 zł) |
| `Koszt_dostawy_wiekszych_zamowien` | 0.00 | — |
| Elementy wyjściowe | `g:id, g:is_bundle, g:color, g:gender, g:age_group, g:adult, g:material, g:availability, g:price, g:sale_price, g:shipping (+country, handling/transit time), g:shipping_weight, g:gtin, g:mpn, g:item_group_id, g:custom_label_0` | — |

## Merchant Center

| Punkt | Wynik | Status |
|---|---|---|
| Problemy z kontem | „Brak problemów do rozwiązania” | OK |
| Produkty (28 dni) | 1759 zatwierdzonych, 0 ograniczonych, 0 niezatwierdzonych; łącznie 1,82 tys. z 60 ręcznymi (nie wyświetlają się) | OK |
| Przetwarzanie feedu (10 wersji 12–21.10) | „Zaktualizowano produkty”, „Nie znaleziono problemów”, wszystkie atrybuty rozpoznane; 16.10 +4 nowe | OK |
| Problemy wymagające uwagi | 63 × obraz < 500×500 (zbliżające się egzekwowanie), 34 × brak `unit_pricing_measure`, 16 × auto-korekta ceny, 10 × auto-korekta dostępności, 4 × niska jakość `image_link`, 1 × auto-korekta ceny przekreślonej | Uwaga |
| Znalezione przez Google | 208 produktów ze sklepu spoza feedu (w powiadomieniach: 36 do dodania) | Info |
| Ochrona produktów | WŁ, 40% | OK |
| Zasady dostawy (konto) | InPost 19,50 / DPD 19,50 / ORLEN 16,00 zł, wszystkie darmowe od 250 zł, 2–3 dni | Nieaktualne |
| Kalkulator dostawy (3661-163, 429 zł) | 0,00 zł „z pliku danych”, zasady konta **nie mają zastosowania** | OK |
| Zasady zwrotów | Standardowy: Polska, zweryfikowany, 100 dni, „Odpowiedzialność klienta”, w statystykach 100% „Bezpłatnie” | Info (niespójność) |
| Jakość sklepu | ogólna: Świetna; oceny 5,0; koszt dostawy: Dobra | OK |
| Powiadomienia | „Zaktualizuj opisy: Koszulki i topy” — 523 produkty, brak „Kolor, Wzór i Materiał” w opisie; promocje cenowe 10 produktów; program lojalnościowy; dodatek Promocje | Info |

**Przyczyna auto-korekt:** GMC pobiera plik o 06:00:13, a IdoSell zaczyna generować o 06:00 (gotowe ~06:07), więc GMC dostaje plik z 02:07. Feed dodatkowy (08:00) pobiera już wersję z 06:07.

**60 produktów „Dodano w Merchant Center”** (np. „Męski szal z kaszmirem”, „Sweter z wełny merino”, „Błękitna kamizelka w kratkę”, „Wzorzyste chusteczki do nosa”), z ID w formacie UUID, 28.11–1.12.2020. Pozostałość po ręcznym dodawaniu.

## Parametry vs sterownik vs atrybuty Google

Mapowanie według [specyfikacji danych produktów Google](https://support.google.com/merchants/answer/7052112?hl=pl) (stan 21.10.2026). Kod XSLT sprawdzony w lokalnej kopii `xslt/P/pewienPan_gAds.xml` (32 164 B). Wersja w panelu ma 33 078 zn., więc przed zmianami trzeba je porównać.

| Parametr w panelu | Wartości | W feedzie | Atrybut Google i zasady ze specyfikacji | Propozycja |
|---|---|---|---|---|
| Kolor | 159, z duplikatami i różną wielkością liter (Beżowy/beżowy), złożone („beżowy, szary”) | `g:color`: do 4 wartości, rozdzielone `/` | `color`: maks. 100 zn., 40 zn. na kolor, separator `/`, bez „wielokolorowy”, kodów i liczb. Wymagany dla odzieży w niektórych krajach. | Wartości złożone z przecinkiem trafiają jako jeden kolor, więc trzeba je rozdzielić w sklepie albo w XSLT (`,` → `/`). Duplikaty porządkuje sklep. |
| Materiał / Material | 35 + 2 | `g:material`: do **4** wartości, rozdzielone `/` | `material`: maks. 200 zn., **do 3 materiałów**, główny pierwszy | W XSLT `position() < 5` → `< 4`. Scalić dwa parametry. |
| Wzór | 25 (Gładka, Kratka, Jodełka, Mikrowzór…) | — | `pattern`: maks. 100 zn. Wymagany, jeśli warianty różnią się wzorem. | **`g:pattern`**: odpowiada sugestii Google (523 produkty) |
| Typ kołnierzyka | 5 (Button down, Kent, Pin Collar, Windsor, Włoski) | — | `product_detail`: do 100 wpisów, `section_name` ≤ 140, `attribute_name` ≤ 140, `attribute_value` ≤ 1000. Bez powtarzania innych atrybutów, cen, promocji i słów kluczowych. | `product_detail` (sekcja „Krój”, nazwa „Kołnierzyk”) |
| Dopasowanie | 2 (Regular, Slim) | — | `size_type` przyjmuje tylko regular/petite/maternity/big/tall/plus, więc „Slim” tu nie pasuje | `product_detail` („Krój” → „Dopasowanie”). Ewentualnie także `custom_label` do segmentacji. |
| Metoda szycia | 2 (Blake, Goodyear) | — | `product_detail` | `product_detail` (obuwie, sekcja „Wykonanie”) |
| Tkanina zasadnicza | 1 | — | `product_detail`. Nie powtarzać `material`. | `product_detail` tylko wtedy, gdy wartość różni się od Materiału |
| Wyróżnik | 34 (np. „100% bawełna oxford”, „Bez podszewki”) | — | `product_highlight`: **2–100 wpisów** na produkt, ≤ 150 zn. każdy. Bez słów kluczowych, promocji i wielkich liter. Nie powtarzać `product_detail` ani `description`. | `g:product_highlight` tylko dla produktów z **co najmniej 2** wartościami. Pominąć frazy, które dublują materiał. |
| Styl | 3 (Casual, Elegancki; duplikaty) | — | `custom_label_0–4`: ≤ 100 zn., maks. 1000 unikalnych wartości na etykietę na koncie. Klient tego nie widzi. | `custom_label_1` (wolna, bo `_0` jest zajęta) |
| Zapach | 7 | — | `unit_pricing_measure` (np. `100ml`) + `unit_pricing_base_measure` (1/2/4/8/10/100 + ta sama jednostka). Wymagane prawem w UE dla produktów sprzedawanych na objętość lub wagę. | **Podejrzenie: to te 34 produkty bez `unit_pricing_measure`** (do potwierdzenia). Pojemność trzeba wziąć z parametru albo z nazwy. |
| Kwota | 11 (karty podarunkowe) | — | — | pominąć |
| Marka | 1 | `g:brand` w feedzie głównym | `brand` ≤ 70 zn., bez „brak marki” | OK |
| Motyw, Typ, Rodzaj/sposób parasola | 2–4 | — | — | niska wartość, pominąć |

### Inne ustalenia ze specyfikacji

- **`g:adult` = `yes`** jest ustawiane w XSLT (wiersze 153–159) razem z `age_group=adult` dla produktów z kategorią menu o id 605. Według specyfikacji `adult=yes` oznacza treści z nagością lub o charakterze seksualnym, a takie produkty są ograniczane przy SafeSearch. Dla odzieży męskiej to błąd. Trzeba sprawdzić, która to kategoria i ile produktów obejmuje, a następnie usunąć `g:adult` i zostawić samo `age_group=adult`. Najlepiej ustawiać `age_group=adult` dla wszystkich produktów, bo sklep sprzedaje wyłącznie dla dorosłych mężczyzn.
- **`gender`** jest ustawiane tylko wtedy, gdy ścieżka menu zawiera „męskie”. Sklep jest wyłącznie męski, więc `male` można ustawić dla wszystkich produktów. Dla akcesoriów unisex warto sprawdzić wyjątki.
- **Zdjęcia:** wymóg minimum 500 × 500 px obowiązuje **od 31 stycznia 2027**. Od tej daty 63 produkty są zagrożone.
- **`size`** jest wymagany dla odzieży i obuwia w bezpłatnych informacjach. Feed natywny go przekazuje, bo w przetwarzaniu nie ma problemów. Opcjonalne `size_system=EU` dla obuwia nie jest potrzebne, bo domyślnie przyjmowany jest kraj docelowy.
- **`free_shipping_threshold`** (kraj + kwota) to osobny atrybut, którego można użyć zamiast lub obok wyliczania `shipping` w XSLT, np. `PL:70 PLN`. Jest to opcja, a nie konieczność.
- **`loyalty_program`**: Google go sugeruje, ale wymaga programu lojalnościowego w ustawieniach konta. To decyzja klienta.

## Proponowane zmiany (do decyzji)

| # | Gdzie | Przed → po | Status |
|---|---|---|---|
| 1 | GMC → źródło „Google Ads PL…” → harmonogram | 06:00 → 07:00 | propozycja |
| 2 | GMC → Zasady dostawy | 19,50/19,50/16,00, darmowa od 250 → InPost 0 zł od 70 (poniżej 19,42), ORLEN 0 zł od 70 (poniżej 15,26), DPD 16,00 / od 250 | propozycja |
| 3 | XSLT feedu [BM] → `Koszt_dostawy` | 12.92 → 15.26 | propozycja |
| 4 | GMC → produkty źródła „Merchant Center” | 60 szt. → archiwizacja | propozycja |
| 5 | XSLT feedu [BM] | + `g:pattern` (Wzór), `g:product_detail` (Typ kołnierzyka, Dopasowanie, Metoda szycia, Tkanina), `g:product_highlight` (Wyróżnik, min. 2 wartości), `custom_label_1` (Styl) | propozycja |
| 6 | Sklep | 63 zdjęcia ≥ 500×500 (termin 31.01.2027), 4 lepszej jakości, cena jednostkowa w 34 produktach | do klienta |
| 7 | XSLT feedu [BM] → `g:adult` | `yes` dla kategorii menu 605 → usunąć (zostaje `age_group=adult`) | **pilne, do weryfikacji** |
| 8 | XSLT feedu [BM] → `g:material`, `g:color` | material: maks. 4 → 3 wartości; color: rozdzielać wartości złożone `,` → `/` | propozycja |

## Wnioski do skilla

- Rozszerzenie nie robi zrzutów w GMC (`Script injection timed out`), tak samo jak w IdoSell. Zrzuty przez `zrzut.py` działają tylko wtedy, gdy karta MCP jest **aktywną kartą widocznego okna**.
- Tabele GMC (źródła dodatkowe, zasady dostawy, historia pobierania) wczytują się z opóźnieniem; czekać 10–12 s, zanim uzna się listę za pustą.
- Wynik `javascript_tool` jest obcinany do ~1000 znaków → tekst zapisywać do `window.__t` i czytać fragmentami.
- Najwięcej daje panel boczny `…/products/diagnostics/history`: liczby stanów i „Problemy wymagające uwagi (N)”.
- Ikona przy kolumnie „Widoczność” w zasadach dostawy otwiera menu „Pokaż/Ukryj w Google”. Szczegóły kosztów odczytujemy strzałką `expand_more` na początku wiersza; formularz „edit” jest kreatorem, który się nie wczytuje.
- Natywny feed Google w IdoSell: `config-pricecomparers.php?return=google_shopping` (zwykła lista porównywarek go nie pokazuje).
