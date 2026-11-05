# ANALIZA — piksel ChatGPT Ads (OpenAI `oaiq`) przez GTM dla idomods.pl

Zadanie: [IdoMods.pl GPTAds - Dodanie konwersji](https://app.clickup.com/t/1ammhmkbw0k) (2026-11-03). Wersja 2 — po odpowiedziach użytkownika i teście formularza.

## Cel

Wdrożyć piksel OpenAI (`oaiq`) na idomods.pl **przez Google Tag Manager**, bez dodatków IdoSell (strona to WordPress/Oxygen), z:

| Zdarzenie | Wywołanie | Kiedy |
|---|---|---|
| page_viewed | `oaiq("measure", "page_viewed", { type: "contents" })` | każda strona |
| kontakt | `oaiq("measure", "custom", { type: "custom" }, { custom_event_name: "kontakt" })` | kliknięcie `tel:` lub `mailto:`, wszystkie podstrony |
| wyslanieformularza | `oaiq("measure", "custom", { type: "custom" }, { custom_event_name: "wyslanieformularza" })` | udane wysłanie formularza „ZAMÓW KONTAKT”, wszystkie podstrony |

Logika piksela jak w wersji IdoSell (`../dodatki/README.md`): kolejka, SDK dopiero po zgodzie, bez `consent false`.

## Ustalenia (2026-11-03)

- **GTM** `GTM-W34PX5W` już na stronie.
- **Zgody**: Complianz 7.5.3.1 (opt-in, integracja z Tag Managerem). Zgody **nie są dostępne w GTM przez „Zgoda”** — trzymamy się zdarzeń w warstwie danych. Complianz wysyła `{ event: "cmplz_event_<kategoria>" }` raz na stronę dla każdej przyznanej kategorii (`functional`, `preferences`, `statistics`, `marketing`) — przy wejściu, gdy zgoda już jest, i od razu po kliknięciu w banerze. Wycofanie zgody przeładowuje stronę. Sprawdzone w `complianz.min.js` (`cmplz_run_tm_event`) i w warstwie danych na `/kontakt/` (bez zgody marketingowej: tylko `cmplz_event_functional`).
- **Formularz** „IdoMods Contact Form v1.1.0”: brak `<form>`, brak `dataLayer.push`. **Test wysyłki 2026-11-03 na `/kontakt/`: brak przekierowania** — adres zostaje ten sam, w miejscu formularza pojawia się blok `#idmCfSuccessView` („Formularz przesłany pomyślnie!”). Po wysłaniu pola formularza zachowują wartości (widok jest tylko ukrywany). Na stronie głównej formularz jest dwa razy (te same `id`).
- **Linki kontaktowe**: `tel:+48733721168`, `tel:661699663`, `mailto:biuro@idomods.pl`.

## Rozwiązanie w GTM

Pliki w tym folderze:

| Plik | Co to |
|---|---|
| `GTM_import_chatgpt_idomods.json` | import kontenera (Administracja → Importuj kontener → **Scal**, „zmień nazwy elementów powodujących konflikt”) |
| `tagi/*.html` | kod każdego tagu HTML — źródło prawdy, do ręcznych drobnych poprawek w GTM |
| `zbuduj_import.py` | składa JSON importu z `tagi/*.html` (po zmianie kodu tagu) |
| `README.md` | konfiguracja tagów i wyzwalaczy, wdrożenie, testy |
| `test/test_tagow.js` | makieta w node: składnia, bufor, kolejność wywołań |

Elementy kontenera:

| Element | Typ | Wyzwalacz |
|---|---|---|
| `OpenAI - Pixel ID` | zmienna stała | — (`UZUPELNIJ_PIXEL_ID`) |
| `OpenAI - 01 init` | HTML | Initialization – All Pages |
| `OpenAI - 02 zgoda i SDK` | HTML | zdarzenie niestandardowe `cmplz_event_marketing` |
| `OpenAI - 03 page_viewed` | HTML | All Pages |
| `OpenAI - 04 kontakt` | HTML | Kliknięcie – tylko linki, `Click URL` regex `^(tel\|mailto)` |
| `OpenAI - 05 nasluch formularza` | HTML | DOM Ready (wszystkie strony) |
| `OpenAI - 06 wyslanieformularza` | HTML | zdarzenie niestandardowe `idm_formularz_wyslany` |

Formularz: tag 05 obserwuje (`MutationObserver`) klasę `#idmCfSuccessView` w każdej karcie formularza; gdy znika `idm-cf-hidden`, wysyła **jeden raz na kartę** `dataLayer.push({ event: "idm_formularz_wyslany" })` — bez danych osobowych w warstwie danych. Tag 06 czyta e-mail, telefon i imię z karty, w której pokazał się sukces, i przekazuje je **surowe** do `init { user }` (`email_sha256`, `phone_number_sha256`, `first_name_sha256`) — SDK normalizuje i hashuje SHA-256 w przeglądarce, do OpenAI idzie tylko hash (jak w `07_order_created` IdoSell). Telefon sprowadzam do E.164 (`+48…` przy 9 cyfrach).

## Założenia

1. Zdarzenia tylko po zgodzie marketingowej (`cmplz_event_marketing`); wcześniejsze czekają w buforze i idą po zgodzie na tej samej stronie. Bez zgody SDK się nie ładuje.
2. Bez ustawień „Zgoda” w tagach GTM (niedostępne) — zgodę pilnuje kod (bufor + tag 02).
3. Kod tagów w ES5 (`var`, bez funkcji strzałkowych) — bezpiecznie dla walidacji GTM.
4. Bez Pixel ID tag 02 nie ładuje SDK i nie wysyła bufora (zabezpieczenie).
5. Widget oddzwaniania — poza zakresem (odp. użytkownika).
6. Nie publikuję w GTM i nie commituję — import, wpisanie Pixel ID i publikacja po stronie użytkownika.

## Stan

- 2026-11-03: import wgrany do GTM (Scal) pomyślnie, **nieopublikowany**. Pierwsza wersja pliku dawała „Błąd analizy JSON: extraneous input ':' expecting {'{', '['}” — przeszła po ujednoliceniu pól ze wzorcem eksportu `Integracje/MS/GTM_MSAds_v4.json` (fingerprint, monitoringMetadata, formatValue, features; bez priority/notes; regex `^(tel|mailto)`).
- **Czeka na Pixel ID** od klienta / z konta ChatGPT Ads.

## Otwarte / do zrobienia po stronie użytkownika

- Lead testowy z 2026-11-03 (imię `TEST GTM`, `test.gtm.20261103@brandsmanago.pl`, tel. `500000000`) — oznaczyć w CRM jako test / usunąć z Mautic.
- Pixel ID — wpisać w zmiennej `OpenAI - Pixel ID` przed publikacją.

## Uwaga poza zakresem

Wtyczka `gtm_consent_mode_init` wypisuje w `<head>` ostrzeżenia PHP (`Undefined array key "cmplz_statistics"` / `"cmplz_marketing"`, linie 37–40) dla odwiedzających bez cookies Complianz; tekst ostrzeżenia psuje wartości `gtag("consent", "update", …)` i ujawnia ścieżkę serwera. Do poprawy (`isset(...)`, `display_errors` off).
