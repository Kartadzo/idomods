# ANALIZA: Test zdarzeń reklamowych po wdrożeniu nowego OSCOP — megadron.pl

Zadanie ClickUp: [MegaDron.pl gAds - Test zdarzeń na nowym OSCOP](https://app.clickup.com/t/1ammhmkcgn4) · Klient: megadron.pl · Data: 2026-11-05
Termin: 6.11 (deadline 12.11) · Budżet czasu: 1 h · Zlecający: Konrad Malski

## Cel
Klient uruchomił w IdoSell nowy OSCOP (proces składania zamówienia). Sprawdzamy, czy po zmianie poprawnie działają zdarzenia **Google Ads**, **Meta Ads** i **TikTok Ads**. Najważniejsze są zdarzenia z etapów zamówienia: rozpoczęcie zamówienia, dane płatności oraz zakup/konwersja. Odpowiadamy na pytanie „czy coś się nie wysypało”.

## Dane wejściowe i wyjściowe
- **Wejście:**
  - sklep megadron.pl (3 sklepy w panelu: megadron.pl, megadron.eu, b2b; test dotyczy megadron.pl);
  - panel IdoSell `megadron.pl/panel`;
  - Meta Events Manager, piksel 677265139109728;
  - Google Ads (konto do ustalenia z integracji lub dodatków);
  - TikTok Events Manager.
- **Stan bazowy Meta (przed OSCOP):** `SI/02_Serwisy/Facebook/Weryfikacja_FB/raporty/megadron.pl_2026-10-26/RAPORT_wewnetrzny.md`. Zawiera wolumeny, EMQ i deduplikację; Purchase serwer/przeglądarka ≈ 4,1×.
- **Wzorzec diagnostyki Google Ads:** `SI/02_Serwisy/Google_Ads/Sledzenie_konwersji/RAPORT_wycieraczkidoszyb_2026-10-26.md`. Opisuje dodatki HTML, wersje językowe i `send_to`.
- **Wyjście** w `raporty/megadron.pl_2026-11-05/`:
  - `RAPORT_wewnetrzny.md`: tabela platforma × etap → OK / problem / dowód;
  - zrzuty, jeśli potrzebne;
  - `komentarz_clickup.txt`: krótki komentarz do wklejenia.

## Plan
1. **Sklep (Claude in Chrome):** przejście karta towaru → koszyk → kolejne kroki OSCOP → strona po zamówieniu. Na każdym kroku sprawdzam w sieci i w dataLayer:
   - **Google:** `gtag` / `AW-…`, `send_to`, konwersje rozszerzone, Consent Mode;
   - **Meta:** `fbq` (PageView, ViewContent, AddToCart, InitiateCheckout, AddPaymentInfo, Purchase), `event_id`, `content_ids`, `value`, `currency`;
   - **TikTok:** `ttq` (ViewContent, AddToCart, InitiateCheckout, AddPaymentInfo, CompletePayment/PlaceAnOrder);
   - dla wszystkich: czy zdarzenie nie odpala się podwójnie i czy nie znikło na nowych krokach.
2. **Panel IdoSell:**
   - integracje systemowe: Google, Meta Pixel/FBE2, TikTok;
   - dodatki HTML przypięte do stron procesu zamówienia: czy po zmianie OSCOP nie wiszą na nieistniejących podstronach i czy mają treść w używanej wersji językowej.
3. **Zamówienie testowe** (zgoda użytkownika 2026-11-05):
   - najtańszy dostępny produkt, 1 szt., płatność **„przelew zwykły”** (nigdy za pobraniem / przy odbiorze; globalna zasada od 2026-11-05);
   - numer zamówienia zapisuję w raporcie, żeby obsługa sklepu mogła je anulować.
4. **Platformy, porównanie przed/po dacie wdrożenia OSCOP:**
   - Meta: Events Manager → wolumen i EMQ InitiateCheckout, AddPaymentInfo i Purchase względem raportu z 26.10; test zdarzeń dla zamówienia testowego;
   - Google Ads: stan akcji konwersji (aktywna / brak ostatnich konwersji), konwersje z ostatnich dni;
   - TikTok: Events Manager → stan piksela i zdarzeń, diagnostyka.
5. **Raport i komentarz:** wynik osobno dla każdej platformy, z rekomendacjami poprawek. Poprawek nie wdrażam bez zgody.

## Założenia
- „OSCOP” to nowy proces składania zamówienia IdoSell (one step checkout). Data wdrożenia jest nieznana. Prośba w ClickUp pochodzi z 2026-11-05, więc OSCOP działa najpóźniej od tego dnia.
- Sprawdzam tylko sklep megadron.pl (PL). Wersje .eu i b2b nie są objęte zadaniem.
- Integracja CAPI IdoSell może dawać nadwyżkę zdarzeń serwerowych. To norma, alarm dopiero przy x10–x100.

## Otwarte pytania
- Dokładna data uruchomienia OSCOP: ustalę z wykresów zdarzeń albo zapytam.
- Forma płatności zamówienia testowego: tylko „przelew zwykły”. Jeśli go brak, pytam przed złożeniem zamówienia.
- Który identyfikator Google Ads jest docelowy, gdy integracja systemowa i dodatki mają różne AW-ID.

## Zasady sesji
- ClickUp tylko do odczytu. Komentarz zapisuję w `komentarz_clickup.txt`, wkleja go użytkownik.
- Git: pracujemy na gałęzi `porzadki-SI`, bez nowej gałęzi, do zakończenia testów skilla `/zadanie`. Sesja nie commituje, `/zapisz` i `/zamknij` wykonuje użytkownik. Dane klienta (`raporty/`) nie trafiają do gita.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md). W tym zadaniu nie planuję kodu, tylko diagnostykę.
- Przeglądarka: tak. Pracuje tylko jedna sesja z Claude in Chrome naraz.
- Zamówienie testowe: minimum (tani produkt, 1 szt.).

## Stan
- 2026-11-05: analiza wstępna (sesja /zadanie).
- 2026-11-05: test wykonany (DevTools MCP, konto testowe). Wynik: Google Ads, Meta i TikTok działają na wszystkich krokach, zamówienie testowe 154136 do anulowania. Raport: `raporty/megadron.pl_2026-11-05/RAPORT_wewnetrzny.md`, komentarz: `komentarz_clickup.txt`. Panelu IdoSell, Google Ads i TikTok Events Managera nie sprawdzałem (niepotrzebne do odpowiedzi).
- 2026-11-06: powtórny test na nowym OSCOP (`place-order.html`), zamówienie 154231 (przelew zwykły) do anulowania. Uwaga o TikTok wycofana, mapowanie w GTM poprawne. Test z 5.11 szedł starą ścieżką `order1`/`order2`.
