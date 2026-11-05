# Dodatki HTML — piksel ChatGPT Ads (OpenAI `oaiq`) dla IdoSell

Kampania dodatków „CHATGPT ADS” (butyolivier.pl, kampania 54). Analiza: `../ANALIZA_piksel_chatgpt_butyolivier.md`.

## Jak to działa

`01_chatgpt_init` ładuje SDK, ustawia `consent false` i definiuje bufor `oaiqSafe(...)`. Wszystkie zdarzenia idą przez `oaiqSafe`, więc do czasu zgody czekają w buforze. `02_consent` ustawia `consent true` i wysyła bufor w kolejności. Dzięki temu nie ma znaczenia, w jakiej kolejności IdoSell wstrzyknie dodatki dynamiczne (zdarzenia wysłane przy `consent false` OpenAI odrzuca bez ponowienia).

Nazwy produktów i miasto są wstawiane przez `<template>` / ukryte `<span>` i czytane jako tekst, więc apostrofy i cudzysłowy w nazwach nie psują skryptu.

## Ustawienia w panelu (Dodatki HTML i JavaScript)

Wszystkie dodatki: **format HTML** (nie „Javascript” — dodatki JS nie są wstawiane przy wyświetlaniu dynamicznym), aktywne w wersji normalnej i mobilnej.

| Plik | Dodatek | Region | Wyświetlany na | Wyświetlanie dynamiczne | Zgoda na cookies |
|---|---|---|---|---|---|
| `01_chatgpt_init.html` | chatgpt_init | head | wszystkie strony | **nie** | nie wymaga (wysyła tylko po `consent true`) |
| `02_consent.html` | consent | head | wszystkie strony | tak | **reklamowe** (jak obecnie) |
| `03_page_viewed.html` | page_viewed | body_bottom | wszystkie strony | tak | jak obecnie |
| `04_contents_viewed.html` | chatgpt_view_product | body_bottom | karta towaru | tak | jak obecnie |
| `05_items_added.html` | items_added | body_bottom | **karta towaru** (zmiana z koszyka) | tak | jak obecnie |
| `06_checkout_started.html` | chatgpt_checkout | body_bottom | **tylko order1** (bez order2 — inaczej zdarzenie 2× na zamówienie) | tak | jak obecnie |
| `07_order_created.html` | chatgpt_purchase | body_bottom | po złożeniu zamówienia + po płatności | tak | jak obecnie |
| — | **data_user** | — | — | — | **wyłączyć** (dane klienta są teraz w `07_order_created`, przed zdarzeniem) |

Usunąć/zostawić wyłączony stary dodatek „chatgpt_page_viewed”, jeśli nadal istnieje w kampanii (dubel `page_viewed`).

## Zmiany względem obecnych dodatków

- `contents_viewed`: prawdziwe dane karty towaru zamiast `id '12345' / amount 13 / name 'test'`.
- `items_added`: przy kliknięciu „Dodaj do koszyka” (`#projector_button_basket`), z ilością z pola ilości.
- `checkout_started`: lista towarów i kwota z koszyka (`[iai:foreach_products_begin]`).
- `order_created`: `event_id` = `order_[iai:order_sn]` (numer zamówienia) zamiast `[iai:order_id]` — ten zwracał login klienta z adresem e-mail (`idosell@…-51`), czyli dane osobowe. Kwoty i ilości jako liczby całkowite.
- Dane klienta: `country` = `[iai:client_country_code]` (kod ISO, wymagany przez OpenAI — było „Polska”), puste pola pomijane, wysyłane przed `order_created` w tym samym dodatku.

## Ograniczenia

- `items_added` liczy kliknięcie przycisku — także wtedy, gdy klient nie wybrał rozmiaru i sklep nie doda towaru (niewielka nadwyżka).
- Kwota `order_created` = wartość zamówienia **z przesyłką** (`[iai:order_worth_cpa2]`), jak w dotychczasowym dodatku. Bez przesyłki: `[iai:products_worth_cpa2]`.
- Jeśli kiedyś dojdzie Conversions API po stronie serwera, `event_id` musi mieć ten sam format (`order_<numer>`), żeby OpenAI zdeduplikowało zakupy.
- Waluta na sztywno `PLN` (sklep PL). Dla innej waluty zmienić w każdym pliku.

## Weryfikacja po wdrożeniu

1. Karta towaru → w OpenAI „Event stream” powinno pojawić się `contents_viewed` z ID i ceną produktu.
2. Klik „Dodaj do koszyka” → `items_added`.
3. Krok dostawy i płatności (order1) → `checkout_started`.
4. Zamówienie testowe (najtańszy produkt, przelew zwykły) → `order_created` z `event_id` `order_<numer>`.

Sprawdzenie składni i bufora: `node ../test/test_dodatkow.js .` uruchomione w folderze `dodatki` (przykładowe wartości znaczników) — wszystkie dodatki OK, przed zgodą 0 wysłanych, po zgodzie bufor w kolejności.
