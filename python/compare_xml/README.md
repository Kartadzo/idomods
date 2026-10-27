# compare_xml — porównywarka dwóch plików XML

Porównuje dwa feedy produktowe XML i pokazuje, czym się różnią: których produktów brakuje
oraz które pola mają inne wartości.

## Uruchomienie

Dwuklik w `app.bat` (albo `python compare_xml.py`) **z poziomu tego folderu**.
Skrypt sam znajduje pliki `.xml` w bieżącym katalogu i zadaje kilka pytań — Enter
przyjmuje wartość domyślną.

Wymagania: Python 3.8+, wyłącznie biblioteka standardowa.

## Co obsługuje

Format rozpoznawany jest automatycznie na podstawie powtarzalnego elementu produktu:

| Format | Element rekordu | Identyfikator |
|---|---|---|
| IOF / IdoSell (także zapakowany w `<rss><channel>`) | `<product>` | `@id`, `@code_on_card`, `<code>` |
| Google Shopping RSS | `<item>` | `<g:id>`, `<id>` |
| Facebook / Atom | `<entry>` | `<g:id>`, `<id>` |
| Ceneo | `<o>` | `@id` |
| Heureka | `<SHOPITEM>` | `<ITEM_ID>` |
| dowolny inny | wykrywany automatycznie | `@id`, `<id>`, `@code`… |

Jeśli oba pliki mają różne formaty, skrypt ostrzega przed porównaniem.

## Jak porównuje

Każdy rekord jest spłaszczany do mapy **ścieżka → wartość**, więc porównywane są
wszystkie pola (także atrybuty), bez sztywnej listy. Przykładowe ścieżki:

```
@id                                   atrybut produktu
description/name                      tekst elementu
sizes/size/@available                 atrybut zagnieżdżonego elementu
sizes/size[uniw]/stock/@quantity      powtarzalny element kluczowany po @id
g:additional_image_link               lista wartości złączona separatorem " | "
```

Zasady:

- powtarzalne rodzeństwo z atrybutem `id`/`size_id`/`code`/`name` dostaje klucz w nawiasie
  (dzięki temu kolejność elementów w pliku nie generuje fałszywych różnic),
- powtarzalne rodzeństwo bez identyfikatora dostaje numer porządkowy,
- powtarzalne czyste wartości tekstowe (np. dodatkowe zdjęcia) trafiają do jednego pola,
- białe znaki są normalizowane (wielokrotne spacje i złamania wiersza nie są różnicą).

## Wielkie pliki

Pliki czytane są strumieniowo (`iterparse`), a porównanie idzie w trzech etapach:

1. przelot przez oba pliki → mapa `ID → skrót MD5` (mało pamięci),
2. dla samych produktów, które się różnią, szczegóły z pliku A lądują w tymczasowej bazie sqlite,
3. przelot przez plik B → porównanie pole po polu i zapis wyniku.

Dzięki temu feedy rzędu setek MB (kilkadziesiąt tysięcy produktów) przechodzą bez
ładowania całego drzewa do pamięci. Baza tymczasowa jest kasowana po zakończeniu.

Orientacyjny czas: dwa feedy IOF po ~570 MB (44 tys. produktów, ~140 pól na produkt)
porównują się w ok. 15–20 minut. Zawężenie zakresu pól nie przyspiesza samego czytania,
ale zmniejsza liczbę produktów kwalifikowanych do etapów 2–3 i rozmiar CSV.

## Pytania kreatora

1. **Które pliki porównać** — przy dokładnie dwóch plikach Enter zatwierdza, `z` zamienia A z B.
   Przy większej liczbie plików podaje się numery z listy.
2. **Zakres pól** — wszystkie (domyślnie), tylko wybrane, albo wszystkie oprócz wybranych.
   Pola wskazuje się numerem z listy **albo fragmentem nazwy** (np. `price` zaznaczy wszystkie
   ścieżki zawierające „price”). Wykluczanie przydaje się, gdy któreś pole zmienia się zawsze
   (np. znaczniki czasu) i zaśmieca raport.
3. **Limity raportu HTML** — ilu produktów z różnicami i ilu brakujących ID pokazać.
   Komplet zawsze trafia do CSV.

## Wyniki

### `differences.csv`

Separator `;`, kodowanie UTF-8 z BOM (otwiera się poprawnie w Excelu).

| Kolumna | Znaczenie |
|---|---|
| `ID` | identyfikator produktu |
| `Typ` | `tylko w A`, `tylko w B`, `różnica`, `pole tylko w A`, `pole tylko w B` |
| `Pole` | ścieżka pola |
| `Plik A` / `Plik B` | wartości |

`pole tylko w A` / `pole tylko w B` oznacza, że sam element lub atrybut istnieje wyłącznie
w jednym pliku (np. atrybut usunięty w nowej wersji feedu).

### `report.html`

- podsumowanie liczbowe (rekordy, unikalne ID, duplikaty, rekordy bez identyfikatora),
- **różnice wg pola** — ranking pól z liczbą produktów, w których dane pole się różni;
  to zwykle najszybsza droga do wskazania, co zepsuł lub naprawił nowy szablon XSLT,
- lista brakujących ID,
- szczegóły produktów z różnicami (kolory: czerwony — inna wartość, niebieski — pole tylko
  w A, zielony — pole tylko w B).

## Uwagi

- Oba pliki wynikowe są nadpisywane przy każdym uruchomieniu.
- Pliki feedów są w repozytorium ignorowane (`.gitignore`) — to robocze dane per maszyna.
