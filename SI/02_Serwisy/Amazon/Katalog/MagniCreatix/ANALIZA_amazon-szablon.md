# ANALIZA: eksport IdoSell (magnicreatix.pl) → szablon Amazon TOY_BUILDING_BLOCK

Data: 2026-11-06 (wersja 2, po odpowiedziach użytkownika)

## Cel

Z eksportu produktów IdoSell wypełnić arkusz „Szablon” w `TOY_BUILDING_BLOCK.xlsm`, żeby wgrać go w Seller Central (amazon.pl, tylko język polski).

Integracja IdoSell–Amazon wystawia tylko oferty (cena, stan) na produkty, które **już są w katalogu Amazon** pod danym EAN. Towary MagniCreatix są dla Amazona nowe, więc szablon ma **utworzyć ich karty katalogowe**. Dzięki temu integracja zmapuje je potem po SKU i będzie sama wysyłać cenę i stan.

Zakres: wszystkie 36 produktów.

## Dane wejściowe

| Plik | Co zawiera | Użycie |
|---|---|---|
| `products_export-magnicreatix.pl-2026-11-05_10.32.xml` | 36 produktów IOF, każdy z jednym rozmiarem „one size” | **źródło danych** |
| `products_export-…csv` | to samo w CSV | nieużywany (p. 8) |
| `TOY_BUILDING_BLOCK.xlsm` | szablon Amazon: 314 kolumn, etykiety w wierszu 4, nazwy atrybutów w wierszu 5, przykład w wierszu 6, dane od wiersza 7 | szablon wyjściowy |

## Dane wyjściowe

- `Amazon_MagniCreatix_<data>.xlsm`: kopia szablonu z wierszami produktów od wiersza 7. Dane wpisuję bezpośrednio do XML arkusza w pliku, więc makra, listy rozwijane i walidacja zostają nietknięte.
- `raport_<data>.csv`: braki i ostrzeżenia dla każdego produktu, np. pusty wymagany atrybut albo skrócony tytuł.

## Zmiany (zrealizowane 2026-11-06)

- `Katalog/amazon_szablon.py` (Python 3.8+, tylko biblioteka standardowa): wspólny dla klientów. Czyta XML, mapuje pola, kopiuje xlsm i wstawia wiersze do arkusza „Szablon”.
- `Katalog/MagniCreatix/konfiguracja.json`: ustawienia klienta (marka, SKU do częściowej aktualizacji, id produktów z bateriami, nazwy parametrów wymiarów, wyjątki wielkich liter). Na tym będzie można zbudować konfigurowalną aplikację, która uzupełni brakujące atrybuty podczas generowania (p. 6).
- `Katalog/MagniCreatix/run.bat`: uruchomienie dwuklikiem, sam wykrywa najnowszy XML w folderze.
- **Zdjęcia**: brane z `iaiext:originals` (PNG/JPG), bo wersje `large` są w WebP, którego Amazon nie przyjmuje. Oryginały WebP (22 szt.) są pomijane i trafiają do raportu.
- **Pomiń ofertę = Tak** dla nowych produktów (pełna aktualizacja). Amazon nie żąda wtedy ceny ani ilości w pliku, a ofertę doda integracja IdoSell.
- Praca na osobnej gałęzi git. Projekt dopiszę do tabeli statusów w `SI/README.md`.

## 1. Mapowanie pól z eksportu

| Kolumna Amazon | Wymagane? | Źródło w XML | Uwagi |
|---|---|---|---|
| SKU | Tak | `size/@code` (np. `9-uniw`) | **identyczny jak w IdoSell** (idIAI-idRozmiaru), żeby zadziałało mapowanie integracji |
| Rodzaj produktu | Tak | stała `TOY_BUILDING_BLOCK` | |
| Działanie związane z ofertą | – | „Utwórz lub zastąp (pełna aktualizacja)”; dla id 9, 10, 12 „Edytuj (częściowa aktualizacja)” | p. 7 |
| Nazwa produktu | Tak | `description/name` po normalizacji | p. 4 |
| Marka / Producent | Tak / warunkowo | `producer/@name` → „MAGNICREATIX” | |
| Typ identyfikatora / Identyfikator | Tak | `EAN` + `size/@code_producer` | dla id 32 brak, więc `code_on_card` (5907426616226). Dla id 38–49 `code_on_card` to kod MAG-…, a EAN jest w `code_producer` |
| Numer modelu / Numer części | warunkowo | `size/@iaiext:code_external` (np. `MAG-T68`) | |
| Główny + inne obrazy (do 8) | warunkowo | `images/large/image/@url` wg `priority` | 1600×1600; dla id 46 tylko 4 zdjęcia |
| Opis produktu | Tak | `long_desc` bez HTML, do 2000 znaków | |
| Punktory 1–5 | Tak (min. 1) | pierwsze 5 elementów `<li>` z `long_desc` | każdy produkt ma 4–29 `<li>`. Przycinam do 500 znaków |
| Kraj pochodzenia | Tak | `@iaiext:country_of_origin`: CN → „Chiny”, PL → „Polska” | **brak (id 10, 45, 48, 49) → „Polska”** |
| Przepisy dot. towarów niebezpiecznych | Tak | stała „Nie dotyczy” | **puste dla id 19 i 48** (prawdopodobnie baterie), w raporcie |
| Liczba sztuk | warunkowo | z nazwy: „68 el.”, „6 szt.”; id 31: 28 + 2 = 30 | |
| Liczba produktów / Ilość paczki | warunkowo | stała 1 | |
| Stan przedmiotu | warunkowo | „Nowy nowy” | |
| Wymiary opakowania (cm) | warunkowo | parametry „Długość/Szerokość/Wysokość towaru w centymetrach” | są w 23 z 36 produktów, pozostałe puste |
| Waga opakowania (kg) | warunkowo | `size/@weight` (g → kg) | **0 dla id 37–49 → puste** |
| Waga produktu (kg) | rekomendowane | `size/@iaiext:weight_net` | 0 → puste |
| Opis gwarancji | opcjonalne | `warranty/@name` | |
| Rodzaj klocków | rekomendowane | „Klocek magnetyczny do zabawy” | |

## 2. Atrybuty zgodności: zostają puste

Zostawiam puste: minimalny wiek, opis przedziału wiekowego, ostrzeżenia z dyrektywy zabawkowej (wiekowe, niezwiązane z wiekiem, język), tekst ostrzeżenia, materiał, atest GPSR, e-maile producenta i osoby odpowiedzialnej, dane baterii, wymagany montaż.

Klient zostanie poproszony o uzupełnienie: `NOTATKA_dla_klienta.md`. Amazon może bez nich odrzucić lub zablokować ofertę zabawki. Raport przetwarzania w Seller Central pokaże konkretne błędy.

## 3. Przyjęte założenia

- Każdy produkt to samodzielny listing, bez wariantów i bez relacji rodzic–dziecko.
- Brak danych nie zatrzymuje skryptu. Komórka zostaje pusta, a brak trafia do raportu.
- Ceny i stanu nie wypełniam, bo wyśle je integracja IdoSell po zmapowaniu SKU.

## 4. Normalizacja tytułów (zaakceptowana)

- Słowa pisane w całości wielkimi literami zamieniam na zwykłe (pierwsza litera zdania wielka). Wyjątki: marka **MAGNICREATIX**, skróty (STEAM) i oznaczenia (MAG-…).
- Usuwam „GRATIS” i dopiski typu „+ 2 GRATIS!” (id 31).
- „KOMPATYBILNE z LEGO®” (id 20, 21) usuwam z tytułu i dodaję jako pierwszy punktor: „Kompatybilne z klockami LEGO®”.
- Usuwam „™” i podwójne spacje. Tytuł ma najwyżej 200 znaków.
- Każdy tytuł przed i po zmianie trafi do raportu do przejrzenia.

## 5. Cena i stan

Nie wypełniam ich, bo przekaże je integracja IdoSell. Do czasu zmapowania karty nowych produktów będą nieaktywne.

## 6. Kierunek na przyszłość

Aplikacja (lub plik konfiguracji per sklep) z wartościami domyślnymi atrybutów zgodności i regułami per produkt, wypełniana podczas generowania pliku. To osobny etap, po odpowiedziach klienta.

## 7. Trzy produkty wysłane testowo (id 9, 10, 12)

Integracja założyła już w Seller Central oferty `9-uniw`, `10-uniw` i `12-uniw` z EAN, ceną i stanem. Dla nich stosuję **częściową aktualizację**: dopisuje dane katalogowe i nie kasuje ceny ani stanu. Pełna aktualizacja zastąpiłaby cały rekord i wyczyściła cenę i stan do kolejnej synchronizacji.

Ryzyko: jeśli Amazon nie przyjmie częściowej aktualizacji dla SKU bez karty katalogowej, te 3 wiersze trzeba wysłać ponownie z pełną aktualizacją. Integracja odtworzy potem cenę i stan.

## 8. XML czy CSV

**XML**: pełna, jednoznaczna struktura (zdjęcia z priorytetem, parametry, rozmiary z EAN i wagą, kraj pochodzenia). CSV z panelu rozbija listy na niezsynchronizowane kolumny. Skrypt czyta tylko XML.

## Otwarte pytania

Brak blokujących. Kwestie dla klienta są w `NOTATKA_dla_klienta.md`.
