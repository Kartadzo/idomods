# Heureka — wymagania feedu
- Źródła: https://heureka.github.io/xml-feed-specs/ oraz podstrony pól: `fields/productname/`, `fields/imgurl/`, `fields/categorytext/`, `fields/delivery_date/`, `fields/delivery/`, `fields/param/`, `fields/itemgroup_id/`
- Data przeglądu: 2026-10-27
- Format: własny XML Heureka (`SHOP`/`SHOPITEM`), akceptuje format Google: nie (specyfikacja o nim nie wspomina)
- Szablon bazowy: `Glami.xml` — Glami używa tej samej struktury `SHOP`/`SHOPITEM` i niemal tych samych nazw pól (ITEM_ID, ITEMGROUP_ID, PRODUCTNAME, URL, IMGURL, IMGURL_ALTERNATIVE, PRICE_VAT, MANUFACTURER, CATEGORYTEXT, PARAM, DELIVERY_DATE, DELIVERY).

## Struktura pliku
```xml
<?xml version="1.0" encoding="UTF-8"?>
<SHOP>
  <SHOPITEM>
    <ITEM_ID/> <PRODUCTNAME/> <PRODUCT/> <DESCRIPTION/>
    <URL/> <IMGURL/> <IMGURL_ALTERNATIVE/>
    <PRICE_VAT/> <VAT/> <ITEM_TYPE/> <HEUREKA_CPC/>
    <MANUFACTURER/> <MANUFACTURER_POSTAL_ADDRESS/> <MANUFACTURER_ELECTRONIC_ADDRESS/>
    <CATEGORYTEXT>Heureka.cz | Elektronika | Telefony</CATEGORYTEXT>
    <EAN/> <ISBN/> <ITEMGROUP_ID/>
    <PARAM><PARAM_NAME/><VAL/></PARAM>
    <DELIVERY_DATE/>
    <DELIVERY><DELIVERY_ID/><DELIVERY_PRICE/><DELIVERY_PRICE_COD/></DELIVERY>
    <ACCESSORY/> <GIFT/> <EXTENDED_WARRANTY/> <SPECIAL_SERVICE/> <SALES_VOUCHER/>
  </SHOPITEM>
</SHOP>
```

## Pola wymagane
Specyfikacja: 26 pól, z czego 8 wymaganych.
| pole | opis/format | limit |
|---|---|---|
| `ITEM_ID` | unikalny w sklepie | 36 znaków |
| `PRODUCTNAME` | nazwa z informacjami obowiązkowymi dla kategorii | 200 znaków |
| `URL` | unikalna karta z ceną i przyciskiem koszyka | 300 znaków |
| `IMGURL` | zdjęcie główne, `http(s)://`, bez spacji | 255 znaków |
| `PRICE_VAT` | cena końcowa brutto w CZK | maks. 2 miejsca po przecinku |
| `CATEGORYTEXT` | ścieżka zaczynająca się od `Heureka.cz | `, poziomy oddzielone ` | ` | 255 znaków |
| `DELIVERY_DATE` | liczba dni 1–999 albo data `RRRR-MM-DD` | — |
| `DELIVERY` | metoda dostawy: pusty albo `DELIVERY_ID` (kod przewoźnika ze słownika) + `DELIVERY_PRICE` (przedpłata); opc. `DELIVERY_PRICE_COD` (pobranie); ceny wg wzoru `\d+([.,]\d{1,2})?` | do 100 wystąpień |

Słownik `DELIVERY_ID` (39 kodów), m.in.: CESKA_POSTA, PPL, DPD, DHL, GLS, UPS, FEDEX, TNT, ZASILKOVNA, ZASILKOVNA_NA_ADRESU, PPL_PARCELSHOP, GLS_PARCELSHOP, DPD_PICKUP, DPD_BOX, Z_BOX, ALZAPOINT, ALZABOX, BALIKOVNA_BOX, WEDO_HOME, WEDO_POINT, ONLINE, VLASTNI_PREPRAVA.

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `IMGURL_ALTERNATIVE` | zdjęcia dodatkowe | do 10, po 255 znaków |
| `PRODUCT` | alternatywna nazwa/kod produktu | — |
| `DESCRIPTION` | opis z cechami i parametrami | — |
| `VAT` | stawka VAT w %, np. `21` | — |
| `MANUFACTURER` | producent/marka | — |
| `MANUFACTURER_POSTAL_ADDRESS`, `MANUFACTURER_ELECTRONIC_ADDRESS` | adres pocztowy i e-mail/www producenta (GPSR) | — |
| `EAN` | EAN-13 | dokładnie 13 cyfr |
| `ISBN` | ISBN-10 lub ISBN-13 | — |
| `ITEM_TYPE` | klasyfikacja towaru | — |
| `HEUREKA_CPC` | stawka CPC, dodatnia liczba dziesiętna | — |
| `ITEMGROUP_ID` | grupuje warianty (kolor, rozmiar, wzór); `[a-zA-Z0-9_-]` | 36 znaków |
| `PARAM` | `PARAM_NAME` + `VAL`, oba niepuste; powtarzalny | — |
| `ACCESSORY` | `ITEM_ID` akcesorium | do 10 |
| `GIFT` | prezent z atrybutem ID | 250 znaków |
| `EXTENDED_WARRANTY` | `VAL` + `DESC` | — |
| `SPECIAL_SERVICE` | usługa, np. montaż | — |
| `SALES_VOUCHER` | `CODE` + `DESC` | — |

## Limity i formaty
- UTF-8 (wg przykładu). Inne wymagania kodowania nie są opisane.
- Ceny w CZK; kategoria w taksonomii Heureka.cz.

## Różnice względem szablonu bazowego
- Względem `Glami.xml`: `CATEGORYTEXT` z prefiksem `Heureka.cz | ` i kategoriami Heureka (nie Glami, bez płci na początku); `ITEM_ID` i `ITEMGROUP_ID` do 36 znaków (Glami 64) i bez spacji/kropek; `URL` do 300 znaków, `IMGURL` do 255 (Glami 767); `EAN` zamiast `GTIN`; `DELIVERY_DATE` = czas dostawy 1–999 dni lub data (w Glami `0` = na stanie); dodatkowe `VAT`, `HEUREKA_CPC`, pola GPSR producenta, `ACCESSORY`, `GIFT`, `EXTENDED_WARRANTY`, `SPECIAL_SERVICE`, `SALES_VOUCHER`; brak `URL_SIZE`.
- `DELIVERY` jest tu wymagany (z kodem ze słownika) — w Glami opcjonalny.

## Uwagi
- Strona główna i podstrony wczytane poprawnie; część opisów na stronie głównej jest skrócona — limity uzupełniono z podstron pól.
- Specyfikacja nie opisuje: `VIDEO_URL`, `PRODUCTNO`, różnic Heureka.cz / Heureka.sk (prefiks `Heureka.sk` i ceny w EUR nie są wspomniane), feedu dostępności. Nie zgadywano.
- `DELIVERY_DATE = 0` nie jest opisane (zakres zaczyna się od 1) — do potwierdzenia, czy oznacza „na stanie”.
- Mapowanie kategorii Google → Heureka.cz istnieje w projekcie osobno (patrz pamięć: mapowanie Google → Heureka.cz).
