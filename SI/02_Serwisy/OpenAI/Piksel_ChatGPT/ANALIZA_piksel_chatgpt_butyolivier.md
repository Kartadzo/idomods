# ANALIZA: piksel ChatGPT Ads (OpenAI `oaiq`) w Dodatkach HTML IdoSell — butyolivier.pl

Data: 2026-10-20 · ClickUp: [ButyOlivier.pl gAds - Kodu konwersji i feed dla ChatGPT Ads](https://app.clickup.com/t/869f2nnxv) · Status: **wdrożone 2026-10-20** (dodatki z `dodatki/`); potwierdzone w OpenAI wszystkie zdarzenia (`page_viewed`, `contents_viewed`, `items_added`, `checkout_started`, `order_created`)

## Cel

Ustalić, dlaczego z kampanii dodatków „CHATGPT ADS” (id 54) do OpenAI dochodzą tylko `init` i `page_viewed`, a nie dochodzą `contents_viewed` i `order_created`, mimo że te same wywołania z konsoli są rejestrowane. Przygotować poprawione dodatki do wklejenia w panelu.

## Ustalenia (test 20.10.2026, tylko odczyt + zamówienie testowe za zgodą)

### Przyczyna główna — kolejność zgody

| Dodatek | Format | Region | Dynamicznie | Blokada do zgody cookies | Aktywny |
|---|---|---|---|---|---|
| chatgpt_init (`consent false` + `init`) | HTML | head | nie | nie | tak |
| consent (`consent true`) | HTML | head | **tak** | nie | tak |
| page_viewed | HTML | body_bottom | tak | tak | tak |
| chatgpt_view_product (`contents_viewed`) | **JS** | body_bottom | było: nie → teraz: tak | nie | tak |
| items_added | HTML | body_bottom | tak | tak | **nie** |
| chatgpt_checkout | HTML | body_bottom | tak | nie | **nie** |
| chatgpt_purchase (`order_created`) | HTML | body_bottom | tak | nie | tak |
| data_user (`init` z `user`) | HTML | body_top | tak | tak | tak |

- Dokumentacja OpenAI: *„When consent is `false`, the Pixel doesn't send measurement-event pings”*, a zdarzenia zablokowane **nie są powtarzane** po `consent true`.
- `init` ustawia `consent false` od razu w `<head>`. `consent true` jest dodatkiem **dynamicznym** — IdoSell wstrzykuje go później przez JS, a kolejność wstrzykiwania dodatków dynamicznych nie jest gwarantowana.
- **Karta produktu (przed zmianą):** w HTML z serwera były tylko init i `contents_viewed`; consent i page_viewed pojawiły się w DOM później. Przechwycone zapytanie SDK przy ładowaniu: tylko `page_viewed` + diagnostyka (`dropped_event_count: 0`). Z konsoli (po zgodzie) `contents_viewed` wychodzi poprawnie.
- **Karta produktu (po zmianie na dynamiczny):** dodatek **w ogóle nie jest wstawiany** (brak znacznika `<!--126|1|54-->` i kodu w DOM). Dodatek ma format **JS**, a wszystkie działające dodatki dynamiczne mają format **HTML** z `<script>…</script>` — dynamiczne ładowanie IdoSell nie wstawia dodatków typu JS.
- **Strona po zamówieniu (zamówienie testowe nr 685311, 14,80 zł):** w DOM są `consent false` → `consent true` → `init(user)` → `order_created` → `page_viewed`, składnia skryptów poprawna, ale do OpenAI poszło **tylko `page_viewed`**. To samo wywołanie `order_created` uruchomione ręcznie po załadowaniu strony **wysyła się** (z oboma wariantami `event_id`). Wniosek: `order_created` wykonał się, zanim SDK dostało `consent true` (oba dodatki dynamiczne bez blokady — kolejność przypadkowa). Ponowne wejście na stronę potwierdzenia nie odtwarza dodatków „po zamówieniu”, więc sekwencji nie dało się zalogować wprost — wniosek opiera się na wyniku zapytań + teście ręcznym + dokumentacji.
- „W innym panelu działa” — prawdopodobnie tam nie ma `consent false` w init albo kolejność dodatków dynamicznych układa się korzystnie. Do porównania, jeśli podasz sklep.

### Problemy dodatkowe

1. **`event_id` = `[iai:order_id]`** renderuje się jako `idosell@brandsmanago.pl-51` (login klienta = e-mail + licznik). To **dane osobowe** wysyłane do OpenAI w jawnej postaci i nie jest numerem zamówienia (`685311`). Należy użyć znacznika numeru zamówienia.
2. **`data_user`: `country: 'Polska'`** — OpenAI wymaga kodu ISO 3166-1 (`PL`). `region: ''` — puste pole lepiej pominąć.
3. **`contents_viewed`** ma dane testowe na sztywno (`id '12345'`, `amount 13`, `name 'test'`).
4. **`'name': '[iai:product_name]'`** w apostrofach — nazwa z apostrofem przerwie skrypt (`SyntaxError`). Bez zmiany w ostatnim teście, ale ryzyko realne.
5. **`'quantity': [iai:product_count]`** renderuje `1.000` — działa (JS liczy 1), OpenAI wymaga liczby całkowitej → bezpieczniej `Math.round(...)`.
6. **consent bez blokady do zgody na cookies** → `consent true` wykonuje się zawsze, niezależnie od decyzji klienta w banerze (kwestia RODO, nie techniczna).
7. **items_added i checkout wyłączone** i bez kwoty/produktów.

## Planowane zmiany

Pliki do wklejenia w panelu (`SI/02_Serwisy/OpenAI/Piksel_ChatGPT/dodatki/`, po jednym `.html` na dodatek + `README.md` z ustawieniami każdego dodatku):

1. **chatgpt_init** — zostaje `consent false` + `init`; dodatkowo mały bufor:
   - `window.oaiqSafe(...)` — jeśli zgoda już jest, woła `oaiq(...)`, w przeciwnym razie odkłada wywołanie do kolejki.
   - Dzięki temu kolejność wstrzykiwania dodatków dynamicznych przestaje mieć znaczenie.
2. **consent** — `oaiq('consent', true)` + ustawienie flagi + opróżnienie kolejki (`oaiqSafe`). Ustawienie: **blokada do czasu zgody na cookies = tak** (zgodność z banerem).
3. **contents_viewed / items_added / checkout_started / order_created** — format **HTML** z `<script>`, wywołanie przez `oaiqSafe('measure', …)` zamiast `oaiq(...)`, prawdziwe znaczniki IdoSell zamiast danych testowych, `amount`/`quantity` jako liczby całkowite, nazwy produktów bezpieczne dla JS.
4. **order_created** — `event_id` z numerem zamówienia zamiast `[iai:order_id]`.
5. **data_user** — `country: 'PL'`, bez pustych pól; przez `oaiqSafe('init', …)`.

## Założenia

- Jeden piksel OpenAI na stronie → `pixelId` w drugim `init` (data_user) można pominąć (dokumentacja na to pozwala).
- Kwoty w groszach (`Math.round(x * 100)`) — zgodnie z przykładem w dokumentacji (`2599` = 25,99).
- Bufor `oaiqSafe` działa niezależnie od SDK (zwykła tablica w `window`), więc nie zależy od momentu załadowania `oaiq.min.js`.

## Decyzje (2026-10-20, po odpowiedziach)

- Znaczniki sprawdzone w panelu (lista w edytorze dodatku): `[iai:order_sn]` = numer zamówienia; karta towaru: `[iai:itemcardpage_product_id]`, `[iai:itemcardpage_product_name]`, `[iai:itemcardpage_product_price_gross_float]`; lista towarów w koszyku: `[iai:foreach_products_begin]…[iai:foreach_products_end]` z `[iai:product_id]`, `[iai:product_count]`, `[iai:product_price_gross_float]`, `[iai:product_name]`; klient: `[iai:client_country_code]`, `[iai:client_city]`, `[iai:client_zip]`, `*_sha256`. Brak wariantu nazwy escapowanej do JS → nazwy przez `<template>` + `textContent`.
- `items_added` — przy kliknięciu „Dodaj do koszyka” na karcie towaru (`#projector_button_basket`).
- Dodatek consent ma w panelu ustawienie „zgoda na pliki cookies: reklamowe” — zostawiamy, bufor w init rozwiązuje kolejność.
- `data_user` scalam z `order_created` w jednym dodatku (najpierw `init` z `user`, potem `measure`) — dane użytkownika są przypisywane do zapytania, więc muszą być ustawione przed zdarzeniem; osobny dodatek z blokadą do zgody mógł wykonywać się po zakupie.
- Zamówienie testowe 685311 anulowane.

## Otwarte pytania (pierwotne — rozstrzygnięte powyżej)

1. **Znaczniki IdoSell** — potrzebuję dokładnych nazw z listy znaczników w edytorze dodatków:
   - numer zamówienia (np. `[iai:order_sn]` / `[iai:order_number]`?),
   - cena i ID produktu na karcie towaru (dla `contents_viewed`),
   - pętla po produktach koszyka na `basketedit` / `order1` (dla `items_added` i `checkout_started`),
   - czy istnieje wariant nazwy produktu escapowany do JS. Jeśli nie — pominę `name` (pole opcjonalne) albo wstawię je przez `textContent` z elementu strony.
2. **items_added** — mierzyć na stronie koszyka (prościej, ale też przy samym wejściu do koszyka) czy przy kliknięciu „Dodaj do koszyka” (dokładniej, wymaga nasłuchu zdarzenia/przycisku)?
3. **consent** — czy włączamy blokadę do zgody na cookies (zalecam), wiedząc, że bez zgody klienta zdarzenia nie pójdą wcale?
4. Zamówienie testowe **nr 685311** (14,80 zł) — do anulowania w panelu (podobnie sportwheels.pl **nr 13637**).
