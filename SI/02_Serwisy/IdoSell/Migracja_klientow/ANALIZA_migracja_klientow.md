# ANALIZA – migracja klientów do IdoSell

## Cel

Przenieść bazę klientów z eksportu innej platformy (plik `*.client.csv`) do sklepu IdoSell przez
**KLIENCI > Eksport/Import klientów > Dodać nowych klientów** (`import-clients.php?mode=own`).
Źródłowy format nie jest formatem IdoSell, więc trzeba go przekonwertować na CSV zgodny ze
specyfikacją importu klientów IdoSell.

**Warunek klienta:** w trakcie migracji **nie wysyłamy** wiadomości o przeniesieniu konta i potrzebie
ustawienia nowego hasła („Mail po zaimportowaniu klientów przez support”). Wyślemy ją później,
osobno.

## Dane wejściowe

| Plik | Zawartość |
|---|---|
| `źródło/test.client.csv` | 1 klient testowy (adres e-mail `dominik.matyjasek@brandsmanago.pl`), 2 bloki adresowe |
| `źródło/a3781dc23d51912b37328b25398de4be.client — kopia.csv` | pełna baza: **16 101 klientów**, 263 kolumny, do 16 adresów na klienta |

Format źródła: UTF-8, separator `,`, kolumny klienta `date_add, first_name, last_name, email,
discount, active, comment` oraz powtarzane bloki adresowe `<pole> N` (N = 1…16):
`address_name, company_name, tax_id, pesel, address_first_name, address_last_name, street_1,
street_2, city, zip_code, state, country, phone, country_code, address_default,
address_shipping_default`.

### Profil pełnej bazy (wynik analizy pliku)

- `active` = `1` u wszystkich, `comment` i `pesel` puste u wszystkich.
- `discount`: 16 093 × `0.00`, 7 × `5.00`, 1 × `10.00`.
- **Bez żadnego adresu: 10 919 klientów (68%)**. 1 adres: 4 180, 2 adresy: 885, 3+: 117.
- Brak imienia lub nazwiska na poziomie klienta: 1 409 (część da się uzupełnić z adresu).
- NIP w adresie 1: 2 922 klientów.
- Kraj w źródle jest w języku lokalnym (`Deutschland`, `España`, `Österreich`…), ale jest też
  `country_code` (ISO 3166-1 alpha-2) – PL 1 622, DE 1 075, FR 707, ES 207, NL 186, GB 185…
- E-mail: brak pustych, **4 duplikaty**.
- Daty rejestracji: 2020-04-06 – 2026-10-19.
- Plik testowy ma w nagłówku `email ` (ze spacją na końcu) – konwerter będzie przycinał nagłówki.

## Dane wyjściowe

`wynik/import_klientow_idosell.csv` – plik zgodny ze specyfikacją
https://www.idosell.com/pl/developers/import-danych/import-klientow/ oraz
`wynik/raport.csv` z listą klientów pominiętych/poprawionych i powodem.

## Mapowanie pól (propozycja)

| Źródło | IdoSell | Uwagi |
|---|---|---|
| `email` | `email`, `login` | login = e-mail (małe litery, przycięty) |
| – | `password` | puste → IdoSell generuje hasło sam |
| `date_add` | `date_of_registration` | format już zgodny `YYYY-MM-DD GG:MM:SS` |
| `active` (1/0) | `block_account` (`n`/`y`) | |
| `first_name`, `last_name` | `firstname`, `lastname` | 1:1; **nie uzupełniamy z adresu** (decyzja 2026-10-22) |
| `discount` | `rebate` | `0.00` → puste (wyłączony) |
| adres z `address_default = 1` | `street`, `zipcode`, `city`, `country`, `phone`, `companyname`, `taxidnumber`, `province` | `street` = `street_1` + `street_2`; `province` tylko US/CA |
| `country_code` | `country` | tłumaczenie ISO2 → polska nazwa skrócona (`DE` → `Niemcy`), słownik w skrypcie |
| adresy z `address_shipping_default = 1` + pozostałe | `delivery_address_*1…N` | adres wysyłkowy domyślny jako `1` |
| adresy z NIP-em | `payer_address_*N` | do potwierdzenia, czy przenosić osobno |
| – | `shop` | ID sklepu docelowego – **do podania** |
| – | `mailing`, `newsletter_sms` | `n` (brak zgód w źródle) |
| `comment`, `pesel`, `address_name` | – | puste/zbędne, pomijam |

## Zmiana zakresu (2026-10-22): działamy od strony przeglądarki

Decyzja użytkownika: import realizujemy w panelu IdoSell przez Claude in Chrome. Kolejność:

1. Rozpoznanie formularza `import-clients.php?mode=own` na zooart6: jakie formaty przyjmuje, czy
   pozwala zmapować nieznane nagłówki źródła (`first_name`, `street_1 1`…) na pola IdoSell.
2. Wgranie `źródło/test.client.csv` → „sprawdź i zaimportuj” → mapowanie → import **bez wysyłki
   maila** (nie zaznaczam klientów do wiadomości „Mail po zaimportowaniu klientów przez support”).
3. Weryfikacja karty klienta testowego.
4. Skrypt konwertujący z sekcji niżej powstaje tylko wtedy, gdy panel nie poradzi sobie z
   formatem źródła (wtedy wracam z tym do akceptacji).

### Wyniki rozpoznania w panelu zooart6 (2026-10-22)

- Panel główny osadza formularz w iframe, więc pracuję bezpośrednio na `/panel/import-clients.php?mode=own`.
  Strona nigdy nie osiąga stanu `document_idle`, więc działa tylko `javascript_tool`.
- Upload: dropzone. Po „sprawdź i zaimportuj” panel pyta o separator (`,` / `;` / `:`), a przy
  nieznanych nagłówkach pokazuje mapowanie kolumna → pole. Lista pól obejmuje tylko pola główne
  klienta: **brak `delivery_address_*` i `payer_address_*`**, nie da się skleić `street_1`+`street_2`
  ani zmapować jednej kolumny na dwa pola (`email` → `email` i `login`).
- **Surowy plik źródłowy z mapowaniem w panelu daje pusty rekord** (wszystkie pola puste, `Sklep 1,2`).
  Tak samo wyszedł import z 2026-10-19 (cała baza → 1 pusty klient). Mapowanie w panelu nie działa
  dla tego pliku.
- **Plik z nagłówkami IdoSell (separator `,`, UTF-8, CRLF) czyta się poprawnie, bez błędów**: login,
  e-mail, imię, nazwisko, adres, kraj `Włochy`, telefon, firma, NIP, data rejestracji. Puste `shop` → `1,2`.
- Import do bazy to osobny krok: zaznaczenie klientów → „Importuj klientów do bazy sklepu” (bez opcji maila).
  Mail wysyła się osobno z widoku „Klienci zaimportowani, niepoinformowani”.
- **Przyczyna pustego rekordu (testy A/B/D, 2026-10-22):** każda kolumna spoza listy IdoSell
  uruchamia krok mapowania, a po nim **cały rekord jest pusty**, także kolumny natywne (`login`).
  A: surowy + `login` → pusto; B: nagłówki IdoSell + kolumny źródła → pusto; D: działający plik +
  jedna kolumna `dodatkowa` → pusto. Brak loginu, spacja w `email `, `active` i cudzysłowy nie są przyczyną.
  **Plik wyjściowy musi zawierać wyłącznie kolumny IdoSell.**
- **Import bez adresu działa** (`test_bez_adresu.client.csv`, 2026-10-22): klient bez ulicy/kodu/miasta
  zaimportowany; panel wstawia domyślnie kraj `Polska`, język `pol`, walutę `PLN`, typ `private`.
  **Brak imienia i nazwiska = błąd importu**: „Nie podano imienia klienta (jeżeli klient jest firmą,
  możesz uzupełnić tylko pole z nazwą firmy)” / „Nie podano nazwiska klienta”. W pełnej bazie
  dotyczy to 1 404 klientów (114 z nich ma nazwę firmy).
  Decyzja: zostawiamy bez zmian – panel ich odrzuci, lista do pobrania jako „błędne rekordy”.
- Klient testowy z `test_idosell.client.csv` zaimportowany (1/1, bez błędów), bez wysyłki maila.
- **Wniosek:** konwersja do nagłówków IdoSell jest konieczna. Wgranie, weryfikacja i import zostają w przeglądarce.

## Zakres ostateczny (decyzja 2026-10-22)

Przemianować pełną bazę wyłącznie na kolumny sprawdzone w udanym teście:
`login,email,firstname,lastname,street,zipcode,city,country,phone,companyname,taxidnumber,date_of_registration,rebate`.

- login = email; imię/nazwisko 1:1 (bez uzupełniania z adresu); adres = `address_default 1`,
  a gdy go nie ma – pierwszy niepusty; dodatkowe adresy pomijamy.
- `country` = polska nazwa z `country_code` (58 kodów, słownik w skrypcie); `street_2` puste w całej bazie.
- `rebate` `0.00` → puste. Klienci bez adresu zostają z pustymi polami adresu (bez testu – decyzja użytkownika).
- Duplikaty e-maili: zostaje pierwszy wiersz, reszta trafia do raportu.
- Język/waluta oraz test pustego adresu – nie robimy.

## Planowane zmiany / pliki (konwersja skryptem – wymagana)

W folderze `Migracja_klientow/`:

1. `konwertuj_klientow.py` – Python 3.8+, tylko biblioteka standardowa, strumieniowo
   (`csv.DictReader`), wykrywa plik `*.client*.csv` w `źródło/`, pyta interaktywnie o ID sklepu
   i separator; zapisuje `wynik/import_klientow_idosell.csv` + `wynik/raport.csv`.
2. `uruchom.bat` – działa po dwukliku (interaktywnie).
3. Test na panelu `zooart6.yourtechnicaldomain.com` przez Claude in Chrome: import
   przekonwertowanego `test.client.csv`, **bez zaznaczania klientów do wysyłki maila**, potem
   weryfikacja karty klienta (dane, adresy, rabat, data rejestracji) i sprawdzenie, czy żaden mail
   nie poszedł (kolejka/historia wiadomości klienta).
4. Dopiero po udanym teście – konwersja pełnej bazy (import produkcyjny wykonuje użytkownik lub ja
   na wyraźne polecenie).

## Założenia

- Import przez „Dodać nowych klientów” z pliku własnego, nie przez „Migrację z innego sklepu”.
- Mail „Mail po zaimportowaniu klientów przez support” wysyła się tylko po ręcznym zaznaczeniu
  klientów i wybraniu tej wiadomości – samego importu nie łączymy z wysyłką. Dodatkowo na teście
  sprawdzę, czy wiadomość jest włączona w Wiadomościach transakcyjnych i czy import nie wyzwala
  jej automatycznie (np. „rejestracja klienta”).
- Kodowanie wyjścia UTF-8. Separator: pomoc IdoSell mówi o **średniku**; mój domyślny to przecinek –
  sprawdzę na teście, który panel przyjmuje, i ustawię ten działający.
- Duplikaty e-maili (4) – scalam do jednego klienta (najstarsza data rejestracji, wszystkie adresy),
  wpis w raporcie.

## Otwarte pytania

1. **Klienci bez adresu (10 919 = 68% bazy).** Specyfikacja IdoSell wymaga `street`, `zipcode`,
   `city`. Opcje: (a) sprawdzić na teście, czy panel przyjmie puste pola; (b) jeśli nie – wstawić
   zaślepkę (np. `-`) i kraj z domyślnego; (c) pominąć takich klientów. Proponuję (a), a przy
   odmowie (b) – czy się zgadzasz?
2. **Brak imienia/nazwiska** po uzupełnieniu z adresu – zaślepka (np. część e-maila przed `@`) czy pominięcie?
3. **ID sklepu** (`shop`) na zooart6 i w sklepie docelowym oraz **język/waluta** klientów –
   wszyscy `pol`/PLN, czy język wg kraju (DE → `ger`, FR → `fre`…)? Baza jest mocno
   międzynarodowa (PL to tylko ~30% klientów z adresem).
4. Czy NIP przenosić tylko jako `taxidnumber` głównego adresu, czy też jako dane nabywcy
   (`payer_address_*`)?
5. Zgody newsletterowe – w źródle ich nie ma, więc wszyscy `n`. Potwierdzasz?
6. Jaka platforma jest źródłem (dla notatki w dokumentacji)? Nie blokuje pracy.
