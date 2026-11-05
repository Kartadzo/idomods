# ANALIZA: weryfikacja konwersji ChatGPT Ads (OpenAI `oaiq`) — butyolivier.pl

Status: **poprawka wdrożona i potwierdzona w OpenAI 2026-11-02** (zamówienie 696163 z `oppref`) · Data: 2026-11-02 · ClickUp: [ButyOlivier.pl GPTAds - Weryfikacja konwersji](https://app.clickup.com/t/1ammhmkbtwa) · Wdrożenie z 2026-10-20: `SI/02_Serwisy/OpenAI/Piksel_ChatGPT/` (dodatki HTML, kampania dodatków 54)

## Cel

Klient ma wrażenie, że konwersje z ChatGPT Ads liczą się źle. Trzeba sprawdzić cały lejek zdarzeń (Dodatki HTML IdoSell → SDK `oaiq` → OpenAI), złożyć zamówienie testowe i ustalić przyczynę.

## Jak testowałem

- Przeglądarka z zaakceptowanymi cookies (zgoda zapisana w SDK: `localStorage.oaiq_consent = true`), konto testowe klienta (zalogowane ręcznie przez użytkownika).
- Wysyłki SDK do `bzr.openai.com/v1/sdk/events` przechwycone po stronie sklepu (podmiana `fetch`/`sendBeacon`, `performance` resource timing). Narzędzie sieciowe rozszerzenia nie pokazuje zapytań do OpenAI.
- **Event stream w OpenAI Ads Manager był dla mnie niedostępny** (strona nie odpowiada rozszerzeniu, każdy odczyt kończy się timeoutem). Wnioski opierają się na stronie sklepu i kodzie SDK `oaiq.min.js` v0.1.97.

## Wyniki — zdarzenia wychodzą poprawnie

| Krok | Zdarzenie | Wynik |
|---|---|---|
| strona główna, wyszukiwarka, logowanie | `page_viewed` | ✅ paczka wysłana (2–3 s po załadowaniu) |
| karta towaru (Gąbka KAPS, ID 1641) | `page_viewed` + `contents_viewed` | ✅ `id 1641`, `amount 490`, nazwa poprawna |
| klik „Dodaj do koszyka” | `items_added` | ✅ wysłane przez `sendBeacon` **przed** przeładowaniem strony; treść: `amount 490`, `quantity 1`, `id 1641`, nazwa |
| order1 (dostawa i płatność) | `checkout_started` | ✅ dodatek wyrenderowany (`1641 / 1 / 4.90`), paczka wysłana |
| order2 (weryfikacja) | — | ✅ brak `checkout_started` (zgodnie z założeniem) |
| po zamówieniu (`orderdetails`) | `init(user)` + `order_created` | ✅ `amount` z `14.80` → 1480, `event_id: order_696131`, `country: pl`→`PL`, hashe e-mail/telefon/imię/nazwisko (64 znaki), miasto, kod pocztowy; paczka wysłana |

Zamówienie testowe: **nr 696131**, Gąbka KAPS ×1 (4,90 zł) + Pocztex Kurier (9,90 zł) = **14,80 zł**, przelew zwykły. **Do anulowania w panelu.**

Wniosek częściowy: zdarzenia docierają do OpenAI. Problem nie leży w tym, *czy* zdarzenia przychodzą, tylko w tym, że **nie da się ich przypisać do kliknięcia reklamy**.

## Przyczyna główna — `consent false` na każdej stronie kasuje ID kliknięcia reklamy

Dodatek `chatgpt_init` (`01_chatgpt_init.html`) na **każdej** stronie woła `oaiq('consent', false)`, a dopiero potem dodatek `consent` woła `oaiq('consent', true)`.

Z kodu SDK (`oaiq.min.js` 0.1.97):

- ID kliknięcia reklamy przychodzi w parametrze URL **`oppref`**. SDK zapisuje je w cookie **`__oppref`** (30 dni), a na kolejnych stronach odczytuje je z tego cookie.
- `oaiq('consent', false)` uruchamia funkcję czyszczącą, która:
  - usuwa cookie `__oppref` (`fe("__oppref", "", 0)`),
  - zeruje `clickId`,
  - usuwa cookie `__obref` (identyfikator przeglądarki), który potem jest tworzony od nowa.
- Kolejne `consent true` szuka ID kliknięcia w URL (już go nie ma) i w cookie (właśnie usunięte) → `clickId = undefined`.
- Zdarzenie dostaje `oppref` tylko wtedy, gdy jest zgoda **i** jest `clickId`.

Test empiryczny (2026-11-02):

| Strona | cookie `__oppref` | `__obref` |
|---|---|---|
| A: karta towaru z `?oppref=claudetest_20261102` | jest | jest |
| B: kolejna strona (kategoria Akcesoria) | **brak** | jest, ale **inna wartość niż na A** |

Skutek: ID kliknięcia ma tylko strona wejścia z reklamy. `contents_viewed` na stronie wejścia może się przypisać, ale `items_added`, `checkout_started` i przede wszystkim **`order_created` idą bez `oppref`** i z nowym identyfikatorem przeglądarki na każdej stronie. W event stream zakupy są widoczne, ale **w kampanii prawie nie ma konwersji** — to pasuje do odczucia klienta.

Ten błąd wprowadziliśmy razem z poprawką z 2026-10-20. Wcześniej był już `consent false` w init, ale zdarzenia i tak nie dochodziły, więc nie dało się go zauważyć.

## Problemy dodatkowe (mniejsze)

1. **Bez zgody na cookies reklamowe zdarzenia nie idą wcale.** To zamierzone (RODO), ale część zakupów z ChatGPT Ads nigdy nie trafi do OpenAI, a OpenAI nie modeluje braków tak jak Google. Klient powinien to wiedzieć, porównując liczby z IdoSell.
2. **Płatności online (BLIK domyślnie zaznaczony, przelew online).** Testowałem przelew zwykły. Przy bramce `order_created` wykona się, o ile klient zobaczy stronę `orderdetails` przed przekierowaniem albo wróci do sklepu po płatności. Dodatek jest ustawiony na „po złożeniu” + „po płatności”, a `event_id` deduplikuje dubel. Bez prawdziwej płatności nie dało się sprawdzić, czy jakieś zakupy giną.
3. `items_added` liczy kliknięcie przycisku, także gdy sklep nie doda towaru (np. brak rozmiaru) — znane ograniczenie z README.

## `data_user` — stan w panelu i dane klienta (sprawdzone 2026-11-02, eksport ICF kampanii 54)

Dodatki w panelu są identyczne z plikami w `SI/02_Serwisy/OpenAI/Piksel_ChatGPT/dodatki/` (porównanie skrótów treści), z jednym wyjątkiem:

| Dodatek | Aktywny | Region | Strony | Dynamiczny | Blokada do zgody |
|---|---|---|---|---|---|
| chatgpt_init | tak | head | wszystkie | nie | nie |
| consent | tak | head | wszystkie | tak | nie (zgoda reklamowa w ustawieniu dodatku) |
| page_viewed | tak | body_bottom | wszystkie | tak | tak |
| chatgpt_view_product | tak | body_bottom | projector | tak | nie |
| items_added | tak | body_bottom | projector | tak | tak |
| chatgpt_checkout | tak | body_bottom | order1 | tak | nie |
| chatgpt_purchase | tak | body_bottom | after_order, payment_success | tak | nie |
| **data_user** | **tak (miał być wyłączony)** | body_top | after_order, payment_success | tak | tak |
| chatgpt_page_viewed | nie | body_bottom | wszystkie | tak | tak |

Stary `data_user` woła `oaiq("init", { user: … })` bezpośrednio (bez bufora), z `country: '[iai:client_country]'` (= „Polska”) i `region: '[iai:client_province]'`. Według kodu SDK:

- `init` z polem `user` **zastępuje** dane użytkownika ustawione wcześniej, a nie scala ich. Jeśli `data_user` wykona się po `chatgpt_purchase` (kolejność dodatków dynamicznych jest losowa), nadpisze dane z `chatgpt_purchase`. Kraj „Polska” SDK odrzuca: akceptuje tylko kod dwuliterowy albo kilka angielskich nazw.
- Po zmianie (SDK ładowane dopiero w `consent`) `data_user` wykonany przed `consent` trafiłby do kolejki przed `init` z `pixelId` → SDK odrzuci go jako `init_invalid_pixel_id`.
- → **`data_user` trzeba wyłączyć.** Dane klienta wysyła tylko `chatgpt_purchase`, przed `order_created`, przez bufor.

Hashowanie: pola `email_sha256`, `phone_number_sha256`, `first_name_sha256`, `last_name_sha256` przyjmują w SDK **gotowy hash (64 znaki hex) albo surową wartość**. Surową SDK normalizuje według reguł OpenAI (e-mail: trim + małe litery; telefon: same cyfry z numerem kierunkowym kraju, bez `+`; imię i nazwisko: małe litery bez znaków interpunkcyjnych) i hashuje SHA-256 w przeglądarce. Do OpenAI idzie tylko hash. Znaczniki IdoSell `*_sha256` nie mają opisanej normalizacji (np. „Jan” zamiast „jan”, telefon bez `48`), więc hash może nie pasować do kont OpenAI. Panel ma znaczniki surowe: `[iai:client_email]`, `[iai:client_phone_e164]`, `[iai:client_name]`, `[iai:client_lastname]`, `[iai:client_province]`.
- → W `chatgpt_purchase` przekazuję **surowe wartości** (przez `<template>`, bezpieczne dla apostrofów), a hashuje je SDK. Telefon w formacie E.164 daje poprawny kierunkowy.

## Planowana zmiana (zaakceptowana 2026-11-02, wariant główny)

Usunąć bezwarunkowe `consent false` z `chatgpt_init` i ładować SDK dopiero po zgodzie:

- **`01_chatgpt_init`** (head, niedynamiczny): tylko kolejka `oaiq` (stub), bufor `oaiqSafe` i funkcje pomocnicze. **Bez** ładowania `oaiq.min.js`, bez `init`, bez `consent false`. Przed zgodą SDK nie działa, więc nie ma cookies ani zapytań — i nic nie kasuje `__oppref`.
- **`02_consent`** (head, dynamiczny, zgoda: reklamowe): `oaiq('init', { pixelId })` → `oaiq('consent', true)` → załadowanie `oaiq.min.js` → opróżnienie bufora. Kolejność wstrzyknięcia dodatków dalej nie ma znaczenia (bufor zostaje).
- **`07_order_created`** (`chatgpt_purchase`): surowe dane klienta zamiast `*_sha256` (patrz sekcja `data_user`), dodany `region`.
- **`data_user`**: wyłączyć w panelu.
- Pozostałe dodatki (03–06) bez zmian.

Działanie po zmianie:
- strona wejścia z `?oppref=…` i zgodą → SDK zapisuje `__oppref`; kolejne strony odczytują je z cookie;
- zgoda kliknięta dopiero na stronie wejścia → `02_consent` wstrzykiwany po zgodzie, `oppref` wciąż jest w URL → zapisany;
- brak zgody → SDK nieładowany, zero zapytań i cookies (lepiej pod RODO niż obecnie).

Alternatywa minimalna: zostawić obecny układ, ale wołać `consent false` tylko wtedy, gdy SDK nie ma zapisanej zgody (`localStorage.oaiq_consent !== 'true'`). Mniej zmian, ale po wycofaniu zgody w banerze IdoSell zapisane `true` w SDK dalej by wysyłało zdarzenia. Dlatego rekomenduję wariant główny.

Weryfikacja po wdrożeniu (powtórzyć ten test):
1. Wejście z `?oppref=test…` → na kolejnej stronie cookie `__oppref` nadal jest, `__obref` bez zmian.
2. Zamówienie testowe → przechwycona paczka `order_created` zawiera pole `oppref`.
3. W event stream OpenAI przy zdarzeniach widać przypisanie kliknięcia.

## Założenia

- Klient korzysta tylko z piksela (bez Conversions API po stronie serwera) — przy CAPI `event_id` `order_<numer>` zostaje bez zmian.
- Zachowanie SDK opisuję według wersji 0.1.97 (pobrana 2026-11-02). OpenAI może je zmienić.

## Test nowej wersji na prawdziwym SDK (2026-11-02, przed wdrożeniem)

Lokalne strony (`localhost`) z wyrenderowanymi dodatkami, prawdziwy `oaiq.min.js` 0.1.97, wysyłki przechwycone i niewysłane do OpenAI (`SI/02_Serwisy/OpenAI/Piksel_ChatGPT/test/strony_testowe.js`). Scenariusz: wejście z `?oppref=testclick_abc123` (`contents_viewed`, zgoda wstrzyknięta na końcu) → strona zamówienia (`order_created` przed `consent`).

| | Stara wersja (2026-10-20) | Nowa wersja |
|---|---|---|
| bez zgody | — | SDK nieładowane, 0 zapytań, 0 cookies, zdarzenia w buforze |
| cookie `__oppref` na stronie zamówienia | **brak** | jest |
| `__obref` strona wejścia → zamówienie | **zmieniony** (`c57e…` → `1a4e…`) | ten sam |
| `oppref` w paczce z `order_created` | **brak** | `testclick_abc123` |
| `order_created` | 1480, `order_700001` | 1480, `order_700001` |
| hashe klienta vs normalizacja OpenAI | — | e-mail, telefon (z `+` i bez), imię, nazwisko z `'` i `-` — zgodne |

SDK wysyła `oppref` na poziomie paczki (raz na wysyłkę), a łączy zdarzenia przez `obref`. W starej wersji oba identyfikatory ginęły przy każdym przejściu między stronami.

## Wdrożenie (2026-11-02)

- `data_user` (id 131) wyłączony przez użytkownika.
- Podmieniona treść (pole `languages[pol][longdescription]`, przycisk „Zmień”): `chatgpt_init` (id 125), `consent` (id 130), `chatgpt_purchase` (id 129). Eksport ICF po zapisie: skróty treści zgodne z plikami, ustawienia (region, strony, dynamiczność, blokada, aktywność) bez zmian.
- Pierwsze wejście tuż po zapisie trafiło jeszcze na stary kod, po chwili sklep serwował już nowy.
- Test na żywym sklepie (bez zamówienia): wejście z `?oppref=claudetest_live2_20261102` na kartę towaru → kategoria. Nowy init, brak `consent false`, jedno SDK (`data-oaiq-sdk`), cookie `__oppref` zostaje, `__obref` bez zmian, paczki wysłane (ec=4 / ec=3).
- Zamówienie testowe po wdrożeniu: **nr 696163** (Gąbka KAPS ×1 + Pocztex = 14,80 zł, przelew zwykły), wejście z `?oppref=claudetest_order_20261102`, odpytywanie event stream włączone przez użytkownika:
  - `items_added` (490) wysłane z `oppref=claudetest_order_20261102`,
  - order1: `checkout_started` wyrenderowany (`1641/1/4.9`), paczka wysłana,
  - po zamówieniu: `order_created` 14.80 → 1480, `event_id: order_696163`, kraj `PL`; dane klienta w SDK jako hashe (e-mail, telefon z `+` i bez, imię, nazwisko), miasto i kod pocztowy; region pusty (brak województwa na koncie) → pominięty,
  - `__oppref` i `__obref` bez zmian od strony wejścia do potwierdzenia, jedno SDK, bufor pusty.
- **Do anulowania w panelu: 696131 i 696163.**

### Potwierdzenie w OpenAI (zrzuty: `ButyOlivier/zrzuty ekranu/`)

- Event stream: `order_created`, czas zdarzenia 2026-11-02 14:06:21 UTC, `pixel_sdk`, JSON: `amount 1480`, `contents` = 1641 / „Gąbka do czyszczenia obuwia KAPS” / 490 / qty 1, PLN.
- Szczegóły zdarzenia: **Identyfikatory → Oppref „····02”** (końcówka `claudetest_order_20261102`) — zakup przypisany do kliknięcia z wejścia na stronę. Dane użytkownika: e-mail (SHA-256), kraj, miasto, kod pocztowy. Telefonu ani imienia i nazwiska panel w tym widoku nie pokazuje, choć SDK je wysłało.
- Pozostałych zdarzeń z sesji nie udało się zrobić zrzutu (bufor 200 zdarzeń przewija się w kilka sekund, a zdarzeń testowych nie da się odróżnić od ruchu klientów).

### Punkt odniesienia do monitoringu (Zdarzenia konwersji, 2026-11-02, przed efektem poprawki)

| Zdarzenie | Pokrycie identyfikatorów | Zdarzenia |
|---|---|---|
| contents_viewed | 1% | 212 tys. |
| page_viewed | 3% | 316,6 tys. |
| items_added | 2% | 6 tys. |
| checkout_started | 20% | 2,7 tys. |
| order_created | 100% | 1,4 tys. |

`order_created` ma 100% dzięki danym klienta (e-mail) na stronie potwierdzenia, ale bez `oppref` zakupy nie łączyły się z kliknięciem reklamy. Po poprawce za kilka dni powinno wzrosnąć pokrycie zdarzeń przed zakupem (dziś 1–3%) i liczba konwersji przypisanych w kampaniach. ### Ostrzeżenia w Diagnostyce (2026-11-02, zrzut `chrome_UsrGhdteyr.jpg`)

| Ostrzeżenie | Poziom | Ocena |
|---|---|---|
| Brakuje informacji o kliknięciu reklamy lub nie można ich powiązać (źródło IDOSELL): „Zachowaj parametr oppref podczas przekierowań, finalizacji zakupu…” | średni | **To naprawiony błąd** (`consent false` kasował `__oppref`). Ostrzeżenie powinno zniknąć po kilku dniach nowych danych. Sprawdzić przy kolejnej weryfikacji. |
| Brak ostatnich zdarzeń międzyserwerowych (brak zdarzeń z serwera w ciągu 24 h) | średni | Sklep wysyła zdarzenia tylko pikselem, bez Conversions API. Zgodne z obecną konfiguracją; CAPI to osobny temat na przyszłość (`event_id` `order_<numer>` jest już gotowy do deduplikacji). |

„Zagrożone zdarzenia: 538,8 tys. w ciągu ostatnich 7 dni” = wszystkie zdarzenia z okresu przed poprawką.

## Decyzje (2026-11-02)

1. Event stream pokazuje tylko ostatnie 200 zdarzeń — zamówienia 696131 nie dało się już znaleźć. Po wdrożeniu powtarzamy test z drugim zamówieniem i równoczesnym odpytywaniem.
2. Wariant główny zaakceptowany, dodatki przygotowane w `SI/02_Serwisy/OpenAI/Piksel_ChatGPT/dodatki/` (`01`, `02`, `07` + README).
3. Zamówienie 696131 anuluje użytkownik po zakończeniu analizy.
4. Ten zestaw dodatków działa tylko na butyolivier.pl (inne sklepy mają inne dodatki albo GTM).
