# ANALIZA — Optymalizacja integracji IdoSell ↔ Facebook (Meta) Ads

Data: 2026-10-14 (wersja 2 — po uwagach użytkownika)

## Cel (własnymi słowami)

Powtarzalna, okresowa weryfikacja integracji sklepu IdoSell z Meta Ads, wykonywana w przeglądarce (Claude in Chrome) dla wielu sklepów. Punktem startu jest zadanie w ClickUp, którego nazwa wskazuje domenę sklepu. Efekt: lista problemów, raport wewnętrzny, raport dla klienta i — po akceptacji — poprawki w panelach.

Charakter: **przegląd stanu i regresji** („czy coś się nie zepsuło / nie zmieniło”), nie pełny audyt wdrożeniowy. Większość konfiguracji ma pozostać domyślna.

## Wejście

- Zadanie ClickUp → domena sklepu (z nazwy zadania).
- Panel IdoSell sklepu (zalogowana sesja w Chrome).
- Meta Business Manager: Commerce Manager (katalog), Events Manager (Pixel / zbiór danych).
- Integracja FB jest prawie zawsze natywna (bez GTM). Odstępstwo odnotowuję w raporcie.

## Wyjście

1. `FB/raporty/<domena>_<RRRR-MM-DD>.md` — raport wewnętrzny: znalezisko → gdzie → wpływ → rekomendacja → status.
2. **Raport dla klienta** — krótki, nietechniczny język, bez danych wewnętrznych.
3. Komentarz w zadaniu ClickUp z podsumowaniem i linkami do raportów.
4. Po akceptacji: lista wdrożonych zmian (przed/po), dopisana do raportu wewnętrznego.

## Lista kontrolna

### A. Panel IdoSell
1. **Cennik dostaw** — czy się nie zmienił względem poprzedniej weryfikacji (koszty, progi darmowej dostawy, kraje). Zmiana bez aktualizacji feedu lub reklam = rozjazd cen dostawy.
2. **Generowanie feedu FB** — czy feed jest włączony i czy data ostatniego wygenerowania jest aktualna.
3. **Historia pobierania feedu** — czy nie ma błędów, czy Meta regularnie pobiera plik.
4. **Konfiguracja integracji** (Pixel, Conversions API, ustawienia feedu) — tylko kontrola, czy nic nie odbiega od wartości domyślnych lub ustalonych.
5. **Parametry towarów vs XSLT** (dodane 2026-10-14) — lista parametrów w sklepie porównana ze zmiennymi `*_nazwa_w_panelu` w sterowniku. Wypisuję: nowe parametry pasujące do istniejących zmiennych (kolor, materiał, płeć, grupa wiekowa, rozmiar…), parametry kluczowe do rozważenia (np. `custom_label`, `product_detail`) oraz te, które mają niską jakość, małe pokrycie albo wymagałyby dużo pracy. Tylko raport, bez zmian w XSLT.

### B. Meta — Commerce Manager (katalog)
1. **Wczytanie feedu** — czy przy ostatnim pobraniu wczytał się cały feed (liczba pozycji w feedzie vs w katalogu), status ostatniego pobrania.
2. **Diagnostyka katalogu** — czy nie pojawił się wysyp błędów. Typowe drobne problemy: aktualność cen, stany, niedostępna strona produktu lub zdjęcie (crawler). Skala i trend ważniejsze niż pojedyncze sztuki.
3. **Dopasowanie katalogu z Pixelem** — procent zdarzeń (ViewContent, AddToCart, Purchase) z `content_ids` dopasowanymi do pozycji katalogu.
4. **Raport błędów** — lista problemów z liczbą pozycji i przykładami ID.

### C. Meta — Events Manager (Pixel / zbiór danych)
1. **Ilość zdarzeń** — czy wolumen się nie załamał (trend kilku dni), czy wszystkie zdarzenia standardowe nadal się pojawiają.
2. **Jakość dopasowania zdarzeń (EMQ)** — wynik per zdarzenie, spadki względem poprzedniej weryfikacji.
3. **Diagnostyka** — ostrzeżenia Pixela i CAPI, deduplikacja, brakujące parametry.
4. **Ustawienia** — tylko kontrola (domyślne zostają).

## Zasady pracy

- Sesje w Chrome: jeśli panel nie jest zalogowany, otwieram stronę logowania i proszę Cię o zalogowanie. Nie wpisuję haseł.
- **Domyślnie tylko odczyt.** Zmiany w panelach dopiero po akceptacji raportu, każda pozycja osobno, z zapisem „przed”.
- **Zamówienie testowe tylko za wyraźną zgodą** dla danego sklepu: zalogowany na konto klienta, metoda płatności zawsze „przelew zwykły”.
- Porównanie z poprzednią weryfikacją (np. cennik dostaw, EMQ) na podstawie poprzedniego raportu w `FB/raporty/` (jeśli istnieje). Przy pierwszej weryfikacji zapisuję stan bazowy.

## Ustalenia (wersja 3)

- **Pilotaż:** zadanie ClickUp `869c8x2g9` — „Pyrawinyl.pl FbAds - Optymalizacja katalogu i API konwersji” (lista „Pyrawinyl.pl - Obsługa Marketing”, cykl co 3 miesiące: czy działa API konwersji, czy da się zoptymalizować katalog Meta).
- **Interwał:** 90 dni. Porównanie z poprzednim raportem sprzed ~90 dni; trendy wolumenu i EMQ z najdłuższego zakresu, jaki pokazuje Events Manager.
- **Raport dla klienta:** zwykły `.docx` na dysku, ze zrzutami ekranu kluczowych elementów. Do zadania ClickUp użytkownik dodaje go sam z czterozdaniowym komentarzem — przygotowuję treść komentarza, nie publikuję jej.

## Rozwiązanie techniczne

### Zrzuty ekranu
Zrzuty z narzędzia Claude in Chrome trafiają tylko do mnie, nie na dysk. Dlatego zapisuję je skryptem Python (Pillow `ImageGrab`, już zainstalowany): okno Chrome musi być widoczne na ekranie, skrypt wycina obszar okna przeglądarki (WinAPI przez `ctypes`) i zapisuje PNG.
- Zapis do `FB/raporty/<domena>_<RRRR-MM-DD>/zrzuty/NN_<opis>.png`.
- Zakres: status feedu i historia pobierania (IdoSell), cennik dostaw, przegląd katalogu i diagnostyka (Commerce Manager), wolumen zdarzeń, EMQ i dopasowanie katalogu (Events Manager).
- Przed zrzutem przewijam do właściwego elementu; dane osobowe klientów (np. lista zamówień) nie trafiają na zrzuty.

### Generator `.docx`
- `narzedzia/raport_docx.py` (od 2026-10-21 wspólny z GMC, w `Optymalizacja_Integracji/narzedzia/`) — buduje raport dla klienta z pliku `dane.json` (znaleziska, rekomendacje, ścieżki zrzutów) zapisanego przeze mnie w trakcie weryfikacji.
- Biblioteka `python-docx` — **wymaga instalacji** (`pip install python-docx`), bo jej nie ma. Alternatywa bez zależności: ręczne składanie XML w ZIP (więcej kodu, trudniej w utrzymaniu).
- Struktura: nagłówek (sklep, data, okres), podsumowanie w 3–4 punktach, sekcje IdoSell / Katalog / Piksel i API konwersji (stan + zrzut + rekomendacja), lista zalecanych działań.
- Obok: `komentarz_clickup.txt` — 4 zdania do wklejenia w zadaniu.

### Uruchamianie „jedną zakładką”
Zakładka w Chrome ani przycisk w ClickUp nie uruchomią Claude Code (przeglądarka nie ma dostępu do terminala). Propozycja:
1. **Skill `weryfikacja-fb`** (`.claude/skills/` w repo) — cała procedura. Wywołanie: `/weryfikacja-fb <link do zadania ClickUp>`.
2. **`FB/Weryfikacja_FB.bat`** — skrót na pulpicie/pasku: po dwukliku pyta o link do zadania ClickUp i uruchamia `claude` w tym folderze z poleceniem skilla.
3. Opcjonalnie skrót (shortcut) w rozszerzeniu Claude in Chrome — działa tylko w przeglądarce, bez zapisu `.docx` na dysk, więc wyłącznie do szybkiego podglądu.

## Wnioski z pilotażu (pyrawinyl.pl, 2026-10-14) — do skilla

**Zasady od użytkownika:**
- Feed XML często pochodzi z własnego XSLT w `/panel/config-pricecomparers.php` (serwis „Facebook ads …”), a nie z natywnego feedu FB. Sprawdzać tam: status, liczbę towarów, „Historia pobrań”, „Ustawienia” (sterownik, eksport, IOF).
- Historia pobrań: sprawdzać **pierwsze 3 strony, potem co 10.** (nie wszystkie).
- **Sterownik XSLT**: zakładamy, że działa, skoro Meta przyjmuje feed. Nie uruchamiam podglądu ani przykładowych danych i nie analizuję logiki. Porównuję tylko zmienne konfiguracyjne z początku sterownika (`*_nazwa_w_panelu`, wartości list, koszty dostawy) z parametrami w `/panel/parameters.php`. Drzewo rozwijam linkami `a.showChildren` i liczę wartości.
- **Diagnostyka piksela / CAPI**: IdoSell zawsze wysyła z API więcej zdarzeń niż było działań i polega na deduplikacji Meta. Mamy podwójną integrację: Purchase z API pochodzi z aktywacji „Meta Pixel” w panelu, a pozostałe zdarzenia API z FBE2. Proporcja rzędu kilku razy (Purchase serwer/przeglądarka ~5×, brak UA i `fbp` w części zdarzeń) jest **normą**. **Błąd** to skok zdarzeń API kilkadziesiąt lub sto razy w górę. Wtedy ustalam z wykresów Events Managera dzień i godzinę początku, robię zrzuty (wykres zdarzeń, szczegóły zdarzenia serwer vs przeglądarka, diagnostyka) i przygotowuję zgłoszenie do obsługi klienta IdoSell z przedziałem czasowym. Porównuję też ze stanem bazowym z poprzedniego raportu.
- **Odrzucone produkty**: prośbę o weryfikację wysyłam tylko wtedy, gdy produkt faktycznie nie narusza zasad.
- **FBE2** przekierowuje na domenę techniczną `clientXXXXX.idosell.com` i wymaga ponownego logowania — sprawdzać **tylko przy problemach ze zdarzeniami API**.

**Technika:**
- Panel IdoSell nigdy nie osiąga `document_idle`, więc `screenshot`, `find` i `get_page_text` z rozszerzenia nie działają. Działa `javascript_tool` (krótkie wywołania < 45 s) i `computer.left_click` po współrzędnych z `getBoundingClientRect()`.
- Zrzuty: `narzedzia/zrzut.py` (PrintWindow). Przed zrzutem oznaczyć kartę: `document.title='[CLAUDE] '+…`, a potem `zrzut.py "[claude]" plik.png --obszar strona` (ucina też pasek zakładek i baner debugowania). Współrzędne viewportu = współrzędne na zrzucie.
- Filtr rozszerzenia blokuje zwrot tekstu z parametrami URL lub tokenami, dlatego XSLT analizuję w przeglądarce (zmienne, `select`, `test`), bez zwracania całej treści.
- Meta: `business.facebook.com/commerce/` otwiera ostatnie portfolio, więc przełączam je listą „Portfolio firmowe”. Potrzebne adresy: `commerce/catalogs/<ID>/data_sources`, `…/events/`, `events_manager2/list/dataset/<pixel>/overview|diagnostics`, `…/overview/<Event>/event_matching|event_deduplication` (z `business_id`).
- Raport: `raporty/<domena>_<data>/` z `dane.json` → `narzedzia/raport_docx.py <folder>` generuje `.docx` i `komentarz_clickup.txt`; do tego ręcznie `RAPORT_wewnetrzny.md`.

## Kolejne kroki

1. Pilotaż na Pyrawinyl.pl: weryfikacja (tylko odczyt), zrzuty, raport wewnętrzny `.md`, `.docx` dla klienta, komentarz do ClickUp.
2. Doprecyzowanie listy kontrolnej na podstawie rzeczywistych ekranów paneli.
3. ✅ Skill `.claude/skills/weryfikacja-fb/SKILL.md` (w katalogu głównym repo) + `FB/Weryfikacja_FB.bat` (ASCII, bez `chcp`, bo cmd psuje odczyt pliku UTF-8 po `chcp 65001`) — 2026-10-14. Następnie ten sam schemat dla GMC (`GMC/`).
