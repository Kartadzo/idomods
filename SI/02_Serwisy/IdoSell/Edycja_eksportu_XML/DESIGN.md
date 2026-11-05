# Apka Edycji Eksportu XML IdoSell — projekt

Aplikacja graficzna (tkinter, tylko biblioteka standardowa): wczytuje eksport z
panelu IdoSell — **XML (IOF 3.0)** albo **CSV** — pozwala wybrać eksportowane
dane, nałożyć reguły przetwarzania i zapisać wynik w jednej z trzech struktur.

Decyzje przyjęte na starcie:

- źródła: `products_export.xml` (IOF 3.0) i `products_export.csv` (eksport tabelaryczny);
- struktury wyjściowe: **płaski CSV**, **prosty XML dla arkuszy**, **przycięty IOF**;
- **bez generowania XSLT** — aplikacja transformuje w Pythonie i zapisuje gotowy plik;
- GUI: **tkinter**, zero zależności, `run.bat` działa po dwukliku;
- skala: **od kilku do setek tysięcy produktów** → streaming od pierwszej linijki kodu.

## 1. Dwa typy źródła

Oba pochodzą z tego samego panelu i opisują ten sam model, ale zapisują go
inaczej. To dobra wiadomość dla architektury: **nagłówki CSV to ścieżki IOF**.

```
CSV:  /description/name[pol]   /sizes/size@code   /price_retail/site@gross
XML:  description/name@xml:lang="pol"   sizes/size/@code   iaiext:price_retail/iaiext:site/@gross
```

Dzięki temu jeden rejestr pól obsługuje oba źródła — pole ma po prostu dwa
adresy, `xml_path` i `csv_header`.

### Różnice, które musi znać UI

| | XML (IOF 3.0) | CSV |
|---|---|---|
| Wiersz | drzewo `product` z zagnieżdżeniami | 1 wiersz = 1 produkt, kilkaset kolumn |
| Wielokrotności | powtórzone elementy | wartości sklejone `\n` **w jednej komórce** |
| Kodowanie | UTF-8, deklaracja w pliku | UTF-8 bez BOM, separator `,` |
| Zestaw kolumn | stały | **zmienny — zależy od sklepu** |
| Zdjęcia | icons, small, medium, large, originals | **tylko large i icons** (+ auction_icon, group_icon) |
| Tylko tutaj | `iaiext:` — omnibus, zdjęcia medium/small/originals, `node_path_translation`, pytania, subskrypcje, daty utworzenia i modyfikacji, ceny zakupu, `common_group_settings` | `@code_producer`, `iai_category`, `series`, `taxcode`, `note`, `warranty`, `attachments/*`, `associated_products`, `auction_*`, `crossedout_*_price`, `@country_of_origin`, `responsible_entity` rozbite na pola |

**Zestaw kolumn CSV jest zmienny** — dowód z dwóch przykładowych plików tego
samego panelu: jeden ma 298 kolumn z językami pol/bul/eng/hun/rum/slv, drugi
334 kolumny z pol/cze/eng/est/fin/lav/lit/rum/rus/ukr. Wniosek dla kodu:
języki, sklepy i parametry **zawsze wykrywane ze skanu**, nigdy zaszyte na
sztywno; czytnik mapuje po nazwie nagłówka, nie po pozycji.

Pola nieobecne w wybranym źródle są w drzewie **wyszarzone z adnotacją**
„niedostępne w CSV" / „niedostępne w XML" — nie znikają, bo użytkownik musi
widzieć pełen zakres możliwości i wiedzieć, czego nie dostanie z tego pliku.
Lista pól to zawsze suma obu źródeł, nie ich część wspólna. Przy przełączeniu
źródła profil zostaje, a aplikacja raportuje: „3 wybrane pola nie istnieją w tym
źródle".

### Pułapka nowej linii — listę sklejają tylko elementy powtarzalne

Znak nowej linii w komórce **nie zawsze** oznacza listę. Sklejone są nim tylko
kolumny elementów, które w obrębie produktu potrafią się powtórzyć (`size`,
`parameter`, `site`, `image`, `stock`, …). W kolumnie skalarnej — `long_desc`,
`short_desc`, `note`, `responsible_entity/producer/*` — nowa linia to **treść**:
opis produktu z panelu to HTML łamany na akapity.

Dzielenie po `\n` bez tego rozróżnienia zostawiało z opisu pierwszą linijkę,
czyli zwykle sam otwierający `<div>`, a resztę gubiło po cichu (potwierdzone na
eksporcie pyrawinyl: 3350 z 3353 produktów miało `\n` w `long_desc`).

Rozstrzyga `is_repeatable()` w `csv_reader.py` — po segmentach ścieżki, nie po
nazwie kolumny, więc `/size_chart@name` zostaje skalarem, a `/sizes/size@name`
nie. Kolumna nieznana traktowana jest jak skalarna: sklejona wartość jest
widoczna, ucięta treść nie.

To samo rozróżnienie po stronie zapisu: writer ma osobno `list_separator`
(sklejanie wielu wartości kolumny) i `newline_replacement` (nowa linia wewnątrz
jednej wartości). Wcześniej był to jeden parametr i opis HTML dostawał ` | `
pomiędzy akapitami.

### Pułapka list w CSV — parowanie po `id`, nigdy po indeksie

Sprawdzone na obu plikach. Listy w komórkach **nie są równoległe**:

```
/parameters/parameter@name[pol]        -> 7 wartości
/parameters/parameter/value@name[pol]  -> 6 wartości   (parametr bez wartości nie zostawia pustego miejsca)

po indeksie (ŹLE):        Dostępność = 4109      GroupID = (brak)
po parameter_id (DOBRZE): Dostępność = Jest      GroupID = 4109
                          Ponownie dostępny od = (brak)   <- faktycznie pusty
```

To samo przy rozmiarach, tylko z drugiej strony — **CSV zwija identyczne
wartości**:

```
/sizes/size@id             -> 4  ['C','D','E','F']
/sizes/size@name           -> 4  ['46','48','50','52']
/sizes/size/stock@quantity -> 4  ['200','200','200','200']
/sizes/size/price@gross    -> 1  ['129.90']          <- w XML stoi przy każdym z 4 rozmiarów
/sizes/size/srp@gross      -> 1  ['0.00']
```

Zwijanie zachodzi **na poziomie bloku, nie pojedynczej kolumny**. Potwierdzone
przez zestawienie dwóch plików: gdy wszystkie rozmiary mają identyczny komplet
cen, cały blok `size/price` + `size/srp` + `size/crossedout_*` schodzi do jednej
wartości (łącznie z `vat`); gdy choć jedna cena się różni, cały blok jest
rozwinięty na każdy rozmiar — także kolumny, które mają wszędzie tę samą wartość:

```
identyczne ceny (25357, 4 rozmiary)     różne ceny (200697, 2 rozmiary)
  price@gross  n=1 ['129.90']             price@gross  n=2 ['12.00','18.00']
  price@vat    n=1 ['23.0']               price@vat    n=2 ['23.0','23.0']
  srp@gross    n=1 ['0.00']               srp@gross    n=2 ['0.00','0.00']
```

Reguły parowania w `csv_reader.py`:

1. **Jest kolumna z kluczem** (`value@parameter_id`, `stock@size_id`, `site@id`,
   `site@service_id`) — parujemy po niej. Zawsze, gdy tylko istnieje.
2. **Klucz `size_id` z wpisem `0`** — wpis o `size_id=0` jest **wartością bazową**
   dla wszystkich rozmiarów bez własnego wpisu. Produkt 200697:
   `price_retail/site@size_id = ['0','1076']`, `@gross = ['12.00','18.00']` —
   rozmiar 1076 dostaje 18.00, rozmiar 1075 dziedziczy 12.00 z wpisu zerowego.
3. **Brak klucza, `n == liczba elementów nadrzędnych`** — parujemy po pozycji.
   Dotyczy kolumn z tego samego elementu (`size@id` + `size@name` + `size@code`,
   `image@url` + `image@hash`).
4. **Brak klucza, `n == 1`** — jedna wartość rozdzielana na wszystkie (zwinięty
   blok cenowy).
5. **Kolumna pusta** — `''` oznacza brak wartości dla wszystkich, nie listę
   jednoelementową. Puste kolumny mają `n=1` niezależnie od reszty bloku.
6. **Każdy inny przypadek** — rekord trafia do raportu błędów, nie do wyniku.

Kolejność list w CSV jest wewnętrznie spójna (`id`, `name`, `code` zgadzają się),
ale **nie jest ta sama co w XML** — dla produktu 25360 CSV daje Q,P a XML P,Q.
Dlatego nigdy nie porównujemy pozycji między źródłami.

To ta sama pułapka, która wcześniej wyszła przy mapowaniu na Ceneo.

## 2. Parametry — trzy tryby wyjścia

Wybór w zakładce Pola, przy grupie „Parametry". Dotyczy obu źródeł.

### `raw` — komórka oryginalna

Jedna kolumna, wartości sklejone tak jak w źródle. Najszybszy, do dalszej
obróbki gdzie indziej.

```
parametry
Kolor fotela: czarny⏎Typ podstawy: nogi⏎Materiał fotela: ekoskóra
```

### `column_per_param` — kolumna na parametr

Jedna kolumna per parametr, nagłówek = nazwa parametru z panelu, komórka =
wartość. Zasada „jeden parametr, jedna kolumna" trzymana także wtedy, gdy
parametr ma kilka wartości — wtedy wartości sklejone separatorem (do ustawienia,
domyślnie `, `).

```
Kolor fotela | Typ podstawy | Materiał fotela | Dostępność | GroupID
czarny       | nogi         | ekoskóra        | Jest       | 4109
```

Wymaga znajomości **pełnej listy parametrów w całym pliku** — bierze się ze
skanu z zakładki Źródło. Użytkownik widzi wykrytą listę i może z niej wybrać,
które parametry mają dostać kolumnę oraz w jakiej kolejności. Parametr, który
pojawi się w eksporcie mimo nieobecności na liście (skan z limitem), trafia do
raportu, a jego wartość — opcjonalnie — do kolumny zbiorczej `parametry_pozostale`.

### `name_value_pairs` — nazwa i wartość w osobnych kolumnach

Dwie kolumny na pozycję, numerowane po kolei:

```
parametr_1_nazwa | parametr_1_wartosc | parametr_2_nazwa | parametr_2_wartosc | ...
Kolor fotela     | czarny             | Typ podstawy     | nogi               | ...
```

Liczba par = maksimum ze skanu, z możliwością ręcznego limitu (np. „tylko 10
pierwszych"). Kolejność parametrów: ze źródła albo wg `priority`, do wyboru.

Uwaga o zamienności: `column_per_param` daje ten sam nagłówek dla tego samego
parametru w każdym wierszu — to format do arkusza i do importu. `name_value_pairs`
znosi zależność od listy parametrów, ale kolumna nie ma stałego znaczenia — to
format do przeglądania, nie do importu.

## 3. Zdjęcia — wybór typu i sposobu rozbicia

Użytkownik wybiera **typ zdjęć** niezależnie od źródła; lista jest zawsze pełna,
a pozycje niedostępne w danym pliku są wyszarzone z adnotacją:

| Typ | XML | CSV |
|---|---|---|
| `large` | tak | tak |
| `icons` | tak | tak |
| `medium` | tak | niedostępne |
| `small` | tak | niedostępne |
| `originals` | tak | niedostępne |
| `auction_icon`, `group_icon` | — | tak |

Sposób rozbicia:

- **jedna kolumna** — wszystkie adresy sklejone separatorem;
- **kolumna na zdjęcie** — `image`, `image_extra_1`, `image_extra_2`, … z limitem
  liczby (domyślnie ze skanu: największa liczba zdjęć w pliku);
- **tylko pierwsze** — jeden adres.

Kolejność: ze źródła (CSV zachowuje kolejność z panelu, która **nie** wynika
z nazwy pliku — pierwszym zdjęciem produktu 25357 jest `…_2.jpg`) albo wg
`@priority`, gdy źródłem jest XML.

## 4. Trzy struktury wyjściowe

Definicje to pliki `structures/*.json` — dodanie nowej nie wymaga zmian w kodzie.
Własną konfigurację można zapisać jako nową strukturę.

### `flat_csv` — płaski CSV

Lista rekordów o stałym zestawie kolumn. Użytkownik buduje kolumny: wybiera pole
z rejestru, nadaje nazwę docelową, ustala kolejność. Opcje zapisu: separator,
cudzysłowy, kodowanie, BOM, nagłówek. Dostępny dla obu źródeł.

### `simple_xml` — prosty XML dla arkuszy

Płaskie drzewo bez atrybutów i przestrzeni nazw, jeden element na wartość —
format, który Excel i Arkusze Google wczytują bez konfiguracji. Puste elementy
zachowane, żeby kolumny się nie rozjechały.

```xml
<?xml version="1.0" encoding="utf-8"?>
<products>
  <product>
    <product_id>113179049</product_id>
    <name>Legginsy Damskie Sugar Skull Burpee Lolli</name>
    <quantity>0</quantity>
    <ean></ean>
    <image>https://unbrokenstore.com/hpeciai/bd0e…_1.jpg</image>
    <image_extra_1>https://unbrokenstore.com/hpeciai/7ba5…_2.jpg</image_extra_1>
    <image_extra_2>https://unbrokenstore.com/hpeciai/ac03…_3.jpg</image_extra_2>
  </product>
</products>
```

Ta sama lista kolumn co `flat_csv` — różni się tylko zapisem. Nazwy elementów
sanityzowane do poprawnych nazw XML (bez spacji i znaków specjalnych, nie
zaczynają się od cyfry); mapowanie „nazwa docelowa → nazwa elementu" widoczne
w zakładce Pola. Dostępny dla obu źródeł.

### `iof_subset` — przycięty IOF

Ten **sam** dokument IOF, tylko z wyciętymi gałęziami. Użytkownik zaznacza
w drzewie, co zostaje; niezaznaczone znika. Zachowane: przestrzenie nazw,
atrybuty, zagnieżdżenia, deklaracja XML. Zastosowanie: odchudzenie eksportu
z 200 ścieżek do 20, zanim trafi do klienta albo do innego narzędzia.

**Tylko dla źródła XML** — przy CSV pozycja jest wyszarzona z wyjaśnieniem.
Z CSV dałoby się IOF zrekonstruować, ale byłaby to budowa nowego drzewa, nie
przycięcie istniejącego: z utratą wszystkiego, czego CSV nie zawiera, i ze
zgadywaniem zagnieżdżeń list. To osobny temat na v2.

```json
{
  "id": "simple_xml",
  "label": "Prosty XML (arkusze)",
  "mode": "flat",
  "sources": ["xml", "csv"],
  "format": "xml",
  "xml": {"root": "products", "item": "product", "keep_empty": true},
  "row_context": "product",
  "columns": [
    {"out": "product_id", "field": "product_id"},
    {"out": "name",       "field": "name"},
    {"out": "quantity",   "field": "stock_quantity"},
    {"out": "ean",        "field": "code_on_card"},
    {"out": "image",      "field": "images_large", "split": "image_extra_{n}"}
  ]
}
```

## 5. Architektura

```
app.py                  uruchomienie GUI
run.bat                 dwuklik
settings.json           ostatnio używany profil, ostatni katalog
core/
  schema.py             rejestr pól: id, etykieta PL, kontekst, xml_path, csv_header, typ, multi
  scanner.py            jeden przelot: języki, sklepy, parametry, maks. liczba zdjęć, liczniki
  readers/
    base.py             wspólny interfejs: iter_records() -> dict pól
    xml_reader.py       iterparse -> strumień rekordów (product / size)
    csv_reader.py       reader + rozbicie list po \n + parowanie wg reguł z sekcji 1
  expanders.py          parametry (3 tryby) i zdjęcia (3 tryby) -> kolumny
  rules.py              silnik reguł: warunki + akcje
  pipeline.py           read -> filtr rekordów -> ekstrakcja -> expandery -> reguły -> zapis
  profile.py            zapis i odczyt profilu JSON
  writers/
    csv_writer.py       flat_csv
    simple_xml_writer.py  simple_xml
    iof_tree_writer.py    iof_subset (tylko źródło XML)
structures/
  flat_csv.json
  simple_xml.json
  iof_subset.json
profiles/               zapisane konfiguracje użytkownika (.json)
gui/
  main_window.py        okno, zakładki, pasek statusu, pasek postępu
  tab_source.py         plik, wykryty typ, skan, granularność, język, sklep
  tab_fields.py         drzewo pól, tryby parametrów i zdjęć, nazwy docelowe
  tab_rules.py          lista reguł, edytor warunek/akcja, filtry rekordów
  tab_output.py         struktura, opcje pliku, ścieżka, eksport
  preview.py            tabela podglądu N pierwszych rekordów
```

Typ źródła wykrywany po zawartości, nie po rozszerzeniu: pierwszy niepusty znak
`<` → XML, w przeciwnym razie CSV (plus sprawdzenie, czy nagłówek wygląda jak
ścieżki IOF). Reszta aplikacji nie wie, skąd przyszedł rekord — czytniki dają
ten sam kształt danych.

### Rejestr pól (`schema.py`)

```python
Field(
  id="name",
  label="Nazwa produktu",
  group="Opis",
  context="product",              # product | size
  xml_path="description/name",    # None -> brak w źródle XML
  csv_header="/description/name", # None -> brak w źródle CSV
  select="text",                  # text | attr:<nazwa> | count
  lang_scoped=True,               # XML: filtr xml:lang; CSV: sufiks [pol]
  site_scoped=False,
  multi=False,                    # True -> kolekcja (zdjęcia, kategorie)
  pair_by="parameter_id",         # klucz parowania list w CSV
  type="text",                    # text | number | bool | url | date
)
```

Rdzeń rejestru pisany ręcznie (etykiety po polsku, grupy, typy). Pola dynamiczne
— parametry z panelu i nietypowe kolumny — dokładane po skanie: z XML po
`parameter/@name`, z CSV wprost z nagłówka, bo to już ścieżka IOF. Nieznana
kolumna CSV nigdy nie jest pomijana po cichu — trafia do grupy „Nierozpoznane"
z surową nazwą.

### Silnik reguł (`rules.py`)

Reguła działa na jednym polu, po ekstrakcji i rozbiciu, a przed zapisem:

```
JEŻELI <warunek>  TO  <akcja>
```

**Warunki** (opcjonalne, brak = zawsze): równa się / różne / zawiera / zaczyna się /
regex / puste / niepuste / większe / mniejsze / w liście. Łączenie AND i OR.
Warunek może badać **inne** pole niż to, które modyfikuje.

**Akcje**: `set`, `map` (słownik wartości), `regex_replace`, `prefix` / `suffix` /
`template` (`{name} - {color}`), `fallback` (pierwsza niepusta z listy pól),
`truncate` (opcja: na granicy słowa), `strip_html` / `strip_cdata` / `collapse_ws`,
`case`, `number` (mnożenie, dodawanie, zaokrąglenie, separator dziesiętny),
`date_format`, `pick` (n-ty element kolekcji albo `join`), `blank`.

**Filtry rekordów** (osobna lista): pomiń rekord gdy warunek spełniony — brak
stanu, cena 0, kategoria z czarnej listy, `available != yes`.

### Profil (`profiles/*.json`)

Cały stan: typ i ścieżka źródła, granularność, język, sklep, wybrane pola
z nazwami docelowymi, tryb parametrów, tryb i typ zdjęć, reguły, filtry,
struktura, opcje zapisu. Zapis, wczytanie, duplikacja — powtarzalny eksport dla
klienta jednym kliknięciem.

## 6. Przepływ w GUI

```
[1 Źródło]  plik -> wykryty typ: XML (IOF 3.0) / CSV
            [Skanuj] -> "2 produkty, 6 rozmiarów, 10 języków, 4 sklepy,
                         19 parametrów, maks. 6 zdjęć"
            granularność: (o) produkt  ( ) rozmiar
            język: pol      sklep: 1

[2 Pola]    drzewo z checkboxami        | nazwa docelowa | podgląd wartości
            + Podstawowe / Opis / Ceny / Zdjęcia / Parametry / Nierozpoznane
            (pola spoza źródła wyszarzone z adnotacją)

            Parametry:  (o) komórka oryginalna
                        ( ) kolumna na parametr    [wybierz parametry…]
                        ( ) nazwa i wartość osobno [maks. par: 10]

            Zdjęcia:    typ: [large v]  (medium/small/originals — tylko XML)
                        (o) kolumna na zdjęcie [maks. 6]
                        ( ) jedna kolumna, separator [, ]
                        ( ) tylko pierwsze

[3 Reguły]  lista reguł + [Dodaj] [Edytuj] [Usuń] [Góra] [Dół]
            filtry rekordów jako osobna sekcja

[4 Wyjście] struktura: (o) Płaski CSV
                       ( ) Prosty XML (arkusze)
                       ( ) Przycięty IOF        [wyszarzone przy źródle CSV]
            opcje zapisu zależne od struktury
            ścieżka pliku + [Eksportuj]

[Podgląd]   dolny panel, tabela 20 pierwszych rekordów, odświeżana na żywo
```

## 7. Wydajność (setki tysięcy produktów)

- XML: `iterparse` + `elem.clear()` po każdym `<product>`, plus usuwanie
  rodzeństwa spod roota — bez tego drzewo i tak urośnie do rozmiaru pliku;
- CSV: `csv.reader` wiersz po wierszu, `csv.field_size_limit` podniesiony —
  komórka ze sklejonymi opisami w 10 językach potrafi mieć kilkadziesiąt kB;
- zapis strumieniowy, bez budowania wyniku w pamięci (dotyczy też `iof_subset`);
- skan: jeden przelot z limitem (domyślnie 2000 produktów, do zmiany w UI) —
  wystarczy do wykrycia parametrów, języków, sklepów i maksimum zdjęć. Tryby
  `column_per_param` i `name_value_pairs` zależą od skanu, więc przy limicie
  niższym niż plik aplikacja ostrzega, że lista kolumn może być niepełna;
- podgląd: pierwsze 20 rekordów, czytanie przerywane po ich zebraniu;
- eksport w wątku roboczym: pasek postępu, przycisk Anuluj, GUI nie zamarza;
- podsumowanie po eksporcie: rekordy zapisane, pominięte przez filtry,
  rozjechane listy, parametry spoza listy kolumn, błędy.

## 8. Zakres wersji

**v1**: wczytanie XML i CSV z wykryciem typu, skan, wybór pól, trzy tryby
parametrów, wybór i rozbicie zdjęć, reguły, filtry, trzy struktury wyjściowe,
profile, podgląd, pasek postępu.

**Później**: rekonstrukcja IOF z CSV, import wielu plików naraz, porównanie
dwóch eksportów (diff), walidacja wyniku wg wymagań sklepu docelowego.

## 9. Rekord pośredni

Czytniki nie zwracają swoich natywnych kształtów — oba produkują **ten sam
rekord pośredni**, kluczowany ścieżką w konwencji nagłówka CSV. CSV jest tu
formatem natywnym, XML się do niego mapuje, a pola obecne tylko w XML dostają
ścieżki w tej samej konwencji (`/omnibus_price_retail/site@gross`).

```python
Record(
  values = {"/description/name[pol]": "Nazwa", "@id": "200697", ...},
  sizes  = [{"@id": "1075", "@name": "180ml", "/price@gross": "12.00", ...}, ...],
  params = [{"id": "24", "name": "Materiał", "value": "welur", ...}, ...],
  images = {"large": [url, url, ...], "icons": [...], ...},
  issues = [...],   # rozjechane listy, nieznane kolumny
)
```

Dzięki temu `expanders`, `rules`, `pipeline` i writery są całkowicie niezależne
od źródła, a różnica XML/CSV kończy się na warstwie czytnika.

## 10. Stan implementacji

Zbudowane i sprawdzone na czterech plikach przykładowych:

| Element | Stan |
|---|---|
| `core/readers/` — XML i CSV do wspólnego rekordu | gotowe |
| `core/scanner.py` — języki, sklepy, parametry, maksimum zdjęć | gotowe |
| `core/schema.py` — rejestr ~90 pól plus dynamiczne | gotowe |
| `core/expanders.py` — 3 tryby parametrów, 3 tryby zdjęć | gotowe |
| `core/rules.py` — 16 akcji, 12 operatorów, filtry rekordów | gotowe |
| `core/writers/` — CSV, prosty XML, przycięty IOF | gotowe |
| `core/pipeline.py`, `core/profile.py`, `core/structures.py` | gotowe |
| `gui/` — 4 zakładki, podgląd, praca w tle | gotowe |

Weryfikacja:

- **parowanie list** — `Dostępność = Jest`, `GroupID = 4109`, parametr bez wartości
  pusty; zwinięty blok cenowy rozdzielony na 4 rozmiary; różne ceny sparowane
  po pozycji; `size_id=0` jako wartość bazowa;
- **reguły** — przycinanie z wielokropkiem, przelicznik ×1,1, warunkowy
  przedrostek tylko dla rozmiaru 46, filtr odrzucający rozmiary 50 i 52;
- **struktury** — wszystkie trzy dają poprawny plik; wynik XML przechodzi
  parsowanie, przycięty IOF zachowuje przestrzenie nazw i deklarację;
- **skala** — plik 510 MB / 15 000 produktów (45 000 wierszy wyniku): eksport
  **22 s**, czyli ok. 2000 wierszy na sekundę, przy szczycie pamięci Pythona
  **0,7 MB**. Streaming działa tak, jak miał: zużycie pamięci nie zależy od
  rozmiaru pliku.

Uwaga o trybie `tree`: przycinanie działa na całych gałęziach, więc zachowany
`description/name` zostawia wszystkie języki. Filtr językowy w przycinaniu to
kandydat na rozszerzenie.

## 11. Otwarte punkty

- **Pusty folder `addon/`** — nie wiem, co miało w nim być; na razie pomijam.

## Uzupełnienia po testach na eksportach z trzech sklepów

Trzy pliki z różnych wdrożeń (agrafka, topfit.sk, zooart6) wymusiły korekty,
których nie było widać na jednym przykładzie:

**Produkt zagnieżdżony to nie produkt.** `associated_products/product` ma tę samą
nazwę co towar najwyższego poziomu. Czytnik liczy teraz zagnieżdżenie i bierze
tylko poziom pierwszy - inaczej sklep z produktami powiązanymi dawał sześć
wierszy tam, gdzie ma jeden towar. Ta sama poprawka jest w przycinaniu IOF.

**Przestrzeń nazw bywa wszędzie.** W jednym eksporcie `images` jest zwykłym
elementem, w innym `iaiext:images`, a w trzecim cały `product` siedzi
w przestrzeni iaiext. Wyszukiwanie gałęzi idzie po nazwie lokalnej, nie po
dosłownym tagu.

**Ikony to trzy różne rzeczy.** CSV rozdziela `icon`, `auction_icon`
i `group_icon` na osobne kolumny, XML trzyma je w jednej gałęzi `icons`.
Czytnik XML rozdziela je tak samo jak CSV, a ikona dostała własną sekcję
w interfejsie - z opcją wystawienia jej jako zdjęcia głównego, bo część sklepów
trzyma tam zdjęcie katalogowe.

**Ta sama wartość, dwie ścieżki.** Kategoria IdoSell to `/iai_category` w CSV
i `/category_idosell` w XML; cena przekreślona to `crossedout_retail_price`
kontra `strikethrough_retail_price`. Pole ma więc drugą ścieżkę (`alt_path`,
`alt_element`) - pojedynczą albo listę - sprawdzaną, gdy pierwsza nic nie
zwróci. To tańsze niż przekazywanie typu źródła w dół i działa też, gdy sklep
wypełnił tylko jedną z nich. Na tej samej zasadzie ścieżka kategorii IdoSell
sięga po `category_idosell_translation`, gdy w języku sklepu jest pusta.

**Język przed ścieżką gołą.** Wartość szukana jest najpierw w wersji
`ścieżka[język]`, dopiero potem bez sufiksu. Odwrotna kolejność oddawała przy
listach tłumaczeń pierwszy język z dokumentu zamiast wybranego w interfejsie.

**Opinie liczone w locie.** IOF nie ma statystyk ocen, ma listę opinii. Czytnik
zlicza je przy przejściu i podaje gotowe wartości (`/opinions@count`,
`@average`, `@note_5`…), a same treści opinii odrzuca - przy setkach tysięcy
produktów trzymanie ich w rekordzie nie miałoby sensu.

**Wielkość liter w nagłówkach** to jeden przełącznik na całe wyjście. Reguły
dopasowują kolumnę bez względu na wielkość liter, więc przełącznik nigdy nie
unieważnia reguł ułożonych wcześniej.

**Sesja pyta, nie przywraca po cichu.** Wcześniej aplikacja sama wczytywała
ostatni profil przy starcie - użytkownik nie miał jak zacząć od czystego stanu
inaczej niż przez ręczne czyszczenie. Teraz zamknięcie zapisuje `last_session.json`
(ten sam format co profil, plus data), a start pokazuje pytanie z opisem tego, co
wróci: kiedy zapisane, jaki plik, ile kolumn i reguł. Odmowa nie kasuje zapisu -
sesja czeka w menu Plik. Profile zostają przy swojej roli: nazwane, świadomie
zapisywane układy dla konkretnego klienta.
