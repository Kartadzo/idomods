# ANALIZA: Romanetka.pl — plik powiązań Base ↔ IdoSell

Data: 2026-10-27. Kontekst i diagnoza integracji: `SI/02_Serwisy/Base/Analiza/sklep/romanetka/ANALIZA_base_idosell_romanetka.md` (wybrany wariant B).
ClickUp: [Romanetka.pl - Problem z połączenie Base - Idosell](https://app.clickup.com/t/869ezaw5q)

## Cel zadania (własnymi słowami)
Zbudować plik importu powiązań do Base, który połączy istniejące produkty katalogu „Domyślny” z istniejącymi towarami IdoSell (integracja „IdoS Romanetka”, ID 3026512). Nie tworzymy żadnych nowych towarów. Po wczytaniu pliku stany i ceny z Base zaczną trafiać do sklepu.

## Dane wejściowe (`źródło/`)

| Plik | Zawartość | Uwagi |
|---|---|---|
| `Base__Products__default_CSV_2026-10-27_17_56.csv` | 98 950 produktów katalogu „Domyślny” (`;`) | SKU **nieunikalne**: 1 784 różnych SKU (np. `zasłony milas` ×1514). EAN ma 42 424 produktów, 30 EAN-ów się powtarza. Część SKU ma na końcu tabulator. |
| `Base__Products_powiązania_CSV_Po_2026-10-27_17_59.csv` | powiązania produktów (szablon z błędnym cudzysłowem, parsowany po typie źródła) | Z IdoSell powiązanych jest **208** produktów BL, ale wskazują tylko **5 towarów** (29228 ×83, 29229 ×78, 29230 ×45, 23532, 29129). To błędne powiązania (np. 83 różne firany → jedna zasłona 29228). |
| `products_export-romanetka.pl-2026-10-27_18.30.csv` | 29 218 towarów IdoSell (CSV z panelu, `,`) | Każdy towar ma jeden rozmiar `uniw` (wymiar = osobny towar w grupie, 138 grup). EAN w `size@code_producer` ma 26 164 towarów (wszystkie unikalne). Wartość grupy zawiera `Wysokość \ Szerokość \ SKU`. 102 towary mają pełne SKU w `@code_producer`. Widoczne: 17 895, ukryte: 11 323. |
| `do powiązania - nie pełna lista.csv` | 50 wierszy `ID_BL;;;SKU;EAN` | Traktuję jako **wzór formatu wyjścia** i próbkę testową od klienta, nie jako zakres. |

## Wyniki wstępnego dopasowania (próba na danych, bez zapisu)

| Metoda | Pary | Jakość |
|---|---|---|
| 1. EAN Base = `size@code_producer` IdoSell | **19 156** (1:1, bez duplikatów po obu stronach) | wymiar z nazwy zgodny w 18 956, brak wymiaru w nazwie 199, 1 „niezgodność” to ucięta nazwa w IdoSell (`450x14`) |
| 2. Pełne SKU z `@code_producer` IdoSell = SKU Base | do 102 (do policzenia po odjęciu metody 1) | SKU typu `004017/FBL/001/300160/1` zawiera wymiar, więc jest jednoznaczne, o ile w Base występuje raz |
| 3. SKU z wartości grupy + wymiar (wys./szer. z grupy ↔ wymiar z nazwy Base) | **686** jednoznacznych, **1 049** niejednoznacznych (2+ produkty Base o tym samym SKU i wymiarze) | niejednoznaczne do raportu, nie do pliku |
| Bez pary | ok. 8 300 towarów IdoSell | w Base brak produktu z takim SKU+wymiarem lub towar nie ma SKU w grupie (701) |

Razem realnie **ok. 19 900 powiązań** z ~29 tys. towarów IdoSell. Pozostałe ~79 tys. produktów Base nie ma odpowiednika w sklepie (to oczekiwane: sklep ma mniej towarów niż Base).

Lista 50 od klienta: 12 trafia metodą 1, kilka kolejnych metodą 2 (np. `002648`, `004017`, `S00001`, `LIONEL/RB0/002/050090/1`). Około 25 pozycji (`002076/FBL`, `MILAS0/POP`, `001321/000`, `P00051`…) **nie ma w IdoSell w ogóle** — nie da się ich powiązać, trzeba je najpierw dodać do sklepu.

## Dane wyjściowe
1. `powiazania_base_idosell_romanetka.csv` — format jak lista od klienta: `ID produktu BL;ID produktu IdoSell;ID wariantu;SKU;EAN` (`;`, bez nagłówka jak w liście klienta). `ID wariantu` puste (wszystkie towary mają rozmiar `uniw`; tak było też przy IVEMAX).
2. `powiazania_raport.csv` — każdy towar IdoSell i produkt Base z listy klienta: metoda, status (`powiązany` / `niejednoznaczny` / `brak w IdoSell` / `brak w Base`), kandydaci.
3. Błędne powiązania (208) — nadpisane w pliku 1, a te bez nowej pary wykazane w raporcie.

## Planowane zmiany
- Nowy skrypt `romanetka/powiaz_base_idosell.py` (Python 3, biblioteka standardowa, strumieniowo) + `run_powiaz_base.bat` do uruchomienia dwuklikiem. Wejście automatycznie z `źródło/`, wyjście do `romanetka/`.
- Kolejność metod: 1 → 2 (do pliku), 3 (tylko raport); produkt Base i towar IdoSell użyte raz nie biorą udziału w kolejnych metodach.
- Kontrola jakości w skrypcie: zgodność wymiaru z nazw dla każdej pary, podsumowanie liczbowe na konsoli.
- Bez API i bez zmian w Base/IdoSell — plik wczytuje użytkownik.

## Przyjęte założenia
- Separator wyjścia `;` (format importu Base i listy klienta), mimo domyślnego przecinka w moich CSV.
- Wymiar porównuję bez kolejności (`300x160` = `160x300`), bo Base i grupy IdoSell zapisują go różnie.
- SKU czyszczę z białych znaków (tabulatory na końcu w Base).
- Powiązanie także z towarami **ukrytymi** w IdoSell (widoczności nie zmieniam).
- Niejednoznaczne przypadki nie trafiają do pliku importu, tylko do raportu.

## Decyzje użytkownika (2026-10-27)
1. **208 błędnych powiązań — nadpisujemy** plikiem importu. Produkty BL, które mają błędne powiązanie i nie dostały nowej pary, trafiają do raportu ze statusem „błędne powiązanie – usunąć ręcznie” (import nie usunie powiązania bez nowej pary).
2. **Eksport cykliczny 158 jest wyłączony.**
3. **Raport CSV dla klienta** (przecinek, UTF-8 z BOM dla Excela): każdy towar IdoSell (powiązany / kandydat SKU+wymiar / bez pary), pozycje z listy klienta bez pary oraz produkty BL z błędnym powiązaniem. Niepowiązanych ~79 tys. produktów Base nie wypisuję wiersz po wierszu — tylko liczba w podsumowaniu.
4. **Tylko pewne pary:** metoda 1 (EAN) i 2 (pełne SKU). Metoda 3 (SKU z grupy + wymiar) trafia wyłącznie do raportu jako kandydaci do decyzji klienta.

Reguła „pewna para” doprecyzowana: klucz występuje dokładnie raz po obu stronach, a jeśli obie nazwy mają wymiar, to muszą mieć wspólny. Para z niezgodnym wymiarem idzie do raportu jako „do sprawdzenia”.

## Wynik (2026-10-27, `run_powiaz_base.bat`)
- `powiazania_base_idosell_romanetka.csv`: **19 179** powiązań (EAN 19 155, pełne SKU 24), bez duplikatów po żadnej stronie. Format `ID_BL;ID_IdoSell;;SKU;EAN`, bez nagłówka.
- Lista klienta: 19 z 50 powiązanych, 31 bez pewnej pary (w raporcie).
- Stare powiązania: nadpisane 4 z 208. **204 zostają błędne** (82 → 29228, 77 → 29229, 44 → 29230, 1 → 29129). To wymiary jednego modelu (np. „Zasłona Granat Srebro… sz 140x150, 180x150…”) podpięte pod jeden towar IdoSell, który ma tylko jeden wymiar. Import ich nie usunie — trzeba je odpiąć ręcznie w Base.
- Raport `powiazania_raport.csv`: powiązany 19 179, brak pary w Base 8 302, niejednoznaczny SKU+wymiar 1 049, kandydat SKU+wymiar 686, błędne powiązanie 204, lista klienta bez pary 31, do sprawdzenia 2 (ucięta nazwa „450x14” oraz batyst na metry, którego SKU ma 978 produktów w Base).

## Stan zadania (2026-10-27) — wstrzymane do decyzji klienta
**Zrobione:** plik powiązań (19 179) i raport dla klienta są gotowe w tym folderze. Nic nie zostało wczytane do Base ani zmienione w IdoSell. Eksport cykliczny 158 jest wyłączony (według użytkownika).

**Czekamy na klienta (na podstawie `powiazania_raport.csv`):**
1. Zgoda na wczytanie `powiazania_base_idosell_romanetka.csv` do Base (integracja „IdoS Romanetka”, ID 3026512).
2. Odpięcie w Base 204 błędnych powiązań (towary IdoSell 29228, 29229, 29230, 29129) — ręcznie, ewentualnie przez nas.
3. Kandydaci SKU+wymiar (686): czy je potwierdza (wtedy dołączyć do pliku jako druga partia).
4. Niejednoznaczne (1 049) i „do sprawdzenia” (2): rozstrzygnięcie ręczne lub uzupełnienie EAN w Base/IdoSell.
5. Produkty bez pary: 31 z listy klienta i 8 302 towary IdoSell — czy dodawać brakujące towary, czy zostawić.

**Po decyzji:** jeśli dane w Base lub IdoSell się zmienią, wgrać nowe eksporty do `źródło/` (skrypt bierze najnowsze pliki) i uruchomić `run_powiaz_base.bat`. Po imporcie sprawdzić w Base kilka par z listy klienta (np. LIONEL/RB0) i logi stanów (powinny pojawić się zmienione produkty).
