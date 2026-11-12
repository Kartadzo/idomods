# ivemax.com — stan panelu IdoSell przed migracją
Panel `client52797.idosell.com` (sklep 1, `shop52797-1.yourtechnicaldomain.com`) · przegląd tylko do odczytu: 2026-11-12 · źródła: panel, ClickUp [1ammhmkbax0](https://app.clickup.com/t/1ammhmkbax0)

Legenda stanu: ✅ gotowe · ⚠️ częściowo / do poprawy · ❌ brak · ❓ nie sprawdzono

## Stan panelu kontra ClickUp

| Obszar | Stan w panelu | Status w ClickUp (listopad) | Bloker / kto / od kiedy |
|---|---|---|---|
| Dane firmy | ✅ VIKI-CZĘŚCI MAKSYM PLENCNER, Sowia 9, 62-080 Tarnowo Podgórne, NIP, REGON, płatnik VAT | ukończone | — |
| VAT i rozliczenia | ✅ sprzedaż PL z VAT, kraje UE z/bez VAT (nie weryfikowano stawek szczegółowo) | ukończone | — |
| Konta e-mail | ❌ jedyne konto: `shop@shop52797-1.yourtechnicaldomain.com` (serwer sklepu). Brak skrzynki w domenie ivemax.com; ten adres trafia do regulaminu i polityki prywatności | w trakcie (Dominik) | DNS/poczta po stronie OVH; delegacja pełna, wpisy z Shoparena do przeniesienia — od 01.10 |
| Języki | ⚠️ 8 języków (PL domyślny, EN, DE, FR, ES, NL, SV, IT), **wszystkie widoczne dla odwiedzających**; waluty PLN + EUR | języki – do zrobienia | tłumaczenia po dostępie do aplikacji; klucz API „Idomods Translator” aktywny, użyty 12.11 10:54 |
| Waluty | ✅ PLN, EUR (kurs na froncie 1 zł = 0,2278 €) | ukończone | — |
| Kraje dostaw | ⚠️ PL, AT, FR, NL, DE; Belgia „nie wysyłamy” (profil dostaw Belgia pusty, 136 klientów z BE); literówka w nazwie profilu „NIemcy” | — | decyzja klienta: BE tak/nie |
| Profile dostaw PL | ⚠️ w panelu „Kurier 1/2/3”, „Kurier Paleta 1/2/3”, odbiór osobisty; na froncie: Kurier Standard, Kurier Multipack, **Niestandardowy**, Kurier Pół Paleta, Kurier Euro Paleta, Kurier Podwójna Paleta — **wszystkie „Gratis!”** (koszyk 250 zł, 1 szt.) | kurierzy i dostawy – ukończone | metody i koszty dostaw liczy **indywidualna aplikacja dostaw** zainstalowana w panelu (informacja użytkownika 12.11) + dodatek „Logika Palet - Test”; do sprawdzenia, czy „Gratis!” dla wszystkich form (także palet) to zamierzony wynik aplikacji |
| Płatności – profil Standard (PL) | ⚠️ przelew bankowy PLN+EUR (Pekao) ✅; IdoPay PayByLink + BLIK ✅; PayPo widoczne w COP; **Pobranie** widoczne w COP; karty ❌; **PayPal ❌; Stripe ❌**; strony powrotu na domenie technicznej | płatności – do zrobienia (Dominik) | Stripe/PayPal – konta klienta; od 09.2026 |
| Płatności – profil Zagranica | ❓ nie odczytano szczegółów | — | — |
| COP / panel klienta | ✅ działa jako gość i z kontem, faktura na inne dane, wysyłka na inny adres; rejestracja hurtownika | ukończone | — |
| Regulaminy, zgody, polityki | ⚠️ PL: regulamin, polityka prywatności, płatności, zwroty – **generowane automatycznie** (szablon IdoSell, w treści e-mail z domeny technicznej); wysyłka – treść własna; inne języki w większości „własne” (do sprawdzenia przy tłumaczeniach) | w trakcie (Dominik) | weryfikacja prawna treści – klient |
| Zwroty i reklamacje | ✅ 14 dni od wysłania / 60 od odebrania, zwrot kosztu przesyłki proporcjonalnie, kreator odstąpienia; zakładka Reklamacje ❓ | w trakcie (Dominik) | — |
| Dokumenty sprzedaży | ❓ | w trakcie (Dominik) | **eNova (grudzień)** – zakres do ustalenia |
| Wiadomości transakcyjne | ⚠️ 136 wiadomości, czysty standard IdoSell (bez marki); FR/ES/NL/SV/IT włączone z treścią PL; 16 wiadomości z wyłączonym PL (m.in. „Przyjęcie wpłaty”, „Podziękowanie… dostarczenie paczki”); SMS 2 – szczegóły `wiadomosci_transakcyjne/RAPORT_stan_wiadomosci.md` | czeka na zewn. | ticket IAI #1239568397 – do zamknięcia (IAI nic nie ustawiał); edycja po decyzji klienta i starcie tłumaczeń |
| CMS – podstrony | ⚠️ domyślne strony IdoSell: „Paczkomaty 24/7 dla wygodnych”, „Karta podarunkowa”, „Oferta specjalna”, „Pozyskiwanie i wymiana punktów”, „Pozostałe informacje 1/2/3”, „Ankiety”; „Zasady dotyczące zwrotów” ma treść demo (patrz pozostałości) | — (opis: „ukrycie domyślnych treści na podstronach CMS”) | — |
| Blog / aktualności | ❌ 4 „przykładowe wpisy na blog” i 2 „przykładowe newsy” (2017–2018) nadal opublikowane | blog – usunięcie standardu: w trakcie (wrzesień: 0,4 h zalogowane) | — |
| Domyślne meta | ⚠️ PL title/description ✅; **EN: „You can change the shop description in MODERATION \ SEO”** (+ keywords); DE/FR/IT/ES/NL/SV = `[iai:shop_name]`; karta produktu: pusty `<title>`, description zaczyna się od `{product_name}` | czeka na wewn. | — |
| robots.txt | ✅ plik dostępny (200); treści nie analizowano pod kątem reguł | czeka na wewn. | do decyzji przy przepięciu domeny |
| Sitemap | ⚠️ tylko domena techniczna (zmieni się po przepięciu) | — | przepięcie domeny |
| Strefy bannerowe | ⚠️ slider: obok „IVECO DAILY” demo-slajdy „Wersje kolorystyczne” i „Bezproblemowe zwroty” | ukończone | — |
| Rabaty / promocje | — wyłączone celowo do Nowego Roku (wyjątek klienta) | ukończone / import – do rozliczenia | — |
| Wyszukiwarka, rekomendacje | ❓ nie weryfikowano (ClickUp: ukończone) | ukończone | — |
| Opinie | ⚠️ moduł opinii IdoSell jest; **Trusted Shops: brak certyfikatu** | opinie – ukończone | pakiet Trusted Shops – klient |
| Analityka | ❌ GTM: pole ID puste; GA4: brak ID; GSC i Clarity – brak informacji | ETAP IV – czeka na zewn. | dostępy klienta |
| Dodatki HTML/JS | ⚠️ 1 dodatek: „Logika Palet - Test” (JS, koszyk, aktywny desktop+mobile, 27.10) | — | nazwa „Test” na produkcji – do potwierdzenia, czy finalny |
| Edrone | ✅ brak w dodatkach i aplikacjach panelu; ❓ DNS (poza panelem) | — | lista rekordów DNS edrone – klient nie wie, gdzie szukać (14.10) |
| Integracje API | ✅ aktywne klucze: „[idomods] API produkty”, „[IdoMods] - MD”, „Idomods Translator”; „Klucz API Base.” (ostatnio użyty 12.11 01:15) **zdezaktywowany 12.11** (informacja użytkownika); nieaktywne: iaiimport, iaidocker | synchronizacja stanów i cen – testy wewn. | synchronizacja stanów i cen – docelowo eNova (grudzień) |
| eNova / Bridge | ⚠️ w komunikatach panelu tickety IdoSell: 09.11 „integracja IdoSell Bridge - enova365 - obsługiwane wersje”, 12.11 „Problem z utworzeniem bazy IdoSellBridge na serwerze Windows” | dokumenty sprzedaży – w trakcie | eNova + IdoSell, grudzień 2026 |
| Aplikacje indywidualne | ✅ „instrukcja ivemax 2025”, „Integracja z YQService” | — | — |
| Importy (produkty, klienci, rabaty) | ❓ nie weryfikowano liczb | import produktów – w trakcie; klientów – czeka na zewn. | — |

## Blokery (zbiorczo)

| # | Bloker | Kto | Od kiedy |
|---|---|---|---|
| 1 | Brak skrzynki e-mail w domenie ivemax.com, DNS na OVH (wpisy z Shoparena + edrone) | klient (dostęp OVH, kod 2FA na mail klienta) + Dominik | 01.10.2026 |
| 2 | Wiadomości transakcyjne – brak odpowiedzi IAI, co ustawiali | IdoSell (ticket #1239568397) / Katarzyna | 22.09.2026 |
| 3 | Integracja eNova (stany, zamówienia, dokumenty sprzedaży) – zakres i termin | klient + eNova + IdoSell (Bridge) | 23.09.2026 (pytania bez odpowiedzi); Base anulowane 12.11 |
| 4 | Stripe i PayPal – brak konfiguracji | klient (konta) + Dominik | 09.2026 |
| 5 | Analityka GA4 / GSC / Clarity / GTM – brak ID | klient (dostępy) | 28.10.2026 (status „czeka na zewn.”) |
| 6 | Trusted Shops – brak certyfikatu w IdoSell, pakiet do sprawdzenia | klient | 09.2026 |
| 7 | Tłumaczenia (8 języków widocznych) | aplikacja Idomods Translator (podłączona) – start prac do potwierdzenia | 04.11.2026 |
| 8 | ~~Klucz API Base aktywny mimo anulowania Base~~ – zdezaktywowany 12.11.2026 | — | rozwiązane |
