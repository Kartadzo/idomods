---
name: weryfikacja-gmc
description: Okresowa (co 90 dni) diagnostyka Google Merchant Center sklepu IdoSell przez Claude in Chrome — weryfikacja konta i CSS, stan produktów, pobieranie i przetwarzanie feedu (historia pobrań IdoSell vs źródła danych GMC), zasady dostawy GMC vs cennik IdoSell vs XSLT, nowe parametry do feedu. Wynik: raport .docx dla klienta ze zrzutami, raport wewnętrzny .md i 4-zdaniowy komentarz do ClickUp. Używaj, gdy użytkownik podaje zadanie ClickUp typu „<domena> gAds - Optymalizacja GMC”, mówi „weryfikacja GMC”, „diagnostyka Merchant Center”, „sprawdź feed Google” albo wywołuje /weryfikacja-gmc <link>.
---

# Diagnostyka IdoSell ↔ Google Merchant Center

KATALOG: `SI/Przeglądarka IdoSell/Optymalizacja_Integracji/GMC/` (narzędzia wspólne z FB: `../narzedzia/`). Specyfikacja: `ANALIZA_GMC.md`.
Wzorzec wyniku: `raporty/pewienpan.pl_2026-10-21/` (`dane.json`, `RAPORT_wewnetrzny.md`).

## Zasady (zawsze)
- **Tylko odczyt**, z jednym wyjątkiem: przy błędzie pobierania feedu wolno kliknąć „Zaktualizuj” przy źródle danych w GMC (ponowne pobranie) i opisać wynik. Pozostałe zmiany proponuję w raporcie i wdrażam dopiero po zgodzie, pozycja po pozycji, z zapisem „przed/po”.
- Nie klikam: „Zapisz”, „Usuń”/kosz, „Zarchiwizuj”, „Dodaj wszystkie znalezione produkty”, „Zastosuj aktualizację”, „Pobierz plik”/„Pobierz produkty”, „Włącz teraz”, „Wyłącz integrację”, „Resetuj” (IP), nie zmieniam widoczności ani ustawień konta.
- **Zdarzeń konwersji Google Ads nie sprawdzam**, chyba że ktoś o to poprosi (patrz sekcja E).
- Logowanie (IdoSell, Google) robi użytkownik.
- Komentarza do ClickUp nie publikuję. Na zrzutach nie może być danych osobowych.
- Sterownik XSLT naszego feedu (podstawowego albo uzupełniającego) uznaję za działający. Czytam tylko zmienne i listę elementów `g:*`, bez podglądu i bez analizy logiki.

## Konta GMC i CSS
- Opis zadania: `google: <link>` (CSS Google Shopping) i `brands: <link>` (CSS BRANDS MANAGO SP. Z O.O.). ID konta = parametr `a=`.
- Standardowo produkty wpinamy do konta **brands**. Konto **google** pobiera towary z konta brands tylko na potrzeby bezpłatnych informacji. Klient z IAI Ads → zwykle tylko brands. Sprzedaż poza Polskę → zwykle tylko google.
- **Pełna analiza dotyczy konta z większą liczbą produktów.** Drugie konto sprawdzam skrótowo: weryfikacja, liczba produktów, czy źródło działa.
- Każde konto przed analizą: `/mc/merchantprofile/businessinfo` → „Twój sklep internetowy” musi mieć status **Zweryfikowany**. Bez tego statusu konto opisuję jako nieużywane i nie analizuję dalej.
- CSS konta odczytuję z przełącznika kont (klik w nazwę konta u góry): „Usługa porównywania cen: …”. Wpisanie fragmentu domeny w „Wyszukaj firmę” pokazuje wszystkie dostępne konta sklepu.

## Technika Claude in Chrome
- W GMC i w panelu IdoSell `screenshot`/`find`/`get_page_text` się zawieszają. Używam `javascript_tool` (krótkie wywołania, czekanie przez `await new Promise(r=>setTimeout(r,N))`) i `computer.left_click` po współrzędnych z `getBoundingClientRect()`.
- Wynik `javascript_tool` jest obcinany do ~1000 znaków: tekst zapisuję do `window.__t` i czytam `__t.slice(a,b)`. Usuwam szum ikon (`thumb_up`, `more_vert`, `expand_more`, `help_outline`…).
- Filtr blokuje query string i base64 (`[BLOCKED: …]`): z linków zwracam tylko `pathname` i nazwy parametrów. Nie obchodzę filtra.
- GMC ładuje tabele z opóźnieniem: po nawigacji czekam 8–12 s, zanim uznam listę za pustą.
- **Zrzuty**: karta MCP musi być **aktywną kartą widocznego okna**. Jeśli `zrzut.py` nie znajduje okna, proszę użytkownika o przełączenie na kartę „[CLAUDE] …”. Przed zrzutem: `document.title='[CLAUDE] '+document.title.replace(/^\[CLAUDE\] /,'')`, potem w KATALOGU:
  `python ../narzedzia/zrzut.py "[claude]" "raporty/<domena>_<data>/zrzuty/NN_opis.png" --obszar strona`
  Podgląd roboczy zapisuję do scratchpada i oglądam przez Read.

## 0. Start
1. `clickup_get_task` (z `include: ["description"]`) → domena (pierwszy człon nazwy) i linki kont. Brak obu linków → pytam.
2. `data` = dzisiaj. Folder: `raporty/<domena>_<data>/zrzuty/`. Poprzedni raport `raporty/<domena>_*/RAPORT_wewnetrzny.md` daje stan bazowy.
3. `tabs_context_mcp` → karta → `https://merchants.google.com/mc/overview?a=<ID>&hl=pl`.

## A. Merchant Center (adresy z `?a=<ID>&hl=pl`)
1. `/mc/merchantprofile/businessinfo` — weryfikacja witryny. **Zrzut 04.**
2. `/mc/products/diagnostics/accountissues` — problemy z kontem i zasadami.
3. `/mc/products/diagnostics/history` — liczby: zatwierdzone / ograniczone / niezatwierdzone / w trakcie, wykres 28 dni, a w panelu bocznym „Problemy wymagające uwagi (N)” (rozwinąć `expand_more`: nazwa, liczba produktów). **Zrzut 05.** Zakładka „Wymaga uwagi” (`/mc/products/diagnostics`) bywa pusta mimo problemów, dlatego liczy się panel boczny.
   Typowe: obraz < 500×500, `unit_pricing_measure`, automatyczne korekty ceny i dostępności (sygnał rozjazdu godzin, patrz A5), niska jakość zdjęć. Pobranie listy produktów to pobranie pliku, więc robię je tylko za zgodą.
4. `/mc/products/sources` — „Znalezione przez Google” (produkty spoza feedu), **Źródła podstawowe** (nazwa, typ, liczba produktów, ostatnia aktualizacja; źródło „Merchant Center / Dodano w Merchant Center” = produkty ręczne). **Zrzut 06.** Zakładka „Źródła dodatkowe” (czekać ~12 s). **Zrzut 06b.**
5. Szczegóły źródła (`/mc/products/sources/detail`, klik w nazwę): „Wyświetl historię aktualizacji” → lista wersji w `[aria-haspopup]` → dla każdej wersji wynik („Zaktualizowano produkty”, „Nie znaleziono problemów”, liczba nowych). Pętlę po 10 wersjach uruchamiam w tle (`(async()=>{…})()` do `window.__v`) i czytam osobnym wywołaniem, bo dłuższe niż 45 s zawiesza `javascript_tool`. Bez źródeł dodatkowych zakładki „podstawowe/dodatkowe” się nie pojawiają. Zakładka „Konfiguracja źródła danych”: harmonogram, URL pliku (tylko host + `pathname`), kraje, metody marketingowe. Zakładka „Reguły atrybutów”.
   **Godziny:** porównuję godzinę pobierania przez GMC z harmonogramem generowania w IdoSell (B2). Pobranie o tej samej godzinie, o której startuje generowanie, oznacza starszy plik i automatyczne korekty cen.
   **Błąd pobierania:** „błąd autoryzacji” (mimo braku blokady pliku) oznacza problem po stronie serwera IdoSell. BOK nie rozwiązuje go przy feedzie niestandardowym: zrzuca winę na nasz feed i proponuje wycenę. „Błąd wewnętrzny” to zwykle strona GMC. W obu przypadkach najpierw klikam „Zaktualizuj” i sprawdzam wynik.
   Gdy błąd autoryzacji powtarza się przy feedzie niestandardowym, w raporcie proponuję obejście, które wykonuję tylko za zgodą, bo zmienia konfigurację źródła:
   1. W źródle GMC podmienić URL na domyślny feed IdoSell (`googleshopping…`).
   2. Zaktualizować źródło.
   3. Przywrócić URL feedu niestandardowego i ponownie go załadować.

   To obejście jest tymczasowe. Jeśli feed domyślny IdoSell też nie działa, dopiero wtedy jest podstawa do zgłoszenia w BOK, bez argumentu o niestandardowym feedzie.
6. `/mc/accountprefs` — „Zabezpieczenie produktów” (checkbox + %).
7. `/mc/shipping/services` — zasady dostawy: rozwinąć wiersz **strzałką `expand_more` na początku wiersza** (kliknięcie po współrzędnych). Odczytuję koszt, próg darmowej dostawy i czas. **Ikona przy kolumnie „Widoczność” otwiera menu „Pokaż/Ukryj w Google” — zamknąć Escape.** Formularz „edit” to kreator, którego nie używam. **Zrzut 07 (08).** Zakładka „Zasady dotyczące zwrotów”.
8. Produkt przykładowy: `/mc/items` → pierwszy link `/mc/items/details` → zakładka „Kalkulator dostawy”: „Koszt dostawy jest określony w pliku danych” oznacza, że **zasady konta nie mają zastosowania**. **Zrzut 09.**
9. `/mc/linkedaccounts/integrations` (Dostęp i usługi → Połączone usługi): Google Ads, GA4, Profil Firmy.
10. `/mc/taskhub` — powiadomienia. „Zaktualizuj opisy: <kategoria>” → „Wyświetlanie produktów” pokazuje brakujące szczegóły („Kolor, Wzór i Materiał”). **Zrzut 10.**

## B. Panel IdoSell (`https://<domena>/panel/`)
0. **Model feedu** rozpoznaję po URL źródła podstawowego w GMC (A5):
   - `googleshopping…xml`: standardowy feed IdoSell + nasz feed uzupełniający (`feed<id>`) jako źródło dodatkowe. Sprawdzam oba.
   - `feed<id>_…xml`: jeden nasz feed podstawowy z XSLT (częsty wariant). Natywnego feedu IdoSell nie sprawdzam (krok 1 pomijam), a wszystkie atrybuty i dostawa pochodzą z XSLT o tym id.

   Wielosklep: `/panel/config-pricecomparers.php` najpierw pokazuje listę stron; wybieram `[wybierz]` przy domenie (`?shop=<id>`).
1. Natywny feed Google: `/panel/config-pricecomparers.php?return=google_shopping` (zwykła lista porównywarek go nie pokazuje): status, „wygenerowany o godzinie”, eksportowane / wyeksportowane. **Zrzut 01.** Feed uzupełniający („[BM] Google ads …”) jest na zwykłej liście `/panel/config-pricecomparers.php`.
2. „Wybierz → Ustawienia”: harmonogram (`select[name=pricecomparers_generate_hour]`, `pricecomparers_generate_intervals`), opcje „Eksportuj”, informacja o ograniczeniu dostępu do adresów IP serwisu.
3. „Wybierz → Historia pobrań” dla obu feedów: strony ładują się AJAX-em, więc przechodzę je wszystkie pętlą w tle (`następna >`, porównanie pierwszego wiersza). Liczę pobrania Google (hosty 173.194 / 172.217 / 74.125 / 172.253), brakujące dni, „Nieudana próba” i ich hosty. **Zrzut 02.**
4. XSLT naszego feedu (`textarea[name=driver_body]` > 30 000 zn. do `window.__xsl`): zmienne `<xsl:variable>` (koszty dostawy, progi, `*_nazwa_w_panelu`) i lista `xsl:element name="g:…"`.
5. Cennik: `/panel/config-shippingprofiles.php` → „Profile dostaw [wybierz]” → `[edytuj]` profilu (kliknąć przez `setTimeout(()=>a.click(),100)`, bo strona przeładowuje się w trakcie). Tabela: kurier, za pobraniem / z przedpłatą (minimalna wartość, koszt, darmowe od). **Zrzut 03.** „Smile” z minimalną wartością X i kosztem 0 oznacza darmową dostawę od X.
6. Parametry: `/panel/parameters.php`, rozwinąć `ul.list-group > li.menu_li_item a.showChildren` (pauza 500 ms), nazwa z `div.showMenuSub.parameter`, wartości z `ul li`. Mapuję je na atrybuty Google według [specyfikacji danych produktów](https://support.google.com/merchants/answer/7052112?hl=pl). Ściąga z limitami i zakazami jest w `specyfikacja_google.md` w katalogu skilla, a przed powołaniem się na termin lub limit sprawdzam go przez WebFetch. Sprawdzam dwie rzeczy:
   - **nowe atrybuty z parametrów:** `pattern`, `product_detail` (np. „Slim” zamiast `size_type`), `product_highlight` (min. 2 na produkt), `custom_label_0–4` (wolne etykiety), `unit_pricing_measure` (produkty na objętość lub wagę);
   - **zgodność obecnego XSLT ze specyfikacją:** liczba wartości (`material` ≤ 3), separator `/` w `color` i `material`, `g:adult=yes` tylko dla treści erotycznych, `gender` i `age_group` dla odzieży, brak duplikatów między `product_detail`, `product_highlight` i `material`.

   Kopię XSLT z repo (`xslt/<litera>/…`) porównuję z wersją w panelu, bo może być nieaktualna. Analiza trafia tylko do raportu wewnętrznego.

## C. Ocena dostawy
**Priorytety GMC:**
- Ręczna edycja produktu w GMC („Edytuj produkt” na karcie towaru) ma pierwszeństwo przed feedem. Jeśli wartość w GMC nie zgadza się z feedem, sprawdzam, czy produkt nie był edytowany ręcznie.
- Koszt dostawy z feedu (`g:shipping`) ma pierwszeństwo przed zasadami dostawy konta. Zasady konta działają tylko dla produktów, dla których feed nie przekazał `shipping`.

**Tryb `g:shipping` w XSLT** rozpoznaję po zmiennej `kwota_dla_darmowej_dostawy`:
- **Stały** (liczba, np. `500`): `Koszt_dostawy`, próg i czasy są wpisane na sztywno. Porównuję je z cennikiem IdoSell, bo po zmianie cennika trzeba je poprawić ręcznie.
- **Dynamiczny** (`*`): koszt pochodzi z profilu dostaw IdoSell (`price/price_marketplace_site/delivery_cost/prepayment/@gross`). Działa tylko wtedy, gdy profil ma ustawioną **domyślną metodę wysyłki z przedpłatą** i produkt mieści się w zasadach tej metody (waga, gabaryt, wartość). Bez tego feed nie zwraca kosztu, produkt dostaje koszt z zasad konta GMC, a przy braku zasad nie ma kosztu w ogóle. Wtedy sprawdzam zaznaczony „domyślny” w kolumnie przedpłaty profilu (B5), limity tej metody oraz aktualność zasad konta GMC jako zapasu.
- Puste (`''`): feed nie przekazuje `shipping`, więc wszystko zależy od zasad konta GMC (status „problem”, jeśli są nieaktualne).

Porównuję trzy źródła: cennik IdoSell, `g:shipping` w feedzie i zasady konta GMC. Jeśli kalkulator mówi „z pliku danych”, klient widzi koszt z feedu, a nieaktualne zasady konta są tylko zapasem (status „uwaga”, nie „problem”). W trybie dynamicznym sprawdzam kalkulator na 2 produktach: tanim i ciężkim lub dużym.

## D. Raport
1. `raporty/<domena>_<data>/dane.json` jak we wzorcu, z polem `"platforma": "Google Merchant Center"`; `sekcje` zwykle: Feed w IdoSell / Pobieranie i przetwarzanie / Stan produktów / Koszty dostawy / Możliwości rozbudowy feedu. Język nietechniczny, bez identyfikatorów, bez analizy parametrów; `komentarz_clickup` = dokładnie 4 zdania.
2. W KATALOGU: `python ../narzedzia/raport_docx.py "raporty/<domena>_<data>"` → `Raport_GMC_<domena>_<data>.docx` + `komentarz_clickup.txt`.
3. `RAPORT_wewnetrzny.md`: identyfikatory i CSS, tabele IdoSell / GMC, zmienne XSLT, parametry → atrybuty, proponowane zmiany (gdzie, przed → po, status).
4. Zamykam kartę. Podsumowanie dla użytkownika: co w normie, co do poprawy, zmiany do decyzji, ścieżki plików i komentarz.

## E. Zdarzenia konwersji (tylko na prośbę)
| Typ | Rozpoznanie | Działanie |
|---|---|---|
| Standardowa IdoSell | moduł Google Ads w panelu, tag bez naszych dodatków | Zrzuty i treść zgłoszenia do Biura Obsługi Klienta IdoSell |
| Dodatki HTML panelu | `gtag`/`conversion` w dodatkach HTML/JS (`<!-- Begin additional html or js -->`) | Nasza: szczegółowa analiza i propozycja poprawek |
| GTM | kontener `GTM-XXXX` w kodzie strony | Propozycja poprawek dla właściciela kontenera |
