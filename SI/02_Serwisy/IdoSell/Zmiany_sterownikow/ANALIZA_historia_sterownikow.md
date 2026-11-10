# ANALIZA: własna historia zmian sterowników XSLT w panelu IdoSell
Pomysł użytkownika · Data: 2026-11-10 · Dotyczy: wszystkie zadania w `Zmiany_sterownikow/<klient>/` i praca z feedami

## Cel
Panel IdoSell nie zapisuje historii zmian sterowników: nie wiadomo, kto i kiedy zmienił sterownik serwisu. Feed pokazuje zmianę z opóźnieniem kilku godzin. Chcemy prowadzić własną historię, niezależną od generowania feedu, i szybko wykrywać sterownik wgrany do niewłaściwego serwisu.

**Powód: incydent eZebra, 2026-11-09.** W serwisie „Google Shopping Polska - indywidualny + google_product_category” (shop=1) znalazł się sterownik Facebook Ads. GMC wykrył to przy pobraniu o 16:20, a alert mailowy przyszedł po 20:00. Nie da się ustalić, kto wgrał sterownik ani kiedy:
- zapisy sesji Claude pokazują tylko odczyt (`ctrl+c`, bez wklejania i zapisu): 10:47–11:00 serwisy Meta, 12:11–12:14 WP i RTB. Po 12:14 Claude w panelu eZebry nie był;
- moment zmiany wyznacza jedynie generowanie feedu, a ono może przesunąć się o kilka godzin w obie strony. Godziny same w sobie nikogo nie wykluczają.

Zakres wersji 1: punkty **1** (zrzut przed i po), **3** (znacznik serwisu z czasem edycji), **4** (dziennik wdrożeń), wpięcie w `/zadanie`, `/zapisz` i `/zamknij` oraz pytanie, kto wgrywa sterownik. Cykliczny zrzut (punkt 2) później, jako rozszerzenie.

## Ustalanie momentu zmiany z generowania feedu (do raportów incydentów)
- W wierszu serwisu panel pokazuje tylko **godzinę zakończenia** generowania („Plik eksportu: wygenerowany o godzinie …”), a nie jego rozpoczęcia.
- **Założenie: generowanie trwa ok. 30 min.** Przy wielu feedach i produktach może trwać dłużej, a sama kolejka może przesunąć start o kilka godzin.
- Założenie robocze: sterownik jest wczytywany na początku generowania. Zmiana wprowadzona w trakcie trafia więc dopiero do następnego pliku. Tego nie da się sprawdzić z zewnątrz.
- Przedział zmiany: od **startu ostatniego poprawnego generowania** (≈ jego koniec − 30 min) do **startu pierwszego błędnego** (≈ jego koniec − 30 min). Granice są przybliżone i tak je opisuję w raporcie.
- Panel nie przechowuje starszych godzin generowania. Godzinę pierwszego błędnego pliku trzeba więc wyprowadzić z GMC (pobranie z błędem) i harmonogramu generowania serwisu. Każdy zrzut (punkt 1) zapisuje dlatego także bieżącą godzinę wygenerowania pliku każdego serwisu. Z czasem powstaje własna historia generacji.
- Zrzuty z punktu 1 dają przedział znacznie dokładniejszy niż ten wyznaczony z feedu. Wyliczenie z generowania zostaje na sytuacje, gdy zrzutu brak.

## Sprawdzone 2026-11-10 na zooart6: odczyt sterowników zwykłym GET-em
- Link „Ustawienia” w `config-pricecomparers.php` to `onclick` z `IAI.aceForm…(this, \`<adres>\`, …)`. Adres jest w backtickach: `/panel/ajax/config-pricecomparers-ace.php` z parametrami `action, shopId, mode, isNewPriceComparer, pricecomparerId`. Panel ładuje okno POST-em AJAX.
- **`fetch` GET tego adresu zwraca ten sam formularz** (status 200) z `textarea[name=driver_body]`.
- Serwisy standardowe (Ceneo, Arena.pl, Domodi itp.) nie mają `driver_body`. Mają go tylko serwisy indywidualne (ID ≥ 10000), czasem pusty (np. „Domyślny feed”, „iof 3.0”).
- shop=1: **35 serwisów w 2,7 s**, w wyniku tylko ID, nazwa, status, godzina generowania, liczba linii i hash. Filtr danych przeglądarki nie blokuje takiego wyniku.
- Kontrola: hash z GET dla 10040 „Facebook ads [IdoMods]” = hash z okna otwartego kliknięciem (830 linii, `98e23880c463…`). Okno zamknięte nawigacją, bez zapisu.
- Przy okazji: 10015 „Do naszej porównywarki” i 10011 „Google Ads test dla konrada” mają identyczny sterownik. Wykrywanie duplikatów działa na prawdziwych danych.

## 1. Zrzut sterowników
**Wejście:** zalogowany panel w karcie Chrome (Claude in Chrome), domena logowania z pliku klienta, lista sklepów (`shop=`).

**Działanie** (jeden `javascript_tool` na sklep, tylko GET):
1. Lista wierszy `config-pricecomparers.php?shop=<n>`: ID (`pricecomparerId` z adresu), nazwa, status, godzina wygenerowania pliku eksportu.
2. GET adresu „Ustawienia” każdego serwisu, odczyt `driver_body`, normalizacja jak w `porownaj_sterownik.py` (BOM, CRLF, końcowe spacje i puste linie), **SHA-256 i liczba linii** przez `crypto.subtle`. Treść sterownika nie opuszcza przeglądarki.
3. Odczyt znaczników z punktu 3, jeśli są.
4. Wynik JSON → `zrzut.py` zapisuje i porównuje lokalnie.

**Wyjście:** `Zmiany_sterownikow/<klient>/_historia/<RRRR-MM-DD_GGMM>_<rodzaj>.json` (do gita):
```json
{"klient": "ezebra.pl", "czas": "2026-11-10T10:05:00+01:00", "rodzaj": "start", "zadanie": "<folder zadania>",
 "serwisy": [{"shop": 1, "id": 10018, "nazwa": "Facebook [indywidualny]", "aktywny": true,
              "wygenerowany": "2026-11-10 09:41:12", "sha256": "…", "linie": 1234,
              "znacznik": {"serwis_id": 10018, "edycja": "2026-11-09 13:20"}}]}
```
Rodzaje: `start`, `przed_wgraniem`, `po_wgraniu`, `zapis`, `koniec`, `reczny`.

Porównanie z poprzednim zrzutem klienta w konsoli:
- serwisy zmienione (inny hash), nowe, usunięte. Zmiana bez wpisu w dzienniku (punkt 4) to **zmiana spoza naszych wdrożeń**, oznaczona wyraźnie;
- **niezgodność znacznika**: znacznik wskazuje inny serwis niż ten, w którym sterownik leży;
- **ten sam sterownik w dwóch serwisach**: ostrzeżenie (wczorajszy przypadek), z możliwością oznaczenia pary jako zamierzonej (lista wyjątków przy kliencie).

Pełną treść zmienionego sterownika pobieram osobno przez schowek i `porownaj_sterownik.py`.

## 3. Znacznik serwisu z czasem edycji
Dodawany **wyłącznie do sterowników, które edytujemy**. Przy samym kopiowaniu sterownika z panelu do repozytorium (kopia, porównanie, podmiana pliku lokalnego) znacznika nie dodaję. Komentarz na początku sterownika, zaraz po deklaracji XML:
```xml
<!-- BM-SERWIS: shop=1 | ID 10018 | Facebook [indywidualny] | plik xslt/E/ezebra/PL/ezebrapl_fbAds.xml -->
<!-- BM-EDYCJA: 2026-11-09 13:20 | omnibus + Black Days -->
```
- Stały prefiks `BM-SERWIS` / `BM-EDYCJA`, łatwy do wyszukania w zrzucie i w `porownaj_sterownik.py`.
- `BM-EDYCJA`: czas przygotowania wersji do wgrania i krótki opis, **bez osoby**. Zawiera tylko ostatnią edycję, pełna historia jest w git.
- Claude dopisuje lub aktualizuje znacznik w kroku edycji pliku. Nikt nie musi o tym pamiętać ręcznie.
- Wpływ na feed: brak, to komentarz XSLT, nie trafia do pliku wyjściowego.
- `porownaj_sterownik.py`: ostrzeżenie, gdy znacznik w panelu wskazuje inny plik lub inny ID serwisu niż wybrany.

## 4. Dziennik wdrożeń
`Zmiany_sterownikow/<klient>/dziennik_wdrozen.csv` (separator `,`, UTF-8), jeden wiersz na wgranie, **bez osoby**:

`czas_wgrania, wgrywa, shop, id_serwisu, nazwa_serwisu, plik_lokalny, sha256_przed, sha256_po, sha256_pliku, zgodne_po_zapisie, zadanie`

- `wgrywa`: `Claude` albo `użytkownik`, wynika z pytania w procesie (niżej), nie z pamięci osoby.
- Po wgraniu Claude robi zrzut `po_wgraniu`, porównuje hash serwisu z hashem pliku lokalnego (`zgodne_po_zapisie`: TAK/NIE) i dopisuje wiersz. NIE oznacza błąd wgrania albo zły serwis i jest zgłaszane od razu.
- `sha256_przed` ze zrzutu `przed_wgraniem`. Jeśli różni się od zrzutu `start`, ktoś zmienił serwis w trakcie naszej pracy: zgłaszam przed wgraniem.

## Wdrożenie: kto wgrywa sterownik
Przed każdym wgraniem pytam: **„Nowy sterownik wgrywasz Ty czy ja?”** (osobno dla każdego zadania, zgoda nie przechodzi na kolejne).

- **Użytkownik:** podaję listę `serwis (shop, ID, nazwa) → plik lokalny`. Po informacji „wgrane” robię zrzut `po_wgraniu` i uzupełniam dziennik.
- **Claude:** dla każdego serwisu z listy:
  1. zrzut `przed_wgraniem`;
  2. sprawdzam zasady z pliku klienta (np. eZebra: bez wdrożeń w piątki);
  3. otwieram „Ustawienia” serwisu wskazanego **po ID** (`pricecomparerId`), nie po nazwie; sprawdzam, że nazwa, ID i ewentualny znacznik w panelu zgadzają się z listą, a `BM-SERWIS` w nowym pliku wskazuje ten sam serwis. Przy niezgodności przerywam;
  4. wklejam treść pliku do `driver_body` (schowek lub ustawienie wartości pola) i zapisuję formularz;
  5. zrzut `po_wgraniu`, porównanie hashy, wiersz dziennika.

  Przed krokiem 4 kopia bieżącej treści serwisu (schowek → plik w `_historia/kopie/`), żeby dało się przywrócić stan sprzed wgrania.

### Test wgrania na zooart6, 2026-11-10 (serwis 10046 „CENEO TEST”, wyłączony)
1. Zrzut startowy shop=1: 35 serwisów, 10046 = `2c84fc21712b`.
2. Kopia oryginału: okno „Ustawienia”, zaznaczenie `driver_body`, `ctrl+c` → plik w scratchpadzie. Hash pliku po normalizacji = hash z panelu.
3. **Metoda A, ustawienie wartości pola:** komentarze `BM-SERWIS`/`BM-EDYCJA` wstawione po deklaracji XML (`ta.value = …` + zdarzenia `input`/`change`), klik „Zapisz” (jedyny widoczny przycisk o tej nazwie, w tym samym formularzu POST `/panel/ajax/config-pricecomparers.php`). Zrzut: zmienił się **tylko** 10046, na oczekiwany hash `27867e8698b8`.
4. **Metoda B, schowek:** przeładowanie strony, ponowne otwarcie okna (panel pokazał już nowy hash), kopia z pliku → `Set-Clipboard`, zaznaczenie pola, `ctrl+v`, kontrola hasha przed zapisem (= oryginał), „Zapisz”. Zrzut: wszystkie 35 serwisów identyczne ze startem.

Wnioski:
- Obie metody działają. Domyślnie **metoda B** (treść z pliku lokalnego przez schowek). Treść nie przechodzi przez wynik narzędzia, nie ma limitu długości, a hash pola sprawdzam **przed** kliknięciem „Zapisz”.
- Po zapisie okno się zamyka, ale ukryty formularz zostaje w DOM. **Nie używać go ponownie:** przed każdym kolejnym serwisem przeładowanie strony i świeże otwarcie okna. Kolejny `driver_body` szukać tylko wśród widocznych elementów.
- Brak komunikatu o zapisie. Potwierdzeniem jest tylko zrzut po wgraniu.

### Pułapki panelu: test na zooart6, 2026-11-10 (serwisy wyłączone 10046, 10021; na koniec 35/35 serwisów i 40/40 pól formularza 10046 zgodnych ze startem)
| # | Pułapka | Co zrobić |
|---|---|---|
| 1 | **Lista serwisów ładuje się skryptem po wczytaniu strony** (POST AJAX `getPriceComparersTableView`). `fetch` strony `config-pricecomparers.php` zwraca HTML bez wierszy (0 serwisów), a GET adresu AJAX daje błąd 500. | Zrzut przechodzi kolejno na stronę każdego sklepu (`?shop=<n>`), czeka na `#table_pricecomparersList` z wierszami i dopiero potem pobiera ustawienia serwisów. Zero wierszy = błąd zrzutu, a nie „brak serwisów”. |
| 2 | **Sterownik jest przypisany do ID serwisu, nie do sklepu.** Formularz 10046 (widoczny tylko w sklepie 1) otwiera się też z `shopId=2`, z tym samym sterownikiem, ale inne ustawienia sklepu (strona innej długości). | Hash w zrzucie kluczowany po ID serwisu, a lista sklepów, w których serwis występuje, zapisywana osobno. Kontrola duplikatów porównuje różne ID, nie ten sam ID w dwóch sklepach. Wgranie zawsze z `shopId` sklepu, w którym serwis jest na liście. |
| 3 | **Nieistniejące ID zwraca błąd 500**, a nie pusty formularz. Wylogowanie w trakcie zwróci stronę logowania. | Każda odpowiedź bez statusu 200 lub bez `form` = błąd zrzutu (przerwanie z komunikatem). Nigdy nie zapisywać jej jako `-` / „brak sterownika”, bo dałoby to fałszywą zmianę. |
| 4 | **Jedno okno edycji na stronie** (`#priceComparerEdit-toplayer`). Otwarcie kolejnego serwisu podmienia poprzednie, ale po zapisie lub zamknięciu ukryte `driver_body` zostaje w DOM. Warunek „pole się pojawiło” jest więc spełniony od razu, przez stare pole. | Czekać na **widoczne** `driver_body`, którego formularz ma ukryte pole `id` = docelowe ID serwisu. Dodatkowo nazwa w nagłówku okna i pole `name`. Przed każdym serwisem przeładowanie strony. |
| 5 | Pole `<input name="id">` przesłania właściwość `form.id` (w DOM widać `FORM#[object HTMLInputElement]`). | W kodzie `form.elements['id'].value`, nigdy `form.id`. |
| 6 | **Panel waliduje sterownik przy zapisie**: niepoprawny XML („Premature end of data…”) i błędy kompilacji XSLT („Failed to compile the XPath expression…”) są odrzucane. W panelu zostaje poprzednia treść, a okno zostaje otwarte z błędną treścią i komunikatem „Uwaga: Dodany sterownik posiada niepoprawną strukturę…”. | Po kliknięciu „Zapisz”: okno nadal widoczne = zapis odrzucony, treść komunikatu do raportu. Przed wgraniem lokalna walidacja (`lxml`, jak w summonFeed), żeby nie trafiać na odrzucenie. Błędów wykonania (np. zły wynik feedu) panel nie wykryje. |
| 7 | **Komunikat błędu zostaje widoczny po późniejszym udanym zapisie** w tej samej stronie. Przycisk „Close” komunikatu zamknął też okno edycji. | Sukcesu nie oceniać po braku komunikatu ani po zamknięciu okna. Jedynym potwierdzeniem jest zrzut `po_wgraniu` (hash = plik). Po błędzie przeładowanie strony przed kolejną próbą. |
| 8 | Zapis wysyła cały formularz (40 pól: ceny, eksport, harmonogram…), nie tylko sterownik. Test: zapis bez zmian w innych polach nie zmienił żadnego pola ani statusu. | Nie zmieniać innych pól. Zrzut zapisuje też status (aktywny/wyłączony), żeby wykryć niezamierzoną zmianę. Formularz zawsze świeżo otwarty (pkt 4), żeby nie wysłać nieaktualnych ustawień. |
| 9 | Zrzut ekranu strony z listą serwisów kończy się przekroczeniem czasu (skrypt strony zajęty). | Stan okna badać przez DOM, nie przez zrzuty ekranu. |

Dodatkowo: treść wraca z panelu z końcami linii LF (plik z CRLF dał inną długość, ten sam hash po normalizacji). Porównanie zawsze po normalizacji.

## Wpięcie w proces pracy z feedami
| Moment | Skill | Krok historii |
|---|---|---|
| Start sesji realizującej zadanie z feedem lub sterownikiem | `/zadanie` (prompt startowy sesji i skille dedykowane: `summonfeed`, `weryfikacja-gmc`, `weryfikacja-fb`) | zrzut `start` przed pierwszą zmianą; zmiany od ostatniego zrzutu klienta pokazuję od razu |
| Przed wdrożeniem | sesja realizująca | pytanie „wgrywasz Ty czy ja?”, zrzut `przed_wgraniem` |
| Po wdrożeniu | sesja realizująca | zrzut `po_wgraniu`, dziennik |
| Zapis postępu | `/zapisz` | gdy w tej sesji był panel: zrzut `zapis`; pliki `_historia/` i `dziennik_wdrozen.csv` w commicie |
| Zamknięcie projektu | `/zamknij` | **przebieg kontrolny po wszystkich sklepach i serwisach klienta** (opis niżej); wynik w podsumowaniu, problemy przed merge |

### Przebieg kontrolny w `/zamknij`
Cel: upewnić się, że w wyniku błędu (naszego, panelu albo IdoSell) sterownik nie został zapisany w więcej niż jednym serwisie albo w niewłaściwym.
1. Zrzut `koniec` **wszystkich** sklepów klienta (każdy `shop=`), nie tylko tych, w których pracowaliśmy.
2. Porównanie z `start` tej sesji:
   - każdy zmieniony hash musi mieć wiersz w dzienniku z `zgodne_po_zapisie = TAK` i ten sam serwis;
   - zmiana bez wpisu = **zapis poza planem**;
   - liczba zmienionych serwisów = liczba wpisów w dzienniku z tej sesji.
3. Duplikaty: hash nowego sterownika (`sha256_pliku` z dziennika) występuje w jakimkolwiek innym serwisie niż docelowy → **zapis w dwóch serwisach**. Pary zamierzone tylko z listy wyjątków klienta.
4. Znaczniki: każdy sterownik z `BM-SERWIS` leży w serwisie o tym samym `shop` i ID.
5. Wynik `OK` / lista problemów. Przy problemie nie robię merge, przechodzę do procedury incydentu.

Ten sam przebieg (kroki 2–4 względem poprzedniego zrzutu klienta) robię na starcie `/zadanie`, żeby wiedzieć, czy przed nami ktoś coś zmieniał.

### Procedura incydentu (błędny zapis lub zmiana spoza naszych wdrożeń)
1. **Spisanie problemu** w folderze zadania (`INCYDENT_<RRRR-MM-DD>.md`): które serwisy, hashe przed i po, czas zrzutów, przedział czasu zmiany, wpisy dziennika, co widać w GMC / Meta.
2. **Przywrócenie poprzedniego stanu** z kopii w `_historia/kopie/`. Wgrywa użytkownik albo Claude, zgodnie z odpowiedzią na pytanie „wgrywasz Ty czy ja?” (osobne pytanie dla przywrócenia). Po przywróceniu zrzut i potwierdzenie hashy.
3. **Ocena przyczyny** zależnie od problemu. Gdy wygląda to na błąd IdoSell (np. jeden zapis trafił do kilku serwisów, bez śladu wgrania po naszej stronie), przygotowuję **treść zgłoszenia do pomocy technicznej IdoSell** (`zgloszenie_idosell.txt`: panel, sklep, ID serwisów, przedział czasu, hashe, kroki). Zgłoszenie wysyła użytkownik.

**Kopie treści do przywrócenia:** zrzut zawiera tylko hashe, więc przywrócenie wymaga treści. Kopie w `_historia/kopie/<shop>_<id>_<hash12>.xml` (poza gitem, reguła w głównym `.gitignore`):
- serwis docelowy: zawsze przed wgraniem (schowek);
- pozostałe serwisy: w zrzucie `start` treść każdego serwisu indywidualnego, którego hasha nie ma jeszcze w `kopie/`, wysłana z przeglądarki do lokalnego odbiornika (`odbiornik.py`, `http.server` tylko na `127.0.0.1`). Ten kanał zadziałał 2026-11-09 przy odczycie sterownika Meta PL eZebry (`POST http://127.0.0.1:8765/save`). Do potwierdzenia w implementacji. Gdyby przeglądarka zablokowała, zostaje schowek dla serwisów, które zmieniły się poza planem: ich poprzednią treść wtedy trzeba odtworzyć z `xslt/` lub z poprzedniej kopii.

Zrzut wymaga zalogowanego panelu. Gdy panel jest wylogowany albo sesja nie korzystała z panelu, `/zapisz` i `/zamknij` pomijają zrzut i odnotowują to w podsumowaniu, bez blokowania commita.

## Planowane pliki
- `_narzedzia/historia_sterownikow/zrzut_panel.js`: fragment do `javascript_tool` (lista serwisów, GET ustawień, normalizacja, SHA-256, znaczniki).
- `_narzedzia/historia_sterownikow/zrzut.py` + `run_zrzut.bat`: zapis zrzutu z JSON, porównanie z poprzednim, wiersz dziennika, kontrola przed `/zamknij`. Interaktywnie po dwukliku (wybór klienta, podgląd ostatnich zrzutów), argumenty jako skrót dla Claude'a.
- `_narzedzia/historia_sterownikow/README.md`.
- `porownaj_sterownik.py`: wspólna normalizacja (import zamiast kopii), kontrola znacznika.
- Skille: `zadanie`, `zapisz`, `zamknij` (kroki z tabeli), `summonfeed`, `weryfikacja-gmc`, `weryfikacja-fb` (zrzut `start`, gdy dotykają sterowników).
- `SI/README.md`: tabela projektów i pkt 9 zasad (znacznik przy edycji, zrzuty, dziennik, pytanie o wgrywającego).

## Założenia
- Python 3.8+, biblioteka standardowa, 4 spacje, komunikaty po polsku.
- Odczyt panelu tylko GET-em, bez logowania przez Claude'a. Zapis w panelu wyłącznie w ścieżce „wgrywa Claude”, po odpowiedzi użytkownika w danym zadaniu.
- Zrzuty JSON (same hashe i metadane, bez kodu klienta) i dziennik idą do gita. Czas commitów jest dodatkowym, niezależnym świadectwem.
- Czas lokalny Europe/Warsaw z przesunięciem w zapisie.
- Klienta nie informujemy o procedurze. Zmiany innych osób wychodzą jako różnica hashy bez wpisu w dzienniku.
- Polecenie „/zakończ” rozumiem jako istniejący skill `/zamknij`.

## Otwarte pytania
Brak. Kopie treści przez lokalny odbiornik zaakceptowane (2026-11-10).

## Zasady sesji
- Git: nowy problem, narzędzie wspólne + zmiany skilli. Proponuję gałąź `historia_sterownikow` od `main`.
- Przed kodem: akceptacja tej analizy przez użytkownika.
- Test zrzutu: zooart6 (sprawdzony odczyt GET), potem eZebra tylko do odczytu, nie w piątek.

## Stan
- 2026-11-10: analiza wstępna (punkty 1 + 3 + 4, czas edycji w znaczniku, uwaga o czasie generowania feedu ~30 min).
- 2026-11-10: decyzje użytkownika: znacznik tylko przy edycji (nie przy kopii); historia w `/zadanie`, `/zapisz`, `/zamknij`; zrzuty w gicie; bez osoby w znaczniku i dzienniku; klienta nie informujemy; pytanie „wgrywasz Ty czy ja?” w procesie. Sprawdzony GET ustawień na zooart6 (sekcja wyżej).
- 2026-11-10: decyzje: przebieg kontrolny po wszystkich serwisach w `/zamknij`; incydent = spisanie, przywrócenie stanu, zgłoszenie do IdoSell tylko gdy wygląda na ich błąd. Test wgrania na zooart6 10046: obie metody działają, oryginał przywrócony, 35/35 serwisów zgodnych ze startem.
- 2026-11-10: zaakceptowane kopie treści przez lokalny odbiornik. Test pułapek na zooart6 (tabela „Pułapki panelu”): lista ładowana AJAX-em, sterownik per ID serwisu, 500 dla złego ID, stare ukryte okno, `form.id`, walidacja XML/XSLT przy zapisie, komunikat błędu po sukcesie, cały formularz w zapisie, brak zrzutów ekranu. Stan panelu po teście = start.
- 2026-11-10: analiza zaakceptowana. Wersja 1 na gałęzi `historia_sterownikow`: `_narzedzia/historia_sterownikow/` (`historia.py`, `run_historia.bat`, `zrzut_panel.js`, `README.md` z procedurą), kontrola znacznika w `porownaj_sterownik.py`, kroki w skillach `zadanie`, `zapisz`, `zamknij`, `summonfeed`, `weryfikacja-gmc`, `weryfikacja-fb`, reguły `kopie/` i `_robocze/` w `.gitignore`, wpis w `SI/README.md`. Testy (README, sekcja „Testy”): zrzut zooart6, pełne wgranie i przywrócenie 10046 przez narzędzie, kontrola OK, dane sztuczne z 6 wykrytymi problemami. Uwaga z testu: pierwsze połączenie strony panelu z odbiornikiem może czekać na zgodę Chrome na dostęp do sieci lokalnej. Zmiana planu: zrzut przechodzi po stronach sklepów (pułapka 1), czas zrzutu = czas odczytu w przeglądarce.
