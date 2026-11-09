# ANALIZA: atrybut „Black Days” w feedach eZebra (Meta, RTB House, WP/Onet)
Zadanie ClickUp: [eZebra - feed - black friday](https://app.clickup.com/t/1ammhmkcme5) · Klient: ezebra.pl · Data: 2026-11-06
Termin: 09.11.2026 (deadline 13.11) · szacunek 1 h · priorytet wysoki

## Cel
Agencje mają oznaczać akcję Black Friday. Do wszystkich feedów Meta (PL i zagraniczne), feedu RTB House i feedu wydawców (WP, Onet) dodać atrybut „Black Days”. Jego wartością jest **wartość parametru o ID 91508**, czyli ID nazwy parametru „Black Friday” w panelu.

## Dane wejściowe i wyjściowe
Sterowniki są w `xslt/E/ezebra/`. Pliki lokalne mogą być nieaktualne względem panelu.

| Feed | Plik lokalny | Uwagi |
|---|---|---|
| Meta PL | `PL/ezebrapl_fbAds.xml` | `g:custom_label_1` zajęte (etykiety marketingowe) |
| Meta AT | `AT/ezebraat_fbAds.xml` | `custom_label_1` zajęte |
| Meta DE | `DE/ezebrade_fbAds.xml` | `custom_label_1` zajęte |
| Meta UA | `UA/ezebraua_fbAds.xml` | `custom_label_1` zajęte |
| Meta UK | `UK/ezebrauk_fbAds.xml` | `g:custom_label_1` i `g:custom_label_2` zajęte |
| RTB House | `PL/ezebra_ceneo_RTB.xml` | potwierdzone przez użytkownika |
| WP + Onet (wydawcy) | `PL/ezebrapl_WP.xml` | serwis PL, ID 10024; jeden feed dla obu wydawców |

ID serwisów Meta i RTB w panelu odczytam w kroku 1.

**Parametr 91508 „Black Friday”** (według eksportu IOF z 02.09, który mógł się zdezaktualizować):
- wartości: 91509 „Black Friday kosmetyki do makijażu” i 91647 „Najlepsze okazje na Black Friday”;
- w eksporcie występował w 276 miejscach;
- ma tłumaczenie `ger`.

**Wyjście:**
- poprawione sterowniki w `xslt/E/ezebra/<kraj>/`, do ręcznego wgrania w panelu;
- poprzednie wersje w `xslt/E/ezebra/<kraj>/old/` z datą;
- `komentarz_clickup.txt` w tym folderze (`Zmiany_sterownikow/ezebra/black_days_2026-11-06/`).

## Plan
1. **Panel IdoSell** (Claude in Chrome, tylko odczyt):
   - aktualne wartości parametru 91508 i ich tłumaczenia (DE/AT/UK/UA);
   - lista serwisów: Meta PL/AT/DE/UA/UK, RTB House, WP (10024), czyli ID i nazwy;
   - sterownik każdego serwisu: tylko odczyt treści `textarea`, bez zapisu.
2. **Zgodność wersji lokalnych z panelem.** Treść z panelu porównuję z plikiem lokalnym.
   - Zgodne: zostawiam.
   - Różne: plik lokalny przenoszę do `xslt/E/ezebra/<kraj>/old/<nazwa>_<RRRR-MM-DD>.xml`, a wersję z panelu zapisuję jako aktualną.
   - Zapisuję listę różnic.
3. **Zmiana w sterownikach** (na wersji z panelu): atrybut z wartości parametru 91508, dopasowanie po `@id` parametru.
   - **Meta:** `custom_label_4`. Wolne są pola 0, 3 i 4; pole 3 zajmie cena omnibus z równoległego zadania (`../cena_omnibus_2026-11-06/`). W PL i UK z prefiksem `g:`, jak pozostałe pola.
   - **RTB i WP:** pole w formacie danego feedu, np. `<black_days>` lub atrybut w bloku parametrów. Format ustalę po odczycie struktury.
   - Brak parametru: pole pomijam.
   - Przed zmianą kopia do `xslt/E/ezebra/<kraj>/old/` z datą.
4. **Weryfikacja i oddanie:**
   - lxml na aktualnym eksporcie IOF: kompilacja, liczba produktów z atrybutem, przykładowe wartości;
   - pliki do ręcznego wgrania i `komentarz_clickup.txt` z listą feedów i nazwą pola dla agencji.

## Założenia
- Wartość pola to **nazwa wartości parametru** w języku feedu, z rezerwą PL, gdy brak tłumaczenia. Atrybut nazywa się „Black Days” w znaczeniu opisu dla agencji, a w Meta jest to `custom_label_4`.
- Wartości parametrów eZebra mogą zawierać HTML i style (jak parametr „RAMKA”), więc przed użyciem sprawdzam je i w razie potrzeby oczyszczam.
- Produkt z kilkoma wartościami: wartości łączę przecinkiem, maksymalnie 100 znaków.
- Do zrobienia: sprawdzić, czy parametr jest na poziomie produktu (`parameters/parameter`), czy w `sizes`.
- Niczego nie zapisuję w panelu. Wgranie sterowników robi użytkownik.

## Otwarte pytania
- W Meta `custom_label_4` (ustalone 2026-11-06 przy zadaniu omnibus: pole 3 = omnibus); do potwierdzenia z klientem w komentarzu.
- Czy w feedach zagranicznych wartość ma być tłumaczona, czy zawsze PL, czy na sztywno „Black Days”? Domyślnie tłumaczenie.
- Czy w RTB i WP nazwa pola ma być `black_days`? Do potwierdzenia po odczycie struktury feedu.

## Zasady sesji
- ClickUp tylko do odczytu. Komentarz zapisuję w `komentarz_clickup.txt`, wkleja go użytkownik.
- Git: gałąź `black_days_ezebra` (wariant „nowy problem”). `/zapisz` i `/zamknij` wykonuje użytkownik, sesja realizująca nie commituje.
  - Na gałąź przeszły też niezacommitowane przenosiny 6 plików `xslt/E/ezebra/PL` → `PL/old/` z `main`.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: tak (panel IdoSell eZebra), jedna sesja z Claude in Chrome naraz.
  - Panel nie osiąga `document_idle`, więc używam `javascript_tool`.
  - Sterownik czytam z `textarea` okna „Ustawienia” serwisu, okno zamykam nawigacją, bez zapisu.
  - Nie klikam „Zapisz” ani „Podgląd wyników działania sterownika”.
- Zamówienie testowe i sprawdzanie zdarzeń: nie dotyczy.

## Stan
- 2026-11-06: przeniesiono do podfolderu `black_days_2026-11-06/` (zasada: osobny folder `<element>_<data>` na zadanie); pole Meta zmienione na `custom_label_4`; kopie sterowników tylko w `xslt/E/ezebra/<kraj>/old/`. Realizacja w poniedziałek 09.11 razem z zadaniem omnibus (wspólne kroki 1–2).
- 2026-11-06: analiza wstępna (sesja /zadanie); poprawki użytkownika:
  - wartość = wartość parametru;
  - WP i Onet = 10024;
  - RTB = `ezebra_ceneo_RTB.xml`;
  - krok porównania z panelem przed zmianą.
- 2026-11-09: Meta (5 feedów) zrobione razem z omnibusem: `custom_label_4` = `parameters/parameter[@id='91508']/value/@name` po przecinku, max 100 znaków (szczegóły i weryfikacja w `../cena_omnibus_2026-11-06/ANALIZA_cena_omnibus_ezebra.md`). Parametr ma już kilkanaście wartości (np. „Perfumy Black Friday”, „Black Friday kosmetyki Nivea”), część łączeń jest obcinana do 100 znaków. RTB House i WP/Onet — do zrobienia.
- 2026-11-09 (RTB i WP/Onet): serwisy shop=1: RTB House = ID 10050 „RTB CUBE [Ceneo][IdoMods] #2” (aktywny; wyłączony 10041 bez #2 pominięty), WP/Onet = ID 10024 „sterownik WP i Onet”.
  - Porównanie z panelem (schowek): oba różne → lokalne w `PL/old/ezebrapl_WP_2026-11-09.xml` i `PL/old/ezebra_ceneo_RTB_2026-11-09.xml`, aktualne = wersje z panelu. WP w panelu to ver. 2.0 z 2026-10-07 (omnibus, akcje, opis bez HTML), lokalny był ver. 1.0. RTB: tylko limit wartości parametru 92435 = 19 (lokalnie 7).
  - Zmiany (potwierdzone przez użytkownika): RTB `<a name="black_days">` na końcu `<attrs>` (szablon `product`), ogólna pętla parametrów bez zmian, więc `<a name="Black Friday">` zostaje; WP `<black_days>` bez prefiksu, przed `adwords_grouping` (kontekst `size`, ścieżka `../../parameters`). Logika jak w Meta.
  - Weryfikacja lxml na eksporcie PL z 02.09: kompilacja OK, bez błędów; oba feedy 81/170 ofert z polem (= 81 produktów z parametrem), max 100 znaków, jedno pole na ofertę; diff do panelu = tylko dodane linie (WP 13, RTB 12).
  - Poprawka użytkownika: WP ma format GMC, więc zamiast `<black_days>` jest `g:custom_label_4` (żaden custom_label nie był zajęty; numer jak w Meta). Ponowna weryfikacja lxml: 81/170, max 100 znaków, diff do panelu +13/−0.
  - `komentarz_clickup.txt` gotowy (7 feedów, nazwy pól). Do zrobienia przez użytkownika: wgranie 2 sterowników w panelu, wklejenie komentarza po wgraniu.
