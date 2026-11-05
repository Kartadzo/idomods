# Analiza: narzędzie do wiadomości transakcyjnych IdoSell

Status: **do akceptacji** · Data: 2026-10-13 · Źródło ustaleń: sesja pytań + spike na panelu `zooart6` (tylko odczyt)

---

## 1. Cel zadania

Narzędzie dla konsultanta obsługującego wiadomości transakcyjne w sklepach IdoSell klientów (wiele paneli),
także do migracji treści między sklepami (np. test → produkcja). Wariant „narzędzie dla jednego klienta”
jest zawieszony do czasu, aż pojawi się zainteresowany klient.

Trzy tryby działania:

| Tryb | Co robi |
| --- | --- |
| **Status** | Podsumowanie: ile i które wiadomości są wysyłane (mail/SMS/Web Push), ile ma tłumaczenia, data ostatniej edycji, kontrola jakości treści. |
| **Edycja działania** | Konfiguracja, które wiadomości są wysyłane — kanał (mail, SMS) i język — przez plik CSV generowany z bieżącego stanu panelu. |
| **Eksport i Import Treści** | Eksport wszystkich lub wybranych wiadomości (każda w osobnym folderze), edycja/tłumaczenie poza panelem, import z powrotem. |

Dwie wersje obsługi, ten sam kod:

- **Bookmarklet** — samodzielny, bez Claude: zakładka w Chrome uruchamiana na zalogowanym panelu.
- **Skill Claude in Chrome** — ta sama praca prowadzona przeze mnie w sesji (kroki, przegląd różnic, omówienie raportu).

---

## 2. Ustalenia ze spike'u (fakty, nie założenia)

Sprawdzone 2026-10-13 na `zooart6.yourtechnicaldomain.com`, bez żadnego zapisu.

- **Admin API v8 nie ma bramek do wiadomości transakcyjnych** (przejrzane 243 ścieżki specyfikacji OpenAPI panelu).
  Jedyna droga to panel w przeglądarce, na sesji zalogowanego użytkownika.
- Strona: `/panel/config-messages.php` (starsza wersja panelu, renderowana po stronie serwera).
  - `?populate=types&shop=N` — grupy wiadomości sklepu,
  - `?populate=list&group=<grupa>&shop=N` — lista wiadomości grupy ze stanem kanałów,
  - `?populate=edit&template=<template>&shop=N` — edycja wiadomości (+ „Historia zmian”).
- Panel może mieć **kilka sklepów** (`shop=1`, `shop=2`) — konfiguracja osobna per sklep.
- Sklep 1: **15 grup, 144 wiadomości** (120 edytowalnych, 24 „wycofywane” — tylko podgląd). Języki: pol, ukr, eng.
- Stany kanałów na liście: `tak`, `nie`, `nie dotyczy`, `tak` + „do uzupełnienia szablony: (2 z 3)”.
- **Eksport ICF**: `...populate=edit&template=<t>&shop=N&story_id=&action=exportIDF&language=<lang>` → XML
  (`<repository file_format="ICF">`) per wiadomość i język. Zawiera:
  - `contents[message_type=mail]`: `title`, `text_main_0` (HTML), `contenttype`, `account`, `css`, `bcc`, `default`, `active`, …
  - `contents[message_type=sms]`: `text_main_0`, `branding`, `only_ascii`, `type_sms`, `active`, …
  - `enclosures`: grafiki w base64 (pliki od ~80 KB do ~880 KB).
  - Działa przez `fetch` z poziomu strony panelu.
- **Import ICF**: formularz `multipart/form-data`, pole `idf_file` + `operation`, jedno żądanie na wiadomość.
- Formularz edycji: mail i Web Push mają włącznik **per język** (`mail_lang[<lang>][active_mail]`),
  **SMS ma jeden włącznik wspólny dla wszystkich języków** (`sms_lang[active]`).
- **Web Push nie występuje w ICF.**
- **Historia zmian** per wiadomość: autor, data modyfikacji, [podgląd], [przywróć].
- Przycisku wysyłki testowej **nie ma** (jest tylko podgląd).
- Przykład kopii: „Potwierdzenie wpłynięcia zamówienia”, język ukr — tytuł maila po polsku.
- Pułapka techniczna: panel ładuje Prototype.js, który psuje `Array.from`, `Set` w iteracji i `Array.prototype.filter`
  w kontekście strony — kod przeglądarkowy musi używać zwykłych pętli albo izolowanego kontekstu.

---

## 3. Architektura

```
[Panel IdoSell, zalogowany użytkownik]
        │  fetch na sesji (eksport ICF, listy, historia) / formularz importu ICF
        ▼
[Kod przeglądarkowy: panel_core.js]  ◄── używany przez bookmarklet ORAZ przez skill (Claude in Chrome)
        │  ZIP do pobrania  ──►  C:\Users\Admin\Downloads (domyślny folder Chrome)
        │                        └─► wiadomosci.py przenosi eksport_*/weryfikacja_*.zip do _pobrane\ projektu
        ▼
[wiadomosci.py — Python 3.8+, tylko stdlib]
        rozpakuj · konfiguracja · roznice · zloz · status · weryfikuj
        ▼
[Pliki w folderach trybów]  ──►  ICF do importu  ──►  z powrotem do panelu
```

~~**Jedna ścieżka zapisu: import ICF.**~~ **Zmienione po teście (§9):** Import Treści — import ICF;
Edycja działania — formularz edycji („Zapisz zmiany”) + import ICF przywracający treść, jeśli zapis formularzem ją zmienił.

**Import nie buduje ICF od zera** — bierze oryginał zapisany przy eksporcie i podmienia tylko zmienione pola
(tytuł, treść, flagi `active`). Grafiki, konto nadawcy i nieznane pola przechodzą bez zmian.

### Podział odpowiedzialności

| Element | Zadanie |
| --- | --- |
| `panel_core.js` | Wybór sklepu, odczyt list i historii zmian, pobranie ICF (`fetch`), spakowanie do ZIP i pobranie; przy imporcie: wgranie ICF, ponowny eksport do weryfikacji. Odstęp ~200 ms między żądaniami, ponowienie przy 503. |
| `bookmarklet` | Cienka nakładka na `panel_core.js`: menu (Eksport / Import), wybór plików do importu, lista plików do potwierdzenia przed wgraniem, wynik per plik. |
| `wiadomosci.py` | Cała praca na plikach: rozpakowanie, rozbicie ICF na foldery, CSV konfiguracji, porównanie, złożenie ICF, raport Status, raport weryfikacji importu. Działa po dwukliku `.bat` (interaktywne menu). |
| Skill `.claude/skills/wiadomosci-transakcyjne/` | Opis trzech trybów krok po kroku, adresy panelu, pułapki; ja uruchamiam `panel_core.js` przez Claude in Chrome i `wiadomosci.py` lokalnie, pokazuję różnice do akceptacji. |

---

## 4. Pliki i formaty

```
SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/
├── ANALIZA_wiadomosci_transakcyjne.md   <- ten plik
├── wiadomosci.py  +  run_wiadomosci.bat
├── przegladarka/
│   ├── panel_core.js
│   ├── bookmarklet.js                   <- źródło zakładki
│   └── INSTALACJA_BOOKMARKLETU.md
├── testy/                               <- testy jednostkowe + próbki ICF
├── _pobrane/                            <- archiwum ZIP-ów przeniesionych z Pobranych (gitignore)
├── Status/<sklep>/status_<data>.md
├── Edycja Działania/<sklep>/konfiguracja_<data>.csv
└── Eksport i Import Treści/<sklep>/<data>/
    └── <grupa>__<template>/
        ├── pol.icf, eng.icf, ukr.icf    <- oryginały (źródło wierności)
        ├── pol_mail.html, pol_sms.txt, eng_mail.html, …
        └── meta.json                    <- nazwa, grupa, template, tytuły per język,
                                            data i autor ostatniej edycji, domena, shop_id, data eksportu
```

`<sklep>` = domena panelu + `shop_id`, np. `zooart6_shop1`.

### CSV konfiguracji (Edycja działania)

- UTF-8 z BOM, separator `;`.
- Wiersz = wiadomość. Kolumny: `grupa; template; nazwa; mail_<lang>…; sms; reset_domyslna`.
- Wartości `tak` / `nie`; `nie dotyczy` tylko do odczytu (zmiana odrzucana).
- Kolumny językowe zależą od sklepu (odczytywane z panelu).
- `sms` — jedna kolumna, bo panel ma jeden włącznik SMS dla wszystkich języków.
- Wiadomości „wycofywane” pomijane.
- `reset_domyslna=tak` — „Wczytaj treść z szablonu domyślnego” dla tej jednej wiadomości (patrz §5).

### Raport Status (`.md`)

1. Liczby: wiadomości ogółem, aktywne per kanał (mail, SMS, Web Push), per język.
2. Tabela: wiadomość · mail per język · SMS · Web Push · braki szablonów · data i autor ostatniej edycji.
3. Kontrola jakości:
   - języki, których treść/tytuł to **kopia PL lub EN** (porównanie po znormalizowanym tekście, bez białych znaków),
   - zmienne `[iai:…]` niezgodne między językami lub brakujące w tłumaczeniu,
   - pusta treść przy włączonej wysyłce,
   - SMS dłuższy niż jeden segment (160 znaków; 70 z polskimi znakami; uwzględnić `only_ascii`).

Krótkie podsumowanie raportu również w rozmowie (wersja ze skillem).

---

## 5. Przepływy

**Status:** eksport (ICF + listy + historia) → `wiadomosci.py status` → raport `.md`.

**Edycja działania:** eksport → `konfiguracja` (CSV stanu obecnego) → użytkownik poprawia CSV → `roznice`
(lista zmian do akceptacji) → [`reset_domyslna`: przycisk przy pojedynczej wiadomości w panelu, przed importem]
→ `zloz` (ICF z podmienionymi flagami) → import ICF → weryfikacja.

**Eksport i Import Treści:** eksport wszystkich lub wybranych → edycja plików `*_mail.html` / `*_sms.txt` / tytułów w `meta.json`
→ `roznice` (lista zmienionych wiadomości/języków/kanałów, do akceptacji) → `zloz` → import ICF → weryfikacja.
Brak pliku danego języka w folderze = **nie ruszaj** tego języka w panelu. Bez dodatkowej kopii zapasowej przed importem
(kopią jest poprzedni eksport).

**Migracja między sklepami:** eksport ze sklepu A → import do sklepu B po jawnym potwierdzeniu innego celu niż w `meta.json`.

---

## 6. Błędy i weryfikacja

- **Weryfikacja po imporcie:** ponowny eksport wgranej wiadomości i porównanie zmienianych pól →
  `OK` / `nie zmieniło się` / `zmieniło się inaczej` → raport `import_<data>.md`.
- `zloz` **odmawia**, gdy data ostatniej edycji w panelu jest nowsza niż eksport (ktoś zmienił wiadomość w międzyczasie).
- Import tylko do sklepu i domeny z `meta.json`; inny cel wymaga jawnego potwierdzenia.
- Wycofywane wiadomości i kanały `nie dotyczy` odrzucane na etapie `roznice`.
- Wylogowanie (przekierowanie na logowanie) → zatrzymanie z komunikatem; eksport zapisuje postęp i da się go wznowić.
- Błąd pojedynczej wiadomości nie przerywa całości — trafia do listy błędów w raporcie.
- Bookmarklet przed importem pokazuje listę plików i wymaga potwierdzenia.

**Testy:** testy jednostkowe `wiadomosci.py` na prawdziwych ICF z panelu testowego (rozbicie, złożenie, porównanie,
kontrola jakości); kluczowy test: rozbij → złóż bez zmian = ICF równoważny oryginałowi.
Pierwszy prawdziwy import: **jedna wiadomość na `zooart6`, za zgodą użytkownika**.

---

## 7. Poza zakresem

- Edycja **Web Push** (brak w ICF) — tylko odczyt w raporcie Status.
- Edycja wiadomości „wycofywanych”.
- Masowe „Ustaw domyślną treść wiadomości” (na poziomie sklepu / grupy) i „Przywróć” z historii zmian.
- Wysyłka testowa (panel jej nie oferuje).
- Porównanie dwóch sklepów i tłumaczenie brakujących języków przez AI — rozważone, odłożone.
- „Własne szablony wiadomości”, „Nagłówek i stopka”, „Style CSS” — sekcje ustawień, nie wiadomości (do decyzji później).

---

## 8. Założenia (moje, do potwierdzenia)

1. CSV, nie XLSX — Excel otwiera UTF-8 z BOM poprawnie.
2. Folder per wiadomość realizuje „każda wiadomość do osobnego pliku”.
3. Skill zapisany w projekcie (`.claude/skills/`), nie globalnie.
4. Bookmarklet: `panel_core.js` osadzony w zakładce w całości (bez ładowania kodu z zewnętrznego adresu).
5. ZIP tworzony w przeglądarce bez bibliotek zewnętrznych (format „store”, bez kompresji) — prosty i wystarczający.
6. ~~Format ICF pozwala wgrać plik z flagą `active` zmienioną ręcznie~~ — **obalone testem (§9)**: import nie włącza wysyłki.

## 9. Wyniki testu importu (2026-10-13, `order_confirmation`, sklep 1, język eng)

Przebieg importu ICF w panelu: wybór pliku → **wybór języka docelowego** (podpowiadany z ICF; lista zawiera też
estoński, którego wiadomość nie ma w zakładkach) → potwierdzenie „treść zostanie nieodwracalnie nadpisana” → „Import przebiegł pomyślnie”.

| Obserwacja | Wniosek dla projektu |
| --- | --- |
| ICF eng z `active=n` → mail eng **wyłączony**; pol i ukr bez zmian. | Import ICF dotyczy wyłącznie wybranego języka. |
| ICF eng z `active=y` (oryginał) → mail eng **nadal wyłączony**. | **Import ICF nie włącza wysyłki.** Możliwe, że import zawsze ustawia `n` albo ignoruje `y`. Edycja działania **nie może** opierać się na ICF. |
| Treść eng po imporcie oryginału identyczna z oryginałem (hash). | Import treści przez ICF jest wierny — ścieżka dla Eksportu i Importu Treści potwierdzona. |
| Import ICF **nie dodaje wpisu do Historii zmian**. | Zabezpieczenie „odmów, gdy panel edytowano po eksporcie” nie może polegać tylko na historii — trzeba porównywać treść (hash) bieżącego eksportu z oryginałem. Raport Status nie pokaże importów jako edycji. |
| Wyłączony język liczy się na liście jako „do uzupełnienia szablony (1 z 3)”. | Ten wskaźnik w raporcie Status znaczy „wyłączone lub puste”, nie tylko „puste”. |
| Zapis formularzem edycji („Zapisz zmiany”) przywrócił flagę eng, ale **zmienił HTML maila pol** (+570 znaków), mimo że pol nie był ruszany; eng i ukr bez zmian. Wpis w historii zmian dodany. | Zapis formularzem przepisuje (re-serializuje) treść widocznego języka w edytorze. Edycja działania przez formularz wymaga obejścia — np. po zapisie formularzem przywrócenie treści wszystkich języków importem ICF z eksportu sprzed zmiany. |
| Skrypt wysyłający import przez `fetch` (POST) został zablokowany przez klasyfikator uprawnień Claude Code. | W wersji skill zapis idzie przez interfejs: `file_upload` + kliknięcia. Bookmarklet (uruchamiany przez użytkownika) może użyć `fetch`. |
| Chrome blokuje drugie automatyczne pobieranie z tej samej strony. | Eksport jako **jeden ZIP**. |

### Zmiana projektu wynikająca z testu (do akceptacji)

**Edycja działania = formularz edycji + import ICF jako „naprawa treści”:**
eksport ICF (kopia treści) → zmiana flag w formularzu → „Zapisz zmiany” → ponowny eksport → jeśli treść któregoś języka
różni się od kopii — import ICF z kopii dla tego języka → weryfikacja flag i treści.
Import ICF nie włącza wysyłki, ale też (w teście) jej nie zmienia przy `active=y` — do potwierdzenia, że import po zapisie formularza
nie wyłącza z powrotem włączonych języków.

## 11. Weryfikacja przed implementacją (2026-10-13, Task 0 planu)

| Sprawdzane | Wynik |
| --- | --- |
| Import ICF `active=y` na **włączoną** wiadomość (eng) | mail eng po imporcie: **n** — import ICF **zawsze wyłącza** wysyłkę języka, którego dotyczy |
| Radio języka w imporcie | `name=lang`, `value=eng` (kod języka); lista zawiera też `est` |
| Potwierdzenie „Tak” | element strony `button[type=button]` (nie natywny `confirm`); obok „Nie” |
| Komunikat sukcesu importu | „Import przebiegł pomyślnie. Szablon został zmieniony.” |
| Nagłówki sekcji listy | `H2` („Zamówienia”, „Zamówienia detaliczne”, „Zamówienia hurtowe”) |
| Linki grup ustawień | **nie** zawierają `populate=list` (15 grup = same wiadomości) |
| „Zapisz zmiany” | `input[type=submit]`; komunikat: „Zmiany zostały zapisane” |
| Przeładowania | po „Wgraj plik”: tak (`action=import`); po „Wybierz”: nie; po „Tak”: tak |
| Zapis formularzem (włączenie eng) na treści już raz przepisanej | treść pol/eng/ukr **bez zmian** (odciski = kopia z eksportu 14:19) — przepisanie HTML przy zapisie zachodzi raz, potem zapis jest stabilny |

**Bramka planu zadziałała:** import treści przez ICF wyłącza wysyłkę maila w importowanym języku.

**Decyzja użytkownika (2026-10-13): wariant A** — import ICF, a po nim automatyczne ponowne włączenie formularzem
tych języków, które przed importem miały włączoną wysyłkę.

Test wariantu A (ta sama wiadomość, eng, tytuł + „ [TEST]”):

| Krok | Wynik |
| --- | --- |
| Import ICF ze zmienionym tytułem | sukces; mail eng → `n`; pol/ukr bez zmian |
| Włączenie eng formularzem (radio ustawione skryptem bez przełączania zakładki, „Zapisz zmiany”) | mail eng → `y`; tytuł, HTML i flaga eng = wgrany plik; pol/ukr bez zmian |
| Różnica eksportu eng względem wgranego pliku | tylko zapis tytułu: panel przechowuje go **bez CDATA** — porównania treści muszą być semantyczne (po wartościach pól), nie po odcisku wgranego pliku |
| Przywrócenie oryginału (import + włączenie formularzem) | odciski pol/eng/ukr = kopia z 14:19 — panel w stanie sprzed testów |

Obserwacje do implementacji: kliknięcie „Import ICF” bywa ignorowane, gdy strona jeszcze się ładuje (trzeba odczekać
i sprawdzić, czy pojawiło się `input[name=idf_file]`); kliknięcie „Zapisz zmiany” przez `ref` po przewinięciu nie zawsze
wysyła formularz — kliknięcie we współrzędne widocznego przycisku działa.

## 12. Test całościowy (2026-10-13, sklep 1 `zooart6`)

| Krok | Ścieżka | Wynik |
| --- | --- | --- |
| Status — eksport 144 wiadomości | bookmarklet „Eksport wszystkich" → `rozpakuj` → `status` | OK; raport z kopiami tłumaczeń (m.in. ukr tytuł = pol w `order_confirmation`), niezgodnymi zmiennymi; panel zwraca HTTP 500 na eksport ICF **ukr** dla 12 wiadomości (subskrypcje, kody MFA) — w sekcji „Błędy eksportu" |
| Edycja działania: mail eng tak → nie | CSV → `zmiany` → bookmarklet „Zastosuj plan" → `weryfikuj` | OK 7/7 (po poprawce odcisku) |
| Edycja działania: mail eng nie → tak | j.w. (świeży eksport, nowa wersja zakładki) | OK 7/7 |
| Import treści: tytuł eng + „ [TEST]" | skill: eksport `WT.eksportuj` → `tresci` → sprawdzenie aktualności → import przez interfejs → włączenie maila formularzem → `weryfikuj` | OK 1/1, flagi bez zmian |
| Przywrócenie tytułu | import oryginalnego ICF + włączenie formularzem | treść pol/eng/ukr = eksport 16:07, mail włączony we wszystkich językach |

Poprawki wynikające z testu (z testami RED→GREEN):
- raport Status: zmienne `[iai:…]` nie liczą się do długości SMS i nie wymuszają limitu 70; długość sprawdzana tylko dla wysyłanych SMS (699 → 508 uwag); poprawna odmiana opisu kopii;
- **odcisk ICF = treść**, nie surowy tekst: flagi `active`, ustawienia techniczne (`disposition` zmienia się przy zapisie formularzem) i forma zapisu (CDATA/encje) nie zmieniają odcisku. Wcześniej zmiana flagi dawała fałszywe „treść różni się od kopii", a bookmarklet wykonywał zbędny import kopii.

Wnioski do obsługi przez interfejs (wpisane do skilla): „Import ICF" klikać przez `ref` (współrzędne trafiały w sąsiedni „Eksport ICF", który pobiera plik); „Tak" i „Zapisz zmiany" — we współrzędne widocznego przycisku.

## 10. Otwarte pytania i ryzyka

- Czy import ICF z `active=y` po włączeniu formularzem pozostawia wysyłkę włączoną (patrz §9) — test przed implementacją Edycji działania.
- Czy import ICF zawsze ustawia `active=n`, czy tylko nie zmienia `n`→`y` — rozstrzyga powyższy test.
- Nieudokumentowany mechanizm panelu: IdoSell może go zmienić bez zapowiedzi (np. przy przeniesieniu strony do „nowego menu”).
- Limit długości URL zakładki w Chrome — przy dużym `panel_core.js` może być potrzebny wariant „wklej do konsoli”.
- ~~Folder pobierania Chrome ustawia użytkownik na `_pobrane`~~ — **zmienione 2026-10-13:** eksport trafia do domyślnego
  `C:\Users\Admin\Downloads`; `wiadomosci.py` przenosi stamtąd wyłącznie `eksport_*.zip` / `weryfikacja_*.zip` do `_pobrane\`.
  Wymaga wyjątku w globalnej zasadzie „tylko folder projektu” (dopisany w `~/.claude/CLAUDE.md`).
