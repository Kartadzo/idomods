# Analiza: import 301 nowych towarów do IdoSell przez API (IVEMAX)

## Cel

Dodać do IdoSell 301 towarów z `nowe_towary_shoparena.csv` (Shoparena, po migracji 2025-07-26) przez REST Admin API. Ustawienia mają odpowiadać towarom przeniesionym wcześniej. Stany magazynowe pomijamy, bo przyjdą z wFirmy przez Base.

## Bramki (specyfikacja panelu v8.12)

1. `POST products/products` — utworzenie towaru. Zdjęcia jako URL (`picturesSettings.picturesSettingInputType = "url"`).
2. `PUT products/products` z `productMenuItems` — przypięcie do menu sklepu. POST nie ma pola menu.

## Wzorzec ustawień

Wzorcem jest towar 4028 (`KZS-7253`, ostatni przeniesiony) i statystyka całego eksportu:

| Pole | Wartość |
|---|---|
| `shopsMask` | 1 (sklep 1) |
| `productVat` | 23 (Shoparena nie ma kolumny VAT, wszystkie przeniesione mają 23) |
| `unitId` | 0 „szt.” (2 towary „zestaw” — w IdoSell takiej jednostki nie ma, też `szt.`) |
| `sizesGroupId` | -1 → rozmiar `uniw` |
| `productInPersistent` | y (widoczny mimo braku stanu) |
| `availableProfile` | 1 „Standard” |
| `productInExportToPriceComparisonSites` | y |
| `productIsVisible` | **y** (3602 z 4035 przeniesionych jest widocznych) |

## Mapowanie pól Shoparena → API

| Shoparena | API | Uwagi |
|---|---|---|
| `name` | `productNames` (pol) | |
| `short_description` | `productDescriptions` (pol) | numer magazynowy = SKU wFirmy, tak jak w przeniesionych |
| `description` | `productLongDescriptions` (pol) | |
| `seo_title`, `seo_description`, `seo_keywords` | `productMetaTitles/Descriptions/Keywords` (pol) | |
| `price` | `productRetailPrice` | brutto, zgodne z przeniesionymi (7253: 2900 = 2900) |
| `producer` | `producerName` | wszystkie istnieją w IdoSell; 4 bez producenta → bez pola |
| `category` | `categoryId` | z przeniesionych towarów tej samej kategorii Shoparena (293). **8** w kategoriach nadrzędnych (np. `Silnik i osprzęt > Turbosprężarki`), których w IdoSell nie ma jako kategorii → `*Kategoria tymczasowa`, tak jak przy migracji |
| `category` | menu `Kategorie\A\B` | wszystkie 301 ścieżek istnieje w menu sklepu |
| `images 1…9` | `productPictures` (URL) | adresy ivemax.com działają (sprawdzone: 200, image/jpeg); 1–8 zdjęć |
| `kod_zewnetrzny` | `productSizeCodeExternal` | `KZS-…` / kod z datą |
| `kod_producenta` | rozmiar `uniw`, kod producenta | 258 towarów. Panel blokuje duplikaty — gdy kod jest zajęty, towar idzie **bez** kodu producenta, z adnotacją w dzienniku |
| `weight` | — | pomijam: w Shoparenie `1`, w IdoSell 31000 lub 0 — brak spójnej reguły |
| `stock` | — | pomijam (decyzja) |

## Kontrola duplikatów przed wysyłką

- Kod zewnętrzny: sprawdzam na żywo (`GET products/sizes`), czy nie istnieje w sklepie. Jeśli istnieje, nie wysyłam.
- 78 towarów ma numer części obecny już w nazwie towaru IdoSell (kolumna `uwagi`). Zgodnie z decyzją wysyłam je, ale w dzienniku zostaje adnotacja.

## Przebieg (`api_nowe_towary.py` + `run_api_nowe_towary.bat`)

1. Odczyt stanu sklepu, plan, walidacja.
2. **Próba: 1 towar** → POST, PUT menu, odczyt kontrolny (nazwa, kategoria, cena, kod zewnętrzny, zdjęcia, menu). Pokażę Ci ID, żebyś mógł go obejrzeć w panelu.
3. Po Twojej akceptacji: reszta paczkami po 20 (zdjęcia z URL wydłużają wywołanie).
4. Dziennik `wyniki/api_nowe_towary_<data>.csv`: kod Shoparena → nowe ID IdoSell, status, uwagi + `.jsonl` z odpowiedziami API.

## Decyzje użytkownika (2026-10-21)

1. Na razie tylko polski. Pozostałe wersje językowe użytkownik dostarczy jutro.
2. Towary **ukryte** (`productInVisible = n`). Jutro razem z tłumaczeniami przyjdzie kolumna, które towary aktywować.

Uzupełnienie bramek: `POST products/products` nie ma pola kodu producenta, więc kod wpisuję po utworzeniu przez `PUT products/sizes` (jak w etapie 1). Ponowne uruchomienie jest bezpieczne, bo towar z kodem zewnętrznym obecnym w sklepie jest pomijany.

## Wynik importu i naprawa (2026-10-21, 18:08–18:30)

Wszystkie 301 kodów zewnętrznych są w sklepie, ale:
- **181 towarów bez zdjęć.** Shoparena serwuje oryginały (PNG do 9,5 MB, pobieranie ~15 s), a IdoSell przerywa pobieranie z URL („Przekroczono limit czasu podczas pobierania obrazka”).
  Rozwiązanie: skrypt sam pobiera plik i wysyła go jako **base64** (`picturesSettingInputType = base64`), po jednym towarze. Sprawdzone na 4808: 3 zdjęcia w 9 s.
- **104 bez menu** i część bez kodu producenta. Paczka POST przekroczyła czas po stronie klienta, a mój klient API ją ponowił. Towary z pierwszego wywołania już istniały, więc ponowienie zwróciło „produkt o podanym kodzie istnieje” i nie przeszło do menu i kodów.
- **4 dublety** (`5766_20250906122016`, `KZS-7280`, `KZS-7298`, `KZS-7338` — po 2 towary) — skutek tego samego ponowienia.
- Poprawka w `api_kod_producenta.py`: POST nie jest już ponawiany po przekroczeniu czasu.

Naprawa: `api_nowe_towary_naprawa.py` — dla każdego kodu bierze towar o najniższym ID i uzupełnia **tylko braki**: zdjęcia (gdy 0), menu (gdy brak), kod producenta (gdy pusty i wolny). Dublety (wyższe ID) tylko raportuje — usunięcie wymaga zgody użytkownika.

### Ciąg dalszy (18:33–19:05)

- Oprócz 4 par znalazło się **42 kopie bez kodu zewnętrznego**, też utworzone przy imporcie: IdoSell założył towar, ale odrzucił kod (`code_adding_error`).
- Decyzja użytkownika: „usuń duplikaty z gorszymi danymi”. `api_usun_duplikaty.py` usunął **46** towarów: 42 kopie bez kodu zewnętrznego + z par o tym samym kodzie ten bez kodu producenta (4660, 4670, 4691, 4744). Warunek: identyczna nazwa, cena i opis, towar ukryty, dodany 18:05–18:40. Towary o tej samej nazwie i innej cenie (np. 4808 i 4810) to osobne produkty Shoparena — zostały.
- `products/sizes` jeszcze przez jakiś czas zwraca usunięte towary. Naprawa i plik powiązań sprawdzają istnienie w `products/products`.
- Stan końcowy (audyt odczytem): 301 towarów, każdy kod zewnętrzny raz, wszystkie z menu i ukryte, kod producenta 203 (98 bez — kod zajęty przez inny towar). Zdjęcia zgodne w 300. **4900** ma 5 z 8 zdjęć: 3 pliki PNG mają 12–13 MB, a limit IdoSell to 10 MB — do zmniejszenia ręcznie.

## Otwarte pytania (zamknięte decyzjami powyżej)

1. **Języki:** przeniesione towary mają opisy w 8 językach (pol, dut, eng, fre, ger, ita, spa, swe). Nowe będą tylko po polsku. Zostawić tak, czy tłumaczenia ktoś zrobi osobno?
2. **Widoczność:** nowe towary od razu widoczne w sklepie (`y`), czy ukryte do czasu powiązania ze stanami z wFirmy?
