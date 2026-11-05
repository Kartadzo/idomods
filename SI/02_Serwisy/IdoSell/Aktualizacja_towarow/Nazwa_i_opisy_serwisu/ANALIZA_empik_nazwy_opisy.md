# ANALIZA: nazwa i opisy towarów dla serwisu Empik (IOF CSV)

## Cel

Z eksportu towarów sklepu magnicreatix.pl przygotować plik CSV do importu w IdoSell (Import / aktualizacja towarów, format IOF CSV). Plik ustawia osobną nazwę, opis krótki i opis długi dla serwisu zewnętrznego **Empik Marketplace**. Dane sklepu (`/description/*`) zostają bez zmian.

## Dane wejściowe

- `Sklep/products_export-magnicreatix.pl-2026-10-21_09.14.csv` to eksport IOF CSV: UTF-8, separator `,`, 253 kolumny.
- Ma 36 towarów, po jednym wierszu na towar (`@id` jest unikalne). Pola wielowartościowe są rozdzielone enterem wewnątrz komórki.
- Strona sklepu (`site_id`) to wszędzie `1`.
- Empik (`service_id` 278) jest już podpięty: występuje w `/pricecomparator_price/site@service_id` obok 73.
- Wypełnienie pól źródłowych:
  - `/description/name[pol]`: 36/36, maks. 80 znaków.
  - `/description/short_desc[pol]`: 36/36, maks. 255 znaków.
  - `/description/long_desc[pol]`: 36/36, HTML, maks. ok. 16 tys. znaków.
  - `/description/pricecomparator_name[pol]`: 20/36.

## Struktura docelowa (wg dokumentacji IOF)

Sekcja „Dane dotyczące nazwy oraz opisu dla serwisów sprzedażowych (porównywarek cen, marketplaces)”:

| Kolumna | Wartość |
|---|---|
| `@id` | ID towaru z eksportu |
| `/services_descriptions/name[pol]` | nazwa dla Empik |
| `/services_descriptions/name@site_id` | `1` |
| `/services_descriptions/name@service_id` | `278` |
| `/services_descriptions/short_desc[pol]` | opis krótki dla Empik |
| `/services_descriptions/short_desc@site_id` | `1` |
| `/services_descriptions/short_desc@service_id` | `278` |
| `/services_descriptions/long_desc[pol]` | opis długi dla Empik |
| `/services_descriptions/long_desc@site_id` | `1` |
| `/services_descriptions/long_desc@service_id` | `278` |

To pola wielowartościowe, więc kolejne serwisy dopisuje się po enterze w tej samej komórce. Tutaj jest tylko jeden serwis, czyli jedna wartość na komórkę.

## Dane wyjściowe

`Nazwa_i_opisy_serwisu/empik_nazwy_opisy_magnicreatix.csv` z kodowaniem UTF-8, separatorem `,`, wszystkimi polami w cudzysłowach i enterami w HTML zachowanymi wewnątrz komórek. Plik zawiera tylko kolumny z tabeli powyżej, więc import nie dotknie cen, stanów, zdjęć ani parametrów.

## Planowane zmiany

- Jednorazowy skrypt `Nazwa_i_opisy_serwisu/empik_opisy.py` (Python, biblioteka standardowa, `csv.DictReader`/`csv.writer`). Wejście i wyjście wykrywa sam we własnym folderze i w `../Sklep/`, więc działa po dwukliku z `run_empik_opisy.bat`.
- Na koniec skrypt wypisuje raport: liczbę towarów, liczbę usuniętych linków i towary z pustą nazwą lub opisem. Nazwa pliku wyjściowego dostaje sklep i znacznik czasu: `empik_nazwy_opisy_<sklep>_<data>.csv`.

## Decyzje (potwierdzone 2026-10-21)

1. Treść kopiuję ze sklepu. Z opisu długiego usuwam wszystkie znaczniki `<a ...>` i `</a>`, a tekst i obrazki ze środka linku zostają. Dzięki temu zdania się nie urywają.
2. `pricecomparator_name` zostaje nietknięte. Nazwę Empik (`/services_descriptions/name[pol]`) biorę z `/description/name[pol]`.
3. Bez opisu krótkiego: kolumn `short_desc` nie ma w pliku.
4. Plik obejmuje wszystkie 36 towarów, także te bez linków, na zapas.

Kolumny wyjściowe: `@id`, `/services_descriptions/name[pol]`, `name@site_id`, `name@service_id`, `long_desc[pol]`, `long_desc@site_id`, `long_desc@service_id`. Wartości to `site_id = 1`, `service_id = 278`.
Format jak w eksporcie IdoSell: UTF-8 bez BOM, nagłówek bez cudzysłowów, wartości w cudzysłowach, końce linii LF.

## Uwagi

- Niektóre opisy (np. id 19, 42, 43, 44, 46, 47, 49) zawierają kafelki polecanych produktów (`mc-tile-img`/`mc-tile-name`) i przyciski. Po usunięciu linków zostaną w nich obrazki i nazwy bez linków. Jeśli te bloki mają zniknąć z opisu Empik w całości, trzeba to zrobić w osobnym kroku.

## Etap 3 (2026-10-21): poprawka gotowego eksportu dla Empik

- Import IOF CSV nie zadziałał, więc nazwę i opis Empik dla 36 towarów ustawiłem ręcznie w panelu (Marketplaces → Empik → „użyj podanego poniżej”).
- Wejście: `IdoSell_empikProducts_2026-10-07_08-53_26_1.csv`. To eksport IdoSell dla Empiku: separator `;`, 13 towarów, 35 kolumn.
- Pole `ProductDescriptionLong` ma postać `\n<div><b>TYTUŁ</b></div>\n<div>OPIS_SKLEPU</div>\n<div>TABELA_PARAMETRÓW</div>\n`.
- `empik_eksport_opisy.py` usuwa `<a>`/`</a>` tylko w części OPIS_SKLEPU. Podmiana odbywa się na surowym tekście, więc reszta pliku zostaje bajt w bajt (separator `;` i CRLF jak w oryginale).
- Wynik: `IdoSell_empikProducts_2026-10-07_08-53_26_1_bez_linkow.csv`. Zmieniono 12 opisów i usunięto 50 linków. Produkt 31 nie miał linków.
