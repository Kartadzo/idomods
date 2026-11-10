# Historia sterowników IdoSell

Własna historia zmian sterowników XSLT w panelu IdoSell. Panel nie zapisuje, kto i kiedy zmienił sterownik, a feed pokazuje zmianę z opóźnieniem kilku godzin. Analiza, decyzje i pułapki panelu: `../../ANALIZA_historia_sterownikow.md`.

## Pliki
- `historia.py` + `run_historia.bat`: odbiornik dla przeglądarki, składanie i porównanie zrzutów, dziennik wdrożeń, kontrola przed `/zamknij`, hash i walidacja pliku. Dwuklik `.bat` otwiera menu.
- `zrzut_panel.js`: fragment dla Claude in Chrome (`BM.zrzutSklepu`, `BM.otworz`, `BM.sprawdz`, `BM.zapisz`), serwowany przez odbiornik.

## Dane klienta (`Zmiany_sterownikow/<klient>/`)
| Ścieżka | Co | Git |
|---|---|---|
| `_historia/<RRRR-MM-DD_GGMMSS>_<rodzaj>.json` | zrzut: ID, nazwa, sklepy, status, godzina generowania, SHA-256, liczba linii, znacznik | tak |
| `_historia/kopie/<shop>_<id>_<sha12>.xml` | treść każdego sterownika (do przywrócenia) | nie |
| `_historia/_robocze/<sesja>/shop<n>.json` | części zrzutu od przeglądarki | nie |
| `_historia/wyjatki_duplikatow.json` | `[[id, id], …]` pary serwisów z tym samym sterownikiem celowo | tak |
| `dziennik_wdrozen.csv` | jeden wiersz na wgranie (bez osoby) | tak |

`<klient>` = nazwa folderu klienta w `Zmiany_sterownikow/` (np. `ezebra`). Rodzaje zrzutu: `start`, `przed_wgraniem`, `po_wgraniu`, `zapis`, `koniec`, `reczny`.

## Procedura (dla Claude'a)

### Zrzut (każdy rodzaj)
1. Odbiornik w tle (Bash, `run_in_background`): `python historia.py odbiornik`. Sprawdzenie: `curl -s http://127.0.0.1:8765/ping`.
2. `python historia.py sesja --rodzaj <rodzaj>` → nazwa sesji.
3. Dla **każdego sklepu klienta** (`shop=` z pliku klienta): nawigacja na `https://<domena logowania>/panel/config-pricecomparers.php?shop=<n>`, potem `javascript_tool`:
   ```js
   eval(await (await fetch('http://127.0.0.1:8765/zrzut_panel.js')).text());
   await BM.zrzutSklepu({klient: '<klient>', sesja: '<sesja>'});
   ```
   Wynik: `shop N: X serwisów (ze sterownikiem Y), nowe kopie Z, błędy 0; odbiornik: OK …`. Błędy ≠ 0 → zrzut niepełny, ustalić przyczynę (wylogowanie, lista się nie załadowała).
   Pierwszy raz na nowej domenie Chrome może zapytać o dostęp strony do sieci lokalnej (urządzenia lokalne). Zgodę daje użytkownik. Do tego czasu wywołanie wisi (limit 45 s narzędzia). Wtedy uruchamiam je bez `await` (wynik do `window.__w`) i odczytuję po chwili.
4. `python historia.py zloz --klient <klient> --sesja <sesja> [--zadanie <folder zadania>]` → raport zmian względem poprzedniego zrzutu klienta (zmiany bez wpisu w dzienniku, nowe duplikaty, niezgodne znaczniki). Kod 1 = jest coś do zgłoszenia.

### Start pracy ze sterownikami (`/zadanie`, skille feedów)
Zrzut `start` przed pierwszą zmianą. Zmiany od poprzedniego zrzutu klienta zgłaszam użytkownikowi od razu (ktoś pracował przed nami).

### Edycja sterownika
Do pliku, który **edytujemy** (nie przy samej kopii z panelu), dopisuję lub aktualizuję po deklaracji XML:
```xml
<!-- BM-SERWIS: shop=<n> | ID <id> | <nazwa serwisu> | plik <ścieżka od katalogu Domino> -->
<!-- BM-EDYCJA: <RRRR-MM-DD GG:MM> | <krótki opis zmiany> -->
```
Przed wgraniem: `python historia.py waliduj --plik <plik>` (XML + kompilacja XSLT przez lxml; zwykłe `python`, nie `-I`, bo lxml jest w pakietach użytkownika).

### Wgranie
Pytanie do użytkownika, osobno dla każdego zadania: **„Nowy sterownik wgrywasz Ty czy ja?”**
- **Użytkownik:** podaję listę `shop, ID, nazwa → plik`, robię zrzut `przed_wgraniem` i czekam na „wgrane”.
- **Claude** (zasady klienta, np. eZebra: bez wdrożeń w piątki). Dla każdego serwisu:
  1. zrzut `przed_wgraniem` (sklep serwisu);
  2. `python historia.py hash --plik <plik>` → `<sha>`;
  3. **przeładowanie** `config-pricecomparers.php?shop=<n>`, `BM.otworz(<id>)` → sprawdzam `nazwa`, `shopId`, że `BM-SERWIS` pliku wskazuje ten serwis, a `sha256` = stan z zrzutu;
  4. plik do schowka (`Set-Clipboard` z pliku, UTF-8), zaznaczenie widocznego pola serwisu (`focus()` + `select()`), `ctrl+v`;
  5. `await BM.zapisz(<id>, '<sha>')`: sprawdza hash pola **przed** kliknięciem, klika „Zapisz” w formularzu tego serwisu. `ODRZUCONE` = panel nie przyjął (komunikat w wyniku), stan w panelu bez zmian;
  6. przeładowanie i zrzut `po_wgraniu`, potem `python historia.py dziennik --klient <klient> --shop <n> --id <id> --plik <plik> --wgrywa Claude|użytkownik --zadanie <folder>`. Kod 1 (NIEZGODNE albo ten sam sterownik w innym serwisie) → procedura incydentu.

Po wgraniu przez użytkownika: krok 6 z `--wgrywa użytkownik`.

### `/zapisz`
Gdy w sesji była praca ze sterownikami i panel jest zalogowany: zrzut `zapis` wszystkich sklepów. Do commita: `_historia/*.json` i `dziennik_wdrozen.csv` klienta. Wylogowany panel → bez zrzutu, odnotowane w podsumowaniu.

### `/zamknij`: przebieg kontrolny
Zrzut `koniec` **wszystkich** sklepów klienta, potem `python historia.py kontrola --klient <klient>` (odniesienie: ostatni zrzut `start`, albo `--od <plik>`). Sprawdza:
- każdy zmieniony sterownik ma wpis w dzienniku z `TAK`, a w panelu jest wgrany plik (inaczej: **zapis poza planem**);
- wgrany sterownik nie występuje w innym ID (**zapis w dwóch serwisach**);
- zmiany statusu i nazwy, niezgodne znaczniki, brakujące sklepy w zrzucie.

Kod 1 → **bez merge**, procedura incydentu.

### Incydent
1. `INCYDENT_<RRRR-MM-DD>.md` w folderze zadania: serwisy, hashe przed/po, czasy zrzutów, przedział czasu zmiany, wpisy dziennika, objawy w GMC / Meta.
2. Przywrócenie poprzedniego stanu z `_historia/kopie/` (ta sama ścieżka wgrania, pytanie „Ty czy ja?” osobno dla przywrócenia), zrzut, potwierdzenie hashy.
3. Gdy wygląda na błąd IdoSell (np. jeden zapis w kilku serwisach bez śladu wgrania po naszej stronie): `zgloszenie_idosell.txt` (panel, sklep, ID, przedział czasu, hashe, kroki). Wysyła użytkownik.

Moment zmiany bez zrzutów: panel pokazuje tylko **zakończenie** generowania feedu (ok. 30 min po starcie, kolejka może przesunąć start o godziny). Przedział: start ostatniego poprawnego ≈ koniec − 30 min, do startu pierwszego błędnego ≈ koniec − 30 min.

## Testy (2026-11-10, zooart6, katalog `--baza` w scratchpadzie)
- Zrzut sklepów 1 i 2: 39 serwisów (jeden w obu sklepach), 26 ze sterownikiem, kopie 26, znany duplikat 10011/10015.
- Wgranie przez Claude'a na 10046 „CENEO TEST” (wyłączony): plik ze znacznikami → `ZGODNE` w dzienniku, znacznik odczytany w zrzucie; przywrócenie oryginału z `kopie/` → `ZGODNE`; `kontrola` start → koniec: OK, stan panelu = start.
- Dane sztuczne: `kontrola` wykryła brak sklepu w zrzucie, dwa zapisy poza planem, zapis w dwóch serwisach, zmianę statusu i niezgodny znacznik (kod 1).
- `porownaj_sterownik.py`: ostrzeżenie, gdy znacznik w panelu wskazuje inny plik niż wybrany.
