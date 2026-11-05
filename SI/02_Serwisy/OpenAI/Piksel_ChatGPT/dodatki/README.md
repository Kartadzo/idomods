# Dodatki HTML — piksel ChatGPT Ads (OpenAI `oaiq`) dla IdoSell

Kampania dodatków „CHATGPT ADS” (butyolivier.pl, kampania 54). Analizy:
- `../ANALIZA_piksel_chatgpt_butyolivier.md` — wdrożenie 2026-10-20,
- `SI/02_Serwisy/OpenAI/Weryfikacja_GPTAds/ANALIZA_GPTAds_butyolivier_2026-11-02.md` — poprawka 2026-11-02 (przypisanie konwersji do kliknięć).

Poprzednia wersja `01`, `02`, `07` i README: `old/2026-10-20/`.

## Jak to działa

`01_chatgpt_init` tworzy tylko kolejkę `oaiq` (stub), bufor `oaiqSafe(...)` i funkcje pomocnicze. **Nie ładuje SDK i nie woła `consent false`.**

`02_consent` (po zgodzie na cookies reklamowe) woła `init` z `pixelId` i `consent true`, ładuje `oaiq.min.js` i wysyła bufor w kolejności. Bez zgody SDK się nie ładuje — nie ma zapytań do OpenAI ani cookies. Kolejność wstrzykiwania dodatków dynamicznych nie ma znaczenia.

Dlaczego bez `consent false`: w SDK `consent false` kasuje cookie `__oppref` (ID kliknięcia reklamy, z parametru URL `oppref`) i `__obref` (identyfikator przeglądarki). Wołane na każdej stronie (wersja z 2026-10-20) sprawiało, że zakupy szły bez `oppref` i z nowym `obref`, więc OpenAI nie łączyło ich z kliknięciem w reklamę.

Nazwy produktów i dane klienta są wstawiane przez `<template>` / ukryte `<span>` i czytane jako tekst, więc apostrofy i cudzysłowy nie psują skryptu.

## Ustawienia w panelu (Dodatki HTML i JavaScript)

Wszystkie dodatki: **format HTML** (nie „Javascript” — dodatki JS nie są wstawiane przy wyświetlaniu dynamicznym), aktywne w wersji normalnej i mobilnej.

| Plik | Dodatek | Region | Wyświetlany na | Wyświetlanie dynamiczne | Zgoda na cookies |
|---|---|---|---|---|---|
| `01_chatgpt_init.html` | chatgpt_init | head | wszystkie strony | **nie** | nie wymaga (nic nie wysyła) |
| `02_consent.html` | consent | head | wszystkie strony | tak | **reklamowe** |
| `03_page_viewed.html` | page_viewed | body_bottom | wszystkie strony | tak | bez zmian |
| `04_contents_viewed.html` | chatgpt_view_product | body_bottom | karta towaru | tak | bez zmian |
| `05_items_added.html` | items_added | body_bottom | karta towaru | tak | bez zmian |
| `06_checkout_started.html` | chatgpt_checkout | body_bottom | tylko order1 | tak | bez zmian |
| `07_order_created.html` | chatgpt_purchase | body_bottom | po złożeniu zamówienia + po płatności | tak | bez zmian |
| — | **data_user** | — | — | — | **wyłączyć** (2026-11-02 nadal aktywny) |
| — | chatgpt_page_viewed | — | — | — | zostaje wyłączony |

Do wklejenia przy poprawce 2026-11-02: **`01`, `02`, `07`** + wyłączenie `data_user`. Pozostałe dodatki są identyczne z panelem.

### Dlaczego `data_user` musi być wyłączony

- Woła `oaiq("init", { user })` bezpośrednio, bez bufora. W SDK `init` z `user` **zastępuje** wcześniejsze dane użytkownika, więc przy losowej kolejności nadpisuje dane z `chatgpt_purchase`.
- `country: '[iai:client_country]'` = „Polska” — SDK przyjmuje tylko kod dwuliterowy, więc kraj odpada.
- Po zmianie wykonany przed `consent` trafiłby do kolejki przed `init` z `pixelId` → SDK odrzuci go (`init_invalid_pixel_id`).

## Dane klienta w `order_created`

Pola `email_sha256`, `phone_number_sha256`, `first_name_sha256`, `last_name_sha256` dostają **surowe** wartości (`[iai:client_email]`, `[iai:client_phone_e164]`, `[iai:client_name]`, `[iai:client_lastname]`). SDK normalizuje je według reguł OpenAI i hashuje SHA-256 w przeglądarce. Do OpenAI idzie tylko hash (sprawdzone na prawdziwym SDK 0.1.97). Znaczniki `*_sha256` IdoSell nie mają opisanej normalizacji (wielkość liter, kierunkowy telefonu), więc ich hash mógłby nie pasować. Telefon w E.164 daje poprawny kierunkowy — SDK wysyła hash wersji z `+` i bez `+`.

`country` = `[iai:client_country_code]` (wielkie litery), `region` = `[iai:client_province]`, puste pola są pomijane.

## Ograniczenia

- `items_added` liczy kliknięcie przycisku — także wtedy, gdy klient nie wybrał rozmiaru i sklep nie doda towaru (niewielka nadwyżka).
- Kwota `order_created` = wartość zamówienia **z przesyłką** (`[iai:order_worth_cpa2]`). Bez przesyłki: `[iai:products_worth_cpa2]`.
- Wycofanie zgody w banerze IdoSell zatrzymuje wysyłkę (SDK się nie ładuje), ale nie usuwa cookies SDK zapisanych wcześniej.
- Jeśli kiedyś dojdzie Conversions API po stronie serwera, `event_id` musi mieć ten sam format (`order_<numer>`), żeby OpenAI zdeduplikowało zakupy.
- Waluta na sztywno `PLN` (sklep PL). Dla innej waluty zmienić w każdym pliku.

## Testy

- Makieta (składnia, bufor, kolejność wywołań): `node ../test/test_dodatkow.js .` w folderze `dodatki`.
- Prawdziwy SDK w przeglądarce: `node ../test/strony_testowe.js . <folder_wyjścia>`, potem `python -m http.server 8765` w folderze wyjścia i kolejno `page3.html` (bez zgody), `page1.html?oppref=test…` (wejście z reklamy), `page2.html` (zamówienie). Wysyłki do OpenAI są przechwytywane do `localStorage.__cap` i **nie wychodzą** do OpenAI.

## Weryfikacja po wdrożeniu

1. Wejście na sklep z `?oppref=test…` → na kolejnej stronie cookie `__oppref` nadal jest, `__obref` bez zmian.
2. Karta towaru → `contents_viewed`; klik „Dodaj do koszyka” → `items_added`; order1 → `checkout_started`.
3. Zamówienie testowe (najtańszy produkt, przelew zwykły) przy włączonym odpytywaniu event stream → `order_created` z `event_id` `order_<numer>`, paczka z `oppref`.
