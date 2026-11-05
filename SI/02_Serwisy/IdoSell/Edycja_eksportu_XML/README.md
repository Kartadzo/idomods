# Edycja eksportu produktów IdoSell

Aplikacja graficzna do obróbki eksportów produktowych z panelu IdoSell. Wczytuje
plik **XML (IOF 3.0)** albo **CSV**, pozwala wybrać dane, nałożyć reguły
przetwarzania i zapisać wynik w jednej z trzech struktur.

Python 3.8+, **tylko biblioteka standardowa** - nic nie trzeba instalować.

## Uruchomienie

Dwuklik na `run.bat`, albo z konsoli:

```
python app.py
python app.py products_export.csv      # ścieżka to skrót, nie wymóg
```

## Jak się tego używa

### 1. Źródło

Wskaż plik. Typ rozpoznaje się po zawartości, nie po rozszerzeniu. Potem
**Skanuj** - to obowiązkowy krok, bo zestaw kolumn CSV zależy od sklepu i bez
skanu nie wiadomo, jakie są w tym pliku języki, sklepy i parametry.

Tu też wybierasz, czy jeden wiersz wyniku ma odpowiadać **produktowi**, czy
**rozmiarowi**, oraz który język i sklep brać, gdy dana występuje w kilku
wersjach.

Limit skanu (domyślnie 2000 produktów) przyspiesza pracę z dużym plikiem. Gdy
skan się na nim zatrzyma, aplikacja o tym mówi - lista parametrów i maksymalna
liczba zdjęć mogą być wtedy niepełne.

### 2. Pola

Po lewej pełne drzewo pól, po prawej kolumny wyniku. Podwójny klik po lewej
dodaje pole, po prawej zmienia nazwę docelową.

Pola, których nie ma w wybranym pliku, **nie znikają** - są wyszarzone
z adnotacją „tylko w XML" / „tylko w CSV". To celowe: masz widzieć pełen zakres
możliwości, a nie część wspólną obu formatów.

Zdjęć i parametrów **nie ma na liście pól** - mają własne sekcje pod spodem,
z pełną konfiguracją. Dublowanie ich na liście dawałoby drugi, uboższy sposób
na to samo.

Przełącznik **nazwy kolumn i elementów WIELKIMI LITERAMI** zmienia pisownię
wszystkich nagłówków naraz - również tych ze zdjęć, ikon i parametrów:
`cena_brutto` → `CENA_BRUTTO`. Reguły zapisane przed przełączeniem działają
dalej - kolumnę rozpoznają bez względu na wielkość liter.

Grupa **Opinie** to statystyki liczone przy odczycie: liczba opinii, liczba
potwierdzonych, średnia ocena, rozkład ocen (ile na 5, 4, 3, 2, 1) i data
ostatniej opinii. IOF nie ma gotowych agregatów - są pojedyncze opinie, więc
aplikacja liczy je sama. Eksport tabelaryczny CSV opinii nie zawiera, więc
te pola są dostępne wyłącznie przy źródle XML.

Grupa **Podmiot odpowiedzialny** ma komplet pól GPSR dla obu podmiotów -
producenta i osoby odpowiedzialnej w UE: identyfikator, kod, nazwa, e-mail,
telefon, strona, opis, kraj, miasto, kod pocztowy, ulica, numer domu i lokalu.

Kilka wartości bywa zapisanych inaczej w każdym z formatów - pole zna obie
postaci i bierze tę, która ma zawartość:

| Pole | CSV | XML |
|---|---|---|
| Ścieżka kategorii IdoSell | `/iai_category@path` | `/category_idosell@path`, a gdy pusta - `category_idosell_translation` |
| Cena przekreślona | `crossedout_retail_price` | `strikethrough_retail_price` |

Tylko XML ma: **kod CN/TARIC**, **promocję** (nazwa, ID, data startu, cena
sprzed promocji), **typ i okres gwarancji** oraz statystyki opinii. Tylko CSV
ma kod producenta na poziomie produktu - w XML jest on przy rozmiarze, więc
bierze go pole „Kod producenta rozmiaru”.

**Parametry** mają trzy tryby:

| Tryb | Wynik | Do czego |
|---|---|---|
| komórka oryginalna | jedna kolumna, wartości jak w źródle | dalsza obróbka gdzie indziej |
| kolumna na parametr | `Kolor \| Materiał \| Rozmiar` | arkusz, import |
| nazwa i wartość osobno | `parametr_1_nazwa \| parametr_1_wartosc \| …` | przeglądanie, gdy lista parametrów jest zmienna |

Tryb „kolumna na parametr" korzysta z listy wykrytej przy skanie - przycisk
**Wybierz parametry…** pozwala ją zawęzić i ustawić kolejność. Parametr, który
pojawi się poza listą, trafia do kolumny `parametry_pozostale` i do raportu.

**Zdjęcia**: wybierasz typ (duże, średnie, małe, oryginalne) i sposób rozbicia -
kolumna na zdjęcie, wszystko w jednej kolumnie, albo tylko pierwsze. Lista typów
jest zawsze pełna; te nieobecne w danym pliku są opisane. Ikon (aukcyjna, grupy,
miniatura karty) nie ma na liście - to nie są zdjęcia produktu.

Nazwy kolumn ze zdjęciami ustawiasz sam: osobno dla pierwszego zdjęcia i dla
kolejnych, gdzie **gwiazdka zastępuje numer**. `image_link` +
`additional_image_link_*` da nagłówki, których oczekuje Google Shopping;
`zdjecie` + `dodatkowe_zdjecie_*` - polskie nazwy do arkusza.

**Ikony** mają własną sekcję, bo to nie są zdjęcia produktu: ikona karty, ikona
aukcyjna i ikona grupy. Wybierasz rodzaj i nazwę kolumny. Opcja **użyj także
jako zdjęcia głównego** wstawia ikonę na pierwsze miejsce wśród zdjęć - zdjęcia
przesuwają się o jedno dalej, a ikona zostaje przy tym w swojej kolumnie.
Przydatne w sklepach, które trzymają zdjęcie katalogowe właśnie w ikonie.

### 3. Reguły

Reguła zmienia jedną kolumnę: `JEŻELI warunek TO akcja`. Warunek jest opcjonalny
i może badać **inną** kolumnę niż ta, którą reguła zmienia.

Akcje: ustaw stałą, mapuj wartości, szukaj i zamień (regex), przedrostek,
przyrostek, złóż z kilku kolumn (`{nazwa} - {kolor}`), pierwsza niepusta,
przytnij do N znaków, usuń HTML, scal białe znaki, wielkość liter, przelicz
liczbę, sformatuj datę, weź n-tą wartość, połącz, wyczyść.

Okno reguły tłumaczy każdy wybór: nad ustawieniami jest zdanie o tym, co robi
akcja, a pod każdym polem - podpowiedź z przykładem. Nie trzeba znać wyrażeń
regularnych ani formatów daty, żeby ułożyć regułę.

Reguły wykonują się po kolei - kolejność ma znaczenie, zmienia się ją strzałkami.

**Filtry rekordów** to ten sam mechanizm warunków, tylko odrzucają cały wiersz:
„pomiń gdy" albo „zostaw tylko gdy".

### 4. Wyjście

Trzy struktury:

- **Płaski CSV** - tabela o stałym zestawie kolumn. Separator, kodowanie,
  cudzysłowy, nagłówek do ustawienia.
- **Prosty XML (arkusze)** - płaskie drzewo bez atrybutów i przestrzeni nazw,
  które Excel i Arkusze Google wczytują bez konfiguracji. Puste elementy zostają,
  żeby kolumny się nie rozjechały.
- **Przycięty IOF** - ten sam dokument IOF z wyciętymi gałęziami. **Tylko dla
  źródła XML**; przy CSV pozycja jest wyszarzona, bo z tabeli byłaby to budowa
  nowego drzewa, a nie przycięcie istniejącego.

Eksport idzie w tle - okno nie zamarza, postęp widać na bieżąco, można przerwać.
Po zakończeniu dostajesz raport: ile zapisano, ile pominęły filtry, czy coś
wymagało uwagi.

### Podgląd

Dolny panel pokazuje pierwsze kilkanaście wierszy wyniku i odświeża się po każdej
zmianie. Czyta tylko tyle, ile trzeba na próbkę, więc jest równie szybki przy
pliku z czterema produktami, co przy pliku z setką tysięcy.

### Poprzednia sesja

Przy zamknięciu aplikacja zapisuje komplet ustawień do `last_session.json`,
a przy następnym uruchomieniu **pyta, czy je wczytać** - z datą zapisu, nazwą
pliku źródłowego i liczbą kolumn, żeby było wiadomo, na co się zgadzasz.
Odmowa niczego nie kasuje: sesję można wczytać później przez
**Plik → Wczytaj ustawienia z poprzedniej sesji**. Gdy plik źródłowy zniknął
z dysku, ustawienia i tak wracają - trzeba tylko wskazać źródło na nowo.

### Profile

Sesja jest jedna i pisze się sama; profil jest nazwany i zapisujesz go świadomie.
**Plik → Zapisz profil** utrwala komplet ustawień: źródło, granularność, język,
sklep, kolumny, tryby parametrów i zdjęć, reguły, filtry, strukturę i opcje
zapisu. Powtarzalny eksport dla klienta to potem jedno wczytanie profilu.

Własny układ kolumn można też zapisać jako nową strukturę
(**Narzędzia → Zapisz obecny układ jako strukturę…**) - trafia do `structures/`
jako plik JSON i pojawia się na liście po restarcie.

## Na co uważać przy CSV

Eksport tabelaryczny z panelu ma dwie właściwości, które łatwo przeoczyć.
Aplikacja radzi sobie z obiema, ale warto o nich wiedzieć.

**Listy w komórkach nie są równoległe.** Wielokrotności są sklejone znakiem
nowej linii, ale parametr bez wartości nie zostawia pustego miejsca w liście
wartości - naiwne parowanie po pozycji daje ciche przekłamanie. Aplikacja paruje
po kolumnie `id` wszędzie, gdzie taka istnieje.

**Panel zwija identyczne bloki.** Gdy wszystkie rozmiary mają ten sam komplet
cen, cały blok cenowy schodzi do jednej wartości; gdy choć jedna cena się różni,
blok jest rozwinięty na każdy rozmiar. Aplikacja rozpoznaje oba przypadki, a to,
czego nie da się jednoznacznie sparować, trafia do raportu, zamiast być
zgadywane.

**Zestaw kolumn zależy od sklepu.** Dwa eksporty z tego samego panelu miały 298
i 334 kolumny z zupełnie innym kompletem języków. Dlatego skan jest obowiązkowy,
a kolumny mapują się po nazwie nagłówka, nie po pozycji.

## Wersja bez Pythona (.exe)

Na urządzenie bez Pythona idzie katalog **`dystrybucja/`**: plik
`Edycja eksportu IdoSell.exe`, katalog `structures/` i instrukcja. Nic więcej
nie trzeba instalować.

Paczkę buduje się na komputerze z Pythonem - dwuklik w **`build_exe.bat`**
(albo `python build_exe.py`). Wymaga PyInstallera: `pip install pyinstaller`.
Budowa trwa kilkadziesiąt sekund, wynik ma około 11 MB.

Trzy rzeczy warto wiedzieć:

- **Plik `.exe` musi leżeć tam, gdzie masz prawo zapisu** - obok niego powstają
  `settings.json`, `last_session.json` i katalog `profiles/`. „Program Files”
  odpada.
- **Katalog `structures/` obok `.exe` jest edytowalny** - dorzucony tam plik JSON
  pojawi się na liście struktur po restarcie. Gdy katalog zniknie, program użyje
  kompletu wbudowanego w `.exe`.
- **Zmiana mapowania pól wymaga przebudowy** - `core/schema.py` jest w środku
  paczki. Po edycji uruchom `build_exe.bat` jeszcze raz.

## Mapowanie pól - gdzie je zmieniać

Wszystkie pola opisuje jedna lista: **`CORE_FIELDS` w `core/schema.py`**. Jeden
wpis to jedno pole widoczne na liście „Dostępne pola”:

```python
_f("promotion_name", u"Nazwa promocji", G_PRICE, KIND_BLOCK,
   element=u"/promotion", attr=u"@name", sources=XML_ONLY),
```

| Człon | Znaczenie |
|---|---|
| `"promotion_name"` | identyfikator - używany w strukturach i profilach, nie zmieniaj po fakcie |
| `u"Nazwa promocji"` | etykieta w interfejsie |
| `G_PRICE` | grupa na liście pól (`G_BASIC`, `G_DESC`, `G_PRICE`, `G_SIZE`, `G_STOCK`, `G_DATE`, `G_OPINION`, `G_ENTITY`) |
| `KIND_BLOCK` | skąd brać wartość: `KIND_VALUE` (ścieżka), `KIND_LANG` (ścieżka zależna od języka), `KIND_BLOCK` (element powtarzalny, wybór po sklepie i rozmiarze), `KIND_SIZE` (klucz rozmiaru) |
| `path=` / `element=` + `attr=` | ścieżka w konwencji nagłówka CSV; `KIND_BLOCK` rozbija ją na element i atrybut |
| `alt_path=` / `alt_element=` | druga postać tej samej wartości, gdy formaty się różnią; może być listą |
| `sources=` | `BOTH` (domyślnie), `XML_ONLY`, `CSV_ONLY` - decyduje o wyszarzeniu pola |
| `type=` | `"text"`, `"number"`, `"date"` |
| `note=` | dopisek w kolumnie „Uwaga” |

Ścieżkę nowego pola najprościej podejrzeć tak: nagłówek w CSV to gotowa ścieżka,
a dla XML atrybut `iaiext:cntaric` na produkcie zapisuje się jako `@cntaric`,
element `<iaiext:taxcode>` jako `/taxcode`, a `<promotion id="34">` jako
`element=u"/promotion", attr=u"@id"`.

Ikony i zdjęcia mają osobną drogę - typ obrazka dokłada się w `IMAGE_BRANCHES`
albo `ICON_KINDS` w `core/readers/xml_reader.py` i w `IMAGE_SOURCES` w
`core/readers/csv_reader.py`. Statystyki opinii liczy `_build_opinions` w tym
pierwszym pliku.

## Układ katalogów

```
app.py              uruchomienie
run.bat             dwuklik
build_exe.py        budowa wersji .exe
build_exe.bat       dwuklik - to samo
app.ico             ikona aplikacji
dystrybucja/        gotowa paczka na inne urządzenie (po budowie)
core/               logika: czytniki, rejestr pól, reguły, writery, potok
structures/         definicje struktur wyjściowych (.json)
profiles/           zapisane profile użytkownika (.json)
gui/                interfejs
settings.json       ostatni katalog i profil
last_session.json   ustawienia z ostatniego zamknięcia (pytanie przy starcie)
```

Nową strukturę dodaje się plikiem JSON w `structures/` - aplikacja czyta katalog
przy starcie, kod nie wymaga zmian. Szczegóły projektowe: `DESIGN.md`.
