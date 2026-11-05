# Analiza: numer części z nazwy → kod producenta w IdoSell (IVEMAX)

## Cel

Wyciągnąć numery części (OE) z nazw towarów IdoSell i przygotować plik aktualizacji pola **kod producenta**. Wpisany kod ma też posłużyć do powiązania produktów wFirma ↔ IdoSell w Base: po SKU automatycznie albo naszym plikiem (patrz `ANALIZA_powiazanie_base_idosell.md`).

## Dane wejściowe

- `products_export-shop52797-…csv` — 4035 towarów IdoSell (4027 `uniw`, 8 z rozmiarami, w tym 5 przykładowych z instalacji sklepu).
- Pomocniczo do wyboru kodu: katalog Base (SKU wFirmy) i `shopArena - 2029-10-21.csv`.

## Stan danych

| | Liczba |
|---|---|
| Kod producenta już wypełniony | 12 towarów (`size@code_producer`, np. `5801593502 `, jeden `5801255814 ; 906943`) + 1 na poziomie produktu (przykładowy produkt 6) |
| Nazwa z 1 kodem | 3372 |
| Nazwa z 2 kodami | 502 (`500043129 ; 504086314 Iveco Daily …`) |
| Nazwa z 3–4+ kodami | 121 |
| Nazwa bez kodu | 40 (przykładowe produkty, oleje Petronas, `- ZAMIENNIK` bez numeru, `skrzynia biegów 2850.6`) |
| Pozycja kodu w nazwie | na początku: 3877, w środku: 67, po myślniku na końcu: 63 |

Reguła rozpoznawania kodu (ta sama co przy dopasowaniu w Base, sprawdzona na 2019 zgodnych parach): ciąg liter i cyfr (z `.`, `-`, `/` w środku), po usunięciu separatorów min. 6 znaków, w tym min. 4 cyfry. Dzięki temu odpadają roczniki (`2014`, `98-06`), pojemności (`2.3`), modele (`35C`, `E5`) i modele skrzyń (`2835.6`, `2850.6`).

## Planowane zmiany / wyjście

Skrypt `kod_producenta_z_nazwy.py` + `run_kod_producenta.bat` (dwuklik, pliki wykrywa sam) w tym folderze. Wyniki:

1. `aktualizacja_kod_producenta.csv` — plik importu do IdoSell: `@id`, `/sizes/size@id`, `/sizes/size@code_producer` (nagłówki jak w eksporcie panelu, separator `,`, UTF-8).
2. `kod_producenta_raport.csv` — dla każdego towaru: ID, nazwa, wszystkie znalezione kody, kod wybrany, obecny kod producenta, status (`nowy` / `bez zmian` / `różni się od obecnego` / `brak kodu` / `wiele kodów`).

## Założenia

- Nazwy **nie zmieniam** — kod zostaje także w nazwie.
- Obecnie wypełnionych 12 kodów **nie nadpisuję**. Gdy różnią się od kodu z nazwy, trafiają do raportu.
- Towary z rozmiarami (8, głównie przykładowe) i bez kodu pomijam — idą tylko do raportu.
- Pole `code_external` (`KZS-…`) zostaje nietknięte, bo to most do Shoparena.

## Decyzje użytkownika (2026-10-21)

- Pkt 2 (GTIN w feedach) — przyjęte do wiadomości.
- Pkt 3 — import **CSV** w panelu.
- Pkt 4 — nasz plik powiązań dla Base jest konieczny niezależnie od kodu producenta.
- Pkt 1 — **towary z kilkoma kodami w nazwie pomijamy.** Klient uzupełni je sam, bo dla tych danych nie ma wspólnej zasady. W pliku importu są tylko nazwy z jednym kodem, a towary z kilkoma kodami trafiają do raportu jako lista dla klienta. Rozkład 623 nazw z kilkoma kodami (do wiadomości):

  | Przypadek | Liczba |
  |---|---|
  | brak pary w wFirmie → pierwszy kod z nazwy | 366 |
  | SKU wFirmy = dokładnie jeden z kodów z nazwy | 196 (153 = pierwszy kod, **43 = inny niż pierwszy**) |
  | SKU wFirmy zawiera kilka kodów z nazwy | 39 |
  | kilka produktów wFirmy na 1 towar (kolizja) | 15 |
  | SKU wFirmy spoza nazwy / mieszane | 7 |

## Otwarte pytania

1. **Który kod wpisać przy 623 nazwach z kilkoma numerami?** Propozycja:
   - jeśli towar jest dopasowany do produktu wFirmy (2347 par), wpisuję ten kod z nazwy, który jest SKU wFirmy. Wtedy kod producenta w IdoSell = SKU w Base, co otwiera automatyczne wiązanie po SKU;
   - w pozostałych przypadkach wpisuję pierwszy kod z nazwy (numer główny), a resztę pokazuję w raporcie.
   Alternatywa: wpisać wszystkie kody razem (`500043129 ; 504086314`), jak w 1 istniejącym przypadku. Odradzam — taki kod nie zadziała jako klucz SKU.
2. **⚠ Kod producenta a GTIN w feedach.** W IdoSell kod producenta bywa wysyłany do Google / porównywarek jako GTIN/EAN. Numer OE Iveco nie jest poprawnym GTIN — w GMC mogą pojawić się ostrzeżenia „Nieprawidłowy GTIN”. Trzeba sprawdzić, czy feedy sklepu (standardowy IdoSell i ewentualne XSLT) biorą GTIN z kodu producenta.
3. **Sposób wgrania:** import CSV w panelu (Towary → import) czy przez REST API? Panelowego importu nie mam przetestowanego na tym formacie nagłówków. Proponuję zrobić CSV, a przed pełnym importem wgrać próbę na 2–3 towarach.
4. Base: które pole IdoSell integracja IVEMAX-IdoSell (37567) czyta jako SKU — kod producenta czy kod zewnętrzny? To decyduje, czy automatyczne wiązanie po SKU zadziała, czy zostaje nasz plik powiązań. Do sprawdzenia w ustawieniach integracji w Base.
