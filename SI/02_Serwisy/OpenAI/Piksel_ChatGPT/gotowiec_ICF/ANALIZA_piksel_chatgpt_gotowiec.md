# ANALIZA: gotowiec ICF — piksel ChatGPT Ads jako kampania dodatków IdoSell
Zadanie ClickUp: [IdoMods YouTube - Pixel pod GPT Ads](https://app.clickup.com/t/36829874/1ammhmkcve9) · Klient: IdoMods (kanał YouTube) · Data: 2026-11-10
Zadanie nadrzędne: [IdoMods YouTube - Film: ChatGPT Ads w IdoSell - Poradnik](https://app.clickup.com/t/1ammhmkb5qh) · Termin: 10.11.2026, deadline 16.11.2026

## Cel
Gotowy plik XML (ICF) z kampanią dodatków HTML piksela ChatGPT Ads (`oaiq`) do zaimportowania w dowolnym sklepie IdoSell. Zmienne (co najmniej Pixel ID) mają być do podania w edycji kampanii, bez edycji kodu. Plik trafi na kanał YouTube IdoMods jako gotowiec do filmu „ChatGPT Ads w IdoSell – Poradnik”.

Komentarz zlecającego (Konrad Malski, 09.11.2026): „prośba o zrobienie gotowego XML do wgrania dodatku HTML/CSS od razu z możliwością podania zmiennych w edycji kampanii”.

## Dane wejściowe i wyjściowe
**Wejście:**
- **Źródło (decyzja użytkownika 2026-11-10):** kampania dodatków „CHATGPT ADS” w panelu butyolivier.pl: `https://butyolivier.pl/panel/snippets.php?action=campaignList&shop=1` (kampania 54). Eksport ICF kampanii (`snippets.php?action=exportIDF&shop=1&campaign=54&language=<lang>`) — **tylko odczyt**, bez zmian w panelu butyolivier.
- Lokalne kopie i dokumentacja: `../dodatki/` (7 plików, README z tabelą ustawień, poprawka 2026-11-02: bez `consent false`), testy `../test/`. Porównać panel z lokalnymi plikami; rozbieżność zgłosić.
- Wnioski: `../ANALIZA_piksel_chatgpt_butyolivier.md`, `SI/02_Serwisy/OpenAI/Weryfikacja_GPTAds/ANALIZA_GPTAds_butyolivier_2026-11-02.md`, notatki pamięci o dodatkach IdoSell i `oaiq` (consent false kasuje `__oppref`).

**Wyjście (w tym folderze):**
- `piksel_chatgpt_ads.xml` — plik ICF do importu (gotowiec dla widzów);
- `INSTRUKCJA.md` — import, podanie Pixel ID, zgody cookies, sprawdzenie zdarzeń; krótka, do opisu filmu / wpisu blogowego;
- `komentarz_clickup.txt` — dla Konrada (wkleja użytkownik).

## Plan
1. **Eksport z butyolivier (Claude in Chrome, tylko odczyt):** lista dodatków kampanii, ICF kampanii dla każdego języka sklepu, ustawienia dodatków (format, region, strony, dynamiczne, `auto_block`, aktywność). Porównanie treści z `../dodatki/`. Kopia eksportu w `zrodlo/` (poza gitem, jeśli zawiera dane sklepu).
2. **Zmienne kampanii:** ustalić, czy ICF / edycja kampanii dodatków IdoSell ma pola konfiguracyjne (zmienne) i jak dodatek się do nich odwołuje. Źródła: eksport ICF kampanii butyolivier, ewentualnie gotowe kampanie IdoSell z parametrami w innym panelu (tylko odczyt). Wynik zapisać tu i w notatce pamięci o dodatkach.
   - Jest mechanizm → Pixel ID (obowiązkowo), waluta (albo znacznik IdoSell waluty, jeśli istnieje), wariant kwoty zakupu z przesyłką / bez jako zmienne.
   - Nie ma → plan B: jedno miejsce konfiguracji na początku `chatgpt_init` (`PIXEL_ID`, waluta), opisane w instrukcji. Decyzję potwierdzam z użytkownikiem.
3. **Uogólnienie:** usunąć wszystko, co jest specyficzne dla butyolivier (Pixel ID, waluta na sztywno, nazwy). Bez `data_user`. Treść dodatków dla każdego języka (pułapka: pusty `zul` = dodatek nie działa) albo jasna informacja w instrukcji, jak dodać język.
4. **Złożenie ICF** z 7 dodatków i ustawieniami z `../dodatki/README.md` (HTML, dynamiczne poza `chatgpt_init`, `consent` pod zgodą na cookies reklamowe). Kontrola: poprawny XML, kod dodatków przechodzi `node ../test/test_dodatkow.js`.
5. **Test importu na sklepie testowym** (proponowany zooart6; **zapis w panelu tylko za zgodą użytkownika**): import, podanie zmiennych, sprawdzenie na stronie sklepu przez Chrome DevTools MCP (ładowanie SDK dopiero po zgodzie, kolejność zdarzeń, `oppref`). Po teście kampanię testową wyłączyć albo usunąć (za zgodą). Bez zamówienia testowego, chyba że użytkownik zdecyduje inaczej (wtedy zasady z sekcji „Zasady sesji”).
6. **Instrukcja i komentarz**, wpis w `SI/README.md` (stan), propozycja skilla „piksel-chatgpt”, jeśli gotowiec zadziała (3. realizacja piksela ChatGPT: butyolivier, idomods.pl GTM, ten gotowiec).

## Założenia
- Gotowiec ma działać w dowolnym sklepie IdoSell, bez danych butyolivier.
- Zachowuję logikę z poprawki 2026-11-02 (bufor `oaiqSafe`, brak `consent false`, surowe dane klienta hashowane przez SDK, `event_id` = `order_<numer>`).
- Panel butyolivier: tylko odczyt.

## Otwarte pytania
1. Czy „zmienne w edycji kampanii” to pola konfiguracyjne kampanii dodatków IdoSell? Jeśli IdoSell ich nie obsługuje — plan B (punkt 2).
2. Test importu na zooart6 — zgoda na zapis kampanii testowej w tym panelu?

## Zasady sesji
- ClickUp tylko do odczytu; komentarz → `komentarz_clickup.txt` (wkleja użytkownik).
- Git: gałąź `piksel_chatgpt_gotowiec` (wariant „nowy problem”); `/zapisz` i `/zamknij` wykonuje użytkownik, sesja realizująca nie commituje.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: tak — jedna sesja z Claude in Chrome naraz. Panele (butyolivier, zooart6) w Claude in Chrome, przez domenę logowania; butyolivier tylko odczyt.
- Zamówienie testowe i sprawdzanie zdarzeń na stronie sklepu (jeśli w planie): **tylko przez Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`, osobny profil), nie przez Claude in Chrome.
  - Zamówienie: tani produkt, 1 szt., płatność „przelew zwykły”, nigdy za pobraniem (globalny CLAUDE.md).
  - Panele i platformy reklamowe zostają w Claude in Chrome.
- To nie jest zmiana sterowników XSLT — procedura historii sterowników nie dotyczy.

## Decyzje użytkownika (2026-11-10, sesja realizująca)
- **Zmienne kampanii — jest mechanizm** (wzorzec: `Integracje/GAds - tag śledzenie i konwersji/idomods_pl-google-ads-tag-with-enhanced-conversion.xml`): w `<element>` po `<classification>` blok `<settings><setting type="config" name="…" description="…" value="…"/></settings>`, w treści dodatków odwołanie `[config:nazwa]`. Plan B odpada.
- **Jeden język:** kampania wgrywa się na jeden język (`<language name="pol"/>`) — tak zostaje. Niestandardowe konfiguracje (inny kod języka, waluta) zgłasza się w zadaniu albo zapisuje w pliku klienta (`SI/Klienci/`).
- **Kontrola poprawności:** sprawdzić kod na kilku losowych sklepach IdoSell (strona sklepu, tylko odczyt: struktura stron, dostępność obiektów, zachowanie skryptu; bez zamówień i bez zapisów w panelach).
- **zooart6:** zgoda na utworzenie kampanii, tworzenie kopii i ich edycję.

## Ustalenia z eksportu butyolivier (2026-11-10)
- ICF kampanii 54 (`zrodlo/`, poza gitem — do dopisania w `.gitignore` za zgodą): 9 dodatków, 7 aktywnych; kod 7 aktywnych **identyczny** z `../dodatki/`. `data_user` i `chatgpt_page_viewed` wyłączone — do gotowca nie wchodzą. `<settings/>` puste.
- Zgoda na cookies: dodatek `consent` ma w edycji zdefiniowany plik cookie (dostawca ChatGPT, kategoria **reklamowe**). **ICF tego nie eksportuje** → krok ręczny w instrukcji (sprawdzę na zooart6, czy import coś tu zmienia).
- `auto_block` w ICF to automatyczne wyłączanie przy wolnych plikach, nie zgoda (notatka pamięci błędnie — poprawiona; README `../dodatki` opisuje zgodę poprawnie). W gotowcu `n` dla wszystkich (dodatki nie linkują plików).

## Zmienne kampanii w gotowcu
| name | opis | domyślnie | użycie |
|---|---|---|---|
| `pixel_id` | Pixel ID ChatGPT Ads (OpenAI) | pusty | `consent`: `init pixelId`; pusty → SDK się nie ładuje |
| `currency` | Waluta sklepu (kod ISO 4217) | `PLN` | wszystkie zdarzenia z kwotą |
| `purchase_with_shipping` | Kwota zakupu z kosztem dostawy (tak/nie) | `tak` | `order_created`: `[iai:order_worth_cpa2]` albo `[iai:products_worth_cpa2]` |

Budowa: `zbuduj_icf.py` czyta `../dodatki/0*.html`, podmienia Pixel ID / `PLN` / kwotę na `[config:…]`, zapisuje `piksel_chatgpt_ads.xml` — powtarzalne przy zmianach dodatków.

## Stan
- 2026-11-10: analiza wstępna (sesja /zadanie). Decyzja użytkownika: źródłem dodatków jest kampania w panelu butyolivier.pl.
- 2026-11-10: plan potwierdzony, decyzje powyżej; start realizacji od eksportu z butyolivier.
- 2026-11-10: gotowiec, instrukcja i komentarz gotowe; testy poniżej. Kampanie testowe na zooart6 (156, 157) wyłączone.

## Wyniki testów (2026-11-10)
- **Lokalnie** `node test_gotowca.js`: WSZYSTKO OK (składnia 7 dodatków, init z Pixel ID ze zmiennej, EUR, wariant bez dostawy, pusty/niepodstawiony Pixel ID → SDK się nie ładuje, zła waluta → PLN, brak `consent false`).
- **Import na zooart6** (`zooart6.yourtechnicaldomain.com`): dwuetapowy (plik → wybór języka pol/eng/est/ukr). Kampania po imporcie **nieaktywna**; w edycji kampanii pola `config_item[pixel_id|currency|purchase_with_shipping]` z opisami z ICF. 7 dodatków aktywnych z ustawieniami z ICF.
- **Sklep zooart6** (Chrome DevTools MCP, izolowany profil, wysyłki do `bzr.openai.com` przechwycone): `[config:currency]` → `EUR`, `[config:pixel_id]` → `pid=TestGotowiecICF02` w zapytaniu SDK (sv 0.1.100); `page_viewed` z `oppref`, cookie `__oppref` zostaje na kolejnych stronach.
- **Plik cookie:** definicja (dostawca, kategoria, opis — **wymagany we wszystkich językach**) zapisuje się od razu przez `ajax/snippets-cookies.php`. zooart6 nie ma banera zgód → dodatek z definicją cookie nie jest wydawany w `ajax/get.php` (piksel milczy — poprawnie). **Po usunięciu definicji dodatek dalej nie był wydawany (także jego kopia „powiel”, także z kategorią funkcjonalne)** — świeży import (157) działał od razu. Wniosek w instrukcji: nie usuwać pliku cookie na próbę; wymagany baner zgód.
- **zooart6 — puste znaczniki karty towaru** w dodatkach dynamicznych (`[iai:itemcardpage_product_id]`, cena puste, nazwa „Domyślna nazwa”) → SDK odrzuca `contents_viewed`/`items_added` (`invalid_event_props`). Na butyolivier.pl (karta 13276) te same dodatki: id 13276, kwota 38900, nazwa poprawna → cecha sklepu testowego, nie gotowca.
- **5 sklepów IdoSell** (ezebra, naturalstyle, pewienpan, shiori, ulubioneobuwie; sonda: init + contents_viewed + items_added bez consent): wszędzie `#projector_button_basket` (BUTTON/submit), pole ilości, zdarzenie w buforze z ID towaru i nazwą (polskie znaki, znaki CJK), przycisk podpięty, brak CSP.
- Niesprawdzone: `checkout_started` i `order_created` w sklepie (bez zamówienia testowego — decyzja w planie); logika ta sama co w butyolivier (zakupy z `oppref` od 2026-11-02).

## Test pełnego procesu — abczoo.gr (decyzja użytkownika 2026-11-10)
- „Przetestujmy na dwóch sklepach cały proces” → „możemy testować na abczoo.gr”. Interpretacja: panel abczoo.gr (dwa sklepy, jeśli panel wielosklepowy; inaczej abczoo.gr + wyniki zooart6).
- Proces: import ICF → zmienne → plik cookie „reklamowe” → strona sklepu (baner, zgoda, zdarzenia do `checkout_started`) → zamówienie testowe tylko po potwierdzeniu w czacie (najtańszy towar, 1 szt., przelew zwykły, numer do anulowania; Chrome DevTools MCP).
- Pixel ID testowy, wysyłki do OpenAI przechwytywane. Po teście kampania wyłączona.

### Wyniki abczoo.gr (2026-11-10, panel `shop38574-1.yourtechnicaldomain.com`, `shop=1`, język sklepu `gre`)
- **Język z pliku, nie z okna importu:** kampanie 8 i 9 (plik z `pol`, w oknie wybrany Greek — także kliknięciem) → treść w `pol`, `gre` puste, nic w sklepie. Kampania 10 (wariant `<language name="gre"/>`) → treść w `gre`. Instrukcja: powielenie kodu we wszystkich wersjach językowych w edycji dodatku (decyzja użytkownika: instrukcja bez edycji pliku); builder: `python zbuduj_icf.py gre` (wewnętrznie).
- **Opóźnienie odświeżania** (~10–15 min statyczny HTML, kilka minut dynamiczne): plik cookie dodany po włączeniu kampanii → `consent` wydawany bez zgody przez kilka minut. Instrukcja: włączenie kampanii na końcu.
- **Bez zgody:** `init` + bufor (`page_viewed`), brak SDK, brak `consent`, zero zapytań do OpenAI. ✔
- **Zgoda w banerze IdoSell:** `consent` pojawia się **dopiero na kolejnej stronie** (nie na tej, na której kliknięto zgodę).
- **Po zgodzie:** SDK `pid=TestGotowiecABC01`, `page_viewed`, `contents_viewed` (10155/10156, 67, EUR, grecka nazwa), `items_added`, `checkout_started` (576, 801, EUR) — `drop=0`. ✔
- **Zamówienie testowe nr 11111** (2026-11-10 13:55, konto testowe Puszek Miałczewski / idosell@brandsmanago.pl podstawione przez sklep, Dolfos Dolvit ProDental 30 g ×1, DPD, **przelew** „Τραπεζικό έμβασμα”, 13,91 €) — **do anulowania przez sklep**. Złożył użytkownik (blokada uprawnień przy akceptacji regulaminu).
- **`order_created`:** `id=order_11111`, `amount=1391` EUR (z dostawą), `user` zahashowany przez SDK (em, ph, php, fn, ln + GR, miasto, kod), `drop=0`. ✔ Paczka z `orderdetails` poszła naprawdę do OpenAI (przejście po kliknięciu użytkownika, poza przechwytem) → **401** (fikcyjny Pixel ID) — nic nie zapisane po stronie OpenAI.
- **Błędy / ograniczenia do decyzji:**
  1. **`oppref` ginie przy zgodzie na stronie wejścia** — SDK czyta `oppref` z adresu bieżącej strony, a `consent` ładuje się dopiero na następnej (bez `oppref` w adresie). Klient wchodzący z reklamy i od razu klikający zgodę traci powiązanie z kliknięciem. Dotyczy też butyolivier. Propozycja: `init` zapamiętuje `oppref` z adresu w `sessionStorage` (bez wysyłki), `consent` przed załadowaniem SDK przekazuje go SDK (do ustalenia jak — dopisanie do adresu `history.replaceState` albo opcja SDK).
  2. **Kwota towaru w `order_created.contents`** = 13,91 (wartość zamówienia) zamiast 8,01 — `[iai:product_price_gross_float]` na stronie po zamówieniu zwraca wartość zamówienia. Suma zamówienia poprawna. Propozycja: inny znacznik ceny towaru dla `after_order` (do sprawdzenia w dokumentacji znaczników IdoSell) albo `contents` bez `amount`.
  3. `items_added` liczy kliknięcie także zablokowanego przycisku (towar niedostępny, 10155) — opisane w instrukcji jako ograniczenie.
- Kampanie 8, 9, 10 wyłączone.

### Poprawki po abczoo.gr (decyzje użytkownika 2026-11-10)
- **Koszt dostawy pomijamy** („lepiej zignorować koszt dostawy”): `order_created.amount` = `[iai:products_worth_cpa2]` („Wartość towarów w zamówieniu”); zmienna `purchase_with_shipping` usunięta (prostsza konfiguracja). Ceny w `contents` skalowane tak, by suma = wartość towarów (na `after_order` `[iai:product_price_gross_float]` dał 13,91 zamiast 8,01; przy poprawnych cenach współczynnik = 1).
- **`oppref` ze strony wejścia** („sprawdź ten pomysł”). SDK 0.1.100: `Ne()` bierze kolejno `explicitClickId` (z `init.oppref`), parametr `oppref` z adresu, cookie `__oppref`; `init.oppref` przyjmowany tylko przy udzielonej zgodzie (`N()`), zapis cookie na 30 dni. Rozwiązanie bez zapisu przed zgodą: w `consent`, gdy adres nie ma `oppref` i nie ma cookie `__oppref`, odczyt `oppref` z `document.referrer` (ta sama domena) → po `consent true` drugie `init({ oppref })`. Ograniczenie: działa, gdy zgoda padła na stronie wejścia (następna strona ma ją w referrerze). Odrzucone: `sessionStorage` przed zgodą (zapis identyfikatora reklamowego bez zgody).
- Zmiany tylko w builderze gotowca (`../dodatki` = wersja wdrożona na butyolivier zostaje); te same poprawki dla butyolivier — do decyzji.
- Weryfikacja: test lokalny z prawdziwym SDK (strony testowe, przechwyt), potem abczoo.gr (import do `pol` + powielenie kodu na `gre`, jak w instrukcji).
- **Wynik testu lokalnego z prawdziwym SDK 0.1.100 (2026-11-10):** strona 1 `?oppref=klik_referrer_test` bez `consent` → brak SDK, bufor; strona 2 (referrer = strona 1, `consent`) → cookie `__oppref=klik_referrer_test`, `page_viewed` z `oppref`; strona 3 → `oppref` w nagłówku paczki (ścieżka z cookie, jak przy zwykłym wejściu). `test_gotowca.js`: WSZYSTKO OK (w tym skalowanie cen, kwota bez dostawy, 5 przypadków referrera).
- Do sprawdzenia na sklepie: `order_created` z `[iai:products_worth_cpa2]` (wymaga zamówienia testowego).
- **butyolivier:** poprawki (`oppref` z referrera, kwota bez dostawy) — decyzja zewnętrzna (użytkownik 2026-11-10); `../dodatki` i panel bez zmian.
- **Drugi test abczoo.gr** (zgoda użytkownika 2026-11-10): droga z instrukcji — import pliku `pol`, zmienne, powielenie kodu na `gre`, plik cookie, włączenie na końcu; zamówienie testowe po potwierdzeniu.

### Wyniki drugiego testu abczoo.gr (kampania 11, 2026-11-10 14:13–14:40)
- Droga z instrukcji zadziałała: import bez wyboru języka → `pol`; „Powiel we wszystkich językach” (`copyTextsToOtherTabs`) + „Zmień” w 7 dodatkach → `gre` = `pol`, ustawienia bez zmian; plik cookie; włączenie na końcu → **`consent` ani razu nie wydany bez zgody** ✔; `init` w HTML po ~30 s, dynamiczne po ~6 min.
- Zgoda na stronie wejścia: tym razem IdoSell wstawił `consent` **od razu na tej samej stronie** → `oppref=test_abczoo_ref2` z adresu, cookie `__oppref`; w pierwszym teście dopiero na następnej (prawdopodobnie pamięć podręczna po dodaniu cookie) — oba przypadki obsłużone (ścieżka referrera sprawdzona lokalnie z prawdziwym SDK).
- `checkout_started` 801 EUR ✔ (z `oppref` w paczce).
- **Zamówienie testowe nr 11113** (14:36, konto testowe Puszek Miałczewski — zalogował użytkownik; Dolfos Dolvit ProDental ×1, DPD, przelew, 13,91 €) — **do anulowania** (razem z 11111). Akceptacje regulaminu i złożenie: użytkownik (blokada uprawnień).
- `order_created`: `id=order_11113`, `oppref=test_abczoo_ref2` ✔, `user` zahashowany ✔, `drop=0`; paczka → 401 (fikcyjny Pixel ID). **Kwota nadal 1391:** na abczoo.gr `[iai:products_worth_cpa2]` (opis: „Wartość towarów w zamówieniu”) **i** `[iai:product_price_gross_float]` zwracają 13.91 (= z dostawą). Kod skalowania zadziałał zgodnie z danymi — błędne są znaczniki.
- Kandydat na poprawkę: `order_worth_cpa2 − delivery_cost_float` — **odrzucony, decyzja użytkownika 2026-11-10: zostajemy przy `[iai:products_worth_cpa2]`** (kwota zgodna z tym, co IdoSell podaje jako wartość towarów; na abczoo.gr ze znacznika wychodzi wartość z dostawą — cecha sklepu/IdoSell). Skalowanie cen w `contents` do tej wartości zostaje.
- Kampania 11 wyłączona.

## Do decyzji użytkownika
- zooart6: usunąć kampanie testowe 156 (z kopią 534 i testowym plikiem cookie „TEST funkcjonalne”) i 157? Obecnie wyłączone. Kampania 155 „CHATGPT ADS” (wcześniejsza kopia z butyolivier) — nie moja, nie ruszałem.
- Skill „piksel-chatgpt” (3. realizacja) — propozycja na później.
