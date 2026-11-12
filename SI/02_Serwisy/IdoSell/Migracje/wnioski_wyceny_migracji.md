# Wnioski do wycen migracji na IdoSell
Baza wiedzy budowana z migracji prowadzonych z SI. Wersja 1: **ivemax.com** (Shoper → IdoSell, 2026-09–11). To pierwsza migracja, więc wnioski są punktem startu, a nie gotowym cennikiem. Aktualizacja: 2026-11-12.

Źródła: ClickUp (zadania „Konfiguracja panelu przed migracją” 869f5tur5, 869f97xb8, 1ammhmkbax0, wpisy czasu), proces PM [869b3dftd](https://app.clickup.com/t/869b3dftd), wyceny yellowsport.pl (869ag9nfu), dresowka.pl (8697g46qm), frezydodrewna.pl (869cu2z82), przegląd panelu i frontu ivemax 12.11 (`klienci/ivemax.com/`).

## 1. Czas: szacunek a wykonanie (ivemax.com, sama konfiguracja panelu)

ClickUp **nie sumuje** czasu podzadań do zadania głównego. Sumy poniżej pochodzą z wpisów czasu wszystkich osób, łącznie z podzadaniami.

| Edycja | Okres | Szacunek | Wykonanie | Gdzie poszedł czas |
|---|---|---|---|---|
| Wrzesień | 22–29.09 | 8 h | 6,1 h | PM 1,1 h; ETAP I 5,0 h (w tym bannery 0,9 h, blog 0,4 h) |
| Październik | 30.09–28.10 | 6 h | **15,6 h** | zadanie główne 5,9 h (PM 1,9 h + technik 4,0 h); ETAP II eksporty/importy 6,3 h (w tym import klientów 1,1 h); ETAP III 2,8 h; ETAP I 0,6 h; ETAP IV 0,1 h |
| Listopad | od 28.10 | 6 h | 1,1 h (do 12.11) | ETAP III 0,5 h, import rabatów 0,3 h, regulaminy i zwroty 0,3 h |
| **Razem** | | **20 h** | **≈22,8 h** | konfiguracja wciąż niezakończona (płatności, analityka, poczta, języki, porządki w treściach) |

Poza tym zadaniem, w osobnych zadaniach ClickUp ivemax: harmonogram migracji 4,2 h, DEV „przeniesienie towarów” 0,9 h, osobny projekt dostaw (logika, mechanizm liczenia, integracja z koszykiem), co miesiąc PM „obsługa projektowa”.

**Wnioski:**
- Szacunek na edycję (6–8 h) był za niski. Konfiguracja panelu przy migracji z Shopera z przeniesieniem danych zajęła **ponad 23 h w trzech miesięcznych transzach i nie jest skończona**. Wycena yellowsport.pl przewidywała 20 rbh na „panel + płatności + kurierzy + domena”. To realny poziom tylko wtedy, gdy klient szybko dostarcza dostępy i decyzje.
- Najwięcej czasu pochłonęły eksporty i importy (ETAP II): 6,3 h w październiku przy szacunku 1 h.
- Rozbijanie zadania na miesięczne kopie z tymi samymi 34 podzadaniami utrudnia rozliczenie. Etap „ukończony” w jednym miesiącu wraca otwarty w kolejnym.
- Ustalenie „czas tylko na etapach” nie zadziałało: ~6 h trafiło na zadanie główne. **Do procesu:** czas logowany na etapach albo na podzadaniach, a zadanie główne tylko dla PM.

## 2. Co robi IdoSell, a co my

| Obszar | ivemax.com | Inne migracje |
|---|---|---|
| Przeniesienie produktów, klientów, treści | IdoSell (IAI) + nasze importy (ETAP II) | dresowka: IdoSell, ale bez klientów, newsletterów, stanów, zdjęć i EAN; frezydodrewna: IdoSell, opisy, parametry i blog przeniesione źle |
| Szablon / wygląd | IdoSell standard + nasze bannery, osobne zadanie analizy maski | frezydodrewna, yellowsport: osobne wyceny szablonu (MVP ~100 rbh) |
| Wiadomości transakcyjne | nie wiadomo, co ustawił IdoSell (ticket z 22.09 bez odpowiedzi) | — |
| Konfiguracja panelu, płatności, dostawy, poczta, analityka | my | yellowsport: panel 12 + płatności 2 + kurierzy 2 + domena 4 rbh |

**Wniosek:** po migracji wykonanej przez IdoSell **zawsze trzeba przewidzieć audyt** (panel i front) oraz porządki. W każdej z trzech migracji IdoSell zostawił braki. W ivemax były to treści demo szablonu standard: przykładowy blog, producenci, linki w stopce, slajd z linkiem do pomocy IdoSell, teksty „zmienisz w dziale MODERACJA”, meta EN z instrukcją. Do tego doszły puste `<title>` na kartach produktu. W yellowsport wyceniono to jako „audyt panelu 7 rbh + audyt szablonu 3 rbh”, co jest rozsądną pozycją bazową.

**Do ustalenia z IdoSell przy zleceniu:** pisemny zakres (co przenoszą: produkty, warianty, parametry, opisy, zdjęcia, klienci, zgody newsletter, blog, CMS, przekierowania 301, wiadomości transakcyjne) i lista tego, co zostawiają w stanie standard.

## 3. Blokery, które wydłużyły ivemax

| Bloker | Wpływ | Jak skrócić następnym razem |
|---|---|---|
| Dostęp do DNS/OVH z 2FA na mail klienta | poczta wciąż na domenie technicznej, regulamin z technicznym e-mailem | w umowie lub na starcie: termin „okna DNS” z klientem albo delegacja dostępu; lista rekordów (poczta, SPF/DKIM, zewnętrzne usługi) przed migracją |
| Zmiana decyzji o ERP (eNova → Base → eNova) | prace w Base (10.2026) do kosza; klucz API Base działał do 12.11 (wtedy zdezaktywowany) | decyzja o ERP i właścicielu integracji przed wyceną; bez decyzji nie startujemy ETAP II |
| Brak odpowiedzi IdoSell (wiadomości transakcyjne) | podzadanie „czeka na zewn.” od 22.09 | pytać IdoSell o zakres przed startem, nie w trakcie |
| Konta płatności (Stripe, PayPal) i analityki po stronie klienta | ETAP III i IV stoją | checklista dostępów na onboardingu |
| 8 wersji językowych bez tłumaczeń | języki widoczne z treściami demo i meta `[iai:shop_name]` | wersje językowe jako osobna pozycja wyceny (konfiguracja + tłumaczenie + kontrola), ukryte do czasu tłumaczeń |
| Dostęp do Base (dane logowania nie działały) | stracony czas technika | dostępy weryfikowane na onboardingu |

## 4. Proponowane pozycje wyceny (do kalibracji przy kolejnych migracjach)

Wersja robocza. Liczby to ivemax jako punkt odniesienia, a nie stawka.

| Pozycja | ivemax: wykonanie | Uwagi do wyceny |
|---|---|---|
| Onboarding, zebranie dostępów i decyzji | (rozproszone w PM) | osobna pozycja; lista pytań startowych niżej |
| Audyt po migracji IdoSell (panel + front) | ~2 h (ten przegląd z SI) + porządki | stała pozycja; porządki wg listy pozostałości |
| Konfiguracja panelu (ETAP I) | ~5,6 h | dane firmy, VAT, maile, regulaminy, meta, robots, CMS, blog |
| Eksporty/importy (ETAP II) | ~6,3 h | zależne od źródła (Shoper: CSV) i liczby rekordów; synchronizacja ERP osobno |
| Konfiguracja po produktach (ETAP III) | ~3,3 h + osobny projekt dostaw | płatności po podaniu kont; dostawy niestandardowe (palety) jako DEV |
| Analityka (ETAP IV) | 0,1 h (czeka) | GA4, GSC, Clarity, GTM – po dostępach |
| Języki i tłumaczenia | 0 h (czeka) | osobno, liczba języków × zakres treści |
| Wiadomości transakcyjne | 0 h (czeka) | skill `/wiadomosci-transakcyjne`: status, eksport, tłumaczenie, import |
| Przepięcie domeny i poczty | jeszcze nie | 4 rbh w yellowsport; plus okno DNS |
| PM | ~3 h na samym zadaniu + miesięczne zadania PM | 10–15% całości (yellowsport: 15 rbh na 150) |

## 5. Lista startowa pytań do klienta

1. **Domena i poczta:** gdzie jest DNS i kto ma dostęp (2FA)? Jakie skrzynki i adres nadawcy maili ze sklepu? Jakie zewnętrzne rekordy są do przeniesienia lub usunięcia (newsletter, marketing automation, np. edrone)?
2. **ERP i magazyn:** jaki system (eNova, Subiekt, Wapro, Optima, Base)? Co synchronizuje: stany, ceny, zamówienia, dokumenty sprzedaży, wysyłki? Kto konfiguruje integrację i kiedy?
3. **Dokumenty sprzedaży:** kto je wystawia i wysyła (IdoSell czy ERP)? KSeF, jeśli NIP jest PL.
4. **Płatności:** jakie operatory i czy są umowy (IdoPay, Stripe, PayPal, PayPo)? Czy ma być pobranie?
5. **Dostawy:** kurierzy, palety i gabaryty, kraje wysyłki, darmowa dostawa i jej progi.
6. **Języki i waluty:** jedna domena czy osobne? Które języki na start, kto tłumaczy (aplikacja i klucz DeepL)?
7. **Opinie:** obecny system (Trusted Shops, Google) i czy przenosimy historię?
8. **Analityka i marketing:** GA4, GTM, GSC, Clarity, Google Ads, Meta, feedy; dostępy.
9. **Treści:** blog, CMS, regulaminy (własne czy generowane), przekierowania 301 ze starych adresów.
10. **Wiadomości transakcyjne:** standard IdoSell czy własne treści, w jakich językach?
11. **Promocje, rabaty, program lojalnościowy, marketplace:** czy przenosimy i od kiedy działają?
12. **Model pracy w panelu:** klient przejmuje panel sam, dostaje całość „od A do Z” czy chce odwzorować stary sklep? (pytanie Dominika z harmonogramu ivemax)
13. **Szkolenie:** kto szkoli (IdoSell czy my) i kiedy?

## 6. Do następnych migracji
- Prowadzić przegląd stanu panelu i frontu z SI na starcie (po przekazaniu przez IdoSell) i przed startem sklepu. Ten sam format: `stan_panelu.md`, `pozostalosci_techniczne.md`.
- Po 2–3 migracjach: kalibracja stawek z sekcji 4 i decyzja o skillu `/migracja-idosell` (automatyczne wyszukiwanie pozostałości: „przykładow”, „MODERACJA”, `iai-shop.com`, `[iai:`, `{…}`, pusty `<title>`, domena techniczna w treściach).
