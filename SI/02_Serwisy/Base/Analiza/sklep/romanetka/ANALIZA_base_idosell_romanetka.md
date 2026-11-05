# ANALIZA: Romanetka.pl — połączenie Base ↔ IdoSell

ClickUp: [Romanetka.pl - Problem z połączenie Base - Idosell](https://app.clickup.com/t/869ezaw5q)
Data: 2026-10-27. Tryb: **tylko odczyt**. Niczego nie zapisywałem ani w Base, ani w IdoSell.
MCP Base (`https://mcp.base.com/mcp`) nie jest podpięty w tej sesji. Według dokumentacji udostępnia tylko „Ask Sidebar” (asystenta tekstowego), a nie API ani logi integracji, więc analizę zrobiłem przez panel w przeglądarce.

## Cel zadania (własnymi słowami)
Klient sprzedaje przez Base na Allegro i ERLI i tam synchronizacja działa. Ze sklepem IdoSell (romanetka.pl) synchronizacja praktycznie nie działa: Base ma ~90 tys. produktów, IdoSell ~29 tys., a powiązanych jest tylko kilka. Trzeba ustalić przyczynę i sposób naprawy (budżet 1 h, w przeciwnym razie wycena).

## Stan integracji w Base (IdoSell „IdoS Romanetka”, ID integracji 3026512)

| Obszar | Ustawienie | Wniosek |
|---|---|---|
| Połączenie API | „Połączenie ze sklepem jest aktywne” | API działa, to **nie** jest problem z kluczem |
| Pobieranie zamówień | **Nie** | Zamówienia z IdoSell nie trafiają do Base, więc sprzedaż w sklepie nie zdejmuje stanów w Base |
| Przekazywanie zamówień z marketplace do sklepu | Nie | OK (obsługa w Base) |
| Pobieranie produktów (podgląd na żywo) | Tak, link `romanetka.pl/pl/products/[product_name]-[product_id].html` | — |
| **Eksport produktów do sklepu** | **Tak** + eksport cykliczny (ID 158) z katalogu **„Domyślny”**, codziennie o 0:00 | Base próbuje **tworzyć** produkty w IdoSell |
| Stany | Base → sklep (sklep podrzędny), na żywo | logi co minutę: **0 zmienionych produktów** |
| Ceny | Base → sklep, co 24 h, zaokrąglenie w górę do pełnej kwoty | 0–5 zmienionych produktów dziennie |
| Katalogi w Base | Domyślny, Oknosfera123-erli, romanetka-pl-erli, producent-firany-erli | Allegro/ERLI działają na katalogach `*-erli` |

### Logi eksportu do IdoSell (Produkty → Import/Eksport → Eksport)
- Komunikat: „Produkty z nieudanymi eksportami nie będą ponawiane do czasu wyczyszczenia błędów (**Produkty z błędami: 17047**)”.
- Eksport 26.10: 822 produkty, 27.10: 852 produkty. W sprawdzonej próbce (150 wierszy) wszystkie mają błąd:
  **`Connector error: Field category_id is required and cannot be empty`**.
- Nie widziałem ani jednego udanego eksportu (brak ID z magazynu zewnętrznego w wierszach).

### Kategorie w katalogu „Domyślny”
- 694 „kategorie”, z czego **tylko 3 mają produkty**: „Brak danych” (496) i dwie po 1. Reszta to kategorie nazwane jak pojedyncze produkty (np. „Firana Na Taśmie Czarna Ze Złotą Nitką sz.100x100”) z zerem produktów. To pozostałość po imporcie.
- Katalogi ERLI mają kategorie w drzewie Allegro i są przypisane (np. „…/Firany/Firany gotowe” 33 945 i 15 782 produktów).
- **Przyczyna błędu eksportu:** produkty w katalogu „Domyślny” nie mają kategorii, a konektor IdoSell wymaga `category_id`, więc eksport każdego produktu kończy się błędem.

### SKU — przykład produktu od klienta „002301”
- Base, katalog Domyślny: **≥ 50 osobnych produktów** (każdy wymiar to osobny produkt: 100x100, 120x140, 120x150…) z **tym samym SKU** `002301/FRE/001/000300/1`. Żaden nie ma integracji IdoSell, mają tylko ERLI/Allegro.
- IdoSell: kod `002301/FRE/001/000300/1` ma 1 towar (ID 29129, „sz. 210x210”, **ukryty na stronie**). Jest też towar 27186 „Woal na metry” z kodem `krem 002301/233/012/000300/1` (ukryty).
- Wniosek: SKU w Base **nie jest unikalne** (wymiar jest tylko w nazwie), więc automatyczne powiązanie po SKU nie zadziała. Część produktów IdoSell powstała wcześniej z Base, ale nie zostały one powiązane.

### Stan IdoSell (z komentarzy w zadaniu i panelu)
- ~29 tys. towarów, w tym roku 1 zamówienie ze sklepu (komentarz z 09.2026). Znalezione towary 002301 są ukryte na stronie.

## Diagnoza
1. **Nie ma połączenia produktów:** prawie żaden produkt Base nie jest powiązany z towarem IdoSell, więc synchronizacja stanów i cen ma na czym działać tylko dla kilku pozycji. To dokładnie objaw z ClickUp („działa na Allegro/ERLI, nie działa na IdoSell”).
2. **Eksport cykliczny z „Domyślnego” stoi na błędzie kategorii** (17 047 produktów z błędem, codziennie ~800–850 nowych prób).
3. **Ryzyko przy „szybkiej naprawie”:** jeśli uzupełnimy kategorie i klikniemy „Oznacz błędy jako rozwiązane”, eksport zacznie tworzyć w IdoSell **nowe** towary dla każdego wymiaru (do ~90 tys.), obok istniejących 29 tys. Grozi to duplikatami i bałaganem w sklepie. **Tego nie wolno robić bez decyzji.**
4. Pobieranie zamówień z IdoSell jest wyłączone. Gdy sklep zacznie sprzedawać, stany w Base nie będą zdejmowane (ryzyko overbookingu na Allegro/ERLI).

## Możliwe kierunki naprawy (do decyzji klienta / opiekuna)

| Wariant | Opis | Plusy | Minusy / ryzyka |
|---|---|---|---|
| A. Base jako źródło, eksport do IdoSell | Uporządkować kategorie w „Domyślnym” (mapowanie na kategorie IdoSell), ustalić model wariantów (wymiary jako rozmiary jednego towaru zamiast osobnych produktów), wyczyścić lub ukryć stare 29 tys. towarów IdoSell, potem wyczyścić błędy i puścić eksport | Jedno źródło prawdy, nowe produkty same trafią do sklepu | Duża praca; ryzyko duplikatów; trzeba zdecydować, co z istniejącymi towarami IdoSell (SEO, linki) |
| B. Powiązanie istniejących towarów IdoSell z Base | Wyłączyć eksport cykliczny, zbudować plik powiązań `ID_BL;ID_towaru_IdoSell;ID_wariantu` (jak dla IVEMAX) po SKU + wymiarze z nazwy | Nie tworzy duplikatów; stany i ceny zaczną działać dla istniejących towarów | SKU nieunikalne, więc dopasowanie po SKU **i** wymiarze z nazwy; dla części produktów może nie być pary |
| C. Minimum | Włączyć pobieranie zamówień z IdoSell (stany) i wyłączyć eksport cykliczny, dopóki nie zapadnie decyzja | Zatrzymuje codzienne błędy | Nie naprawia synchronizacji produktów |

Rekomendacja: **B**, poprzedzone C. Najpierw trzeba ustalić z klientem, czy sklep IdoSell ma mieć pełny asortyment z Base (wtedy A), czy wystarczą istniejące towary.

## Wycena (orientacyjna)
- Analiza (wykonana): ~1 h.
- Wariant B: eksport katalogu z Base i towarów z IdoSell, skrypt dopasowania SKU + wymiar, walidacja na produktach od klienta (milas, 002301, dona), plik importu powiązań, kontrola po wczytaniu: **6–10 h** (zależnie od jakości nazw i wariantów).
- Wariant A: **15–25 h** (kategorie, model wariantów, porządek w IdoSell, eksport etapami).
- Wariant C: ok. 0,5 h (zmiany w ustawieniach integracji, za zgodą).

## Otwarte pytania
1. Czy IdoSell ma zawierać pełny asortyment z Base (~90 tys.), czy tylko obecne ~29 tys.? Dlaczego towary w IdoSell są ukryte na stronie?
2. Kto i kiedy włączył eksport cykliczny z „Domyślnego” (utworzony 16.08.2026)? Czy klient wie, że codziennie próbuje tworzyć ~800 produktów?
3. Czy wymiary (np. 100x100, 120x140) mają być w IdoSell rozmiarami jednego towaru, czy osobnymi towarami, jak w Base?
4. Dlaczego pobieranie zamówień z IdoSell jest wyłączone? Czy zamówienia ze sklepu obsługuje się poza Base?
5. Do weryfikacji przy wariancie B: produkty „milas” i „dona” (nie sprawdzałem ich w tej sesji).

## Uwagi techniczne
- Wzór pliku powiązań i pułapki eksportu CSV z Base są opisane w pamięci (`reference-base-szablon-csv-powiazania`, przypadek IVEMAX).
- Nie klikałem: „Oznacz błędy jako rozwiązane”, „Zapisz”, „Przetestuj połączenie”, edycji eksportu cyklicznego.
- Otwarcie linku do załącznika ClickUp w przeglądarce mogło pobrać plik `image.png` do folderu Pobrane. Nie otwierałem go.
