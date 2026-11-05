# Analiza mapowania parametrów CSV → atrybuty Ceneo

Produktów w CSV: **120152** · par parametr\wartość: **1325619** · unikalnych nazw parametrów: **49** (mniej niż żądane 60 — to komplet)

Atrybutów Ceneo w gałęzi `Księgarnia`: **43** unikalnych nazw w 69 kategoriach.

## Współwystępowanie (rozstrzyga kolejność w XSLT)

- `Strony` — 102425 produktów
- `Elementy` — 44302 produktów
- `Strony+Elementy` — 38830 produktów
- `Autorzy` — 114987 produktów
- `Redakcja` — 2581 produktów
- `Autorzy+Redakcja` — 2542 produktów
- `Redakcja bez Autorzy` — 39 produktów

## Tabela zbiorcza — wszystkie 49 parametrów

| # | Parametr CSV | Wystąpień | Unikalnych | Typ w CSV | Atrybut Ceneo | Dopasowanie | Typ w Ceneo | Werdykt | Podobne w Ceneo |
|---|---|---:|---:|---|---|---|---|---|---|
| 1 | Rok wydania | 115789 | 22 | rok 100% | Rok wydania | dokładne (Księgarnia) | rok | ✅ typ zgodny | — |
| 2 | Oprawa | 115131 | 17 | tekst 100% | Okładka | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 3 | Autorzy | 114987 | 359 | tekst 100%, tekst długi 0% | Autor | synonim (Księgarnia) | — | ➖ brak próbki Ceneo | — |
| 4 | Stan | 114656 | 1 | tekst 100% | Stan | poza Księgarnią | tekst | ⚠️ nie w Księgarni | — |
| 5 | Data premiery | 108385 | 337 | data 100% | — | — | — | ❌ brak w Ceneo | — |
| 6 | Format | 105270 | 346 | wymiar 100% | Format | dokładne (Księgarnia) | tekst | ⚠️ typ różny | — |
| 7 | Strony | 102425 | 186 | int 100% | Ilość stron | synonim (Księgarnia) | int | ✅ typ zgodny | — |
| 8 | Waga | 90775 | 245 | liczba+jednostka 100% | Waga | poza Księgarnią | liczba+jednostka, tekst | ⚠️ nie w Księgarni | — |
| 9 | Cena okładkowa | 72819 | 1 | bool 100% | — | — | — | ❌ brak w Ceneo | Okładka |
| 10 | Długość towaru w centymetrach | 51197 | 140 | dec 83%, int 17% | — | — | — | ❌ brak w Ceneo | — |
| 11 | Wysokość towaru w centymetrach | 51197 | 103 | dec 79%, int 21% | — | — | — | ❌ brak w Ceneo | — |
| 12 | Szerokość towaru w centymetrach | 51197 | 105 | dec 80%, int 20% | — | — | — | ❌ brak w Ceneo | — |
| 13 | Waga gabarytowa w gramach | 51173 | 379 | dec 95%, int 5% | — | — | — | ❌ brak w Ceneo | — |
| 14 | Elementy | 44303 | 197 | int 100% | Ilość stron | synonim (Księgarnia) | int | ✅ typ zgodny | — |
| 15 | Język | 42954 | 6 | tekst 100% | Język | dokładne (Księgarnia) | tekst | ✅ typ zgodny | — |
| 16 | Kampania | 24056 | 98 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 17 | Seria | 19831 | 321 | tekst 100% | Seria | dokładne (Księgarnia) | — | ➖ brak próbki Ceneo | — |
| 18 | Kampania-Walentynki | 16687 | 3 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 19 | Język nauczany | 7854 | 16 | tekst 100% | Język | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 20 | Klasa | 7010 | 53 | przedział wieku 66%, tekst 32%, int 3% | Klasa | dokładne (Księgarnia) | int | ⚠️ typ różny | — |
| 21 | Wyprzedaz | 2771 | 30 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 22 | Prezenty 2023 | 2608 | 14 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 23 | Redakcja | 2581 | 330 | tekst 98%, tekst długi 2% | Autor | synonim (Księgarnia) | — | ➖ brak próbki Ceneo | — |
| 24 | Grupa wiekowa | 2339 | 84 | przedział wieku 94%, tekst 6% | Wiek | synonim (Księgarnia) | tekst | ⚠️ typ różny | — |
| 25 | Minimalny wiek | 2246 | 21 | przedział wieku 94%, tekst 6% | Wiek | synonim (Księgarnia) | tekst | ⚠️ typ różny | — |
| 26 | Nowosci | 1669 | 12 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 27 | Nr dopuszczenia | 984 | 362 | tekst 99%, int 1%, rok 0% | — | — | — | ❌ brak w Ceneo | — |
| 28 | Liczba elementów | 622 | 37 | dec 94%, int 6%, rok 0% | Ilość stron | synonim (Księgarnia) | int | ⚠️ typ różny | — |
| 29 | Opakowanie | 587 | 12 | tekst 100% | Opakowanie | poza Księgarnią | liczba+jednostka, tekst | ⚠️ nie w Księgarni | — |
| 30 | Liczba tomów | 573 | 20 | int 100% | Zestaw | synonim (Księgarnia) | tekst | ⚠️ typ różny | — |
| 31 | TOP Bestsellery | 413 | 6 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 32 | Format pliku | 158 | 4 | tekst 100% | Format | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 33 | Rodzaj zabezpieczenia | 90 | 2 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 34 | Język publikacji | 55 | 1 | tekst 100% | Język | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 35 | Materiał | 41 | 11 | tekst 100% | Material | poza Księgarnią | tekst | ⚠️ nie w Księgarni | — |
| 36 | Rodzaj | 41 | 7 | tekst 100% | Rodzaj | dokładne (Księgarnia) | tekst | ✅ typ zgodny | — |
| 37 | Nośnik | 37 | 3 | tekst 100% | Format | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 38 | Wymiary | 29 | 17 | tekst 66%, wymiar 34% | Wymiary | poza Księgarnią | wymiar | ⚠️ nie w Księgarni | — |
| 39 | TOP zapowiedzi | 28 | 1 | tekst 100% | — | — | — | ❌ brak w Ceneo | — |
| 40 | Waga towaru w gramach | 15 | 15 | int 93%, dec 7% | — | — | — | ❌ brak w Ceneo | — |
| 41 | eksportowane-do-empik | 15 | 1 | bool 100% | — | — | — | ❌ brak w Ceneo | — |
| 42 | Długość audio | 7 | 7 | tekst 100% | Format | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 43 | maksymalnie 1 produkt | 5 | 1 | int 100% | — | — | — | ❌ brak w Ceneo | — |
| 44 | Pojemność | 3 | 2 | int 100% | Pojemność | poza Księgarnią | int, liczba+jednostka, tekst | ⚠️ nie w Księgarni | — |
| 45 | Producent | 2 | 1 | tekst 100% | Wydawnictwo | synonim (Księgarnia) | tekst | ✅ typ zgodny | — |
| 46 | eksportowane-do-emag | 1 | 1 | bool 100% | — | — | — | ❌ brak w Ceneo | — |
| 47 | eksportowane-do-kaufland | 1 | 1 | bool 100% | — | — | — | ❌ brak w Ceneo | — |
| 48 | eksportowane-do-inpostvonhalsky | 1 | 1 | bool 100% | — | — | — | ❌ brak w Ceneo | — |
| 49 | Ilość stron | 1 | 1 | int 100% | Ilość stron | synonim (Księgarnia) | int | ✅ typ zgodny | — |

## Luka pokrycia — atrybuty Księgarni, których nie zasila żaden parametr CSV

| Atrybut Ceneo | Kategorii | Kluczowy w | Wzorcowe wartości |
|---|---:|---:|---|
| Kod | 69 | 61 | — |
| ISBN | 66 | 46 | — |
| Szkoła | 1 | 1 | Przedszkole |
| Producent | 2 | 1 | Ceneo – promocje |
| Ujęcie | 1 | 0 | Historia |
| Seria wydawnicza | 2 | 0 | Mały chłopiec |
| Forma | 5 | 0 | Album, atlas |
| Miejsca | 1 | 0 | Afryka |
| Typ | 1 | 0 | Amerykańskie |
| Model | 61 | 0 | — |
| Bohater | 23 | 0 | Hello Kitty |
| Język oryginału | 41 | 0 | Angielski |
| ISSN | 1 | 0 | — |
| Język publikacji | 1 | 0 | Afrykanerski |
| Podręczniki | 5 | 0 | A fondo, Abenteuer Deutsch, Accord, Affresco Italiano, Diełowaja riecz |
| Przeznaczenie | 8 | 0 | Dla nauczycieli, Dla przedszkolaków |
| Kolor | 1 | 0 | Białe |
| Na rok | 1 | 0 | Kalendarze archiwalne |
| Back to School Podręczniki | 1 | 0 | Tak |
| Przedmiot | 1 | 0 | Biologia |
| Kategorie | 7 | 0 | Aplikacje biurowe, Architektura, malarstwo, grafika, Atlasy, Bajki i baśnie, Biografie i wspomnienia, Dom i ogród |
| Wybrani autorzy | 57 | 0 | Stephen King |
| Nagrody i wyróźnienia | 1 | 0 | — |
| Podróżnicy | 1 | 0 | Beata Pawlikowska |
| Tematyka | 16 | 0 | ADHD, dysleksja, depresja, niepełnosprawność, Akwarystyka, Alkohole, Aplikacje biurowe, Architektura, Armada |
| Poziom zaawansowania | 7 | 0 | Angielski dla dzieci, Certyfikat CELI, Certyfikat DELE, Certyfikat DELF, Certyfikat Deutsch als Fremdsprache, Matura z rosyjskiego |
| Ćwiczenia | 7 | 0 | Tak, z kluczem |
| Lektor | 1 | 0 | Adam Ferency |
| Znani ludzie | 1 | 0 | Aktorzy i reżyserzy |
| Oprawa | 18 | 0 | — |
| Układ kalendarza | 1 | 0 | Dzienny |

## Szczegóły — 36 losowych wartości na parametr

### 1. `Rok wydania` — 115789 wystąpień, 22 unikalnych wartości

- **Profil typu:** `rok` 100%
- **Atrybut Ceneo:** `Rok wydania` (dokładne (Księgarnia)) — w 67 kategoriach, kluczowy w 9
- **Wzorcowe wartości Ceneo:** `1950`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** `2000`, `2004`, `2005`, `2006`, `2008`, `2009`, `2010`, `2012`, `2013`, `2014`, `2015`, `2016`, `2017`, `2018`, `2019`, `2020`, `2021`, `2022`, `2023`, `2024`, `2025`, `2026`
- **36 losowych wartości z CSV:** `2018`, `2013`, `2024`, `2025`, `2026`, `2013`, `2022`, `2023`, `2020`, `2025`, `2023`, `2024`, `2024`, `2026`, `2022`, `2025`, `2026`, `2021`, `2026`, `2026`, `2025`, `2026`, `2019`, `2026`, `2025`, `2023`, `2013`, `2020`, `2024`, `2024`, `2025`, `2023`, `2025`, `2025`, `2024`, `2025`

### 2. `Oprawa` — 115131 wystąpień, 17 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Okładka` (synonim (Księgarnia)) — w 48 kategoriach, kluczowy w 8
- **Wzorcowe wartości Ceneo:** `Miękka`
- **Przykładowe kategorie:** Księgarnia > Książki (288); Księgarnia > Książki > Albumy (426); Księgarnia > Książki > Beletrystyka > Fantastyka i fantasy (407)
- **Wszystkie unikalne wartości:** `Inna`, `Karton`, `Miekka`, `Miękka ze skrzydełkami`, `Plastikowa`, `Twarda`, `Twarda z obwolutą`, `broszurowa`, `broszurowa spirala`, `całokartonowa`, `etui kartonowe`, `laminowana`, `oprawa twarda`, `pudełko`, `skóropodobna`, `teczka`, `zintegrowana`
- **36 losowych wartości z CSV:** `broszurowa`, `Miekka`, `broszurowa`, `broszurowa`, `broszurowa`, `broszurowa`, `Twarda`, `Twarda`, `broszurowa`, `broszurowa`, `broszurowa`, `broszurowa`, `Twarda`, `Miekka`, `Twarda`, `broszurowa`, `Miekka`, `Twarda`, `Twarda`, `broszurowa`, `broszurowa`, `Miekka`, `Miekka`, `pudełko`, `broszurowa`, `broszurowa`, `broszurowa`, `broszurowa`, `Twarda`, `Miekka`, `broszurowa`, `broszurowa`, `broszurowa`, `broszurowa`, `broszurowa`, `broszurowa`

### 3. `Autorzy` — 114987 wystąpień, 359 unikalnych wartości

- **Profil typu:** `tekst` 100%, `tekst długi` 0%
- **Atrybut Ceneo:** `Autor` (synonim (Księgarnia)) — w 67 kategoriach, kluczowy w 64
- **Wzorcowe wartości Ceneo:** _brak (pusty Value)_
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki > E-Beletrystyka (3445)
- **Wszystkie unikalne wartości:** _(359 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `Georges Charpak, Dominique Saudinos`, `Aleksandra Muraszka`, `Praca zbiorowa`, `M. Bazhan`, `Emily Stone`, `Joan Garriga`, `Adam Wajrak`, `RAFAŁ BLUTH`, `Jozef Karika`, `Tomasz Gaj OP, Magdalena Pajkowska`, `I.M. Darks`, `Ewa Waligóra`, `Nathan Fairbairn, Michele Assarasakorn`, `Vladimir Nabokov`, `Praca zbiorowa`, `Jenny Dooley`, `Helen Chilton, Lynda Edwaeds`, `Javier Pina, Humberto Ramos, Jesus Saiz`, `Praca zbiorowa`, `Bogdan Kocańda OFMConv`, `Richard Israel i Vanda North`, `Michał Leśniewski`, `Tomasz Żaglewski`, `Fernanda Melchor`, `Fabien Vehlmann, Bruno Gazzotti`, `Mamare Touno`, `Anne-Kathrin Gomringer`, `Tomasz Kwaśniewski, Jacek Wasilewski`, `Madeline Miller`, `Monika Sznajderman`, `Dr Sami Timimi`, `Jan Van Rijckenborgh`, `Sarvepalli Radhakrishnan`, `Miłosz Horodyski`, `Jim Hohnberger`, `Kim Scott`

### 4. `Stan` — 114656 wystąpień, 1 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Stan` (poza Księgarnią) — w 62 kategoriach, kluczowy w 1
- **Wzorcowe wartości Ceneo:** `Niski`, `Nowe`
- **Przykładowe kategorie:** Moda > Odzież damska > Jeansy damskie (3588); Moda > Odzież damska > Spodenki damskie (1091); Moda > Odzież damska > Spodnie damskie (1378)
- **Wszystkie unikalne wartości:** `Nowy`
- **36 losowych wartości z CSV:** `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`, `Nowy`

### 5. `Data premiery` — 108385 wystąpień, 337 unikalnych wartości

- **Profil typu:** `data` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(337 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `2023-06-15`, `2026-06-01`, `2020-11-18`, `2024-04-12`, `2025-10-20`, `2012-09-27`, `2022-04-13`, `2025-09-11`, `2021-02-25`, `2016-09-01`, `2026-07-31`, `2026-03-28`, `2022-10-10`, `2025-03-21`, `2021-01-26`, `2021-02-19`, `2026-01-13`, `2024-12-16`, `2020-11-12`, `2020-09-01`, `2013-11-13`, `2025-11-30`, `2023-10-25`, `2021-10-27`, `2026-06-12`, `2025-11-12`, `2023-11-07`, `2023-09-13`, `2023-03-24`, `2020-12-30`, `2023-02-06`, `2024-02-14`, `2021-04-20`, `2019-08-20`, `2022-08-08`, `2024-02-28`

### 6. `Format` — 105270 wystąpień, 346 unikalnych wartości

- **Profil typu:** `wymiar` 100%
- **Atrybut Ceneo:** `Format` (dokładne (Księgarnia)) — w 69 kategoriach, kluczowy w 13
- **Wzorcowe wartości Ceneo:** `A5`, `CD audio`, `PDF`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** _(346 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `225x150 mm`, `235x167 mm`, `160x10 mm`, `248x182 mm`, `206x135 mm`, `168x240 mm`, `220x140 mm`, `235x152 mm`, `145x5 mm`, `25.0 x 25.0 cm`, `214x160 mm`, `198x269 mm`, `194x124 mm`, `242x175 mm`, `235x165 mm`, `205x145 mm`, `208x174 mm`, `142x211 mm`, `238x267 mm`, `140x209 mm`, `14.5x21.0cm`, `235x165 mm`, `238x165 mm`, `205x140 mm`, `148x229 mm`, `0.0 x 0.0 cm`, `146x206 mm`, `215x303 mm`, `470x670 mm`, `230x160x14 mm`, `17x23 cm`, `12.0 x 17.0 cm`, `210x148 mm`, `237x170 mm`, `210 x 300`, `144x209 mm`

### 7. `Strony` — 102425 wystąpień, 186 unikalnych wartości

- **Profil typu:** `int` 100%
- **Atrybut Ceneo:** `Ilość stron` (synonim (Księgarnia)) — w 68 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `10`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** _(186 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `520`, `244`, `64`, `67`, `400`, `148`, `8`, `264`, `320`, `364`, `380`, `320`, `150`, `176`, `400`, `380`, `192`, `288`, `32`, `64`, `64`, `405`, `424`, `208`, `289`, `238`, `352`, `210`, `192`, `160`, `670`, `44`, `448`, `198`, `420`, `376`

### 8. `Waga` — 90775 wystąpień, 245 unikalnych wartości

- **Profil typu:** `liczba+jednostka` 100%
- **Atrybut Ceneo:** `Waga` (poza Księgarnią) — w 599 kategoriach, kluczowy w 53
- **Wzorcowe wartości Ceneo:** `0,1 kg`, `0,150kg`, `0,155kg`, `0,5 kg`, `1 g`, `1 kg`, `1,1 kg`, `1,25kg`, `1,2Kg`, `1,5kg`, `1,6 kg`, `1,93 kg`
- **Przykładowe kategorie:** Biuro i firma > Artykuły BHP > Instrukcje i znaki BHP (2319); Biuro i firma > Artykuły BHP > Kaski i czapki ochronne (3497); Biuro i firma > Artykuły BHP > Obuwie robocze (1486)
- **Wszystkie unikalne wartości:** _(245 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `230 g`, `56 g`, `290 g`, `400 g`, `620 g`, `450 g`, `370 g`, `316 g`, `605 g`, `415 g`, `580 g`, `522 g`, `638 g`, `266 g`, `366 g`, `600 g`, `200 g`, `1140 g`, `325 g`, `294 g`, `372 g`, `195 g`, `220 g`, `794 g`, `550 g`, `0 g`, `296 g`, `105 g`, `54 g`, `844 g`, `422 g`, `374 g`, `668 g`, `290 g`, `200 g`, `56 g`

### 9. `Cena okładkowa` — 72819 wystąpień, 1 unikalnych wartości

- **Profil typu:** `bool` 100%
- **Atrybut Ceneo:** brak odpowiednika (najbliższe nazwy: Okładka)
- **Wszystkie unikalne wartości:** `NIE`
- **36 losowych wartości z CSV:** `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`, `NIE`

### 10. `Długość towaru w centymetrach` — 51197 wystąpień, 140 unikalnych wartości

- **Profil typu:** `dec` 83%, `int` 17%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(140 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `19.5`, `24`, `19.4`, `22.5`, `22.2`, `19.9`, `21.4`, `20.9`, `29.6`, `20.6`, `21`, `1.8`, `19.8`, `23.5`, `21.3`, `19.4`, `17.3`, `21.4`, `30`, `19.8`, `4.4`, `21.2`, `1.5`, `0.5`, `2`, `21.3`, `28`, `1.2`, `21.7`, `23.5`, `4.6`, `29`, `19.1`, `0.8`, `2`, `2`

### 11. `Wysokość towaru w centymetrach` — 51197 wystąpień, 103 unikalnych wartości

- **Profil typu:** `dec` 79%, `int` 21%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(103 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `21`, `21`, `2.6`, `0.5`, `19.5`, `20.5`, `21.1`, `21.5`, `21`, `1`, `4.7`, `6.1`, `19`, `1.7`, `1.9`, `23.5`, `1.1`, `0.8`, `3.1`, `1.3`, `1.8`, `1.3`, `1.4`, `2.5`, `3.2`, `2`, `2.9`, `3.3`, `35`, `2.2`, `0.9`, `1`, `3.5`, `3`, `4.8`, `1.5`

### 12. `Szerokość towaru w centymetrach` — 51197 wystąpień, 105 unikalnych wartości

- **Profil typu:** `dec` 80%, `int` 20%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(105 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `16.8`, `17.6`, `16.5`, `15.5`, `13.5`, `17.4`, `20.5`, `14.1`, `15.5`, `15.1`, `17`, `14.1`, `12.9`, `17.4`, `22.4`, `13.6`, `13.7`, `17`, `20.6`, `14.2`, `13.6`, `22`, `22.9`, `15.5`, `24`, `13.5`, `17`, `25.5`, `14.5`, `17`, `12.8`, `15.4`, `21.1`, `15.1`, `20.6`, `21`

### 13. `Waga gabarytowa w gramach` — 51173 wystąpień, 379 unikalnych wartości

- **Profil typu:** `dec` 95%, `int` 5%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(379 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `480.36`, `432.67`, `112.75`, `258.5`, `30.46`, `81`, `89.38`, `424.08`, `125.13`, `66.15`, `348.04`, `60.13`, `86.13`, `1138.67`, `80.59`, `17.42`, `343`, `233.81`, `131.25`, `315.01`, `50.23`, `144.05`, `138.81`, `138.78`, `31.08`, `290.95`, `135.05`, `119.25`, `145.2`, `98.97`, `124.25`, `394.84`, `120.7`, `58`, `168.1`, `535.67`

### 14. `Elementy` — 44303 wystąpień, 197 unikalnych wartości

- **Profil typu:** `int` 100%
- **Atrybut Ceneo:** `Ilość stron` (synonim (Księgarnia)) — w 68 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `10`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** _(197 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `448`, `320`, `40`, `658`, `112`, `160`, `269`, `71`, `408`, `296`, `400`, `104`, `320`, `356`, `144`, `368`, `149`, `456`, `48`, `414`, `336`, `542`, `268`, `40`, `216`, `272`, `320`, `480`, `292`, `250`, `388`, `168`, `520`, `116`, `104`, `322`

### 15. `Język` — 42954 wystąpień, 6 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Język` (dokładne (Księgarnia)) — w 8 kategoriach, kluczowy w 1
- **Wzorcowe wartości Ceneo:** `Język angielski`, `Język arabski`, `Po angielsku`, `Polski`, `Włoski`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki > E-nauka języków obcych (3447); Księgarnia > Książki > Literatura obcojęzyczna (724)
- **Wszystkie unikalne wartości:** `angielski`, `francuski`, `hiszpański`, `polski`, `rosyjski`, `włoski`
- **36 losowych wartości z CSV:** `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `włoski`, `polski`, `polski`, `polski`

### 16. `Kampania` — 24056 wystąpień, 98 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(98 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `young-adult-ogolne`, `wielkanoc-2024`, `strefaznakslonecznedni`, `strefaznakdziendziecka`, `young-adult-ogolne`, `komunia-sw`, `young-adult-remigiusz-mroz`, `wielkanoc-2024-ksiazki`, `dzien-kobiet-mezczyzn-2024-do-149-PLN`, `walentynki-2023-do-49-PLN`, `strefaznakkryminal`, `walentynki-2023-dla-niej`, `dzien-kobiet-mezczyzn-2024-do-199-PLN`, `wielkanoc-2024-ksiazki`, `dzien-kobiet-mezczyzn-2024-dla-niej`, `dzien-kobiet-mezczyzn-2024-do-149-PLN`, `wielkanoc-2024`, `dzien-kobiet-mezczyzn-2024-do-149-PLN`, `podrecznikiedycja2024`, `yrodniczenauki_matematyczno_prz`, `young-adult-ogolne`, `ZnakFerie`, `wielkanoc-2024`, `dzien-kobiet-mezczyzn-2024-dla-niej`, `walentynki-2023-dla-niej`, `young-adult-ogolne`, `dzien-kobiet-mezczyzn-2024-dla-niego`, `dzien-kobiet-mezczyzn-2024-do-99-PLN`, `dzien-kobiet-mezczyzn-2024-dla-niej`, `dzien-kobiet-mezczyzn-2024-do-49-PLN`, `young-adult-remigiusz-mroz`, `walentynki-2023-do-149-PLN`, `wielkanoc-2024`, `Znakgrudziennowosci`, `walentynki-2023-do-49-PLN`, `dzien-kobiet-mezczyzn-2024-dla-niej`

### 17. `Seria` — 19831 wystąpień, 321 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Seria` (dokładne (Księgarnia)) — w 59 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** _brak (pusty Value)_
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki > E-Beletrystyka (3445); Księgarnia > E-booki > E-biografie i dzienniki (3440)
- **Wszystkie unikalne wartości:** _(321 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `Mroczna strona`, `BIBLIOTEKA EUROPEJSKA`, `Miłość to wojna`, `SULINA`, `Uniwersum DC`, `Akademicka. Podręczniki Obowiązkowe`, `Zapiski zielarki`, `Opowieść Panny Młodej`, `Na osi czasu`, `Norweski dziennik`, `AKADEMIA DOBRA I ZŁA`, `Charlotte Winters`, `Monografie`, `DragonJesien`, `MATEMATYKA Z PLUSEM`, `Otwórz i odkryj`, `REPORTAŻ`, `Mój pierwszy komiks 5+`, `BIBLIOTEKA OSHO`, `TO O CZYM DOROŚLI CI NIE MÓWIĄ`, `APLIKACJE PRAWNICZE`, `Usagi Yojimbo Saga`, `KOLEKCJA INDYWIDUALNEGO ROZWOJU`, `Klatka dla ptaków`, `Black Science`, `The Frontiers Saga`, `DAIMONION`, `TYPY BRONI I UZBROJENIA`, `Karol Czerski`, `MATYLDA`, `NIE GRYZIE!`, `BIURO DETEKTYWISTYCZNE LASSEGO I MAI`, `Kolorowy potwór`, `Log Horizon - West Wind Brigade`, `Historia`, `Ex Oriente`

### 18. `Kampania-Walentynki` — 16687 wystąpień, 3 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-strefa-rekomendacji-4`
- **36 losowych wartości z CSV:** `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niego`, `walentynki-dla-niego`, `walentynki-strefa-rekomendacji-4`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niej`, `walentynki-dla-niej`, `walentynki-dla-niego`, `walentynki-dla-niego`

### 19. `Język nauczany` — 7854 wystąpień, 16 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Język` (synonim (Księgarnia)) — w 8 kategoriach, kluczowy w 1
- **Wzorcowe wartości Ceneo:** `Język angielski`, `Język arabski`, `Po angielsku`, `Polski`, `Włoski`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki > E-nauka języków obcych (3447); Księgarnia > Książki > Literatura obcojęzyczna (724)
- **Wszystkie unikalne wartości:** `angielski`, `duński`, `francuski`, `hebrajski`, `hiszpański`, `japoński`, `koreański`, `niderlandzki`, `niemiecki`, `norweski`, `polski`, `portugalski`, `pozostałe`, `rosyjski`, `włoski`, `łaciński`
- **36 losowych wartości z CSV:** `polski`, `hiszpański`, `francuski`, `francuski`, `angielski`, `angielski`, `niemiecki`, `angielski`, `angielski`, `hiszpański`, `francuski`, `angielski`, `angielski`, `hiszpański`, `niemiecki`, `francuski`, `hiszpański`, `niemiecki`, `niemiecki`, `angielski`, `niemiecki`, `angielski`, `angielski`, `angielski`, `angielski`, `duński`, `angielski`, `angielski`, `angielski`, `angielski`, `angielski`, `niemiecki`, `angielski`, `angielski`, `hiszpański`, `angielski`

### 20. `Klasa` — 7010 wystąpień, 53 unikalnych wartości

- **Profil typu:** `przedział wieku` 66%, `tekst` 32%, `int` 3%
- **Atrybut Ceneo:** `Klasa` (dokładne (Księgarnia)) — w 1 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `0`
- **Przykładowe kategorie:** Księgarnia > Książki > Podręczniki szkolne (412)
- **Wszystkie unikalne wartości:** _(53 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `zsz`, `zsz`, `ZSZ 1-3`, `LO 2`, `16+`, `15+`, `3+`, `4`, `16+`, `4-6`, `6+`, `3+`, `SP 3`, `4+`, `zsz`, `18+`, `zsz`, `8+`, `18+`, `8+`, `5+`, `18+`, `18+`, `18+`, `4+`, `0-3`, `3+`, `liceum/technikum`, `3+`, `8+`, `3+`, `LO 2`, `18m+`, `12+`, `3+`, `4+`

### 21. `Wyprzedaz` — 2771 wystąpień, 30 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(30 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `poradniki`, `albumy`, `popularnonaukowe`, `podreczniki`, `ksiazki-dla-dzieci`, `podreczniki`, `nauka-jezykow-obcych`, `podreczniki`, `poradniki`, `podreczniki`, `podreczniki`, `romans`, `podreczniki`, `zdrowie-i-uroda`, `podreczniki`, `podreczniki`, `podreczniki`, `nauka-jezykow-obcych`, `podreczniki`, `ksiazki-dla-dzieci`, `podreczniki`, `literatura-piekna`, `podreczniki`, `popularnonaukowe`, `ksiazki-dla-dzieci`, `ksiazki-dla-dzieci`, `fantastyka`, `podreczniki`, `podreczniki`, `literatura-faktu`, `nauka-jezykow-obcych`, `horror`, `podreczniki`, `podreczniki`, `komiksy`, `popularnonaukowe`

### 22. `Prezenty 2023` — 2608 wystąpień, 14 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `dziecko-gry-planszowe`, `dziecko-ksiazki`, `dziecko-lego`, `dziecko-nastolatek`, `dziecko-przedszkolak`, `dziecko-zabawki`, `on-hobby`, `on-ksiazki`, `on-lifestyle`, `on-zabawa`, `ona-hobby`, `ona-ksiazki`, `ona-lifestyle`, `ona-zabawa`
- **36 losowych wartości z CSV:** `dziecko-nastolatek`, `ona-lifestyle`, `ona-ksiazki`, `ona-ksiazki`, `on-zabawa`, `ona-ksiazki`, `dziecko-nastolatek`, `on-lifestyle`, `ona-ksiazki`, `dziecko-nastolatek`, `on-hobby`, `dziecko-ksiazki`, `ona-ksiazki`, `on-ksiazki`, `ona-ksiazki`, `ona-lifestyle`, `ona-ksiazki`, `dziecko-nastolatek`, `ona-ksiazki`, `on-hobby`, `on-hobby`, `on-ksiazki`, `on-ksiazki`, `ona-lifestyle`, `ona-ksiazki`, `ona-lifestyle`, `dziecko-ksiazki`, `on-ksiazki`, `ona-hobby`, `ona-ksiazki`, `dziecko-nastolatek`, `ona-ksiazki`, `dziecko-nastolatek`, `ona-ksiazki`, `on-ksiazki`, `ona-ksiazki`

### 23. `Redakcja` — 2581 wystąpień, 330 unikalnych wartości

- **Profil typu:** `tekst` 98%, `tekst długi` 2%
- **Atrybut Ceneo:** `Autor` (synonim (Księgarnia)) — w 67 kategoriach, kluczowy w 64
- **Wzorcowe wartości Ceneo:** _brak (pusty Value)_
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki > E-Beletrystyka (3445)
- **Wszystkie unikalne wartości:** _(330 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `Wallas Tadeusz, Fiedler Radosław`, `Jałowiec Tomasz, Wincewicz-Bosy Marta`, `Kurasz Irena`, `Timms John`, `Difin`, `Plamowski Maciej`, `Courtine Jean-Jacques`, `Gothner Emma`, `Barks Carl`, `Polański Przemysław`, `Ćwik Anna`, `Mawart`, `Małgorzata Poździk / d2d.pl`, `Klonowska J.`, `Jogałła Elżbieta`, `Rosiński Grzegorz`, `Difin`, `Kucharska Ludmiła`, `Jogałła Elżbieta`, `Panek Tomasz`, `Jannasz Marek`, `Rogowska Katarzyna`, `Difin`, `Smoleń Paweł`, `kboom`, `WDS Sandomierz`, `Jogałła Elżbieta`, `Wróbel Anna, Jędrzejowska Karina, Rewizorski Marek`, `Roba Jean`, `red. Dominik M. Piotrowski, Liliana Lewandowska`, `Hardej Iwona`, `Jegier Aneta`, `Dudek Grzegorz, Oleś Mariusz, Wszołek Przemysław`, `Bowles Paula`, `Juszczyk Sławomir`, `Kawka Magdalena`

### 24. `Grupa wiekowa` — 2339 wystąpień, 84 unikalnych wartości

- **Profil typu:** `przedział wieku` 94%, `tekst` 6%
- **Atrybut Ceneo:** `Wiek` (synonim (Księgarnia)) — w 2 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `3-latki`, `Dla malucha (0-3 lata)`
- **Przykładowe kategorie:** Księgarnia > Książki > Beletrystyka > Literatura dla dzieci i młodzieży (403); Księgarnia > Książki > Podręczniki szkolne (412)
- **Wszystkie unikalne wartości:** _(84 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `18+`, `8 - 12`, `12+`, `6 - 8`, `6 - 10`, `14+`, `14+`, `4 - 5`, `14+`, `3 - 5`, `6 lat +`, `16+`, `12+`, `3 - 5`, `5+`, `36- m`, `12+`, `16+`, `12+`, `od 3 lat`, `18+`, `6- m`, `10+`, `6+`, `9 - 12`, `10+`, `3+`, `6+`, `14+`, `6 - 12`, `6 - 10`, `4 - 10`, `0 - 2`, `12+`, `6 - 9`, `12+`

### 25. `Minimalny wiek` — 2246 wystąpień, 21 unikalnych wartości

- **Profil typu:** `przedział wieku` 94%, `tekst` 6%
- **Atrybut Ceneo:** `Wiek` (synonim (Księgarnia)) — w 2 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `3-latki`, `Dla malucha (0-3 lata)`
- **Przykładowe kategorie:** Księgarnia > Książki > Beletrystyka > Literatura dla dzieci i młodzieży (403); Księgarnia > Książki > Podręczniki szkolne (412)
- **Wszystkie unikalne wartości:** `0 mies. +`, `1+`, `10 lat +`, `11 lat +`, `12 lat +`, `12 mies. +`, `13 lat +`, `14 lat +`, `15 lat +`, `16 lat +`, `16 mies. +`, `18 lat +`, `2 lata +`, `3 lata +`, `4 lata +`, `5 lat +`, `6 lat +`, `6 mies. +`, `7 lat +`, `8 lat +`, `9 lat +`
- **36 losowych wartości z CSV:** `9 lat +`, `14 lat +`, `15 lat +`, `8 lat +`, `18 lat +`, `14 lat +`, `14 lat +`, `5 lat +`, `14 lat +`, `3 lata +`, `7 lat +`, `14 lat +`, `3 lata +`, `6 lat +`, `14 lat +`, `3 lata +`, `3 lata +`, `0 mies. +`, `15 lat +`, `12 lat +`, `16 lat +`, `14 lat +`, `0 mies. +`, `0 mies. +`, `14 lat +`, `12 mies. +`, `18 lat +`, `6 lat +`, `12 lat +`, `9 lat +`, `9 lat +`, `3 lata +`, `15 lat +`, `14 lat +`, `14 lat +`, `3 lata +`

### 26. `Nowosci` — 1669 wystąpień, 12 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `beletrystka-literatura-piekna`, `dla-dzieci`, `dla-mlodziezy`, `fantastyka`, `horrory-thrillery`, `najnowsze`, `ostatni-miesiac`, `ostatni-tydzien`, `podreczniki`, `poradniki`, `sensacja-i-kryminal`, `top-30`
- **36 losowych wartości z CSV:** `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `dla-dzieci`, `ostatni-tydzien`, `poradniki`, `ostatni-miesiac`, `ostatni-miesiac`, `horrory-thrillery`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `sensacja-i-kryminal`, `fantastyka`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-tydzien`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-tydzien`, `ostatni-miesiac`, `horrory-thrillery`, `ostatni-miesiac`, `ostatni-miesiac`, `sensacja-i-kryminal`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `ostatni-miesiac`, `poradniki`

### 27. `Nr dopuszczenia` — 984 wystąpień, 362 unikalnych wartości

- **Profil typu:** `tekst` 99%, `int` 1%, `rok` 0%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** _(362 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `1159/1/2022`, `950/1/2019`, `903/4/2020/z1`, `781/2/2018`, `Reforma 2012`, `1140/1/2026`, `1165/2/2024`, `AZ-3-01/18 AZ-4-01/18`, `AZ-1-01/18`, `1140/3/2023`, `1136/2022`, `1015/3/2024/z1`, `1189/2023`, `875/2/2018`, `1002/2/2020`, `588/1/2012`, `AZ-12-01/18-RA-15/21`, `1068/1/2019`, `855/2/2017`, `1014/4/2025/z1`, `1219/1/2024`, `1089/3/2022`, `1114/1/2022`, `833/2/2018`, `1142/1/2022, 1142/2/2022`, `899/3/2019`, `AZ-1-01/18`, `9/2017`, `1097/1/2020`, `976/1/2019`, `1026/4/2021`, `10-14/N5142/XIV`, `862/2/2019`, `792/3/2019`, `1147/2/2023`, `781/3/2019`

### 28. `Liczba elementów` — 622 wystąpień, 37 unikalnych wartości

- **Profil typu:** `dec` 94%, `int` 6%, `rok` 0%, `tekst` 0%
- **Atrybut Ceneo:** `Ilość stron` (synonim (Księgarnia)) — w 68 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `10`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** _(37 różnych — poniżej losowa próbka)_
- **36 losowych wartości z CSV:** `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `200`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `20.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `6.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `130.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `1`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`, `10.0000000000000000`

### 29. `Opakowanie` — 587 wystąpień, 12 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Opakowanie` (poza Księgarnią) — w 157 kategoriach, kluczowy w 4
- **Wzorcowe wartości Ceneo:** `20 szt.`, `30 szt.`, `Ampułki`, `Butelka`, `Butelka plastikowa`, `Butelka z atomizerem`, `Karton`, `Karton ozdobny`, `Kartonik`, `Oryginalne`, `Pojedyncze`, `Pudełko`
- **Przykładowe kategorie:** Budowa i remont > Dachy i rynny > Pokrycia dachowe (1708); Budowa i remont > Elektryka i akcesoria elektryczne > Przewody i kable (3500); Budowa i remont > Materiały budowlane > Cement (1763)
- **Wszystkie unikalne wartości:** `blister`, `broszurowa`, `broszurowa spirala`, `etui`, `etui kartonowe`, `folia`, `karton`, `koperta`, `laminowana`, `pudełko`, `teczka`, `twarda`
- **36 losowych wartości z CSV:** `pudełko`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `etui kartonowe`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `folia`, `pudełko`, `pudełko`, `folia`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `etui`, `pudełko`, `pudełko`, `etui`, `pudełko`, `pudełko`, `pudełko`, `pudełko`, `blister`, `pudełko`, `pudełko`, `pudełko`, `pudełko`

### 30. `Liczba tomów` — 573 wystąpień, 20 unikalnych wartości

- **Profil typu:** `int` 100%
- **Atrybut Ceneo:** `Zestaw` (synonim (Księgarnia)) — w 7 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `Sama książka`
- **Przykładowe kategorie:** Księgarnia > Książki > Nauka języków obcych > Język angielski (430); Księgarnia > Książki > Nauka języków obcych > Język francuski (432); Księgarnia > Książki > Nauka języków obcych > Język hiszpański (433)
- **Wszystkie unikalne wartości:** `1`, `10`, `11`, `12`, `14`, `15`, `17`, `18`, `2`, `22`, `240`, `3`, `4`, `42`, `5`, `6`, `7`, `72`, `8`, `9`
- **36 losowych wartości z CSV:** `2`, `2`, `4`, `3`, `1`, `1`, `1`, `1`, `9`, `1`, `2`, `2`, `2`, `1`, `1`, `15`, `1`, `2`, `1`, `1`, `1`, `6`, `5`, `15`, `3`, `5`, `3`, `2`, `1`, `2`, `1`, `14`, `1`, `1`, `1`, `2`

### 31. `TOP Bestsellery` — 413 wystąpień, 6 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `Top 100`, `Top 200 ksiazki`, `Top 200 lalki`, `Top 200 zabawki`, `Top 30 Gry planszowe`, `Top 30 Lego`
- **36 losowych wartości z CSV:** `Top 200 zabawki`, `Top 100`, `Top 30 Gry planszowe`, `Top 200 zabawki`, `Top 100`, `Top 200 zabawki`, `Top 30 Lego`, `Top 200 ksiazki`, `Top 200 ksiazki`, `Top 100`, `Top 100`, `Top 200 ksiazki`, `Top 100`, `Top 200 ksiazki`, `Top 100`, `Top 200 ksiazki`, `Top 200 ksiazki`, `Top 200 zabawki`, `Top 200 zabawki`, `Top 200 ksiazki`, `Top 200 zabawki`, `Top 200 zabawki`, `Top 100`, `Top 200 zabawki`, `Top 200 zabawki`, `Top 30 Lego`, `Top 200 ksiazki`, `Top 200 zabawki`, `Top 200 ksiazki`, `Top 200 zabawki`, `Top 200 lalki`, `Top 200 ksiazki`, `Top 30 Gry planszowe`, `Top 100`, `Top 100`, `Top 200 ksiazki`

### 32. `Format pliku` — 158 wystąpień, 4 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Format` (synonim (Księgarnia)) — w 69 kategoriach, kluczowy w 13
- **Wzorcowe wartości Ceneo:** `A5`, `CD audio`, `PDF`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** `epub`, `mobi`, `mp3`, `pdf`
- **36 losowych wartości z CSV:** `mobi`, `pdf`, `mobi`, `epub`, `mobi`, `epub`, `epub`, `pdf`, `mobi`, `mobi`, `pdf`, `epub`, `pdf`, `epub`, `mobi`, `mobi`, `pdf`, `pdf`, `epub`, `epub`, `mobi`, `mobi`, `epub`, `pdf`, `mobi`, `pdf`, `pdf`, `mp3`, `mp3`, `pdf`, `epub`, `epub`, `epub`, `mobi`, `epub`, `epub`

### 33. `Rodzaj zabezpieczenia` — 90 wystąpień, 2 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `DL-ebwm`, `DL-wm`
- **36 losowych wartości z CSV:** `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-wm`, `DL-ebwm`, `DL-wm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`, `DL-ebwm`

### 34. `Język publikacji` — 55 wystąpień, 1 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Język` (synonim (Księgarnia)) — w 8 kategoriach, kluczowy w 1
- **Wzorcowe wartości Ceneo:** `Język angielski`, `Język arabski`, `Po angielsku`, `Polski`, `Włoski`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki > E-nauka języków obcych (3447); Księgarnia > Książki > Literatura obcojęzyczna (724)
- **Wszystkie unikalne wartości:** `polski`
- **36 losowych wartości z CSV:** `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`, `polski`

### 35. `Materiał` — 41 wystąpień, 11 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Material` (poza Księgarnią) — w 1 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `Metal`
- **Przykładowe kategorie:** Budowa i remont > Ogrzewanie > Kominki i akcesoria > Akcesoria kominkowe > Kosze na drewno (4474)
- **Wszystkie unikalne wartości:** `Bawełna`, `Ceramiczne`, `Karton`, `Papier / Makulatura`, `Silikon`, `Tkanina`, `Tworzywo sztuczne`, `bawełna, poliester`, `inny`, `metal`, `plastik`
- **36 losowych wartości z CSV:** `Tworzywo sztuczne`, `Papier / Makulatura`, `metal`, `Tworzywo sztuczne`, `bawełna, poliester`, `Tworzywo sztuczne`, `Papier / Makulatura`, `Papier / Makulatura`, `Tworzywo sztuczne`, `plastik`, `plastik`, `Tworzywo sztuczne`, `Tkanina`, `plastik`, `Papier / Makulatura`, `Karton`, `Tworzywo sztuczne`, `Karton`, `Ceramiczne`, `Papier / Makulatura`, `metal`, `plastik`, `plastik`, `Karton`, `Tworzywo sztuczne`, `metal`, `Tworzywo sztuczne`, `metal`, `inny`, `Tworzywo sztuczne`, `Papier / Makulatura`, `Tworzywo sztuczne`, `Bawełna`, `Papier / Makulatura`, `Papier / Makulatura`, `Silikon`

### 36. `Rodzaj` — 41 wystąpień, 7 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Rodzaj` (dokładne (Księgarnia)) — w 11 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `Atlasy`, `Gramatyka`, `Humor, satyra`, `Kalendarze biurowe`, `Ćwiczenia`
- **Przykładowe kategorie:** Księgarnia > Książki > Komiksy (410); Księgarnia > Książki > Literatura podróżnicza i przewodniki (399); Księgarnia > Książki > Nauka języków obcych > Język angielski (430)
- **Wszystkie unikalne wartości:** `biurkowy`, `dla nauczycieli`, `dziurkacz`, `klej`, `książkowy`, `organizer`, `ścienny`
- **36 losowych wartości z CSV:** `dla nauczycieli`, `organizer`, `dla nauczycieli`, `książkowy`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `książkowy`, `książkowy`, `dla nauczycieli`, `dla nauczycieli`, `klej`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `książkowy`, `książkowy`, `biurkowy`, `organizer`, `ścienny`, `ścienny`, `dziurkacz`, `biurkowy`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `książkowy`, `organizer`, `klej`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`, `dla nauczycieli`

### 37. `Nośnik` — 37 wystąpień, 3 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Format` (synonim (Księgarnia)) — w 69 kategoriach, kluczowy w 13
- **Wzorcowe wartości Ceneo:** `A5`, `CD audio`, `PDF`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** `CD`, `DVD`, `winyl`
- **36 losowych wartości z CSV:** `CD`, `DVD`, `CD`, `CD`, `DVD`, `CD`, `CD`, `CD`, `DVD`, `CD`, `CD`, `CD`, `CD`, `CD`, `CD`, `DVD`, `winyl`, `CD`, `CD`, `CD`, `CD`, `DVD`, `CD`, `CD`, `DVD`, `CD`, `DVD`, `DVD`, `CD`, `CD`, `CD`, `CD`, `CD`, `CD`, `CD`, `CD`

### 38. `Wymiary` — 29 wystąpień, 17 unikalnych wartości

- **Profil typu:** `tekst` 66%, `wymiar` 34%
- **Atrybut Ceneo:** `Wymiary` (poza Księgarnią) — w 34 kategoriach, kluczowy w 6
- **Wzorcowe wartości Ceneo:** `1,5x2m`, `100x100 cm`, `100x150 cm`, `100x40x46`, `179 x 197`, `21x21cm`, `30,5x34,5cm`, `64,5×42`, `7 x 3,6 cm`
- **Przykładowe kategorie:** Budowa i remont > Drzwi, okna i schody > Okna i parapety > Okna i drzwi balkonowe (1705); Budowa i remont > Drzwi, okna i schody > Okna i parapety > Pozostałe okna (1706); Budowa i remont > Elektryka i akcesoria elektryczne > Domofony i videodomofony > Unifony (796)
- **Wszystkie unikalne wartości:** `165 x 235 mm`, `17x17x15`, `17x34x15`, `180mm x 180mm x 8mm`, `230 x 270 x 22`, `230mm x 230mm x 10`, `230x230x10`, `240mm x 175mm x 20mm`, `253mm x 285mm x 56mm`, `25x27x42`, `270mm x 230mm x 10mm`, `310mm x 340mm x 310mm`, `35 cm x 35 cm x 20.5 cm`, `51x24x20`, `8x18x18`, `Wysokość: 8 cm`, `Średnica: 8 cm`
- **36 losowych wartości z CSV:** `180mm x 180mm x 8mm`, `8x18x18`, `Średnica: 8 cm`, `Średnica: 8 cm`, `230 x 270 x 22`, `270mm x 230mm x 10mm`, `17x17x15`, `25x27x42`, `270mm x 230mm x 10mm`, `51x24x20`, `Wysokość: 8 cm`, `270mm x 230mm x 10mm`, `Wysokość: 8 cm`, `230x230x10`, `Średnica: 8 cm`, `165 x 235 mm`, `Średnica: 8 cm`, `Wysokość: 8 cm`, `270mm x 230mm x 10mm`, `25x27x42`, `230mm x 230mm x 10`, `25x27x42`, `310mm x 340mm x 310mm`, `253mm x 285mm x 56mm`, `17x34x15`, `253mm x 285mm x 56mm`, `Wysokość: 8 cm`, `35 cm x 35 cm x 20.5 cm`, `240mm x 175mm x 20mm`

### 39. `TOP zapowiedzi` — 28 wystąpień, 1 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `Bestseller`
- **36 losowych wartości z CSV:** `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`, `Bestseller`

### 40. `Waga towaru w gramach` — 15 wystąpień, 15 unikalnych wartości

- **Profil typu:** `int` 93%, `dec` 7%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `0.5`, `1095`, `136`, `1405`, `174`, `214`, `222`, `282`, `290`, `378`, `472`, `500`, `5000`, `552`, `796`
- **36 losowych wartości z CSV:** `214`, `1405`, `796`, `1095`, `0.5`, `222`, `174`, `282`, `5000`, `500`, `472`, `290`, `136`, `552`, `378`

### 41. `eksportowane-do-empik` — 15 wystąpień, 1 unikalnych wartości

- **Profil typu:** `bool` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `nie`
- **36 losowych wartości z CSV:** `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`, `nie`

### 42. `Długość audio` — 7 wystąpień, 7 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Format` (synonim (Księgarnia)) — w 69 kategoriach, kluczowy w 13
- **Wzorcowe wartości Ceneo:** `A5`, `CD audio`, `PDF`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** `10:11:00`, `11:13:00`, `12:28:00`, `2:00:00`, `33:10:47`, `7:16:00`, `9:15:00`
- **36 losowych wartości z CSV:** `2:00:00`, `7:16:00`, `33:10:47`, `12:28:00`, `9:15:00`, `10:11:00`, `11:13:00`

### 43. `maksymalnie 1 produkt` — 5 wystąpień, 1 unikalnych wartości

- **Profil typu:** `int` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `1`
- **36 losowych wartości z CSV:** `1`, `1`, `1`, `1`, `1`

### 44. `Pojemność` — 3 wystąpień, 2 unikalnych wartości

- **Profil typu:** `int` 100%
- **Atrybut Ceneo:** `Pojemność` (poza Księgarnią) — w 339 kategoriach, kluczowy w 234
- **Wzorcowe wartości Ceneo:** `0,1 L`, `0,1 l`, `0,18l`, `0,1L`, `0,1l`, `0,35 L`, `0,4 l`, `0,5 l`, `0,5l`, `0,6 l`, `0,65L`, `0.125GB`
- **Przykładowe kategorie:** Biuro i firma > Gastronomia i hotelarstwo > Urządzenia gastronomiczne > Urządzenia chłodnicze (2922); Biuro i firma > Gastronomia i hotelarstwo > Urządzenia gastronomiczne > Urządzenia do gotowania i pieczenia (2923); Biuro i firma > Rolnictwo > Hodowla zwierząt (2905)
- **Wszystkie unikalne wartości:** `5000`, `910`
- **36 losowych wartości z CSV:** `910`, `5000`, `5000`

### 45. `Producent` — 2 wystąpień, 1 unikalnych wartości

- **Profil typu:** `tekst` 100%
- **Atrybut Ceneo:** `Wydawnictwo` (synonim (Księgarnia)) — w 67 kategoriach, kluczowy w 8
- **Wzorcowe wartości Ceneo:** `Znak`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki > E-Beletrystyka (3445)
- **Wszystkie unikalne wartości:** `Matfel`
- **36 losowych wartości z CSV:** `Matfel`, `Matfel`

### 46. `eksportowane-do-emag` — 1 wystąpień, 1 unikalnych wartości

- **Profil typu:** `bool` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `NIE`
- **36 losowych wartości z CSV:** `NIE`

### 47. `eksportowane-do-kaufland` — 1 wystąpień, 1 unikalnych wartości

- **Profil typu:** `bool` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `nie`
- **36 losowych wartości z CSV:** `nie`

### 48. `eksportowane-do-inpostvonhalsky` — 1 wystąpień, 1 unikalnych wartości

- **Profil typu:** `bool` 100%
- **Atrybut Ceneo:** brak odpowiednika
- **Wszystkie unikalne wartości:** `nie`
- **36 losowych wartości z CSV:** `nie`

### 49. `Ilość stron` — 1 wystąpień, 1 unikalnych wartości

- **Profil typu:** `int` 100%
- **Atrybut Ceneo:** `Ilość stron` (synonim (Księgarnia)) — w 68 kategoriach, kluczowy w 0
- **Wzorcowe wartości Ceneo:** `10`
- **Przykładowe kategorie:** Księgarnia > Audiobooki (3453); Księgarnia > E-booki (2696); Księgarnia > E-booki (2696)
- **Wszystkie unikalne wartości:** `150`
- **36 losowych wartości z CSV:** `150`


## Atrybuty Ceneo w gałęzi Księgarnia — pełna lista

| Atrybut | Kategorii | Kluczowy w | Zasilany z CSV | Wzorcowe wartości |
|---|---:|---:|---|---|
| Autor | 67 | 64 | Autorzy, Redakcja | — |
| Back to School Podręczniki | 1 | 0 | — | Tak |
| Bohater | 23 | 0 | — | Hello Kitty |
| Forma | 5 | 0 | — | Album, atlas |
| Format | 69 | 13 | Format, Format pliku, Nośnik, Długość audio | A5, CD audio, PDF |
| ISBN | 66 | 46 | — | — |
| ISSN | 1 | 0 | — | — |
| Ilość stron | 68 | 0 | Strony, Elementy, Liczba elementów, Ilość stron | 10 |
| Język | 8 | 1 | Język, Język nauczany, Język publikacji | Język angielski, Język arabski, Po angielsku, Polski, Włoski |
| Język oryginału | 41 | 0 | — | Angielski |
| Język publikacji | 1 | 0 | — | Afrykanerski |
| Kategorie | 7 | 0 | — | Aplikacje biurowe, Architektura, malarstwo, grafika, Atlasy, Bajki i baśnie, Biografie i wspomnienia, Dom i ogród, Fantastyka i fantasy |
| Klasa | 1 | 0 | Klasa | 0 |
| Kod | 69 | 61 | — | — |
| Kolor | 1 | 0 | — | Białe |
| Lektor | 1 | 0 | — | Adam Ferency |
| Miejsca | 1 | 0 | — | Afryka |
| Model | 61 | 0 | — | — |
| Na rok | 1 | 0 | — | Kalendarze archiwalne |
| Nagrody i wyróźnienia | 1 | 0 | — | — |
| Okładka | 48 | 8 | Oprawa | Miękka |
| Oprawa | 18 | 0 | — | — |
| Podróżnicy | 1 | 0 | — | Beata Pawlikowska |
| Podręczniki | 5 | 0 | — | A fondo, Abenteuer Deutsch, Accord, Affresco Italiano, Diełowaja riecz |
| Poziom zaawansowania | 7 | 0 | — | Angielski dla dzieci, Certyfikat CELI, Certyfikat DELE, Certyfikat DELF, Certyfikat Deutsch als Fremdsprache, Matura z rosyjskiego, Poziom podstawowy |
| Producent | 2 | 1 | — | Ceneo – promocje |
| Przedmiot | 1 | 0 | — | Biologia |
| Przeznaczenie | 8 | 0 | — | Dla nauczycieli, Dla przedszkolaków |
| Rodzaj | 11 | 0 | Rodzaj | Atlasy, Gramatyka, Humor, satyra, Kalendarze biurowe, Ćwiczenia |
| Rok wydania | 67 | 9 | Rok wydania | 1950 |
| Seria | 59 | 0 | Seria | — |
| Seria wydawnicza | 2 | 0 | — | Mały chłopiec |
| Szkoła | 1 | 1 | — | Przedszkole |
| Tematyka | 16 | 0 | — | ADHD, dysleksja, depresja, niepełnosprawność, Akwarystyka, Alkohole, Aplikacje biurowe, Architektura, Armada, Astrologia i horoskopy, Atlasy przyrody |
| Typ | 1 | 0 | — | Amerykańskie |
| Ujęcie | 1 | 0 | — | Historia |
| Układ kalendarza | 1 | 0 | — | Dzienny |
| Wiek | 2 | 0 | Grupa wiekowa, Minimalny wiek | 3-latki, Dla malucha (0-3 lata) |
| Wybrani autorzy | 57 | 0 | — | Stephen King |
| Wydawnictwo | 67 | 8 | Producent | Znak |
| Zestaw | 7 | 0 | Liczba tomów | Sama książka |
| Znani ludzie | 1 | 0 | — | Aktorzy i reżyserzy |
| Ćwiczenia | 7 | 0 | — | Tak, z kluczem |
