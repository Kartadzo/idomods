# ANALIZA: cena omnibus w `custom_label_3` feedów Meta eZebra
Zadanie ClickUp: [eZebra - Feed Meta ads - cena omnibus](https://app.clickup.com/t/1ammhmkck0y) · Klient: ezebra.pl · Data: 2026-11-06

| | |
|---|---|
| Termin | 09.11.2026 |
| Szacunek | 1,5 h |
| Priorytet | wysoki („pilne”) |
| Realizacja | poniedziałek 09.11 |

Klient zgodził się w komentarzu na poniedziałek. Powody: w piątki nie wdrażamy, a w IdoSell trwają prace techniczne.

## Cel
We wszystkich pięciu feedach Meta (PL, UK, DE, AT, UA) dodać do `custom_label_3` cenę omnibus, czyli najniższą cenę z ostatnich 30 dni. Format jak „49,99 zł”, w walucie danego feedu.

## Dane wejściowe i wyjściowe
| Feed | Plik lokalny (`xslt/E/ezebra/`) | Zajęte etykiety | Omnibus już w kodzie |
|---|---|---|---|
| Meta PL | `PL/ezebrapl_fbAds.xml` | `g:custom_label_1` | tak, w logice `g:price` (l. 78–105) |
| Meta DE | `DE/ezebrade_fbAds.xml` | `custom_label_1` | tak, zmienna `$omnibus` (l. 295–298) |
| Meta AT | `AT/ezebraat_fbAds.xml` | `custom_label_1` | nie |
| Meta UA | `UA/ezebraua_fbAds.xml` | `custom_label_1` | nie |
| Meta UK | `UK/ezebrauk_fbAds.xml` | `g:custom_label_1`, `g:custom_label_2` | nie |

**Źródło w IOF:** `iaiext:omnibus_price_retail/iaiext:site[@id]/@gross`.
- Element jest na poziomie produktu, z atrybutem `size_id`.
- Przykład z eksportu z 02.09: `gross="40.98" new_price="false"`.

**Wyjście:**
- poprawione sterowniki w `xslt/E/ezebra/<kraj>/`, do ręcznego wgrania;
- poprzednie wersje w `xslt/E/ezebra/<kraj>/old/` z datą;
- `komentarz_clickup.txt` w tym folderze.

## Plan
Kroki 1 i 2 są wspólne z zadaniem `../black_days_2026-11-06/`, bo zmieniane są te same pliki. Robię je raz.

1. **Panel IdoSell** (Claude in Chrome, tylko odczyt): sterowniki 5 serwisów Meta, waluta i strona (`site id`) każdego eksportu. Sprawdzam też, czy IOF serwisu zagranicznego podaje `omnibus_price_retail` w walucie feedu.
2. **Zgodność z panelem.** Gdy plik lokalny różni się od panelu, przenoszę go do `xslt/E/ezebra/<kraj>/old/<nazwa>_<RRRR-MM-DD>.xml`, a jako aktualną zapisuję wersję z panelu.
3. **XSLT:** `custom_label_3` (PL i UK z prefiksem `g:`) = `format-number(@gross)` + waluta:
   - PL: `49,99 zł`
   - DE i AT: `49,99 €`
   - UK: `£49.99`
   - UA: `49,99 грн`

   Szczegóły:
   - Wybór `site` i `size_id` zgodny z ceną użytą w `price` danego feedu: w PL i DE ta sama ścieżka co obecna logika, w AT, UA i UK analogicznie.
   - Brak ceny lub 0: pole pomijam.
   - Black Days idzie do `custom_label_4`, osobne zadanie.
4. **Weryfikacja przez lxml** na aktualnym eksporcie IOF:
   - kompilacja;
   - liczba produktów z ceną i bez niej;
   - po 3 przykłady na feed;
   - porównanie `custom_label_3` z `price` / `sale_price`.
5. **Oddanie:** `komentarz_clickup.txt` z listą feedów, polem i formatem.

## Założenia
- Cena omnibus jest brutto, w walucie eksportu danego serwisu (IOF zagraniczny po przeliczeniu waluty sklepu). Do sprawdzenia w kroku 1.
- Format ceny w PL, DE i AT: przecinek dziesiętny, 2 miejsca, symbol po kwocie ze spacją. W UK: symbol przed kwotą, kropka dziesiętna.
- Gdy produkt ma rozmiary z różnymi `size_id`, biorę wartość dla rozmiaru eksportowanego jako `entry`. Gdy jest tylko `size_id="0"`, biorę ją dla wszystkich wariantów.

## Otwarte pytania
- Czy w UA ma być „грн” czy „UAH”, a w UK „£49.99” czy „49.99 £”? Domyślnie zapis lokalny; potwierdzić z klientem w komentarzu.
- Czy pokazywać cenę, gdy omnibus jest równa cenie bieżącej (`new_price="false"`, brak promocji)? Domyślnie tak, zawsze gdy > 0.

## Zasady sesji
- ClickUp tylko do odczytu. Komentarz zapisuję w `komentarz_clickup.txt`, wkleja go użytkownik.
- Git: gałąź `black_days_ezebra`, wspólna z zadaniem Black Days (wariant „nowy problem”). `/zapisz` i `/zamknij` wykonuje użytkownik, sesja realizująca nie commituje.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: tak (panel IdoSell eZebra), jedna sesja z Claude in Chrome naraz.
  - Używam `javascript_tool`.
  - Sterownik czytam z `textarea` okna „Ustawienia”, bez zapisu.
  - Nie klikam „Zapisz” ani „Podgląd wyników działania sterownika”.
- Kopie sterowników tylko w `xslt/E/ezebra/<kraj>/old/`.
- Zamówienie testowe i sprawdzanie zdarzeń: nie dotyczy.

## Stan
- 2026-11-06: analiza wstępna (sesja /zadanie); realizacja w poniedziałek razem z Black Days.
