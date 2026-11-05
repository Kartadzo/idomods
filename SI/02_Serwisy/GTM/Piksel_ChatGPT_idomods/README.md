# Piksel ChatGPT Ads (OpenAI `oaiq`) przez GTM — idomods.pl

Wersja dla stron **bez IdoSell** (idomods.pl: WordPress, GTM `GTM-W34PX5W`, zgody Complianz). Zadanie: [IdoMods.pl GPTAds - Dodanie konwersji](https://app.clickup.com/t/1ammhmkbw0k). Analiza: `ANALIZA_piksel_chatgpt_gtm_idomods.md`. Logika piksela jak w dodatkach IdoSell (`../dodatki/README.md`).

## Pliki

| Plik | Co to |
|---|---|
| `GTM_import_chatgpt_idomods.json` | import do GTM (generowany — nie edytować ręcznie) |
| `tagi/*.html` | kod tagów HTML — **źródło prawdy**; drobna łatka = zmiana tutaj + wklejenie w GTM |
| `zbuduj_import.py` | `python zbuduj_import.py` — składa JSON importu z `tagi/` |
| `test/test_tagow.js` | `node test/test_tagow.js` — makieta: składnia ES5, bufor, kolejność, formularz |

## Jak to działa

1. `01 init` (Initialization) tworzy kolejkę `oaiq` i bufor `oaiqSafe(...)`. **Nie ładuje SDK, nic nie wysyła.**
2. Zdarzenia (`page_viewed`, `kontakt`, `wyslanieformularza`) idą przez `oaiqSafe` — bez zgody czekają w buforze.
3. Complianz po zgodzie marketingowej wysyła do warstwy danych `cmplz_event_marketing` (przy wejściu z zapisaną zgodą albo od razu po kliknięciu w banerze). Na to zdarzenie `02 zgoda i SDK` woła `init` z Pixel ID, `consent true`, ładuje `oaiq.min.js` i wysyła bufor.
4. Bez zgody SDK się nie ładuje (brak zapytań do OpenAI i cookies). Bez `consent false`, bo kasuje cookie `__oppref` (ID kliknięcia reklamy).

Zgody **nie są dostępne w GTM przez „Zgoda”** (Complianz podaje je tylko jako zdarzenia w warstwie danych), dlatego tagi mają ustawienia zgody „Nie ustawiono”, a zgodę pilnuje kod.

## Konfiguracja w GTM

### Zmienne

| Nazwa | Typ | Wartość |
|---|---|---|
| `OpenAI - Pixel ID` | Stała | `UZUPELNIJ_PIXEL_ID` → **wpisać ID piksela (strumienia danych)** |
| `Click URL` | wbudowana (Kliknięcia) | włączona |

### Wyzwalacze

| Nazwa | Typ | Warunek |
|---|---|---|
| `OpenAI - CE cmplz_event_marketing` | Zdarzenie niestandardowe | nazwa zdarzenia = `cmplz_event_marketing` |
| `OpenAI - klik tel/mailto` | Kliknięcie – tylko linki | niektóre kliknięcia: `Click URL` pasuje do wyrażenia regularnego (bez rozróżniania wielkości liter) `^(tel\|mailto)`; „czekaj na tagi” i „sprawdź poprawność” wyłączone |
| `OpenAI - DOM Ready` | DOM gotowy | wszystkie strony |
| `OpenAI - CE idm_formularz_wyslany` | Zdarzenie niestandardowe | nazwa zdarzenia = `idm_formularz_wyslany` |

### Tagi (wszystkie: HTML niestandardowy, „raz na zdarzenie”, zgoda „Nie ustawiono”)

| Tag | Kod | Wyzwalacz |
|---|---|---|
| `OpenAI - 01 init` | `tagi/01_init.html` | Initialization – All Pages (priorytet 100) |
| `OpenAI - 02 zgoda i SDK` | `tagi/02_zgoda_sdk.html` | `OpenAI - CE cmplz_event_marketing` |
| `OpenAI - 03 page_viewed` | `tagi/03_page_viewed.html` | All Pages |
| `OpenAI - 04 kontakt` | `tagi/04_kontakt.html` | `OpenAI - klik tel/mailto` |
| `OpenAI - 05 nasluch formularza` | `tagi/05_nasluch_formularza.html` | `OpenAI - DOM Ready` |
| `OpenAI - 06 wyslanieformularza` | `tagi/06_wyslanieformularza.html` | `OpenAI - CE idm_formularz_wyslany` |

### Formularz „ZAMÓW KONTAKT” (tagi 05 i 06)

Formularz (IdoMods Contact Form v1.1.0) **nie przekierowuje** (sprawdzone 2026-11-03) i nie pisze do warstwy danych. Po udanej wysyłce (odpowiedź CRM OK) z bloku `#idmCfSuccessView` znika klasa `idm-cf-hidden`.

- `05` obserwuje tę klasę w każdej karcie formularza (na stronie głównej są dwie) i wysyła `dataLayer.push({ event: 'idm_formularz_wyslany' })` **raz na kartę**. Do warstwy danych nie trafiają dane osobowe.
- `06` czyta z karty, w której pokazał się sukces, e-mail, telefon i imię i przekazuje je **surowe** w `init { user }` jako `email_sha256`, `phone_number_sha256`, `first_name_sha256`. SDK normalizuje je i hashuje SHA-256 w przeglądarce, do OpenAI idzie tylko hash. Telefon sprowadzany do E.164 (`661 699 663` → `+48661699663`).
- Błąd walidacji albo błąd CRM („Ups, coś poszło nie tak”) **nie** jest konwersją.

Jeśli autor formularza zmieni `id` / klasy (`idmCfSuccessView`, `idm-cf-hidden`, `idmCfEmail`, `idmCfPhone`, `idmCfFirstName`), konwersja przestanie się liczyć — wtedy poprawić tagi 05/06. Pewniejsza alternatywa: dopisanie w formularzu `dataLayer.push({ event: 'idm_formularz_wyslany' })` przy `view('success')` i wyłączenie tagu 05.

## Wdrożenie

1. GTM → Administracja → **Importuj kontener** → plik `GTM_import_chatgpt_idomods.json` → nowy obszar roboczy → **Scal** → „Zmień nazwy elementów powodujących konflikt”. Sprawdzić podgląd zmian: tylko dodania (6 tagów, 4 wyzwalacze, 1 zmienna).
2. Zmienne → `OpenAI - Pixel ID` → wpisać ID piksela.
3. Podgląd (Tag Assistant) — testy poniżej.
4. Publikacja.

Drobna łatka: zmienić plik w `tagi/`, wkleić jego zawartość w tag w GTM, uruchomić `node test/test_tagow.js` i `python zbuduj_import.py` (żeby import był aktualny).

## Testy

- Makieta: `node test/test_tagow.js` (w tym folderze).
- Podgląd GTM:
  1. Bez zgody marketingowej: `01`, `03`, `05` odpalone; brak `cmplz_event_marketing`; w Network brak `bzrcdn.openai.com`.
  2. Akceptacja w banerze → `cmplz_event_marketing` → `02`; w Network `oaiq.min.js` i wysyłka bufora (`page_viewed`).
  3. Klik numeru telefonu / maila → `04 kontakt`.
  4. Wejście z `?oppref=test…` → na kolejnej stronie cookie `__oppref` nadal jest.
  5. Formularz (dane testowe) → zdarzenie `idm_formularz_wyslany` → `06`; w zapytaniu do OpenAI `custom_event_name: wyslanieformularza` i hashe zamiast surowych danych. **Lead testowy oznaczyć w CRM jako test.**
- Po publikacji: zdarzenia w panelu ChatGPT Ads (`page_viewed`, `kontakt`, `wyslanieformularza`).

## Ograniczenia

- `kontakt` liczy kliknięcie linku `tel:` / `mailto:`, także w komunikatach po wysłaniu formularza, nie faktyczne połączenie ani wysłanie maila.
- Wycofanie zgody w Complianz przeładowuje stronę, więc SDK się nie załaduje, ale cookies SDK zapisane wcześniej zostają.
- Pole `Click URL` musi być włączone w zmiennych wbudowanych (import je dodaje).
