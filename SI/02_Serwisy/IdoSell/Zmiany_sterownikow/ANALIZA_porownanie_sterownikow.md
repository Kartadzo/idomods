# ANALIZA: skrypt porównania sterownika z panelu z plikiem lokalnym
Pomysł użytkownika · Data: 2026-11-09 · Dotyczy: wszystkie zadania w `Zmiany_sterownikow/<klient>/`

## Cel
Krok stały każdej zmiany sterownika to porównanie wersji z panelu IdoSell z plikiem w `xslt/<litera>/<klient>/<kraj>/`. Ten krok chcemy zastąpić jednym lokalnym skryptem. Dziś robię go ręcznie: kopiuję przez schowek, normalizuję, robię diff, przenoszę stary plik do `old/` z datą i zapisuję wersję z panelu.

W zadaniach eZebra z 09.11 lokalna wersja różniła się od panelu w 3 z 7 sterowników:
- PL fbAds: blok GTIN/MPN;
- WP: ver. 2.0 w panelu, ver. 1.0 lokalnie;
- RTB: limit wartości parametru.

Tego kroku nie można więc pominąć.

## Dane wejściowe i wyjściowe
**Wejście:**
- Tekst sterownika z panelu. Domyślnie ze schowka: Claude in Chrome zaznacza `textarea[name=driver_body]` i kopiuje go Ctrl+C. Opcjonalnie z pliku `.xml` lub `.txt`.
- Plik lokalny: wybór z menu po kliencie i kraju albo ścieżka jako argument.

**Wyjście:**
- Werdykt w konsoli:
  - `ZGODNE`;
  - `ZGODNE poza białymi znakami`;
  - `RÓŻNE` z liczbą linii +/− i pierwszymi fragmentami diffu.
- Przy `RÓŻNE`:
  - pełny diff w pliku `porownanie_<plik>_<RRRR-MM-DD>.diff` w folderze zadania, a gdy go nie podano, obok skryptu w `wyniki/`;
  - opcjonalnie podgląd HTML (`difflib.HtmlDiff`) do otwarcia w przeglądarce.
- Po potwierdzeniu `[T/n]`:
  - lokalny plik trafia do `<kraj>/old/<nazwa>_<RRRR-MM-DD>.xml` (gdy taka nazwa już jest, dostaje sufiks `_2`, `_3`);
  - wersja z panelu zostaje zapisana pod nazwą lokalną.

## Plan
1. Lokalizacja: `SI/02_Serwisy/IdoSell/Zmiany_sterownikow/_narzedzia/porownaj_sterownik/`, z plikami `porownaj_sterownik.py`, `run_porownaj.bat` i `README.md`. Przed kodem czytam `AI_Instrukcje/Python/`.
2. **Odczyt schowka:** `tkinter.clipboard_get()` (biblioteka standardowa, polskie znaki i duże teksty działają). Gdyby to zawiodło, PowerShell `Get-Clipboard -Raw` z wymuszonym UTF-8.
3. **Kontrola wejścia:** tekst musi wyglądać na XSLT, czyli zawierać `xsl:stylesheet` lub `xsl:transform`. Inaczej pojawia się komunikat „w schowku nie ma sterownika” i nic nie jest zapisywane.
4. **Normalizacja przed porównaniem:** usuwam BOM, zamieniam CRLF/CR na LF, obcinam spacje i tabulatory na końcach linii i końcowe puste linie. Różnica wyłącznie w białych znakach dostaje osobny werdykt i nie wymaga podmiany. Normalizacja w osobnej funkcji, a skrypt wypisuje też SHA-256 znormalizowanego tekstu. Dzięki temu w przyszłości można porównywać hashe z panelu (zob. sekcja o Admin API).
5. **Tryb interaktywny po dwukliku `.bat`** (zasada: skrypty interaktywne, nie flagowe):
   - menu klientów z `xslt/*/*/`, potem kraju i pliku (Enter = pozycja 1);
   - źródło: schowek albo plik;
   - na końcu pytanie o podmianę.

   Argumenty jako skrót, żeby Claude mógł uruchamiać skrypt w sesji bez pytań: `--lokalny <ścieżka>`, `--panel <plik>` (domyślnie schowek), `--folder-zadania <ścieżka>`, `--zastap` / `--bez-zmian`.
6. **Zapis wersji z panelu:** UTF-8 bez BOM. Końce linii jak w dotychczasowym pliku lokalnym, żeby kolejny `git diff` nie pokazywał całego pliku.
7. **Test** na plikach eZebra z 09.11, które już leżą w `PL/old/`:
   - para zgodna: wersja z panelu kontra sam plik;
   - para różna: `ezebrapl_WP_2026-11-09.xml` kontra obecny `ezebrapl_WP.xml`;
   - para różniąca się tylko CRLF.
8. **Wpięcie w proces:**
   - wpis w `SI/README.md` (tabela i pkt 9 zasad: „porównanie skryptem `_narzedzia/porownaj_sterownik`”);
   - aktualizacja notatek w pamięci (zmiany sterowników, odczyt sterownika).

## Założenia
- Sam odczyt z panelu zostaje w Claude in Chrome przez schowek. Skrypt nie loguje się do panelu.
- Biblioteka standardowa Pythona 3.8+, wcięcia 4 spacje, komunikaty po polsku.
- Skrypt niczego nie wgrywa do panelu i niczego nie usuwa. Stara wersja zawsze trafia do `old/`.
- Jeden sterownik na jedno uruchomienie. Kilka feedów naraz wymagałoby kilku kolejnych odczytów schowka, więc nie zyskałoby się na tym.

## Admin API IdoSell: sprawdzone 2026-11-09 na zooart6 (do rozważenia przy większym zadaniu)
Wniosek: **API nie zwraca treści sterowników XSLT.** Wersja 1 zostaje przy schowku.
- Specyfikacja OpenAPI v8 (`https://zooart6.iai-shop.com/api/doc/admin/v8/json`, 243 ścieżki): nie ma w niej endpointu ze sterownikiem ani pól `driver`/`xsl`. Porównywarek dotyczą tylko ceny i nazwy towaru w serwisie (`priceComparisonSites…`, `productNamesInPriceComparer`).
- `GET system/config` (i `system/shopsData`) zwraca jednak **spis serwisów**: `price_comparers` {id → `key`, `name`, `active`}, także indywidualne ID ≥ 10000 (na zooart6 do 10053), a per sklep `active_price_comparers` [{`id`, `default_price_percent_diff`}].

Pomysł na zadanie typu „aktualizacja ~12 sterowników” (np. nowe pole we wszystkich feedach klienta):
1. **Inwentaryzacja: z panelu, nie z API** (decyzja użytkownika 2026-11-09). Serwisy klientów mają zwykle niestandardowe sterowniki, a spis z nazwami szybciej odczytać z `config-pricecomparers.php` w panelu, niż zakładać klientowi klucz API. Mapa `serwisy.json` (sklep, ID serwisu, plik lokalny) przy kliencie, nadal opcjonalna.
2. **Szybkie porównanie bez schowka:** w karcie Chrome z panelem `javascript_tool` pobiera stronę ustawień każdego serwisu (`fetch` w tej samej domenie, tylko GET), znormalizowany tekst `textarea[name=driver_body]` zamienia na **SHA-256 i liczbę linii**, a zwraca tylko krótką listę `{id: hash}`. Obchodzi to obcinanie wyniku do ok. 1000 znaków. Skrypt liczy te same hashe lokalnie (ta sama normalizacja), a schowek jest potrzebny już tylko dla sterowników różnych.
3. Do sprawdzenia przed tym: czy ustawienia serwisu da się pobrać zwykłym GET-em (adres z `config-pricecomparers.php`), czy to formularz POST lub AJAX. Bez tego punkt 2 odpada i zostaje schowek po kolei.

## Otwarte pytania
- **Lokalizacja:** `Zmiany_sterownikow/_narzedzia/` czy osobny folder w `SI/_wspolne/`? Proponuję `_narzedzia`, bo narzędzie służy tylko temu procesowi.
- **Domyślne miejsce pliku `.diff`:** folder zadania (np. `ezebra/black_days_2026-11-06/`) czy wspólne `wyniki/`? Pliki `.diff` zawierają kod klienta. Proponuję folder zadania i dopisanie `*.diff` do głównego `.gitignore`, gdyby miały nie trafiać do gita.

## Zasady sesji
- Git: wariant „nowy problem”, narzędzie wspólne. Proponuję nową gałąź `porownanie_sterownikow` od `main` po zamknięciu `black_days_ezebra`. Commituje użytkownik.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: nie, tylko test lokalny na plikach z `PL/old/`.

## Stan
- 2026-11-09: analiza wstępna. Zaakceptowana przez użytkownika z decyzjami: kod na nowej gałęzi `porownanie_sterownikow` od `main` po zamknięciu `black_days_ezebra`; `.diff` w folderze zadania i `*.diff` w `.gitignore`; folder `_narzedzia/porownaj_sterownik/`.
- 2026-11-09: sprawdzone Admin API na zooart6 (sekcja wyżej): brak treści sterowników, jest spis serwisów.
- 2026-11-09: wersja 1 gotowa na gałęzi `porownanie_sterownikow`: `_narzedzia/porownaj_sterownik/` (`porownaj_sterownik.py`, `run_porownaj.bat`, `README.md`). Testy na plikach eZebra (kopie w scratchpadzie): zgodne, tylko CRLF i spacje, różne z podmianą (nowy plik = panel bajt w bajt, CRLF zachowane), sufiks `_2` w `old/`, schowek bez XSLT (kod 2), schowek z XSLT, pełne menu. Menu plików pomija eksporty IOF (XSLT szukane w pierwszych 64 KB). Reguły `porownanie_*` dopisane do `Domino/.gitignore`. Brak `AI_Instrukcje/Python/` w repo, więc styl przyjęty według `SI/01_Feedy/Heureka_kategorie/app.py`.
- 2026-11-09: sprawdzenie GET-u ustawień serwisu nie powiodło się: panel zooart6 (`iai-shop.com` i `yourtechnicaldomain.com`) wymaga logowania, którego Claude nie wykonuje. Do sprawdzenia przy pierwszym zadaniu w zalogowanym panelu (np. eZebra), przez `fetch` GET adresu „Ustawienia” i sprawdzenie, czy odpowiedź zawiera `textarea[name=driver_body]`.
