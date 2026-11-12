# ANALIZA: weryfikacja pliku Amazon uzupełnionego przez klientkę (MagniCreatix)
Zadanie ClickUp: [MagniCreatix.pl - Aktualizacja/dodanie oferty na amazon](https://app.clickup.com/t/869fhg0k0) · Klient: magnicreatix.pl · Data: 2026-11-12

## Cel
Natalia (opiekun) odesłała 2026-11-12 plik `Amazon_MagniCreatix_2026-11-06.xlsm` uzupełniony przez klientkę i pyta, czy jest poprawnie wypełniony. Trzeba:
- porównać go z naszą wersją z 2026-11-06;
- sprawdzić go względem wymagań szablonu Amazon `TOY_BUILDING_BLOCK`;
- sprawdzić, czy klientka odpowiedziała na 7 pytań GPSR z 2026-11-04;
- przygotować odpowiedź do ClickUp.

## Dane wejściowe i wyjściowe
Wejście (lokalnie, poza gitem, w `../MagniCreatix/`):
- `Amazon_MagniCreatix_2026-11-06.xlsm`: nasza wersja (1 164 162 B);
- `Plik od klienta/Amazon_MagniCreatix_2026-11-06.xlsm`: wersja klientki (1 311 862 B, to samo co ostatni załącznik w ClickUp);
- `TOY_BUILDING_BLOCK.xlsm`: pusty szablon (arkusze z listami wartości i definicjami pól);
- `raport_2026-11-06.csv`: nasz raport per SKU (akcja, tytuły, zdjęcia, uwagi);
- `products_export-magnicreatix.pl-2026-11-05_10.32.(csv|xml)`: eksport IdoSell.

Wyjście:
- **narzędzie** (w gicie): `Weryfikacja_pliku/porownaj_amazon.py` + `run_porownaj.bat` (interaktywny, działa po dwukliku). Porównuje dwa pliki Amazon i waliduje je względem szablonu;
- **wyniki** (lokalnie, poza gitem): `../MagniCreatix/weryfikacja_2026-11-12/`:
  - `weryfikacja_2026-11-12.md`: podsumowanie, czyli co jest dobrze, co do poprawy i czego brakuje;
  - `zmiany_klientki.csv`: SKU, kolumna, nasza wartość, wartość klientki, typ (dopisane / nadpisane / usunięte);
  - `uwagi_per_sku.csv`: błędy walidacji i braki GPSR;
  - `komentarz_clickup.txt`: odpowiedź dla Natalii (wkleja użytkownik);
  - opcjonalnie poprawiona kopia `.xlsm`, ale tylko oczywiste poprawki formatu i tylko po zgodzie użytkownika.

## Plan
1. **Odczyt plików `.xlsm`:**
   - arkusz z produktami, wiersze nagłówków (etykieta, nazwa pola);
   - arkusze definicji i list dozwolonych wartości z szablonu.
   Pierwszy wybór to biblioteka standardowa (`zipfile` + XML), bo `openpyxl` nie jest zainstalowany. Instalacja `openpyxl` tylko po zgodzie użytkownika.
2. **Porównanie** nasza wersja ↔ wersja klientki, komórka po komórce, wiersze dopasowane po SKU:
   - dopisane pola;
   - nadpisane nasze wartości (do wyjaśnienia);
   - nowe lub usunięte wiersze;
   - zmiany makr i arkuszy (tylko informacyjnie).
3. **Walidacja według szablonu:**
   - pola wymagane dla akcji (Utwórz lub zastąp / Edytuj częściowa);
   - wartości spoza list dozwolonych;
   - formaty liczb i jednostek (waga, wymiary);
   - EAN (13 cyfr, suma kontrolna);
   - powiązania rodzic–wariant;
   - wielkie litery w tytułach, punktorach i opisach (ryzyko blokady);
   - długości pól.
4. **Kontrola GPSR**, czyli 7 punktów z komentarza z 2026-11-04:
   - wiek (ustalone: od 3 lat);
   - ostrzeżenia z opakowania (magnesy, małe elementy);
   - materiał (ustalone: plastik, magnes);
   - dane producenta;
   - osoba odpowiedzialna w UE;
   - baterie (robot KIDIBOTS, świecące kulki);
   - waga i wymiary 13 nowszych produktów.

   Przy każdym punkcie: czy jest uzupełniony, czy jest spójny we wszystkich wierszach i jakie są wyjątki. Kraj pochodzenia ustawiliśmy domyślnie na Polskę, więc sprawdzam, czy klientka go potwierdziła albo zmieniła.
5. **Wynik:** pliki z sekcji „Wyjście” + `komentarz_clickup.txt`. W komentarzu: krótkie „gotowe / do poprawy”, lista konkretnych poprawek per produkt i otwarte pytania do klientki.

## Założenia
- Przeglądarka nie jest potrzebna. Pracuję na plikach. Panelu IdoSell i Seller Central nie dotykam.
- Plik klientki jest źródłem prawdy dla danych GPSR. Nasze dane (tytuły, zdjęcia, punktory) były już zweryfikowane 2026-11-06, więc ich zmiany przez klientkę zgłaszam jako „do potwierdzenia”, a nie jako błąd.
- Dane klientów (pliki `.xlsm`, eksporty, wyniki) nie trafiają do gita. Do gita idzie tylko narzędzie i ta analiza.
- Skrypt, który zbudował plik z 2026-11-06, nie zachował się w repo. Porównanie piszę od nowa jako narzędzie wielokrotnego użytku (kolejne rundy poprawek, inni klienci na Amazonie).

## Otwarte pytania
- Czy wolno zainstalować `openpyxl`? Tylko jeśli odczyt biblioteką standardową okaże się niewystarczający.
- Domena logowania do panelu IdoSell magnicreatix.pl jest nieznana (do pliku klienta). Do tej weryfikacji nie jest potrzebna.

## Zasady sesji
- ClickUp tylko do odczytu; komentarz → `komentarz_clickup.txt` (wkleja użytkownik).
- Git: worktree .worktrees/amazon_magnicreatix, gałąź amazon_magnicreatix; nie przełączaj gałęzi; /zapisz i /zamknij wykonuje użytkownik w tym oknie.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: nie — jedna sesja z Claude in Chrome naraz.
- Zamówienie testowe i sprawdzanie zdarzeń na stronie sklepu: nie dotyczy.
- Przeczytaj `SI/Klienci/magnicreatix.pl.md` i przestrzegaj zasad klienta.
- `../MagniCreatix/` to dowiązanie (junction) do folderu w `Domino`, więc pliki zapisane tam lądują fizycznie w `Domino` i są poza gitem (`.gitignore`). Narzędzie i analizę zapisuję w `Weryfikacja_pliku/` (w worktree, do commita).

## Decyzje
- 2026-11-12: użytkownik zgodził się na instalację `openpyxl` (odczyt `.xlsm`).
- 2026-11-12: wynik to sam raport, bez poprawionej kopii `.xlsm`.

## Stan
- 2026-11-12: analiza wstępna (sesja /zadanie).
- 2026-11-12: plan zaakceptowany, start implementacji.
- 2026-11-12: gotowe narzędzie `porownaj_amazon.py` i `run_porownaj.bat`. Poza zakresem z planu doszły kontrole logiczne: produkt większy lub cięższy od opakowania, ta sama wartość w ≥ 6 wierszach, przeciągnięta seria liczb, kraj spoza UE bez osoby odpowiedzialnej. W `uwagi_per_sku.csv` doszła kolumna `zrodlo_wartosci` (klient / nasza wersja).
- 2026-11-12: wyniki w `../MagniCreatix/weryfikacja_2026-11-12/`. Werdykt: plik nie jest gotowy do wgrania.
  - Błąd krytyczny: nagłówek kolumny 227 nadpisany ostrzeżeniem o magnesach.
  - Wymiary i wagi wpisane jako wartości zastępcze (55×40×20 we wszystkich SKU, seria 5,0–5,9 kg).
  - Brakuje rodzaju baterii i osoby odpowiedzialnej w UE (kraj: Chiny).
  - Komentarz do ClickUp: `komentarz_clickup.txt`.
