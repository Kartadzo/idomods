# Zmienne konfiguracyjne szablonów

Pełną, aktualną listę zmiennych globalnych zawsze odczytuję z szablonu:
`python narzedzia/konfiguruj.py zmienne <Szablon.xml>`. Ten plik opisuje tylko znaczenie zmiennych i pułapki dopasowania (stan z 2026-10-27).

## Formaty list
- `|a|b|c|` — lista rozdzielona `|`, z `|` na początku i końcu. Pusta lista to `|`, a nie pusty ciąg.
- Dopasowanie nazw parametrów jest zwykle **bez rozróżniania wielkości liter** (`translate` do małych liter). Wyjątki opisuję w tabelach.

## Standard zapisu (ustalenie 2026-10-27)
- **Parametry:** `|<@id>|<@name po polsku>|`, a dla kilku parametrów pary jedna za drugą: `|21|Kolor|52|Kolor ramy|`. ID zapewnia działanie w innych językach i innych sklepach panelu, nazwa ułatwia czytanie i wyszukanie parametru w panelu. Nazwę zapisuję dokładnie tak, jak w panelu (`/panel/parameters.php`).
- **Węzły menu 1** (`*_id_menu`): `|<@id>|<nazwa węzła po polsku>|`. ID są wspólne dla sklepów tylko wtedy, gdy menu 1 jest współdzielone (`/panel/navigation.php`). W przeciwnym razie zapisuję w `zmiany.md`, że konfiguracja dotyczy jednego sklepu.
- **Wartości parametrów** (`gender_male`, `age_group_kids`…): `|<id wartości>|<nazwa PL>|`.
- Nazwę zapisuję tak jak w panelu. Docelowo wielkość liter nie będzie miała znaczenia (ustalenie z użytkownikiem 2026-10-27).
- Jak to działa w szablonach:
  - `kolor_`, `material_` — `|<@id>|<nazwa>|`. Szablon dopasowuje po ID i po nazwie.
  - `gender_nazwa_w_panelu`, `age_group_nazwa_w_panelu` — docelowo `|<@id>|<nazwa>|` (nowa wersja szablonu przyjmuje listę). Wersja z 2026-10-27 porównuje je jeszcze jako jedną wartość (`@id = $…`). Wtedy `konfiguruj.py` odrzuca listę, a ja wpisuję pojedyncze ID i nazwę podaję w `zmiany.md`.
  - `*_id_menu` — liczy się tylko ID, a nazwa w liście jest tylko dla człowieka.
    ID znajduję po słowach kluczowych w nazwach węzłów Menu 1 (`narzedzia/menu1.js`, SKILL.md krok 1).
  - `waga_`, `pojemnosc_`, `certyfikaty_`, `informacje_wyroznione_` — zostaje zapis, który szablon rozumie (kolumna „Uwagi”), dopóki szablon nie zostanie dostosowany (`propozycje_szablonow.md`).
  - Ogólna reguła: `konfiguruj.py` odrzuca listę `|…|` dla każdej zmiennej, którą szablon porównuje znakiem `=` (`@name = $X`). Ta sama konfiguracja zadziała, gdy szablon zostanie zaktualizowany.

## Google.xml (i Facebook.xml, który ma podzbiór tych zmiennych)

| Zmienna | Znaczenie | Uwagi |
|---|---|---|
| `dlugosc_opisu` | maks. długość `g:description` | Google ≤ 5000 |
| `dlugosc_opisu_z_parametrow` | maks. długość części opisu budowanej z parametrów | |
| `zignoruj_dlugi_opis_jesli_krotki_przekracza` | gdy krótki opis ma więcej znaków niż ta wartość, długi opis jest pomijany | |
| `minimalna_dlugosc_opisu_dla_parametrow` | powyżej tej długości opisu nie dokleja się opisu z parametrów | Google 500, FB 120 |
| `corrected` | słowa w tytule zostawiane z dużej litery, format `\SŁOWO\` | `select`, bez apostrofów w wartości |
| `kwota_dla_darmowej_dostawy` | `*` = dostawa dynamiczna z profilu dostaw (`price_marketplace_site/delivery_cost`); liczba = próg darmowej dostawy; puste = bez `g:shipping` | patrz pytanie o dostawę w SKILL.md |
| `kwota_dla_wiekszych_zamowien` | próg, od którego obowiązuje `Koszt_dostawy_wiekszych_zamowien` | opcjonalna |
| `Koszt_dostawy` | koszt dostawy poniżej progów | format `20.00` |
| `Koszt_dostawy_wiekszych_zamowien` | koszt powyżej `kwota_dla_wiekszych_zamowien` | |
| `Kraj_dostawy` | kod kraju (ISO 3166-1 alfa-2). Służy też do sufiksu linku `.googleshopping<kraj>.html` | `select` |
| `Czas_obsługi_zamówienia_na_magazynie` | dni robocze obsługi (`min/max_handling_time`) | tylko Google, `select` liczbowy |
| `Czas_dostawy_zamówienia` | dni robocze transportu (`min/max_transit_time`) | tylko Google, `select` liczbowy |
| `Serwis_dostawy_zamówienia` | nazwa usługi w `g:shipping/g:service` | |
| `Dni_obsługi_zamówienia_na_magazynie`, `Dni_dostawy_zamówienia` | dni robocze obsługi i dostawy | tylko Google |
| `gender_nazwa_w_panelu` | **jedna** nazwa albo ID parametru płci (nie lista) | puste = tylko `CONTEXT_SEX` lub menu |
| `gender_male` / `_female` / `_unisex` | listy wartości parametru płci | |
| `gender_id_w_panelu` | niepuste = sprawdzaj ID węzłów menu; `*male` = stała wartość dla wszystkich produktów | |
| `gender_*_id_menu` | listy ID węzłów menu (`iaiext:priority_menu`) | przykładowe ID z szablonu **zawsze czyszczę** do `|` |
| `age_group_nazwa_w_panelu`, `age_group_*`, `age_group_id_w_menu`, `age_group_*_id_menu` | jak dla płci (newborn, infant, toddler, kids, adult) | j.w. |
| `kolor_nazwa_w_panelu` | lista nazw/ID parametrów koloru | gdy jest `CONTEXT_COLOR`, ma pierwszeństwo |
| `material_nazwa_w_panelu` | lista nazw/ID parametrów materiału | |
| `informacje_wyroznione_nazwa_w_panelu` | lista parametrów do `g:product_highlight` | **wartość pisać małymi literami** — szablon nie zmienia wielkości liter zmiennej |
| `waga_nazwa_w_panelu` | **dokładna** nazwa parametru wagi (np. `Waga [g]`) | rozróżnia wielkość liter |
| `pojemnosc_nazwa_w_panelu` | **dokładna** nazwa parametru pojemności | rozróżnia wielkość liter |
| `jednostki_-_analiza_nazwy_z_kategorii` | lista ID kategorii, w których jednostki (`unit_pricing_measure`) czytane są z nazwy; `|` = wszystkie | |
| `unitsList` | rozpoznawane jednostki | `select` |
| `certyfikaty_nazwa_w_panelu` | lista parametrów certyfikatów (`g:certification`) | |
| `sales_stocks` | lista ID magazynów liczonych do dostępności | ustawiam według magazynów sklepu |

Placeholdery kanału (Google): `<title>00000</title>`, `<link>https://00000/</link>`, `<description>Produkty ze sklepu https://00000/</description>` — podmieniam przez sekcję `teksty` w `konfiguracja.json`.

Parametry wykluczone z opisu i `product_detail`: szablon pomija parametry użyte w `informacje_wyroznione_`, `certyfikaty_`, `waga_`, `pojemnosc_`.

## Ceneo.xml

| Zmienna | Znaczenie |
|---|---|
| `dlugosc_opisu`, `dlugosc_opisu_z_parametrow`, `minimalna_dlugosc_opisu_dla_parametrow`, `corrected` | jak w Google |
| `czas_dostawy` | `avail` Ceneo dla towaru dostępnego: 1, 3, 7, 14, 90 (na zamówienie), 99 (sprawdź w sklepie), 110 (przedsprzedaż) |
| `czas_dostawy_magazyn_obcy_m0` | jw. dla towaru dostępnego tylko w magazynie obcym (m0) |

## Pozostałe szablony
Glami, Idealo, Compari, Billiger, MCAds, Synerise, samba mają starsze nazwy zmiennych (np. Glami: `Kwota_dostawa_darmo`, `Koszt_wysyłki`). IAI_gAds i Pinterest nie mają zmiennych globalnych. Listę zawsze odczytuję skryptem.
