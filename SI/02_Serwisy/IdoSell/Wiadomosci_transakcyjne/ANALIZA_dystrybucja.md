# Analiza: wersja dystrybucyjna i porządki

Status: **zaakceptowana i wykonana 2026-10-13** — usunąć wszystko, `.exe` z ostrzeżeniem SmartScreen, założenia z §5 przyjęte.
Wykonanie: dane testowe (19 pozycji) przeniesione do **Kosza Windows** (odzyskiwalne, zamiast folderu `_DO_USUNIECIA_…`);
`.exe` zbudowany i sprawdzony w kopii tymczasowej (menu, rozpakowanie, raport obok `.exe`, pauza po błędzie).

Data: 2026-10-13 · Kontekst: narzędzie gotowe na gałęzi `wiadomosci-transakcyjne` (zostaje bez scalania — opcja 3).

## 1. Cel zadania

1. **Porządki:** usunąć z folderu narzędzia pliki powstałe podczas testów na panelu `zooart6`.
2. **Instrukcja dla osoby nietechnicznej:** krok po kroku, bez terminala i bez pojęć programistycznych.
3. **Folder dystrybucyjny z `.exe`:** gotowy do przekazania — działa po dwukliku na Windows, bez instalowania Pythona.

## 2. Porządki — co jest „plikiem testowym”

| Element | Rozmiar | Co to jest | Propozycja |
| --- | --- | --- | --- |
| `_pobrane/` (ZIP-y, `task0/`, `task11_koniec/`, luźne `.icf`) | 16 MB | eksporty i pliki z testów na zooart6 | **usunąć** |
| `Eksport i Import Treści/zooart6_shop1/` (4 eksporty, w tym pełny 144 wiadomości) | 15 MB | rozpakowane eksporty z testów | **usunąć** |
| `Edycja Działania/zooart6_shop1/` (2 CSV, 2 plany) | 4,5 MB | plany zmian z testów | **usunąć** |
| `Status/zooart6_shop1/status_2026-10-13_160750.md` | 108 KB | raport z testu | **usunąć** (pytanie 1) |
| `testy/`, `przegladarka/testy/` | — | testy automatyczne (67 + 12) | **zostawić** w źródłach — to zabezpieczenie przed regresją; **nie trafiają** do dystrybucji |
| `ANALIZA_*.md`, `PLAN_implementacji.md` | — | dokumentacja projektu | zostawić w źródłach, nie w dystrybucji |
| `.superpowers/sdd/PLAN_implementacji/` (korzeń repo) | — | rejestr postępu wykonania planu | usunąć |
| `wt/__pycache__`, `testy/__pycache__` | — | pliki tymczasowe Pythona | usunąć |

Wszystkie pozycje do usunięcia są w `.gitignore` (nie ma ich w repozytorium) — usunięcie jest nieodwracalne.
**Sposób:** zasady bezpieczeństwa nie pozwalają mi trwale kasować plików, więc przeniosę je do jednego folderu
`_DO_USUNIECIA_dane_testowe/` (poza strukturą narzędzia), a Ty usuniesz go jednym kliknięciem (lub zostawisz jako archiwum).
Puste foldery `Status/`, `Edycja Działania/`, `Eksport i Import Treści/`, `_pobrane/` zostają — program z nich korzysta.

## 3. Folder dystrybucyjny

```
dystrybucja/Wiadomosci_transakcyjne/
├── Wiadomości transakcyjne.exe     <- dwuklik: menu programu (jak run_wiadomosci.bat)
├── INSTRUKCJA.html                 <- instrukcja dla użytkownika (otwiera się w przeglądarce, da się wydrukować)
├── zakladka_do_Chrome.txt          <- zawartość bookmarklet.txt (adres zakładki)
├── konsola.js                      <- wariant awaryjny bez zakładki
├── Status/ · Edycja Działania/ · Eksport i Import Treści/ · _pobrane/   <- puste, program zapisuje tu wyniki
```

- `.exe` budowany **PyInstaller 6.14 (już zainstalowany — nic nie pobieram)**, tryb jednoplikowy, okno konsoli (menu tekstowe).
- Skrypt budujący w źródłach: `zbuduj_dystrybucje.bat` (przebudowanie po każdej zmianie kodu jednym dwuklikiem).
- Skill Claude in Chrome **nie** trafia do dystrybucji (wymaga Claude Code).

### Zmiany w kodzie potrzebne do `.exe`

1. **Katalog roboczy programu:** spakowany program rozpakowuje się do katalogu tymczasowego, więc `wt/wspolne.py`
   musi brać folder **pliku .exe** (`sys.executable`) zamiast folderu modułu — inaczej wyniki trafiałyby do katalogu tymczasowego i znikały.
2. **Folder Pobrane:** obecnie `%USERPROFILE%\Downloads`. Na komputerach z przeniesionym folderem (np. OneDrive) to inna ścieżka —
   odczyt rzeczywistej lokalizacji z Windows (Known Folder „Downloads”), z powrotem do `%USERPROFILE%\Downloads`, gdy się nie uda.
3. **Okno nie znika przy błędzie:** w `.exe` po nieoczekiwanym błędzie komunikat + „Naciśnij Enter, aby zamknąć”
   (dziś `.bat` ma `pause`, `.exe` by się zamknął i użytkownik nie zobaczyłby błędu).

Każda zmiana z testem (TDD), cały zestaw testów zielony, potem budowa i uruchomienie `.exe` na próbnym eksporcie
(tylko lokalnie — bez zapisu w panelu).

## 4. Instrukcja dla osoby nietechnicznej (`INSTRUKCJA.html`)

Zakres: tylko to, co robi użytkownik — **zakładka w Chrome + program `.exe`**. Bez terminala, Pythona, gita.

1. Co to jest i do czego służy (3 tryby jednym zdaniem każdy).
2. Jednorazowa instalacja: rozpakowanie folderu, dodanie zakładki (z obrazkowym opisem kroków), co zrobić, gdy Chrome nie przyjmie zakładki (konsola).
3. Scenariusz „Raport stanu wiadomości” (Status).
4. Scenariusz „Włączam / wyłączam wiadomości” (CSV w Excelu: które kolumny zmieniać, `tak`/`nie`, jak zapisać).
5. Scenariusz „Zmieniam / tłumaczę treść” (które pliki edytować, czym — Notatnik / VS Code, czego nie ruszać).
6. Weryfikacja po każdej zmianie — co znaczą „OK”, „nie zmieniło się”, „zmieniło się inaczej”.
7. Bezpieczeństwo: najpierw sklep testowy; import chwilowo wyłącza wysyłkę i narzędzie ją przywraca; migracja do innego sklepu — dodatkowe potwierdzenie.
8. Najczęstsze problemy (sesja wygasła, „Chrome blokuje pobieranie wielu plików”, Windows SmartScreen przy pierwszym uruchomieniu `.exe`, plik CSV zapisany w złym formacie).

Język prosty, bez żargonu; zrzuty ekranu — **nie** (nie mogę ich wiarygodnie wykonać z panelu klienta w tej sesji; opis słowny z nazwami przycisków).

## 5. Założenia (do potwierdzenia)

1. Instrukcja jako **HTML** (otwiera się dwuklikiem w przeglądarce, drukowalna) — bez Worda/PDF.
2. `.exe` i folder `dystrybucja/` **nie** trafiają do gita (binarka ~10 MB) — wpis w `.gitignore`; w repo zostaje skrypt budujący i źródło instrukcji.
3. Testy automatyczne zostają w źródłach.
4. `.exe` budowany na tym komputerze (Windows 10, 64-bit) — zadziała na Windows 10/11 64-bit.

## 6. Pytania i ryzyka

1. Czy pełny eksport 144 wiadomości z zooart6 i raport Status chcesz zachować jako materiał referencyjny, czy też do usunięcia?
2. Ryzyko: programy antywirusowe i Windows SmartScreen bywają podejrzliwe wobec `.exe` z PyInstallera („Nieznany wydawca”).
   Instrukcja opisze „Więcej informacji → Uruchom mimo to”. Alternatywa bez tego problemu: dystrybucja z `.bat` + przenośnym Pythonem (większa, ~30 MB).
3. Pierwsza wersja dystrybucyjna nadal ma nieprzetestowane na panelu scenariusze z wersją PL (z przeglądu końcowego) — instrukcja zaleci próbę na sklepie testowym przed użyciem u klienta.
