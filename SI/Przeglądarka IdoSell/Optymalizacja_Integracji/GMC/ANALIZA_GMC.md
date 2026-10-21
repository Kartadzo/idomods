# ANALIZA — Diagnostyka integracji IdoSell ↔ Google Merchant Center

Data: 2026-10-21 (wersja 1, przed pilotażem)

## Cel (własnymi słowami)

Skill `weryfikacja-gmc` to powtarzalna, okresowa diagnostyka konta Google Merchant Center sklepu IdoSell, prowadzona w przeglądarce (Claude in Chrome) według tego samego schematu co `weryfikacja-fb`. Zaczyna się od zadania ClickUp typu „<domena> gAds - Optymalizacja GMC”, w którego opisie są linki do kont GMC. Kończy się raportem wewnętrznym, raportem `.docx` dla klienta i 4-zdaniowym komentarzem do ClickUp.

To przegląd stanu i regresji, a nie audyt wdrożeniowy. Skupiam się na czterech obszarach:
1. **Feed produktowy**: odrzucone i ograniczone produkty, problemy na poziomie atrybutów i trend.
2. **Pobieranie i przetwarzanie feedu**: ostatnio problemy pojawiały się zarówno po stronie serwera IdoSell, jak i po stronie GMC.
3. **Cennik dostaw w GMC** (jeśli jest skonfigurowany): zgodność z cennikiem w IdoSell i z kosztem dostawy w feedzie.
4. **Nowe elementy feedu**: parametry z panelu i atrybuty Google, które warto dodać do feedu (analogicznie do FB).

**Zdarzeń konwersji Google Ads nie sprawdzam**, chyba że ktoś wyraźnie o to poprosi (sekcja E).

## Wejście

- Zadanie ClickUp → domena (pierwszy człon nazwy) i linki do kont GMC z opisu, w formacie:
  ```
  google: <link lub puste>
  brands: <link lub puste>
  ```
  Parametr `a=<ID konta>` w linku to ID konta Merchant Center. Przykład pilotażowy: [PewienPan.pl gAds - Optymalizacja GMC](https://app.clickup.com/t/86939c9w4), w którym jest tylko `brands: …?a=9465371`.
- Panel IdoSell sklepu (zalogowana sesja w Chrome).
- Merchant Center (zalogowana sesja Google z dostępem do kont).
- Poprzedni raport `GMC/raporty/<domena>_*/RAPORT_wewnetrzny.md` jako stan bazowy, jeśli istnieje.

## Konta GMC i CSS — reguły

Mamy własny CSS, więc sklep może mieć dwa konta GMC:
- **google** to konto pod CSS Google Shopping,
- **brands** to konto pod CSS BRANDS MANAGO SP. Z O.O.

Typowe przypadki:
| Sytuacja | Co zwykle widać |
|---|---|
| Standard | oba konta |
| Klient ma równolegle IAI Ads | tylko konto **brands**, bo miejsce pod CSS Google Shopping zajmuje inna firma |
| Sprzedaż poza Polskę | tylko konto **google** |

Odstępstwo od tych reguł odnotowuję w raporcie wewnętrznym jako „info”. Nie traktuję go jako błędu.

**Konta nieużywane:** mogę mieć dostęp do kont, których już się nie używa. Przed analizą każdego konta sprawdzam, czy **witryna jest zweryfikowana i zgłoszona** (Ustawienia → Informacje o firmie → Witryna) i czy konto nie jest zawieszone. Jeśli konto nie jest zweryfikowane, odnotowuję to i nie analizuję go dalej. Konto zweryfikowane, ale bez produktów lub bez źródła danych, opisuję krótko jako „nieaktywne”.

## Lista kontrolna

### 0. Start
1. `clickup_get_task` → nazwa, domena, linki `google`/`brands` → ID kont. Brak obu linków → pytam użytkownika.
2. Poprzedni raport → stan bazowy (liczba produktów, odrzucone, źródła danych, harmonogram, cennik dostaw).
3. Folder wyników: `GMC/raporty/<domena>_<data>/zrzuty/`.

### A. Panel IdoSell
1. `/panel/config-pricecomparers.php`: wiersze Google („Google ads …”, natywny „Google Merchant Center”, inne). Dla każdego sprawdzam status, „wygenerowany o godzinie”, liczbę eksportowanych i wyeksportowanych towarów. Dopasowuję serwis do źródła danych w GMC po adresie pliku (tylko `pathname`, bo filtr rozszerzenia blokuje tokeny).
2. **Historia pobrań** (pierwsze 3 strony, potem co 10.): regularność pobrań przez Google, luki, zdarzenia inne niż pobranie, błędy. Na tej podstawie odróżniam problem po stronie IdoSell (plik niewygenerowany lub nieaktualny, brak wpisów mimo prób GMC) od problemu po stronie GMC (plik gotowy, GMC go nie pobrał lub przetworzył z błędem).
3. **Ustawienia → sterownik XSLT**: tylko zmienne konfiguracyjne z początku (`Koszt_dostawy`, progi darmowej dostawy, `Kraj_dostawy`, `*_nazwa_w_panelu`, listy `gender_*`, `age_group_*`, `kolor_*`, `material_*`, etykiety `custom_label`). Sterownika nie uruchamiam i nie analizuję jego logiki.
4. **Cennik dostaw**: `/panel/config-shipping.php` → profile dostaw → najtańszy kurier i progi dla kraju feedu (tak jak w FB, kroki A5).
5. **Parametry**: `/panel/parameters.php` porównane ze zmiennymi z A3 (tak jak w FB, krok A6) i zmapowane na atrybuty Google (sekcja D).

### B. Merchant Center — stan konta i feedu
Dla każdego aktywnego konta (google / brands):
1. **Weryfikacja i stan konta**: witryna zweryfikowana/zgłoszona, problemy na poziomie konta (zawieszenie, wprowadzanie w błąd, brak danych firmy, weryfikacja tożsamości lub telefonu), przypisany CSS. **Zrzut.**
2. **Przegląd produktów**: zatwierdzone, ograniczone, niezatwierdzone, oczekujące, w podziale na kanały (reklamy produktowe i bezpłatne informacje), trend względem stanu bazowego. **Zrzut.**
3. **Problemy z produktami (diagnostyka)**: lista problemów z liczbą produktów, wpływem i przykładowymi ID. Rozróżniam błędy feedu (brak GTIN, nieprawidłowa cena lub dostępność, za duże obrazy, zła kategoria, niezgodność ceny ze stroną) od błędów zasad. Drobne problemy (aktualność cen i stanów, niedostępna strona) oceniam według skali i trendu. **Zrzut.**
4. **Źródła danych**: typ (plik zaplanowany, API, Content API, automatyczne ze strony), harmonogram pobierania, data i wynik ostatniego pobrania, liczba przetworzonych pozycji, ostrzeżenia i błędy przetwarzania (np. „nie udało się pobrać”, timeout, błąd HTTP, zbyt duży plik), historia ostatnich pobrań. Porównuję liczbę pozycji z liczbą towarów w IdoSell (A1). **Zrzut.**
5. **Automatyczne ulepszenia** (ceny, dostępność, jakość zdjęć): czy są włączone. Ich masowe użycie przy aktualizacji cen sygnalizuje rozjazd feedu ze stroną.
6. **Połączone konta**: czy konto jest połączone z Google Ads (bez analizy konwersji).

### C. Merchant Center — dostawa i zwroty
1. **Ustawienia dostawy** (jeśli istnieją): kraje, przewoźnik, koszt, próg darmowej dostawy, czas obsługi i dostawy. **Zrzut.**
2. Porównanie z cennikiem IdoSell (A4), z kosztem dostawy w XSLT (A3) i z poprzednim raportem. Pamiętam o pierwszeństwie: atrybut `shipping` w feedzie nadpisuje ustawienia konta, więc rozjazd liczy się tylko tam, gdzie feed nie podaje kosztu.
3. **Zasady zwrotów**: czy są skonfigurowane (tylko informacyjnie).

### D. Nowe elementy feedu
Lista parametrów z panelu (A5) zmapowana na atrybuty Google. Wynik trafia tylko do raportu wewnętrznego:
- pasujące do istniejących zmiennych sterownika, w tym różnice wielkości liter,
- kandydaci do dodania: `color`, `size`, `material`, `pattern`, `gender`, `age_group`, `condition`, `product_detail`, `product_highlight`, `custom_label_0–4`, `product_type`, `google_product_category`, `unit_pricing_measure`, `certification`, `free_shipping_threshold` i inne aktualnie wspierane atrybuty (listę sprawdzam w specyfikacji Google przy pilotażu),
- parametry niskiej jakości lub wymagające dużo pracy,
- atrybuty, które GMC wskazuje w diagnostyce jako brakujące lub zalecane (np. „Brak wartości [color]”) — to najmocniejszy argument za zmianą.

### E. Zdarzenia konwersji (tylko na wyraźną prośbę)
Najpierw ustalam typ integracji:
| Typ | Jak rozpoznać | Co robimy |
|---|---|---|
| Standardowa IdoSell | moduł Google Ads w panelu IdoSell, tag w kodzie strony bez naszych dodatków | Nie mamy na nią wpływu. Robię zrzuty i przygotowuję treść zgłoszenia do Biura Obsługi Klienta IdoSell. |
| Niestandardowa w dodatkach HTML | kod `gtag`/`conversion` w dodatkach HTML/JS panelu (znacznik `<!-- Begin additional html or js -->`) | Nasza. Analizuję szczegółowo i proponuję poprawki. |
| Niestandardowa w GTM | kontener `GTM-XXXX` w kodzie strony, tag konwersji w GTM | Nie nasza. Proponuję poprawki właścicielowi kontenera. |

## Wyjście

Tak samo jak w FB:
1. `GMC/raporty/<domena>_<data>/dane.json` → `Raport_GMC_<domena>_<data>.docx` + `komentarz_clickup.txt` (4 zdania, publikuje użytkownik).
2. `GMC/raporty/<domena>_<data>/RAPORT_wewnetrzny.md`: ID kont i CSS, tabele A–D, stan bazowy, parametry vs sterownik vs atrybuty Google, proponowane zmiany (gdzie, przed → po, status).
3. Skill `.claude/skills/weryfikacja-gmc/SKILL.md` + `GMC/Weryfikacja_GMC.bat` (ASCII, wzór: `FB/Weryfikacja_FB.bat`).

## Planowane zmiany w plikach

- `GMC/ANALIZA_GMC.md` — ten plik.
- **Narzędzia wspólne**: `zrzut.py` jest niezależny od platformy, a `raport_docx.py` ma na sztywno „Meta Ads” w tytule i nazwie pliku. Proponuję przenieść oba do `Optymalizacja_Integracji/narzedzia/` i dodać do `dane.json` pole `platforma` (`Meta Ads` / `Google Merchant Center`) z domyślną wartością „Meta Ads”, żeby stare raporty FB generowały się bez zmian. Skill FB zaktualizuję o nową ścieżkę.
- `.claude/skills/weryfikacja-gmc/SKILL.md` — pisany **po pilotażu** na PewienPan.pl, z rzeczywistymi selektorami i adresami GMC (jak przy FB).
- `GMC/Weryfikacja_GMC.bat`.
- Pamięć: wpis projektowy GMC i odnośnik w `MEMORY.md`.

Pracuję na gałęzi `optymalizacja-integracji-gmc`.

## Zasady (przejęte z FB)

- Tylko odczyt. Nie klikam „Zapisz”, „Usuń”, „Pobierz teraz”/„Pobierz ponownie”, „Poproś o weryfikację”, „Połącz” ani „Odłącz”. Zmiany proponuję w raporcie i wdrażam po zgodzie, z zapisem „przed/po”.
- Logowanie (IdoSell, Google) robi użytkownik.
- Na zrzutach nie ma danych osobowych.
- Technika Chrome jak w `weryfikacja-fb` (panel IdoSell przez `javascript_tool`, zrzuty przez `zrzut.py`, filtr URL-i).

## Założenia

- Interwał 90 dni, jak w FB.
- Kraj docelowy feedu odczytuję ze sterownika (`Kraj_dostawy`) i z ustawień GMC.
- Merchant Center to nowy interfejs („Merchant Center Next”). Adresy i selektory ustalę podczas pilotażu.
- Jeśli oba konta (google i brands) korzystają z tego samego pliku feedu, sekcję A robię raz, a sekcje B–C osobno dla każdego konta.

## Ustalenia (wersja 2, 2026-10-21 — odpowiedzi użytkownika)

1. **Pobranie ręczne:** przy błędzie pobierania wolno kliknąć „Pobierz teraz” (lub odpowiednik) w GMC. Ponowienie zwykle wystarcza, a problem po stronie GMC mógł być jednorazowy. Wynik ponowienia zapisuję w raporcie. To jedyny wyjątek od zasady „tylko odczyt”.
2. **Wspólne narzędzia:** zatwierdzone — `zrzut.py` i `raport_docx.py` przenoszę do `Optymalizacja_Integracji/narzedzia/`, `dane.json` dostaje pole `platforma`.
3. **Które konto analizuję:** to **z większą liczbą produktów**. Standardowo produkty wpinamy do konta pod CSS BRANDS MANAGO SP. Z O.O., a konto pod CSS Google Shopping pobiera towary tylko na potrzeby bezpłatnych informacji (free listings) **z konta BRANDS MANAGO**. Drugie konto sprawdzam skrótowo: weryfikacja, liczba produktów, czy źródło danych działa.
4. **Wzorce problemów z pobieraniem (komunikat w GMC):**
   - **błąd autoryzacji** mimo braku blokady pliku → problem po stronie serwera IdoSell,
   - **błąd wewnętrzny** (bez szczegółów) → zwykle po stronie GMC.
   W obu przypadkach najpierw ponawiam pobieranie i sprawdzam wynik. Błąd powtarzający się po ponowieniu, potwierdzony w historii pobrań IdoSell, opisuję w raporcie i przygotowuję treść zgłoszenia.
5. **Pilotaż:** PewienPan.pl, konto `brands` 9465371 — start od razu.

## Wnioski z pilotażu (pewienpan.pl, 2026-10-21) — przeniesione do skilla

- Wynik: `raporty/pewienpan.pl_2026-10-21/` (stan bazowy). Skill: `.claude/skills/weryfikacja-gmc/SKILL.md`, launcher `Weryfikacja_GMC.bat`.
- Natywny feed Google w IdoSell jest pod `config-pricecomparers.php?return=google_shopping` (zwykła lista porównywarek go nie pokazuje), a nasz feed uzupełniający („[BM] Google ads …”, XSLT) jest na zwykłej liście i podpięty w GMC jako źródło dodatkowe.
- IdoSell ogranicza dostęp do pliku do „predefiniowanych adresów IP serwisu”. Obce serwery dostają „Nieudana próba pobrania”. **Hipoteza do potwierdzenia:** „błąd autoryzacji” w GMC pojawia się, gdy Google pobiera z adresu IP spoza listy IdoSell.
- Godzina pobierania w GMC równa godzinie startu generowania w IdoSell oznacza pobranie starszego pliku i automatyczne korekty cen i dostępności.
- Zasady dostawy w GMC nie działają, gdy feed podaje `shipping` (sprawdzić w „Kalkulatorze dostawy” produktu).
- Technika: rozszerzenie nie robi zrzutów w GMC, więc używamy `zrzut.py` (karta musi być aktywna w widocznym oknie). Wynik JS jest obcinany do ~1000 znaków. Tabele GMC ładują się 8–12 s. Ikona przy kolumnie „Widoczność” w zasadach dostawy otwiera menu ukrywania.

## Wersja 3: specyfikacja Google jako podstawa analizy parametrów (2026-10-21)

- Na prośbę użytkownika mapowanie parametrów na atrybuty opieram na [specyfikacji danych produktów Google](https://support.google.com/merchants/answer/7052112?hl=pl).
- Ściąga z limitami jest w `.claude/skills/weryfikacja-gmc/specyfikacja_google.md`. Krok B.6 skilla oprócz nowych atrybutów sprawdza też zgodność obecnego XSLT ze specyfikacją.
- Przed powołaniem się na limit lub termin sprawdzam go ponownie przez WebFetch, bo specyfikacja się zmienia.
- Wynik dla pewienpan.pl:
  - `g:adult=yes` dla kategorii menu 605 jest błędne,
  - `material` może mieć najwyżej 3 wartości, a XSLT przekazuje 4,
  - `product_highlight` wymaga co najmniej 2 wpisów,
  - „Slim” nie pasuje do `size_type`, więc trafia do `product_detail`,
  - termin dla zdjęć 500 × 500 px to 31.01.2027.

## Wersja 4: model feedu i błąd autoryzacji (2026-10-21)

- **Model feedu** rozpoznajemy po URL źródła podstawowego:
  - `googleshopping` oznacza standardowy feed IdoSell z naszym feedem uzupełniającym,
  - `feed<id>` oznacza jeden nasz feed XSLT. Natywnego feedu wtedy nie sprawdzamy.
- **Błąd autoryzacji** to problem serwera IdoSell. Hipoteza o adresie IP jest wycofana jako niepotwierdzona.
  - Obejście (za zgodą): podpiąć feed domyślny IdoSell → zaktualizować źródło → przywrócić feed niestandardowy.
  - Zgłoszenie do BOK ma sens dopiero wtedy, gdy feed domyślny też nie działa.
