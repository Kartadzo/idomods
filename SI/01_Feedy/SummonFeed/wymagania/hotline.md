# Hotline.ua — wymagania feedu
- Źródła: https://hotline.ua/about/pricelists_specs/
- Data przeglądu: 2026-10-27
- Format: własny XML Hotline (zalecany), także YML (ograniczone warunki dostawy/sprzedaży), CSV/XLS, TXT; akceptuje format Google: nie (strona o nim nie wspomina)
- Szablon bazowy: `Ceneo.xml` — najbliższy logicznie (własny XML ofert, parametry jako `param name=`/`a name=`, ścieżka kategorii); wymaga jednak dodania słownika kategorii i nagłówka sklepu. Żaden szablon nie odpowiada 1:1.

## Struktura pliku
```xml
<?xml version="1.0" encoding="UTF-8"?>
<price>
  <date>2026-10-27 12:00</date>
  <firmName/> <firmId/> <rate/>
  <categories>
    <category><id/><parentId/><name/></category>
  </categories>
  <delivery/>      <!-- sposoby dostawy sklepu -->
  <store/>         <!-- punkty odbioru: id, name, address -->
  <items>
    <item>
      <id/> <categoryId/> <code/> <barcode/> <vendor/> <name/>
      <description/> <url/> <image/> <priceRUAH/> <priceRUSD/>
      <stock/> <shipping/> <guarantee type="manufacturer"/>
      <param name=""/> <condition/>
    </item>
  </items>
</price>
```

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| `price` (korzeń), `categories`, `items` | elementy obowiązkowe pliku | — |
| `category` (`id`, `name`, opc. `parentId`) | drzewo kategorii sklepu | — |
| `item/id` | stały ID oferty: cyfry, litery łacińskie, `-`, `_` | 20 znaków |
| `item/categoryId` | ID kategorii z `categories`, jedna na produkt | — |
| `item/vendor` | jeden producent, bez kraju produkcji | — |
| `item/name` | nazwa modelu bez reklam | — |
| `item/url` | HTTPS, strona w języku ukraińskim | — |
| `item/priceRUAH` | cena detaliczna w UAH z podatkami, bez separatora tysięcy | — |
| `item/code` / `item/barcode` | kod producenta / kod kreskowy — wymagane „w określonych przypadkach” | — |
| `item/shipping` | czas wysyłki — wymagany dla towarów na zamówienie | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `description` | niewidoczny na stronie, służy do budowy charakterystyk | — |
| `image` | JPEG (zalecany), GIF, PNG; białe tło, bez napisów | — |
| `priceRUSD` + `rate` | cena w USD (na stronie i tak pokazywana w UAH); `rate` wymagany przy cenach USD | — |
| `stock` | „В наявності”, „Під замовлення”, „Немає” | słownik |
| `guarantee` | okres gwarancji, `type` = `manufacturer`/`shop`, `unit="days"` dla dni | — |
| `param name=""` | parametry techniczne z nazwami i jednostkami zgodnymi z katalogiem | — |
| `condition` | 0 nowy, 1 odnowiony, 2 uszkodzone opakowanie, 3 używany (nieładowany) | słownik |
| `region`, `custom`, `delivery`, `payment` | region wyświetlania, wybór do aukcji, opcje dostawy/płatności | — |

## Limity i formaty
- UTF-8 lub windows-1251 (zadeklarowane w nagłówku).
- Zakaz HTML we wszystkich elementach; zakaz znaków kontrolnych 0–31 poza 9, 10, 13; `< > & ' "` jako encje.
- Maks. 150 000 produktów w pliku.
- Plik dostępny przez HTTP(S) bez autoryzacji, przekierowań i ładowania JS. Aktualizacja kilka razy dziennie.
- Kategoria „Одяг для спорту і відпочинку” tylko w XML/YML (nie CSV/XLS).

## Różnice względem szablonu bazowego
- Wymagany słownik `categories` z ID i odwołaniem `categoryId` (Ceneo: ścieżka tekstowa w `cat`) — w XSLT trzeba zbudować unikalną listę kategorii (np. klucz Muencha).
- Pola jako elementy, nie atrybuty `o`; `priceRUAH` w hrywnach; opis bez HTML; nagłówek z `date`, `firmName`, `firmId`.
- Brak sekcji `imgs` — pojedynczy `image` (strona nie opisuje zdjęć dodatkowych).

## Uwagi
- Strona wczytana poprawnie (oryginał po ukraińsku).
- Kiedy dokładnie `code` i `barcode` są obowiązkowe — strona podaje to warunkowo; szczegóły do doczytania przy wdrożeniu.
- Wymaga waluty UAH i ukraińskojęzycznej wersji sklepu.
