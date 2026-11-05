# Analiza: powiązanie produktów Base ↔ IdoSell (`data (37).csv`)

> **Status 2026-10-21 (wieczór): wznowione — plik dla 2412 pewnych par.** Trzy metody: (A) SKU wFirmy → `short_description` Shoparena → `KZS-…` w IdoSell (także 301 nowo importowanych towarów), (B) numer części z nazwy IdoSell, (C) SKU wFirmy = krótki opis IdoSell. Do pliku idzie para wskazana przez ≥ 1 metodę, jeśli żadna inna metoda nie wskazuje innego towaru. Sprzeczności: 0. Wyjście: `powiazania_base_idosell.csv` (`ID_BL;ID_produktu;ID_wariantu`, wariant pusty, bez nagłówka, `;`, jak plik z Base) + `powiazania_base_raport.csv` (metody, nazwy po obu stronach, 1659 bez pary). ID nowych towarów skrypt `powiaz_base_idosell.py` pobiera ze sklepu na żywo po kodzie zewnętrznym.
>
> Poprzednio: **wstrzymane.** Dopasowanie po OE (~2234 pewnych z 4071) użytkownik uznał za za niskie. Czekamy na eksport z wFirmy od klienta — ma dać dodatkowe kody do dopasowania produktów wFirma ↔ IdoSell.

## Cel

Uzupełnić plik `data (37).csv` z Base o kolumny „ID produktu” i „ID wariantu” ze sklepu IdoSell,
tak żeby dało się go wczytać w Base i powiązać produkty z katalogu BL z towarami w sklepie.
Format wiersza wg Base: `ID produktu z katalogu BL;ID produktu;ID wariantu` (SKU i EAN na końcu są opcjonalne).

## Dane wejściowe

| Plik | Zawartość |
|---|---|
| `data (37).csv` | 4071 wierszy, uzupełniona tylko kolumna 1 (ID BL, zakres 1307406336–1307411586). Kolumna 4 to SKU, ale **bez cudzysłowów** — SKU zawierające `;` (np. `16683435 ; 16683434`) rozjeżdżają kolumny (215 wierszy ma 6–10 pól). |
| `Base__Produkty__…csv` | Katalog BL, 11 706 produktów, separator `;`. Wszystkie 4071 ID z `data (37)` są w nim. SKU ma 4066 z nich, EAN — żaden. |
| `products_export-shop52797…csv` | Eksport IdoSell, 4035 towarów. 4027 to `uniw` (bez rozmiarów), 8 ma rozmiary. Kody: `@code_producer`, `size@code_external` prawie puste — **numery OE są wpisane w nazwy** (`14058721 Iveco Daily 35S 98-06 nakrętka strzemienia resoru`). |

## Ustalenia z analizy danych

1. **Dokładne dopasowanie nie działa.** Po nazwie pasuje 1 produkt, po SKU vs kody IdoSell — 7.
2. **Działa dopasowanie po numerach OE**: z SKU i nazwy BL wyciągam tokeny typu „kod” (≥ 6 znaków, ≥ 4 cyfry, bez kropek/myślników) i szukam ich w nazwie + polach kodów IdoSell. Do tego punktacja zgodności słów nazwy (bez „Iveco”, „Daily”). Wstępny wynik:

   | Klasa | Liczba | Przykład |
   |---|---|---|
   | pewne (wszystkie kody SKU trafione, ≥ 50% słów, wyraźna przewaga nad 2. kandydatem) | 2234 | `14058721 nakrętka strzemienia resoru 35S 98-06` → 3255 |
   | prawdopodobne | 111 | `3803145 POSZYCIE PODŁOGI PRZY DRZWIACH PRZESUWNYCH` → 3803145 … środkowe poszycie podłogi |
   | niejednoznaczne (kilku kandydatów) | 406 | `1906401 KLOCKI HAMULCOWE P/T` → oryginał czy „ZAMIENNIK”? |
   | brak kandydata | 1320 | `000025 OBUDOWA TYLNEGO MOSTU` — SKU wewnętrzne, brak OE |

3. **Duża część niejednoznacznych to para oryginał / „ZAMIENNIK”** w IdoSell z tym samym numerem OE. Reguła: jeśli nazwa BL nie zawiera „zamiennik”, wybieram towar IdoSell bez „ZAMIENNIK” (i odwrotnie) — powinno to rozstrzygnąć sporą część z 406.
4. **⚠ Podejrzenie duplikatów w katalogu BL.** W katalogu Base jest ~4000 starszych produktów (ID 1227…) o nazwach identycznych z IdoSell — wyglądają na zaimportowane ze sklepu i zapewne już powiązane. Aż **2683** towary IdoSell, które dopasowałem do nowej partii 1307…, mają już taki „starszy” odpowiednik w BL. Nowa partia (nazwy WIELKIMI LITERAMI, SKU magazynowe) wygląda na osobny import tych samych części.
5. 23 towary IdoSell trafiają do więcej niż jednego produktu BL — do oznaczenia, nie wpisuję automatycznie.

## Eksport powiązań z Base (`Base__Produkty__powiazania_CSV_po_…csv`)

- Źródła w BL: `accounting` wFirma.pl — 4074 produkty (dokładnie partia 1307…), `shop` 20947 „IVEMAX.COM” (Shoparena) — 4009, `otomoto` — 1398, `shop` 37567 **„IVEMAX-IdoSell”** — tylko 3.
- Te 3 istniejące powiązania wFirma→IdoSell (2332, 3247, 2968) — moje dopasowanie po OE daje dokładnie tych samych kandydatów (jedynych). Walidacja OK.
- Potwierdzone: `wariant_id` pusty dla towarów IdoSell bez rozmiarów → pytanie 3 zamknięte.
- Produkty już powiązane z IVEMAX-IdoSell pomijam w pliku importu.

## Eksport Shoparena (`shopArena - 2029-10-21.csv`, 4220 produktów)

Kontekst od klienta: towary w IdoSell pochodzą z Shoparena, bo mają tam lepsze dane. W Shoperze zamiast kodu producenta jest liczba porządkowa. Numer części celowo wpisywano w nagłówek (nazwę), a polityki magazynowej wtedy nie było. Docelowo produkty mają być powiązane przez Base z wFirmą (ceny, stany).

- **Most Shoparena → IdoSell:** `size@code_external` w IdoSell = `KZS-<product_code>` albo `<product_code>` (forma `6420_20231213101120`). Dokładnie 3917 z 4220 kodów Shoparena ma swój towar w IdoSell, bez duplikatów.
- **Most wFirma → Shoparena:** SKU wFirmy = `short_description` w Shoparenie (np. `14058811`). Kody `barcode`, `producer_code` i `warehouse_code` są puste.
- Łańcuch wFirma SKU → Shoparena → IdoSell daje 2127 jednoznacznych par. Na 3 istniejących powiązaniach (SKU 14058811 → 5542 → 2332 itd.) daje 3/3 trafień. Tych 3 produktów nie ma w `data (37)`, bo Base pominął już powiązane.
- **Porównanie z dopasowaniem po OE (ścisłym, 2239):** w 2019 przypadkach dopasowanych obiema metodami wynik jest **zgodny w 100%**. Suma obu metod: **2347** z 4071.
- 19 towarów IdoSell trafia do więcej niż jednego produktu wFirmy (65 wierszy) — do weryfikacji.
- Bez pary zostaje 1724 produktów wFirmy przy 1734 wolnych towarach IdoSell. Liczby są prawie równe, więc większość prawdopodobnie ma swoją parę, tylko kody jej nie łączą (puste SKU, SKU wewnętrzne `0000xx`, nazwy pisane inaczej). Kandydat na kolejny krok: dopasowanie nazw tylko w obrębie tych pozostałych.

## Planowane zmiany / wyjście

Skrypt jednorazowy (Python, stdlib) w tym folderze, np. `powiaz_base_idosell.py` + `run_powiaz.bat` (działa po dwukliku, pliki wykrywa sam po prefiksach). Wyjście:

- `powiazania_do_importu.csv` — tylko wiersze **pewne** (+ rozstrzygnięte regułą oryginał/zamiennik), format `ID_BL;ID_produktu;ID_wariantu;SKU;EAN`, kodowanie UTF-8, separator `;` (wymóg Base, nie mój domyślny przecinek).
- `powiazania_do_weryfikacji.csv` — prawdopodobne, niejednoznaczne, konflikty i brak kandydata: ID BL, SKU, nazwa BL, top 3 kandydatów IdoSell (ID + nazwa + punktacja), klasa — do ręcznego przejrzenia.

## Założenia

- **ID wariantu puste** dla towarów `uniw` (wszystkie dopasowane są `uniw`; 8 towarów z rozmiarami nie trafiło do żadnego dopasowania).
- SKU biorę z eksportu katalogu Base (poprawnie cytowany CSV), nie z rozjechanego `data (37)`.
- Jeden towar IdoSell → jeden produkt BL; przy kolizji oba trafiają do weryfikacji.

## Otwarte pytania

1. ~~Duplikaty (pkt 4)~~ — **wyjaśnione przez użytkownika:** starsze produkty BL (1:1 z nazwami IdoSell) pochodzą z Shoparena i nie są powiązane z wFirmą. Nowa partia 1307… to produkty z wFirmy (źródło cen i stanów) — to je wiążemy z IdoSell. Podwójne dopasowanie nie jest problemem, tylko celem.
2. Czy do pliku importu wpuścić też klasę „prawdopodobne” (111), czy tylko „pewne”?
3. ~~Puste pole czy `0` dla wariantu~~ — puste, potwierdzone eksportem powiązań.
4. Import w Base trzeba wykonać w kontekście integracji **IVEMAX-IdoSell (37567)**, nie IVEMAX.COM (Shoparena).
