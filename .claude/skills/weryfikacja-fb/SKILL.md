---
name: weryfikacja-fb
description: Okresowa (co 90 dni) weryfikacja integracji sklepu IdoSell z Meta Ads (Facebook) przez Claude in Chrome — feed i cennik dostaw w panelu IdoSell, katalog w Commerce Managerze, piksel/API konwersji w Events Managerze, parametry vs konfiguracja sterownika XSLT. Wynik: raport .docx dla klienta ze zrzutami, raport wewnętrzny .md i 4-zdaniowy komentarz do ClickUp. Używaj, gdy użytkownik podaje zadanie ClickUp typu „<domena> FbAds - Optymalizacja katalogu i API konwersji”, mówi „weryfikacja FB”, „sprawdź integrację Meta/Facebook”, „przegląd katalogu i piksela” albo wywołuje /weryfikacja-fb <link>.
---

# Weryfikacja integracji IdoSell ↔ Meta Ads

KATALOG: `SI/Przeglądarka IdoSell/Optymalizacja_Integracji/FB/`. Specyfikacja i wnioski techniczne: `ANALIZA_FB_Ads.md`.
Wzorzec wyniku: `raporty/pyrawinyl.pl_2026-10-14/` (`dane.json`, `RAPORT_wewnetrzny.md`).

## Zasady (zawsze)
- **Tylko odczyt.** Niczego nie zapisuję w panelu IdoSell ani w Meta. Zmiany proponuję w raporcie, a wdrażam dopiero po zgodzie, pozycja po pozycji, z zapisem „przed/po”.
- Nie klikam: „Zapisz”, „Zmień”, „Wyłącz integrację”, „Usuń”, „Połącz teraz”, „Prześlij ponownie plik danych”, „Zaktualizuj”.
- Logowanie robi użytkownik. Strona „Logowanie użytkownika” lub logowanie Meta → proszę o zalogowanie i czekam.
- Zamówienie testowe tylko za wyraźną zgodą dla danego sklepu: zalogowany na konto klienta, płatność zawsze „przelew zwykły”.
- Komentarza do ClickUp nie publikuję. Użytkownik dodaje go sam razem z `.docx`.
- „Poproś o weryfikację” odrzuconych produktów tylko za zgodą i tylko wtedy, gdy produkt faktycznie nie narusza zasad.
- **Sterownik XSLT uznaję za działający**, skoro Meta przyjmuje feed. Nie uruchamiam „Podglądu wyników działania sterownika” ani „Odśwież zestaw przykładowych danych” i nie analizuję logiki. Czytam tylko zmienne konfiguracyjne z początku.
- **FBE2** (przekierowuje na `clientXXXXX.idosell.com` i wymaga ponownego logowania) otwieram tylko przy anomalii zdarzeń API (patrz krok C3).
- Na zrzutach nie może być danych osobowych klientów (listy zamówień, klienci).

## Technika Claude in Chrome
- Panel IdoSell nigdy nie osiąga `document_idle`, więc `screenshot`, `find` i `get_page_text` się zawieszają. Używam `javascript_tool` (krótkie wywołania, < 45 s, czekanie przez `await new Promise(r=>setTimeout(r,N))`) i `computer.left_click` po współrzędnych z `getBoundingClientRect()`.
- Filtr rozszerzenia blokuje wyniki z parametrami URL lub tokenami (`[BLOCKED: …]`). Z linków zwracam tylko `pathname`, a z XSLT pojedyncze zmienne bez adresów. Filtra nie obchodzę (żadnego base64 ani kodowania).
- Po `navigate` na Meta karta często przekierowuje (`business.` ↔ `eventsmanager.`). Przy błędzie „navigated to a different domain” robię `tabs_context_mcp` i ponawiam.
- **Zrzuty**: przed zrzutem oznaczam kartę: `document.title='[CLAUDE] '+document.title.replace(/^\[CLAUDE\] /,'')`, potem w KATALOGU:
  `python narzedzia/zrzut.py "[claude]" "raporty/<domena>_<data>/zrzuty/NN_opis.png" --obszar strona`
  (PrintWindow, okno nie może być zminimalizowane; ucina pasek zakładek i baner debugowania). Współrzędne na zrzucie = współrzędne viewportu do `left_click`. Podgląd roboczy zapisuję do scratchpada i oglądam przez Read.

## 0. Start
1. Link ClickUp → `clickup_get_task` (ID z `/t/<workspace>/<id>`). Domena = pierwszy człon nazwy zadania (np. „Pyrawinyl.pl FbAds …” → `pyrawinyl.pl`). Podaję użytkownikowi nazwę zadania i domenę.
2. `data` = dzisiaj (RRRR-MM-DD). Folder wyników: `raporty/<domena>_<data>/zrzuty/`.
3. Poprzedni raport: najnowszy `raporty/<domena>_*/RAPORT_wewnetrzny.md`. Biorę z niego identyfikatory (piksel, business_id, katalog, źródło feedu, ID serwisu) i **stan bazowy** do porównania (cennik dostaw, liczba produktów, proporcje zdarzeń, EMQ). Brak raportu → ta weryfikacja jest stanem bazowym.
4. `tabs_context_mcp` → nowa karta → `https://<domena>/panel/`.

## A. Panel IdoSell
1. `/panel/social-services.php`: stan integracji z ikon `fa-check-circle-o` (WŁ) / `fa-times-circle-o` (WYŁ) w wierszach: Logowanie FB, FBE2, Eksport bazy, Feed produktowy, Pobieranie katalogów, Meta Pixel. ID piksela: link w wierszu „Meta Pixel” → pole „Identyfikator Meta Pixel”.
2. `/panel/config-pricecomparers.php` (po ~6 s): wiersz „Facebook ads …”: status, „wygenerowany o godzinie”, eksportowane i wyeksportowane towary (porównać z Google ads i z poprzednim raportem). **Zrzut 01.** Jeśli nie ma takiego serwisu, a w A1 natywny feed jest WŁ, sprawdzam feed natywny.
3. „Wybierz → Historia pobrań” (`a` z tekstem „Historia pobrań” w wierszu): **pierwsze 3 strony, potem co 10.** (link „następna >”, numer strony z elementu z klasą active). Szukam zdarzeń innych niż „Pobranie pliku porównywarki”, hostów spoza `*.fbsv.net` i dużych luk. **Zrzut 02.**
4. „Wybierz → Ustawienia” (okno „Udostępnianie oferty…”, id serwisu w tytule): format IOF, opcje „Eksportuj”, sterownik (`textarea` > 60 000 zn. do `window.__xsl`). Ze sterownika czytam **tylko zmienne**: `Koszt_dostawy`, `kwota_dla_darmowej_dostawy`, `kwota_dla_wiekszych_zamowien`, `Koszt_dostawy_wiekszych_zamowien`, `Kraj_dostawy`, `*_nazwa_w_panelu` i listy wartości (`gender_*`, `age_group_*`, `kolor_*`, `material_*`). Okno zamykam nawigacją, bez zapisu.
5. Cennik dostaw: `/panel/config-shipping.php` (kraje i profile) → `/panel/config-shippingprofiles.php` → „Profile dostaw” → `[edytuj]` profilu z kraju feedu (tabela kurierów: koszt, darmowe od). **Zrzut 03.** Najtańszy kurier z przedziałami → jego `[edytuj]` → przewinąć do tabeli „Kwota od/do”. **Zrzut 04.** Porównuję z kosztem i progiem w XSLT oraz z poprzednim raportem.
6. Parametry: `/panel/parameters.php`, rozwinięcie wszystkich `ul.list-group > li.menu_li_item a.showChildren` (pętla z pauzą 400 ms), nazwa z `div.showMenuSub.parameter`, wartości z zagnieżdżonych `ul li`. Porównuję ze zmiennymi z A4 i wypisuję:
   - parametry pasujące do istniejących zmiennych (także różnice wielkości liter, np. `|kolor|` vs „Kolor”),
   - nowe lub kluczowe do rozważenia (stan/kondycja → `condition`, flagi typu „TAK” → `custom_label`, format/typ → segmentacja),
   - parametry o niskiej jakości (śmieciowe wartości, „do uzupełnienia”, wymieszane typy), z małą liczbą wartości lub produktów albo wymagające dużo pracy.
   Panel nie podaje liczby produktów na parametr, więc oceniam po liczbie i jakości wartości. Tę analizę umieszczam tylko w raporcie wewnętrznym.

## B. Meta — Commerce Manager (katalog)
1. `https://business.facebook.com/commerce/` → lista „Portfolio firmowe” (klik w nazwę u góry lewego panelu, wpisać fragment domeny) → portfolio sklepu → katalog. Zapisuję `business_id` i ID katalogu.
2. `…/commerce/catalogs/<katalog>/data_sources?business_id=<id>`: liczba produktów, status, ostatnia aktualizacja, harmonogram. **Zrzut 05.** Klik w nazwę feedu → podsumowanie ostatniego przesłania: zaktualizowano, usunięto, błędy, problemy, naruszenia. **Zrzut 06.**
3. `…/catalogs/<katalog>/home/?business_id=<id>` (przegląd): zatwierdzone, odrzucone, problemy. **Zrzut 07.**
4. `…/catalogs/<katalog>/events/?business_id=<id>`: wskaźnik dopasowania katalogu (zalecane ≥ 90%). **Zrzut 08.** „Wyświetl” → podział na ViewContent, AddToCart, Purchase i ostrzeżenia. **Zrzut 09.**
5. `…/catalogs/<katalog>/products?business_id=<id>` → zakładka „Działania”: odrzucone produkty (nazwa, naruszenie, ID, początek opisu) i inne ostrzeżenia. **Zrzut 15.** Przeglądam też opisy pod kątem śmieci (np. niewypełnione szablony).
   Typowe drobne problemy (aktualność cen i stanów, niedostępna strona lub zdjęcie, „out of stock” przy eksporcie towarów niedostępnych) oceniam po skali i trendzie, nie po pojedynczych sztukach.

## C. Meta — Events Manager (piksel / API konwersji)
1. `https://business.facebook.com/events_manager2/list/dataset/<piksel>/overview?business_id=<id>`: tabela zdarzeń (status, integracja, EMQ, liczba, ostatnio odebrane) oraz wykres dzienny (wiersz `stats` w `innerText`). **Zrzut 10.**
2. `…/diagnostics?business_id=<id>`: aktywne i wcześniej wykryte błędy. **Zrzut 11.**
3. Zakup: klik w wiersz „Zakup” na przeglądzie → wykres serwer (`serverProcessedCount`) vs przeglądarka (`browserProcessedCount`) — sumuję. **Zrzut 12.** Potem `…/overview/Purchase/event_matching` (parametry klienta, **Zrzut 14**), `…/overview/ViewContent/event_matching` (**Zrzut 13**), `…/overview/Purchase/event_deduplication` (pokrycie `event_id`).
   **Norma IdoSell:** API zawsze wysyła więcej niż piksel. Meta deduplikuje, a Purchase z API pochodzi z aktywacji „Meta Pixel”, pozostałe zdarzenia API z FBE2. Proporcja Purchase serwer/przeglądarka rzędu kilku razy, piksel < 25% CAPI, brak UA i `fbp` w części zdarzeń, `s2s_missing_ua` — **to nie jest błąd**.
   **Anomalia:** zdarzeń API kilkadziesiąt lub sto razy więcej niż zwykle (względem stanu bazowego lub PageView/przeglądarki). Wtedy: z wykresów ustalam dzień i godzinę początku, robię zrzuty (wykres, serwer vs przeglądarka, diagnostyka), sprawdzam FBE2 i przygotowuję treść zgłoszenia do obsługi klienta IdoSell z przedziałem czasowym. Zgłoszenia nie wysyłam sam.
4. Spadek lub wzrost wolumenu dziennego > 25% względem początku okresu lub poprzedniego raportu odnotowuję jako „info” do porównania z ruchem i budżetami.

## D. Raport
1. `raporty/<domena>_<data>/dane.json` (struktura jak we wzorcu): `sklep`, `data`, `okres`, `kolejna_weryfikacja` (+90 dni), `podsumowanie` (3–4 punkty), `sekcje` (tytuł, `status`: ok / uwaga / problem, `wynik`, `opis`, `zrzuty`, opcjonalnie `rekomendacja`), `dzialania` (priorytet, działanie, kto), `komentarz_clickup` (dokładnie 4 zdania). Język nietechniczny, bez wewnętrznych identyfikatorów i bez analizy parametrów.
2. W KATALOGU: `python narzedzia/raport_docx.py "raporty/<domena>_<data>"` → `Raport_Meta_<domena>_<data>.docx` + `komentarz_clickup.txt`.
3. `raporty/<domena>_<data>/RAPORT_wewnetrzny.md` (jak we wzorcu): identyfikatory, tabele A/B/C, stan bazowy proporcji, parametry vs sterownik, proponowane zmiany (gdzie, przed → po, status).
4. Zamykam kartę. Podsumowanie dla użytkownika: co w normie, co do poprawy, propozycje zmian do decyzji, ścieżki plików i treść komentarza do ClickUp.
