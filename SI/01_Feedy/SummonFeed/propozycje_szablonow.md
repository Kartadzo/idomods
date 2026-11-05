# Propozycje zmian w szablonach Google.xml i Facebook.xml

Ten plik zawiera tylko propozycje. Szablony zmienia użytkownik, a skill ich nie edytuje.

## 1. Jednolity format zmiennych parametrów: `|<@id>|<@name PL>|` (2026-10-27)

**Status:** odłożone. Użytkownik zaktualizuje szablony, gdy pojawi się potrzeba. Do tego czasu skill stosuje zapis zgodny z szablonem (`zmienne_szablonow.md`, „Standard zapisu”).

**Cel:** jedna konfiguracja działa w każdej wersji językowej i w każdym sklepie panelu, bo dopasowanie idzie po ID parametru. Polska nazwa ułatwia czytanie i znalezienie parametru w panelu. Przykład: `|21|Kolor|`, `|36|Materiał wykonania|`, a dla kilku parametrów `|21|Kolor|52|Kolor ramy|`.

**Jednolity predykat** (XSLT 1.0, kontekst `parameter`, `V` = zmienna). Dwie ostatnie alternatywy zachowują zgodność ze starym zapisem pojedynczą nazwą (`Płeć`, `Waga [g]`):
```xpath
(contains($V, concat('|', @id, '|'))
 or contains(translate($V, $upperLetters, $lowerLetters), concat('|', translate(@name, $upperLetters, $lowerLetters), '|'))
 or @name = $V or @id = $V)
```
Wykluczenie (np. z `product_detail`): `not( <predykat> )`.

### Stan obsługi w szablonach (2026-10-27)
| Zmienna | Google | Facebook | Co zmienić |
|---|---|---|---|
| `kolor_nazwa_w_panelu`, `material_nazwa_w_panelu` | dopasowanie OK (ID + nazwa bez wielkości liter) | OK | Google l. 1070–1071, 1083–1084: wykluczenie z `product_detail` porównuje nazwę małymi literami z niezmienioną zmienną, więc `|21|Kolor|` nie wyklucza → predykat |
| `informacje_wyroznione_nazwa_w_panelu` | tylko nazwa, zmienna bez `translate` (l. 1048–1052, 1066, 1072, 1079, 1085) | — | predykat |
| `certyfikaty_nazwa_w_panelu` | tylko nazwa (l. 819–820); wykluczenie `contains($V, @name)` (l. 1069, 1082) | — | predykat |
| `waga_nazwa_w_panelu`, `pojemnosc_nazwa_w_panelu` | `@name = $V` (l. 898–899, 922–923); wykluczenie `contains($V, @name)` (l. 1073–1074, 1086–1087) | — | predykat (w `raw` też: `parameters/parameter[<predykat>]/value/@name`) |
| `gender_nazwa_w_panelu`, `age_group_nazwa_w_panelu` | `@name = $V` lub `@id = $V` (l. 677–691, 737–751); wykluczenie `contains($V, @name)` (l. 1067–1068, 1080–1081) | to samo (l. 587–601, 638–652) | predykat; `gender_wer` i `id_gender_wer` brać z tego samego `parameters/parameter[<predykat>]` |

Numery linii dotyczą stanu szablonów z 2026-10-27.

## 2. Listy ID węzłów menu: `|<@id>|<nazwa węzła PL>|`

Dotyczy zmiennych `gender_*_id_menu`, `age_group_*_id_menu` (`iaiext:priority_menu/site/menu[1]/item/@id`). Dopasowanie `contains($V, concat('|', @id, '|'))` już przyjmuje ten format. **Szablon nie wymaga zmian**, nazwa w liście służy tylko człowiekowi.

Warunek przenośności: ID węzłów są wspólne dla sklepów tylko wtedy, gdy menu 1 jest współdzielone między sklepami panelu. Sprawdzam to w `/panel/navigation.php`. Gdy menu nie jest współdzielone, konfiguracja działa tylko w sklepie, dla którego ją przygotowano, i zapisuję to w `zmiany.md`.

Wartości parametrów (`gender_male`, `age_group_kids`…) dopasowywane są po nazwie wartości bez wielkości liter albo po ID wartości, gdy `*_nazwa_w_panelu` wskazuje parametr po ID. Proponuję ten sam zapis `|<id wartości>|<nazwa PL>|`, ale pełna niezależność od języka wymaga, żeby `id_gender_wer` był liczony zawsze, a nie tylko przy dopasowaniu parametru po ID (rozwiązuje to predykat z pkt 1).

## 3. Ceneo.xml — avail, „Wersja”, aktualizacje z Google.xml (2026-10-28, shop49855-1)

| Zmiana | Obecnie w Ceneo.xml | Propozycja |
|---|---|---|
| Warunek czasu wysyłki | `sum(stock/@available_stock_quantity) > 0` — stan nieograniczony (`-1`) trafia do gałęzi „brak stanu” (`czas_dostawy_magazyn_obcy_m0`) | `$avail > 0` (zmienna już zamienia `-1` na 999999) |
| Atrybut „Wersja” | `<![CDATA[towar fizyczny]]>` z wcięciami → wartość z `\n` i spacjami | `<xsl:text>towar fizyczny</xsl:text>` |
| Magazyny | sztywna lista ID w `sum(stock[@id = '1' or …])` | zmienna `sales_stocks` jak w Google.xml (2026.01.13) |
| Tytuł | stara `nazwaTowaru` bez sprawdzenia języka i limitu | `wybierzZrodloNazwy` z Google.xml (2026.04.30), limit 146 + „...” |
| `strip-tags` | wersja bez `open`/`close` | wersja z Google.xml (2026.05.07) |

Wdrożone w kopii `sterowniki/shop49855-1.yourtechnicaldomain.com/` (opis w `zmiany.md`).

## 4. Ceneo.xml a sterowniki klientów matfel i ezebra (2026-10-28)

Porównane: `xslt/szablony/Ceneo.xml` (treść z 2025-07-23, brak datowanych komentarzy) z `xslt/M-N/matfel/matfel_Ceneo.xml` (2026-10-13), `SI/01_Feedy/Ceneo_mapowanie_parametrow/matfel_Ceneo.xml` (wersja robocza z mapowaniem) i `xslt/E/ezebra/PL/ezebra_ceneo_RTB.xml` (2026-10-13). Inna branża (książki, elektronika), ale logika wspólna.

| Element | Ceneo.xml | matfel | ezebra | Ocena |
|---|---|---|---|---|
| **Opis — potok czyszczenia (2026.07.08)** | tylko `strip-tags` + `tokenize` | `string-normalize-all` → `&nbsp;`→spacja → usunięcie komentarzy, `<style>`, `<img>` → `strip-tags` → `tokenize` | jak matfel | **Brak w szablonie** — główna przyczyna różnic w opisie; ten sam potok jest w Google.xml |
| Normalizacja encji HTML → Unicode | brak | tak | tak | brak w szablonie |
| Opis z bloków HTML (`$klasy_opisu`, 2026.08.28) | brak | — | tak | opcjonalne, dedykowane sklepom z sekcjami opisu |
| `strip-tags` z `open`/`close` (2026.05.07) | stara wersja | tak | tak | brak w szablonie (w kopii magnicreatix już podmienione) |
| Kategoria `cat` | `category/@name` | `ceneoCat`: mapowanie kategorii sklepu → ścieżka/ID Ceneo (generowane `mapowanie_kategorii.py`), fallback na kategorię sklepu | `category/@name` | propozycja: pusty szablon nazwany `ceneoCat` z fallbackiem — wypełniany per sklep ze słownika API |
| Atrybuty kategorii | wszystkie widoczne parametry pod nazwą z panelu | dedykowane mapowanie Księgarni (Autor, Okładka, Ilość stron, Język, Wydawnictwo, Format, ISBN/EAN) | kolor, płeć, wiek, adult, omnibus_price, product_highlight (nazwy w stylu Google) | dedykowane — nie przenosić; do szablonu najwyżej mechanizm warunkowania atrybutów po `$ceneo_cat_id` |
| EAN | tylko po `producer_code_standard` | walidacja cyfr 8/13, odsiew `_BAD_EAN`, ISBN-10/13 | po standardzie | propozycja: walidacja długości/cyfr EAN |
| Towary wirtualne | avail jak fizyczne | osobna gałąź, avail = 1 | — | dedykowane (matfel: e-booki) |
| GPSR (ID) | tak | tak | tak | zgodne |

**Do decyzji przy aktualizacji szablonu głównego** (kopia zapasowa do `xslt/szablony/old/`): potok opisu 2026.07.08 + normalizacja encji, `strip-tags` 2026.05.07, poprawki z pkt 3 (avail `-1`, „Wersja”, `sales_stocks`, `wybierzZrodloNazwy`), opcjonalnie pusty `ceneoCat` i walidacja EAN.
