# ANALIZA: ivemax.com — stan panelu przed migracją i wnioski do wycen
Zadanie ClickUp: [ivemax.com - Konfiguracja panelu przed migracją listopad](https://app.clickup.com/t/1ammhmkbax0) · Klient: ivemax.com · Data: 2026-11-12

## Cel
1. Ustalić rzeczywisty stan panelu IdoSell przed migracją z Shopera, nie tylko stan zadań ClickUp. Część konfiguracji wykonał IdoSell (IAI), więc w ClickUp nie widać całej migracji.
2. Przejrzeć kluczowe elementy sklepu pod kątem **technicznych pozostałości**, np. teksty widoczne dla klienta, które odsyłają do ścieżki w panelu, gdzie robi się konfigurację. Do tego domyślne treści IdoSell, przykładowe wpisy, standardowy blog i placeholdery.
3. Zebrać wnioski do wycen przyszłych migracji. Przyjmujemy, że to **pierwsza migracja prowadzona wspólnie z SI**: wnioski są początkiem bazy, a nie gotowym wzorcem. Skill powstanie dopiero po kilku kolejnych migracjach.

## Kontekst i ustalenia
- **System zaplecza: w grudniu 2026 bezpośrednio na eNovę.** Wszystko, co ustalono z Base/Baselinkerem, jest **anulowane** (ustalenie użytkownika z 2026-11-12, zmienia zapis w ClickUp „do końca roku Baselinker”). Projekt `SI/02_Serwisy/Base/Powiazania_produktow/ivemax` nie jest już aktualny.
- Panel: `client52797.idosell.com`. Domena techniczna sklepu: `shop52797-1.yourtechnicaldomain.com`. Stary sklep: Shoper/Shoparena (`sklep407784`).
- Języki: jedna domena z wersjami językowymi. Płatności: IdoPay + Stripe + PayPal. Promocje i marketplace na Shoperze są wyłączone, wracają po Nowym Roku. Edrone do usunięcia (współpraca zakończona). Opinie: na Shoperze Trusted Shops.
- Poprzednie edycje zadania (ten sam układ 5 etapów, 34 podzadania):
  - [wrzesień](https://app.clickup.com/t/869f5tur5) (22–29.09): szacunek 8 h, zalogowane ~4,7 h;
  - [kontynuacja](https://app.clickup.com/t/869f97xb8) (30.09–28.10): szacunek 6 h, zalogowane 5,9 h na zadaniu głównym i 7,9 h na etapach; do sprawdzenia, czy czas etapów wlicza się w 5,9 h;
  - listopad (od 28.10): szacunek 6 h, zalogowane ~0,6 h.

## Dane wejściowe i wyjściowe
Wejście:
- zadanie ClickUp z podzadaniami i komentarzami (tylko odczyt);
- panel IdoSell i front sklepu (Claude in Chrome, tylko odczyt);
- wcześniejsze wyceny migracji w ClickUp (dresowka.pl, frezydodrewna.pl, yellowsport.pl) oraz proces PM [[Proces] Migracja na idosell](https://app.clickup.com/t/869b3dftd).

Wyjście (w tym folderze, chyba że zaznaczono inaczej):
- `stan_panelu.md`: pozycja → stan w panelu → stan w ClickUp → bloker / kto / od kiedy;
- `pozostalosci_techniczne.md`: znaleziska na froncie i w treściach (URL, cytat, gdzie poprawić w panelu);
- `wiadomosci_transakcyjne/`: raport stanu (skill `/wiadomosci-transakcyjne`, tylko odczyt) i przygotowanie do pracy nad treściami;
- `komentarz_clickup.txt`: pytania do klienta i zespołu, wkleja użytkownik;
- `../../wnioski_wyceny_migracji.md` (poziom projektu `Migracje`): czas na etap, szacunek kontra wykonanie, blokery, lista startowa pytań do klienta.

## Plan
1. **Przegląd panelu** (Claude in Chrome, tylko odczyt) według listy z opisu zadania i podzadań. Obejmuje też obszary skonfigurowane przez IdoSell: dane firmy, VAT, poczta, dostawy, płatności, COP, panel klienta, regulaminy, zwroty i reklamacje, CMS, blog, meta, robots.txt, języki, waluty, rabaty, opinie, wyszukiwarka, rekomendacje, bannery. Wynik: `stan_panelu.md`.
2. **Pozostałości techniczne na froncie:** strona główna, karta i lista produktów, koszyk i COP (bez składania zamówienia), panel klienta, stopka, podstrony CMS i regulaminy, blog i aktualności, strona 404, maile podglądowe. Szukam:
   - tekstów typu „Panel → Moduły → …”, „Ustaw w panelu”, „Lorem ipsum”, „Przykładowy…”;
   - domyślnych treści IdoSell i danych demo;
   - linków do domeny technicznej lub do Shopera;
   - resztek edrone.
   Wynik: `pozostalosci_techniczne.md`.
3. **Wiadomości transakcyjne:** raport stanu skillem `/wiadomosci-transakcyjne` (tylko odczyt). Przygotowanie do pracy nad treściami, w tym nad wersjami językowymi. **Edycję i tłumaczenia wstrzymuję do czasu dostępu do dedykowanej aplikacji do tłumaczeń** (klucz DeepL podany 2026-11-04; czekamy na dostęp).
4. **Blokery:** tabela z właścicielem i datą + `komentarz_clickup.txt`. Pozycje Base (synchronizacja stanów i cen, dokumenty sprzedaży) przepinam na eNovę jako „do ustalenia z eNovą, grudzień”.
5. **Wnioski do wycen:** `../../wnioski_wyceny_migracji.md`, czyli czas z trzech edycji i porównanie z wcześniejszymi wycenami oraz procesem PM. Zaznaczam, co robi IdoSell, a co my, oraz pytania startowe (DNS i poczta, ERP, opinie, języki, płatności, analityka, wiadomości transakcyjne).

## Kolejność realizacji (potwierdzana 2026-11-12)
Zakres frontu: **tylko wersja PL** (inne języki po tłumaczeniach) — decyzja użytkownika 2026-11-12.

| # | Krok | Narzędzie | Wynik |
|---|---|---|---|
| 1 | Odczyt zadania listopadowego: opis, 34 podzadania (statusy), komentarze | ClickUp (odczyt) | notatki robocze do kroku 4 |
| 2 | Odczyt edycji wrzesień (869f5tur5) i październik (869f97xb8): statusy, komentarze, czas zalogowany na zadaniu i etapach | ClickUp (odczyt) | dane do `wnioski_wyceny_migracji.md` |
| 3 | Odczyt procesu PM (869b3dftd) i wycen dresowka.pl, frezydodrewna.pl, yellowsport.pl | ClickUp (odczyt) | dane porównawcze do wniosków |
| 4 | Przegląd panelu `client52797.idosell.com` obszar po obszarze: dane firmy, VAT, poczta, dostawy, płatności (IdoPay/Stripe/PayPal), COP, panel klienta, regulaminy, zwroty i reklamacje, CMS, blog, meta, robots.txt, języki, waluty, rabaty, opinie (Trusted Shops), wyszukiwarka, rekomendacje, bannery, edrone, integracje (Base → eNova) | Claude in Chrome (odczyt) | `stan_panelu.md` |
| 5 | Przegląd frontu PL (`shop52797-1.yourtechnicaldomain.com`): strona główna, lista i karta produktu, koszyk i COP do kroku przed złożeniem, logowanie/panel klienta, stopka, podstrony CMS i regulaminy, blog/aktualności, 404; wyszukiwanie fraz technicznych i linków do domeny technicznej/Shopera/edrone (także w kodzie strony) | Claude in Chrome (odczyt) | `pozostalosci_techniczne.md` |
| 6 | Raport stanu wiadomości transakcyjnych (bez edycji i tłumaczeń) | skill `/wiadomosci-transakcyjne` (odczyt) | `wiadomosci_transakcyjne/` |
| 7 | Tabela blokerów (właściciel, od kiedy) w `stan_panelu.md` + pytania do klienta i zespołu | — | `komentarz_clickup.txt` |
| 8 | Wnioski do wycen: czas na etap, szacunek vs wykonanie, co robi IdoSell a co my, blokery, lista startowa pytań | — | `../../wnioski_wyceny_migracji.md` |
| 9 | Aktualizacja „Stan” w tej analizie, `Migracje/README.md` i historii w `SI/Klienci/ivemax.com.md` (po akceptacji wpisów) | — | — |

Po krokach 3, 5 i 8 krótkie podsumowanie dla użytkownika. Nic w panelu ani w ClickUp nie zmieniam; git (`/zapisz`, `/zamknij`) wykonuje użytkownik.

## Założenia
- Niczego w panelu nie zmieniam bez osobnej zgody użytkownika. Etap analizy jest tylko do odczytu.
- Nie składam zamówienia testowego, bo nie ma go w planie. Jeśli okaże się potrzebne, robię je przez DevTools i według zasad globalnych.
- Haseł z opisu zadania i komentarzy ClickUp nie przepisuję do żadnych plików.

## Otwarte pytania
- Co dokładnie skonfigurował IdoSell (IAI)? Pytanie zadano w tickecie 22.09, odpowiedzi nadal nie ma. Przegląd panelu częściowo to pokaże.
- Kiedy będzie dostęp do aplikacji do tłumaczeń?
- Zakres integracji z eNovą: kto ją konfiguruje, czy dokumenty sprzedaży wysyła eNova, czy obejmuje wysyłki. Kiedy w grudniu?
- Czy czas etapów w ClickUp wlicza się w czas zadania głównego? Ważne przy liczeniu godzin do wycen.

## Zasady sesji
- ClickUp tylko do odczytu; komentarz → `komentarz_clickup.txt` (wkleja użytkownik).
- Git: worktree .worktrees/migracja_ivemax, gałąź migracja_ivemax; nie przełączaj gałęzi; /zapisz i /zamknij wykonuje użytkownik w tym oknie.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: tak (panel i front sklepu przez Claude in Chrome) — jedna sesja z Claude in Chrome naraz.
- Zamówienie testowe i sprawdzanie zdarzeń na stronie sklepu (jeśli w planie): **tylko przez Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`, osobny profil), nie przez Claude in Chrome.
  - Zamówienie: tani produkt, 1 szt., płatność „przelew zwykły”, nigdy za pobraniem (globalny CLAUDE.md).
  - Panele i platformy reklamowe zostają w Claude in Chrome.
- Przeczytaj `SI/Klienci/ivemax.com.md` i przestrzegaj zasad klienta.

## Stan
- 2026-11-12: analiza wstępna (sesja /zadanie), uwzględnia odpowiedzi użytkownika: eNova w grudniu, Base anulowane, pozostałości techniczne, tłumaczenia po dostępie do aplikacji.
- 2026-11-12: kroki 1–5, 7, 8 wykonane: `stan_panelu.md`, `pozostalosci_techniczne.md`, `komentarz_clickup.txt`, `../../wnioski_wyceny_migracji.md`. Odpowiedź na otwarte pytanie: czas podzadań **nie** wlicza się w czas zadania głównego (wpisy czasu; razem ≈22,8 h przy szacunku 20 h). Nowe ustalenia z panelu: aplikacja „Idomods Translator” już podpięta (klucz API aktywny); „Klucz API Base.” był aktywny – zdezaktywowany 12.11 (użytkownik); metody dostaw obsługuje indywidualna aplikacja w panelu (użytkownik); tickety IdoSell o Bridge–enova365 (09.11, 12.11). Krok 6 wykonany: `wiadomosci_transakcyjne/RAPORT_stan_wiadomosci.md` (eksport ZIP za zgodą użytkownika, pliki w `Wiadomosci_transakcyjne/Eksport i Import Treści/client52797_shop1/2026-11-12_113445/`). Odpowiedź na otwarte pytanie: IdoSell nie dostosowywał wiadomości (czysty standard). W koszyku sesji przeglądarki został 1 szt. produktu 2992027 (bez zamówienia).
