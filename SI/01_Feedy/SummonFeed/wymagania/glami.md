# Glami — wymagania feedu
- Źródła: https://www.glami.pl/info/feed/
- Data przeglądu: 2026-10-27
- Format: własny XML (`SHOP`/`SHOPITEM`, wzorowany na Heurece), także CSV (bez szczegółów); akceptuje format Google: nie wynika ze strony
- Szablon bazowy: `Glami.xml` — istniejący szablon tego serwisu, struktura `SHOP`/`SHOPITEM`.

## Struktura pliku
```xml
<?xml version="1.0" encoding="utf-8"?>
<SHOP>
  <SHOPITEM>
    <ITEM_ID/> <ITEMGROUP_ID/> <PRODUCTNAME/> <DESCRIPTION/>
    <URL/> <URL_SIZE/> <IMGURL/> <IMGURL_ALTERNATIVE/>
    <PRICE_VAT/> <MANUFACTURER/> <CATEGORYTEXT/> <GTIN/>
    <PARAM><PARAM_NAME>kolor</PARAM_NAME><VAL>biały</VAL></PARAM>
    <PARAM><PARAM_NAME>rozmiar</PARAM_NAME><VAL>41</VAL></PARAM>
    <PARAM><PARAM_NAME>materiał</PARAM_NAME><VAL>bawełna</VAL><PERCENTAGE>50%</PERCENTAGE></PARAM>
    <DELIVERY_DATE>0</DELIVERY_DATE>
    <DELIVERY><DELIVERY_ID/><DELIVERY_PRICE/><DELIVERY_PRICE_COD/></DELIVERY>
    <GLAMI_CPC/> <PROMOTION_ID/>
  </SHOPITEM>
</SHOP>
```
Jeden `SHOPITEM` = jedna kombinacja kolor + rozmiar.

## Pola wymagane
Strona nie oznacza pól pojedynczo jako wymagane — poniżej pola opisane jako obowiązkowe lub konieczne.
| pole | opis/format | limit |
|---|---|---|
| `ITEM_ID` | unikalny dla wariantu; litery, cyfry, `/ \ - _ . :` i spacja; taki sam jak w GLAMI Pixel | 64 |
| `ITEMGROUP_ID` | wspólny dla wariantów jednego modelu | 64 |
| `PRODUCTNAME` | zalecane: płeć, materiał, kolor, cechy; **bez rozmiaru** i dopisków typu „darmowa dostawa”; taki sam jak w Pixelu | 200 |
| `DESCRIPTION` | wymagany dla każdego produktu, język lokalny, może być CDATA | 65 535 |
| `URL` | pełny adres produktu bez rozmiaru | 767 |
| `URL_SIZE` | adres konkretnego rozmiaru (np. `?size=41`) | 767 |
| `IMGURL` | zdjęcie produktowe (packshot) | 767 |
| `PRICE_VAT` | cena brutto bez waluty i separatora tysięcy, kropka lub przecinek | decimal |
| `CATEGORYTEXT` | ścieżka kategorii GLAMI rozdzielona `|`, płeć jako pierwszy poziom | 255 |
| `PARAM` rozmiar | `PARAM_NAME`=`rozmiar`, jedna wartość na item; obowiązkowy poza torebkami, szalikami, zegarkami, okularami | 255 |
| `PARAM` kolor | każdy produkt powinien mieć kolor | 255 |
| `DELIVERY_DATE` | **dostępność**, nie czas dostawy: `0` = na stanie, liczba = dni do dostępności | integer |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `IMGURL_ALTERNATIVE` | powtarzalne; zalecane min. 3 zdjęcia na modelu | 767 |
| `MANUFACTURER` | marka; pominąć element, jeśli produkt bez marki | 200 |
| `GTIN` | ean8/12/13/14/18, gtin12/13/14; unikalny dla koloru i rozmiaru | integer |
| `PARAM` materiał | `PARAM_NAME`, `VAL`, `PERCENTAGE`; powtarzać per materiał | 255 |
| `PARAM` size_system | wymagany, gdy system inny niż EU/INT (`UK`, `US`…) | 255 |
| `DELIVERY` | `DELIVERY_ID` (np. PPL), `DELIVERY_PRICE`, `DELIVERY_PRICE_COD`; bez odbioru osobistego | — |
| `GLAMI_CPC` | indywidualna stawka, liczona tylko gdy wyższa od bazowej | decimal |
| `PROMOTION_ID` | ID vouchera z panelu | integer |
| `CATEGORY_ID` | nieobsługiwany — nie zastępuje `CATEGORYTEXT` | — |

## Limity i formaty
- Pobieranie automatyczne co godzinę. Produktów wyprzedanych nie wysyłać.
- Zdjęcia: realne (bez renderów), dokładnie ten kolor, białe/jasne tło, bez znaków wodnych i tekstów; najlepiej 1500 px, min. 400 px na bok. Zdjęcia pobierane tylko przy rejestracji — po zmianie zdjęcia zmienić URL. Serwer zdjęć musi wpuszczać IPv4 `62.109.141.192/27` i IPv6 `2001:1ab0:f002::/48`.
- Tagi wielkimi literami, `&` jako `&amp;` lub CDATA, URL bez spacji i polskich znaków.
- Nazwy filtrów `PARAM` muszą pasować do listy GLAMI (strona `/tag-csv/`).

## Różnice względem szablonu bazowego
- Sprawdzić w `Glami.xml`: obecność `URL_SIZE`, `PARAM` materiał z `PERCENTAGE`, `size_system`, `GTIN` (nie `EAN`), `PROMOTION_ID`, `DELIVERY_DATE` jako dostępności (0 dla stanu > 0) oraz pomijanie wariantów bez stanu.
- `CATEGORYTEXT` musi zaczynać się od płci i używać kategorii GLAMI — wymaga mapowania, nie ścieżki sklepu.

## Uwagi
- Strona wczytana poprawnie.
- Niespójność nazw: tekst mówi „EAN”, przykłady XML używają `GTIN`; nazwa parametru koloru występuje jako `kolor`, `color` i `colour` — potwierdzić z GLAMI.
- Szczegóły formatu CSV nie są opisane.
