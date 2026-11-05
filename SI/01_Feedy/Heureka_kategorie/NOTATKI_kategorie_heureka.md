# Kategorie Heureka — notatki robocze

Ustalenia z 2026-08-24. Czytaj przed kolejną zmianą w tym folderze.

## Zasada nadrzędna

**Pracujemy wyłącznie na plikach z tego folderu.** Nie szukamy danych w innych
katalogach repozytorium ani poza nim. Jeśli czegoś brakuje — pytamy, a
brakujący plik zostaje przeniesiony tutaj.

## Co jest czym

| Plik | Rola |
| --- | --- |
| `app.py` + `run.bat` | mapowanie kategorii źródłowych na Heurekę, wytwarza raporty i XSLT ID→ID |
| `raport_idosell_SK.csv` | kategorie menu sklepu (`category/@id`) → ID Heureka, 46 dopasowań z 205 |
| `raport_google_CZ.csv` | taksonomia Google → ID Heureka, 1354 dopasowania z 5595 |
| `povinné názvy SK / CZ - List 1.csv` | ID Heureka → segment + nazwa kategorii |
| `build_categorytext.py` + `run_categorytext.bat` | składa z powyższych blok XSLT i wstawia go do arkusza feedu |
| `heureka_categorytext.xslt` | ten sam blok osobno, do podglądu |
| `topfitSK_Heureka.xml` | arkusz feedu Heureka dla topfit.sk (bliźniak z `xslt/1-+0/4fizjo/`) |

## Postać CATEGORYTEXT

`Heureka.sk | <segment> | <nazwa kategorii>` — np. `Heureka.sk | Šport a outdoor | Kettlebell`.

Segment i nazwa pochodzą z pliku „povinné názvy”. **To nie jest pełna ścieżka
z drzewa Heureki** — brakuje poziomów pośrednich, bo w tym folderze nie ma
pliku z pełnym drzewem (`CATEGORY_FULLNAME`). Jeśli Heureka zacznie odrzucać
kategorie, trzeba dorzucić tutaj eksport ich drzewa i przebudować
`heureka-id-to-path`.

## Skąd biorą się ID w feedzie

* **Taksonomia Google** — `searchGoogleCategory` w arkuszu feedu: `category_idosell/@id`
  → ID taksonomii Google. To **ręczne mapowanie utrzymywane przez MD**, 30 wpisów.
  Zwraca `0`, gdy nie zna kategorii.
* **Menu sklepu** — `category/@id` (np. `1214554027`). Klucz `raport_idosell_SK.csv`.
* **`price_comparison/@category_id` odpada** — węzeł `iaiext:price_compare_categories`
  nie jest dostępny w silniku XSLT 1.0 IdoSell w czasie generowania feedu.
  Nie wracać do tego pomysłu.
* **`category_idosell/@id` nie jest ID Google** — sprawdzone na eksporcie 371 par:
  tylko 4 zgodne z numerem wiersza taksonomii. To wewnętrzna numeracja IdoSell
  i właśnie dlatego potrzebny jest ręczny `searchGoogleCategory`.

### Pokrycie łańcucha Google (stan 2026-08-24)

Z 30 wpisów `searchGoogleCategory` tylko **8** ma odpowiednik w
`google-category-to-heureka` — reszta to ID Google, którym app.py nie znalazł
żadnej kategorii Heureka (score 0.0). Pozostałe 22 to w dużej części kategorie,
które w Heurece istnieją (plavecké okuliare, podložky na jogu, penové valce,
cvičebné lopty, posilňovacie hrazdy) — fuzzy ich nie złapało. Najtańsza
poprawa: uzupełnić `heureka_id` przy tych wierszach w `raport_google_CZ.csv`
ręcznie i przebudować blok generatorem.

## Mapa CZ w feedzie SK

`raport_google_CZ.csv` powstał na taksonomii cs-CZ (Google nie ma sk-SK), ale
**ID kategorii Heureki są wspólne dla .cz i .sk** — 3658 z 3661 ID z pliku SK
występuje też w CZ. Dlatego mapujemy po ID z raportu CZ, a nazwę i segment
bierzemy z pliku SK. 7 wpisów Google odpada, bo ich ID nie ma w wykazie SK.

## Kolejność w `topfitSK_Heureka.xml`

Sekcja CATEGORYTEXT (ok. linii 349):

1. `searchGoogleCategory` z `category_idosell/@id` → `$var_google_product_category`,
   a to przez `google-category-to-heureka` na ID Heureki — **taksonomia Google ma
   pierwszeństwo** (decyzja MD z 2026-08-24),
2. jeśli pusto — `idosell-category-to-heureka` z `category/@id` (menu sklepu),
3. jeśli dalej pusto — dotychczasowa logika: ścieżka z menu (`iaiext:navigation`),
   `category_idosell/@path`, `category/@name`.

Wybór źródła robi jawny `xsl:choose`, nie `concat` dwóch zmiennych. Sklejenie
dwóch niepustych ID dałoby liczbę spoza mapowania, czyli **cichy brak
CATEGORYTEXT** zamiast błędu — dlatego gałęzie muszą być rozłączne wprost.

Szablony mapowania siedzą na końcu pliku między `<!-- HEUREKA-MAP:START -->`
a `<!-- HEUREKA-MAP:END -->` i są **generowane** — ręczne poprawki nadpisze
`build_categorytext.py`. Poprawiaj raporty CSV i przebuduj blok.

## Pułapki

* Arkusze feedów są w **CRLF**. Generator czyta i zapisuje z `newline=""`,
  żeby nie przerobić całego pliku na LF (raz już się to zdarzyło).
* W komentarzach XML **nie może być podwójnego myślnika** — parser to odrzuca.
* Zmiana dotyczy kopii w `SI/01_Feedy/Heureka_kategorie/`. Bliźniaczy plik w
  `xslt/1-+0/4fizjo/topfitSK_Heureka.xml` trzeba nadpisać osobno, świadomie.
* Jakość mapowania: fuzzy, sufit trafności ok. 25% dla kategorii sklepu.
  Kolumna `do_przegladu` w raportach wskazuje wpisy warte ręcznej weryfikacji —
  poprawka w CSV plus ponowne uruchomienie generatora wystarczy.
