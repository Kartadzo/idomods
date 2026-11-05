# Idealo — wymagania feedu
- Źródła: https://idealo.github.io/csv-importer/en/csv/
- Data przeglądu: 2026-10-27
- Format: CSV (własna specyfikacja idealo), akceptuje format Google: nie wynika ze strony (opisany jest tylko CSV idealo)
- Szablon bazowy: `Idealo.xml` — istniejący szablon tego serwisu (XSLT generujący dane dla idealo); należy sprawdzić, czy wypuszcza CSV zgodny z poniższymi kolumnami.

## Struktura pliku
Jeden wiersz = jedna oferta, kolejność kolumn dowolna, separator `,`, nagłówek z nazwami kolumn:
```
sku,brand,title,categoryPath,url,hans,description,imageUrls,price,basePrice,delivery,deliveryCosts_dhl,paymentCosts_paypal,eans,size,colour,gender,material,packagingUnit
```

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| `sku` | unikalny numer artykułu w sklepie | — |
| `title` | nazwa z producentem i modelem; przy wielopakach z liczbą sztuk | — |
| `url` | adres oferty zgodny z RFC 3986 | — |
| `price` | cena brutto bez symbolu waluty, kropka dziesiętna | — |
| `delivery` | czas dostawy w dniach roboczych, bez ogólnikowych sformułowań | — |
| `deliveryCosts_<przewoźnik>` | min. jedna kolumna; `0.00` = darmowa; np. `deliveryCosts_dhl`, `_dpd`, `_gls`, `_ups`, `_deutsche_post`, `_hermes`, `_spedition` | — |
| `paymentCosts_<metoda>` | min. jedna kolumna; `0.00` = bez opłaty; np. `paymentCosts_paypal`, `_credit_card`, `_cash_on_delivery`, `_invoice` | — |
| `basePrice` | wymagane przy obowiązku ceny jednostkowej: cena za 1 kg, l, m, m², m³ | — |
| `packagingUnit` | wymagane dla wielopaków: liczba identycznych sztuk | — |
| `EEC_efficiencyClass`, `EEC_spectrum`, `eec_labelUrl`, `eec_dataSheetUrl` | wymagane dla produktów z etykietą energetyczną; etykieta PNG/JPG/WebP/PDF z czytelnym QR, karta PDF | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `brand` | marka/producent (od 2026-09-28 już niewymagany) | — |
| `categoryPath` | ścieżka od kategorii głównej sklepu, bez producenta i haseł promocyjnych | — |
| `hans` | numer artykułu producenta (MPN), jeden na ofertę | — |
| `description` | czysty tekst bez HTML | 1000 znaków |
| `imageUrls` | URL-e zdjęć, pierwszy = główne; PNG/JPG | do 3 MB/zdjęcie |
| `eans` | GTIN/EAN, jeden na ofertę (listy rozdzielane `;`) | — |
| `size`, `colour`, `gender`, `material` | osobna oferta na każdy wariant; buty — rozmiary EU | — |
| `formerPrice` | cena przed obniżką (nie wyświetlana) | — |
| `voucherCode` | `KOD (opis/ważność)`, dla wszystkich klientów | 200 znaków |
| `deliveryComment` | tekst bez promocji | 150 znaków |
| `deposit`, `maxOrderProcessingTime`, `freeReturnDays`, `fulfillmentType`, `twoManHandlingFee`, `disposalFee`, `condition`, `conditionType`, `download`, `replica`, `EEC_version` | pola uzupełniające | — |
| atrybuty kategorii | części samochodowe (`oens`, `kbas`), soczewki, wino, opony, leki (`pzns`), suplementy, kosmetyki | — |

## Limity i formaty
- UTF-8, separator kolumn `,`, separator dziesiętny `.`, listy wewnątrz pola `;`, cytowanie wg RFC 4180.
- Dopuszczalna kompresja ZIP/gzip. Plik przez link (może być z hasłem), FTP lub HTTP(S); import zwykle co 30 min. Wymagana whitelista adresów IPv4 idealo.

## Różnice względem szablonu bazowego
- Do weryfikacji w `Idealo.xml`: czy wynik to CSV (a nie XML), czy kolumny mają aktualne nazwy (`imageUrls`, `delivery`, `eans`, `hans`, `colour`), czy są kolumny `deliveryCosts_*` i `paymentCosts_*`, przycięcie opisu do 1000 znaków bez HTML, warianty jako osobne wiersze.
- Kolumny checkout zostały wycofane w 2023 r. — jeśli szablon je zawiera, można usunąć.
- Uwaga na listę zdjęć: specyfikacja mówi o URL-ach rozdzielanych przecinkiem, co koliduje z separatorem kolumn — wymaga cytowania pola.

## Uwagi
- Strona wczytana poprawnie.
- Niespójność w dokumentacji: przykład używa `imageUrl` i `deliveryTime`, tabela — `imageUrls` i `delivery`. Kontakt techniczny: tam@idealo.de.
- Separator przecinek zgadza się z domyślną konwencją projektu.
