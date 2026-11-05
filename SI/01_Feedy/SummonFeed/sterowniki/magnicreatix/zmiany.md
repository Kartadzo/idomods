# Sterownik Ceneo — shop49855-1.yourtechnicaldomain.com (sklep 1)

- Data: 2026-10-28
- Szablon: `xslt/szablony/Ceneo.xml`, commit 4979c07 (2026-06-10), sha256 8f0171900494, bez niezatwierdzonych zmian
- Wynik: `shop49855-1.yourtechnicaldomain.com_ceneo.xml` (XSLT 1.0) — do ręcznego wgrania w panelu (serwis Ceneo jeszcze nie istnieje w porównywarkach sklepu)
- Wymagania: `wymagania/ceneo.md` (przegląd 2026-10-27, aktualne)

## Odpowiedzi
| Pytanie | Odpowiedź |
|---|---|
| Dostawa | nie dotyczy — format Ceneo nie ma kosztu dostawy |
| Link (`o/@url`) | **C** — link z oferty `card/@url` (bez sufiksu `.ceneo.html`) |
| `item_group_id` | nie dotyczy — w Ceneo każdy rozmiar to osobna oferta |
| `avail` dla towaru bez stanu w magazynach sprzedaży | **3** (`czas_dostawy_magazyn_obcy_m0`), było 1 |
| Test | eksport sklepu `products_export-magnicreatix.pl-2026-10-28_14.47.xml` (36 produktów, dostarczony przez użytkownika); wcześniej próbka zastępcza `SI/01_Feedy/SummonFeed/dane/products_export.xml` |

## Dane sklepu (panel, odczyt)
- Jeden sklep (`shop=1`), 36 produktów w feedach Google/FB.
- Magazyny: M1 główny (wysyłka < 1 dzień), M0 obcy (czas zależny od dostawcy), MM przesunięć, MP przedsprzedaży.
- Parametry (6): Długość/Szerokość/Wysokość towaru w cm, Waga gabarytowa w gramach, „rodzaj” (1), „Stan” (Nowy). Brak koloru, materiału, płci — szablon Ceneo przekazuje wszystkie widoczne parametry jako `attrs/a`, więc nie wymaga mapowania.

## Zmienne
| Zmienna | Przed | Po |
|---|---|---|
| `czas_dostawy` | 1 | 1 (M1 wysyła < 24 h) |
| `czas_dostawy_magazyn_obcy_m0` | 1 | **3** |
| `sales_stocks` (nowa, z Google.xml) | — | `\|0\|1\|` (M0, M1) |

## Zmiany logiki w kopii
1. **Link — wariant C:** `substring-before(card/@url, '.feed')` + `.ceneo.html` → sam `card/@url`.
2. **Tytuł (z Google.xml 2026.04.30):** `nazwaTowaru` → `wybierzZrodloNazwy` (nazwa dla porównywarki tylko w języku oferty, `wordFormat` przed korektą wielkości liter, przycięcie do 146 znaków + „...” — mieści się w limicie Ceneo 150). Pominięto `normalize-polish-pairs` (brak w szablonie Ceneo).
3. **Opis z parametrów (z Google.xml 2026.07.08):** blok `from_parameters_raw`/`from_parameters` był już identyczny — bez zmian.
4. **Dostępność (z Google.xml 2026.01.13):** stany liczone tylko z `sales_stocks` zamiast sztywnej listy ID (`1,0,2…6,-1,-2,-3`) w `stocksGobalCheck`, `avail` i warunku czasu wysyłki.
5. **`strip-tags` (z Google.xml 2026.05.07):** nowa wersja z parametrami `open`/`close` i obsługą niedomkniętego znacznika.
6. **Poprawka `avail`:** warunek „towar na stanie” był `sum(stock/@available_stock_quantity) > 0`, więc stan nieograniczony (`-1`) trafiał do gałęzi „brak stanu” (na próbce wszystkie 45 ofert miały avail = wartość dla M0). Teraz `$avail > 0` (zmienna już zamienia `-1` na 999999). → **propozycja do szablonu Ceneo.xml**.
7. **Atrybut „Wersja”:** CDATA z wcięciami dawało w wartości znaki nowej linii; teraz `<xsl:text>towar fizyczny|wirtualny</xsl:text>`. → **propozycja do szablonu**.

## GPSR
- Kopia przekazuje w `attrs` tylko identyfikatory: „Producent odpowiedzialny” = `iaiext:responsible_entity/producer/@id`, „Podmiot odpowiedzialny” = `iaiext:responsible_entity/persons/person/@id`. Bloków `responsibleProducers`/`responsiblePersons` nie generujemy (ustalenie z użytkownikiem 2026-10-28) — pełne dane wgrywane plikiem CSV w panelu Ceneo.
- CSV generuje narzędzie `python/transform_xml — gpsr` z eksportu IOF: kolumna „Nazwa wlasna” = te same `@id`. Błąd gałęzi „Podmiot” (dane z `producer` zamiast `persons/person`) opisany w `python/transform_xml — gpsr/ANALIZA_gpsr_ceneo.md`; skrypt źródłowy poprawił użytkownik.
- **Narzędzie:** oryginał `python/transform_xml — gpsr` (poprawiony przez użytkownika 2026-10-28; tymczasowa kopia `gpsr/` usunięta).
- Wynik na eksporcie sklepu: 2 wiersze — Producent ID 1, Podmiot ID 2 (oba „ZABAWKI DLA DZIECI EWA POCHEĆ”, Radkowice 108A, 27-225 Pawłów, bez telefonu). ID zgodne z atrybutami w feedzie (35 z 36 ofert).

## Weryfikacja
`weryfikuj.py --element o --wymagane "@id,@url,@price,@avail,name,cat"` → **OK**, 45 rekordów `<o>` z 48 produktów próbki (3 odfiltrowane: cena 0 lub brak nazwy). Ręcznie: link `card/@url`, avail 1 przy stanie nieograniczonym, „Wersja” bez białych znaków, nazwa ≤ 150 znaków.

## Weryfikacja na eksporcie sklepu (po zmianie opisu przez użytkownika)
`weryfikuj.py --oferta products_export-magnicreatix… --element o` → **OK**, 36 ofert = 36 rozmiarów w ofercie; avail 1 (35) i 3 (1); nazwa max 149 znaków; link wariant C z `card/@url`.

## Uwagi
- **Produkt 45** („Klocki Magnetyczne Zestaw magnetycznych Figurek 4 el.”): pusty blok GPSR w panelu (brak atrybutów odpowiedzialnych w feedzie), kategoria „*Kategoria tymczasowa” (trafi do `cat` w Ceneo), adres karty bez `/pl/products/`. Do uzupełnienia w panelu przed wysyłką do Ceneo.
- Opis w sterowniku zmieniony przez użytkownika (warunki Ceneo) — nie modyfikowałem go.
- Atrybut `set` z szablonu nie jest opisany w poradniku Ceneo — zostawiony bez zmian.
