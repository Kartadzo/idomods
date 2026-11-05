# Analiza: raport Status w CSV + graficzny edytor treści

Data: 2026-10-14 · Status: **zaakceptowana 2026-10-14** (z poprawkami poniżej) · **wykonana 2026-10-14**

Wykonanie: 87 testów OK; test okna na kopii alpha-teile; oba `.exe` zbudowane i uruchomione.
**Odkrycie przy testach:** maile nigdy niewypełnione w panelu mają w ICF pusty kanał `<contents message_type="mail"></contents>`
(alpha-teile: 3 maile PL). Import podmienia istniejące pola, więc takiej treści nie utworzy — edytor pokazuje je
tylko do odczytu z wyjaśnieniem, a `tresci.roznice_tresci` zgłasza czytelny błąd zamiast cichego pominięcia.
Utworzenie bloku od zera (pola skopiowane z innego języka) wymagałoby testu na panelu — otwarte. · Gałąź: `wiadomosci-dlugie-sciezki` (kontynuacja)

## 1. Cel

1. **Status czytelny w Excelu:** obok obecnego `status_<data>.md` program zapisuje prosty `status_<data>.csv`.
2. **Edytor treści dla osoby nietechnicznej:** okno, w którym widać wiadomości po polsku (grupa, nazwa, język),
   bez chodzenia po folderach o angielskich nazwach i bez otwierania `meta.json`/`.html` w Notatniku.
   Edytor pozwala zmienić tytuł maila, treść HTML (z podglądem w przeglądarce) i usunąć mail z paczki do importu.

## 2. Raport CSV

- Plik: `Status\<sklep>\status_<data>.csv`, obok `.md`, zapisywany tym samym poleceniem (pozycja 2 menu).
- Format jak CSV konfiguracji: UTF-8 z BOM, średnik — otwiera się dwuklikiem w Excelu z polskimi znakami.
- **Jeden wiersz = jedna wiadomość**, nagłówki po polsku, języki pełnymi nazwami:

| Grupa | Wiadomość | Mail polski | Mail niemiecki | … | SMS | Web Push | Wycofywana | Braki szablonów | Ostatnia edycja | Kto edytował | Problemy (liczba) | Problemy (opis) | Kod wiadomości |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Złożenie zamówienia | Potwierdzenie wpłynięcia zamówienia | tak | tak | | nie | — | nie | — | 2026-03-16 13:49:56 | IdoMods | 2 | niemiecki: tytuł maila identyczny z polski; … | order_confirmation |

- Wartości `tak` / `nie` / `nie dotyczy`; problemy kontroli jakości złączone w jednej komórce (`; `), z pełnymi
  nazwami języków. Kod wiadomości (`template`) na końcu — dla porządku, zwykły użytkownik go nie potrzebuje.
- **Decyzja użytkownika: CSV ma dwie części.** Najpierw status ogólny zgrupowany do grup panelu (wiersz = grupa:
  liczba wiadomości, edytowalne, wycofywane, maile włączone per język, SMS, Web Push, braki szablonów, problemy
  kontroli jakości + wiersz RAZEM), pusta linia, potem tabela wiadomości jak wyżej.
- Nazwy języków: słownik kodów panelu (`pol`→polski, `ger`→niemiecki, `eng`→angielski, `cze`→czeski, `ukr`→ukraiński,
  `slo`→słowacki, `fre`→francuski, `ita`→włoski, `spa`→hiszpański, `rum`→rumuński, `hun`→węgierski, `lit`→litewski,
  `lav`→łotewski, `est`→estoński, `dut`→niderlandzki, `por`→portugalski, `swe`→szwedzki, `dan`→duński, `nor`→norweski,
  `fin`→fiński, `rus`→rosyjski, `bul`→bułgarski, `gre`→grecki, `scr`→chorwacki, `slv`→słoweński); nieznany kod — pokazany jak jest.
  Ten sam słownik wykorzystuje edytor.

## 3. Edytor treści (GUI)

**Technologia:** tkinter (biblioteka standardowa, jak w innych naszych apkach), bez nowych zależności.
**Uruchamianie:** osobny plik `Edytor treści.exe` w folderze dystrybucji (okno, bez czarnej konsoli) +
pozycja w menu programu „Edytor treści (okno)”. W źródłach `edytor_tresci.py` + `run_edytor.bat`.
Silnik (`wt/`) bez zmian w logice — edytor korzysta z `eksport`, `icf`, `tresci`, `wspolne`; logika edytora
w osobnym module bez tkintera (`wt/edytor.py`), żeby dało się ją testować, okno w `edytor_tresci.py`.

```
┌ Edytor treści — alpha-teile.de, sklep 1 · eksport z 2026-10-14 12:04 ──────── [Zmień eksport ▾] ┐
│ Szukaj: [__________]   ☐ tylko zmienione                                                       │
│ ┌ Wiadomości ──────────────────────┐ ┌ Potwierdzenie wpłynięcia zamówienia ───────────────────┐ │
│ │ ▸ Obsługa subskrypcji Newslettera │ │ Język: (•) polski  ( ) niemiecki     wysyłka: włączona │ │
│ │ ▾ Złożenie zamówienia             │ │ Tytuł maila: [Zamówienie nr [iai:order_sn] przyjęte ]  │ │
│ │    Potwierdzenie wpłynięcia… ✎    │ │ Treść maila (HTML):                                    │ │
│ │    Prośba o potwierdzenie…        │ │ ┌────────────────────────────────────────────────────┐ │ │
│ │ ▸ Klienci                         │ │ │ <p>Dziękujemy, zamówienie [iai:order_sn] …</p>     │ │ │
│ │   …                               │ │ └────────────────────────────────────────────────────┘ │ │
│ └───────────────────────────────────┘ │ [Podgląd w przeglądarce] [Cofnij zmiany] [Usuń mail]  │ │
│                                       │ [Zapisz]                                               │ │
│ Zmienione: 3 maile        [Przygotuj paczkę do importu]                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Lista:** drzewo grupa → wiadomość, polskie nazwy z panelu; znacznik ✎ przy zmienionych, przekreślenie/szarość
  przy usuniętych; wiadomości wycofywane i bez plików pominięte (jak w imporcie). Wyszukiwarka po nazwie.
- **Edycja tytułu maila** → zapis do `meta.json` (`tytuly.<język>`), jak dziś ręcznie.
- **Edycja HTML** → pole tekstowe z kolorowaniem znaczników `<…>` i zmiennych `[iai:…]`; zapis do `<język>_mail.html`
  bez zmiany końców linii. Ostrzeżenie (nie blokada) przy zapisie, gdy zniknie lub dojdzie zmienna `[iai:…]`
  względem oryginału — najczęstszy błąd przy tłumaczeniu.
- **Podgląd w przeglądarce** → tymczasowy plik HTML (tytuł + treść z edytora, także niezapisana) otwierany w
  domyślnej przeglądarce. Zmienne `[iai:…]` zostają jako tekst (podświetlone) — panel podstawia je dopiero przy wysyłce,
  więc obrazki z adresem w zmiennej się nie wyświetlą; zwykłe adresy obrazków tak.
- **Cofnij zmiany** → przywraca tytuł i HTML z oryginału w `<język>.icf` (to, co jest dziś w sklepie).
- **Usuń mail** (decyzja: mail nie jest aktualizowany przy „Zastosuj plan”) → po potwierdzeniu język trafia na listę
  `wykluczone` w `meta.json`, a pliki treści (`_mail.html`, `_sms.txt`) do `_usuniete\<wiadomość>\` w eksporcie.
  `<język>.icf` **zostaje** — to oryginał, z którego „Edycja działania” robi kopie bezpieczeństwa i raport Status
  liczy kontrolę. `tresci.roznice_tresci` pomija wykluczone języki (tytuł też). Przycisk „Przywróć” odwraca operację.
  Nic nie jest kasowane w panelu.
- **Przygotuj paczkę do importu** → to samo co pozycja 5 menu (`tresci.zloz`): lista zmian do potwierdzenia, folder
  `do_importu_<data>`, komunikat „w panelu: zakładka → Zastosuj plan → wskaż folder …” z przyciskiem „Otwórz folder”.
- SMS: poza zakresem prośby — edytor go nie pokazuje, edycja jak dziś przez plik `_sms.txt` (pytanie 3).
- Zamknięcie z niezapisanymi zmianami → pytanie „Zapisać?”.

## 4. Pliki

- `wt/status.py` — `raport_csv()`, zapis obok `.md`; `wt/wspolne.py` — słownik `NAZWY_JEZYKOW` + `nazwa_jezyka()`.
- `wt/edytor.py` (nowy) — model: lista wiadomości/języków, odczyt/zapis tytułu i HTML, cofnij, usuń/przywróć, plik podglądu.
- `edytor_tresci.py` (nowy, tkinter), `run_edytor.bat`; `wiadomosci.py` — pozycja menu + komunikat o CSV.
- `zbuduj_dystrybucje.py` — drugi `.exe` (`--windowed`); `dokumentacja/INSTRUKCJA.html` — rozdział o edytorze
  zamiast ręcznej edycji `meta.json`, wzmianka o CSV.
- `testy/` — CSV statusu, model edytora (zapis, cofnij, usuń/przywróć, zmiany widoczne w `roznice_tresci`).

## 5. Założenia

- Edytor pracuje na już rozpakowanym eksporcie (rozpakowanie zostaje w programie z menu) — jeśli nie ma żadnego,
  okno to powie i wskaże, co zrobić.
- „Nazwy” w prośbie = **tytuł (temat) maila** w danym języku. Nazwa wiadomości w panelu (np. „Potwierdzenie
  wpłynięcia zamówienia”) jest stała po stronie IdoSell — import jej nie zmienia, więc edytor jej nie edytuje.
- Długie ścieżki: edytor korzysta z tych samych ścieżek rozszerzonych (`\\?\`).

## 6. Pytania — odpowiedzi 2026-10-14: 1) wykluczenie z „Zastosuj plan”, 2) tak, `_usuniete`, 3) SMS później

1. **„Usuwanie maili”** rozumiem jako: wykluczenie maila w danym języku z paczki importu (usunięcie lokalnych plików,
   sklep bez zmian). Jeśli chodzi o coś innego — np. **wyłączenie wysyłki** tego maila w sklepie (to robi dziś
   „Edycja działania”) albo **wyczyszczenie treści** w sklepie — napisz, bo to zmienia projekt.
2. Usuwanie do `_usuniete\` (odwracalne) zamiast trwałego kasowania — OK?
3. SMS w edytorze: dodać pole edycji SMS (z licznikiem znaków) teraz, czy zostawić na później?
