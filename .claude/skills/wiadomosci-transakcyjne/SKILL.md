---
name: wiadomosci-transakcyjne
description: Status, edycja działania (które maile/SMS w jakich językach są wysyłane) oraz eksport i import treści wiadomości transakcyjnych w panelu IdoSell przez Claude in Chrome. Używaj, gdy użytkownik prosi o raport wiadomości transakcyjnych, włączenie/wyłączenie wiadomości, eksport/import/tłumaczenie treści wiadomości albo migrację wiadomości między sklepami.
---

# Wiadomości transakcyjne IdoSell

Folder narzędzia: `SI/API IdoSell/Wiadomości transakcyjne/` (dalej KATALOG). Specyfikacja: `ANALIZA_wiadomosci_transakcyjne.md`.

## Zasady bezpieczeństwa (zawsze)
- Panel: `https://<domena>/panel/config-messages.php`. Użytkownik loguje się sam; ja nie wpisuję haseł.
- Przed KAŻDYM zapisem w panelu: eksport ICF wiadomości na dysk (krok „Eksport") i zgoda użytkownika na listę zmian.
- Nigdy: „Ustaw domyślną treść wiadomości" (masowe), „Przywróć" z historii, wiadomości „wycofywane", Web Push.
- Zapis w panelu wykonuję przez interfejs (`file_upload` + kliknięcia), nie przez `fetch` POST.
- JS na stronie panelu: tylko zwykłe pętle (Prototype.js psuje `Array.from`, `filter`, iterację `Set`).
- `window.WT` znika po każdej nawigacji karty — przed `WT.eksportuj`/`WT.odcisk` wczytaj `konsola.js` ponownie.
- Odcisk (`WT.odcisk` / `wt.icf.odcisk`) opisuje samą treść (tytuł, HTML, SMS, załączniki) — zmiana flag nie zmienia odcisku.
- Narzędzie Claude in Chrome ukrywa w wynikach tekst z adresami URL — nie przepycham treści ICF przez wyniki JS; pliki idą przez pobieranie ZIP.

## Przygotowanie
1. `tabs_context_mcp` (przy wielu przeglądarkach — zapytaj użytkownika, którą wybrać), nowa karta.
2. Pobieranie: Chrome zapisuje ZIP do `C:\Users\Admin\Downloads` (bez zmiany ustawień). Z Pobranych czytam i przenoszę WYŁĄCZNIE `eksport_*.zip` / `weryfikacja_*.zip` — przez `python wiadomosci.py rozpakuj|weryfikuj`, które przenosi je do `KATALOG\_pobrane`. Innych plików w Pobranych nie otwieram ani nie listuję.
3. Otwórz `…/config-messages.php`; jeśli tytuł strony to „Logowanie użytkownika" — poproś o zalogowanie i czekaj.
4. Ustal sklep (`shop`) — lista stron na `config-messages.php`.

## Eksport (wspólny początek trybów)
1. Na stronie panelu `javascript_tool` z całą zawartością `przegladarka/konsola.js` BEZ ostatniej linii `WTUI.pokaz();`
   (wczytuje `window.WT`), potem: `const r = await WT.eksportuj({shop: N, onPostep: () => {}}); ({nazwa: r.nazwa, n: r.manifest.wiadomosci.length, niekompletny: r.manifest.niekompletny})`.
   Wybrane wiadomości: `templates: ['order_confirmation', …]`.
2. `python wiadomosci.py rozpakuj "C:\Users\Admin\Downloads\<nazwa>"` (w KATALOGU; `<nazwa>` = `r.nazwa` z kroku 1). Niekompletny → eksport ponownie z `templates` = `manifest.pozostale`, potem `rozpakuj <zip1> <zip2>`.

## Tryb Status
Eksport → `python wiadomosci.py status "<katalog eksportu>"` → przeczytaj raport `Status/<sklep>/status_<data>.md` i streść: liczby, braki tłumaczeń, kopie PL/EN, problemy zmiennych, długie SMS-y.

## Tryb Edycja działania
1. Eksport → `python wiadomosci.py konfiguracja "<katalog>"` → podaj użytkownikowi ścieżkę CSV.
2. Użytkownik edytuje CSV (albo opisuje zmiany w rozmowie — wtedy ja edytuję CSV i pokazuję diff).
3. Podgląd zmian (bez zapisu planu):
   `python -c "import sys; from wt import eksport, konfiguracja as k; m=eksport.wczytaj_eksport(sys.argv[1]); z,b=k.roznice(m,k.sciezka_csv(m)); print(z); print(b)" "<katalog>"`
   → pokaż użytkownikowi listę; po jego „tak": `python wiadomosci.py zmiany "<katalog>" --tak` (tworzy `Edycja Działania/<sklep>/zmiany_<data>/plan_konfiguracji.json` + `kopie/`).
4. Dla każdej zmiany w `plan_konfiguracji.json` (interfejs panelu):
   a. aktualność: dla każdego języka z `kopie` w karcie panelu `await WT.odcisk(await WT.pobierzIcf('<t>', N, '<j>')) === '<kopie[j].odcisk>'` — `false` = ktoś edytował po eksporcie → pomiń i zgłoś;
   b. `navigate` → `…/config-messages.php?populate=edit&template=<t>&shop=<N>`;
   c. dla każdego języka z `mail`: kliknij zakładkę „Język: <nazwa>" → radio „Wysyłaj ten list" tak/nie; SMS: radio w sekcji SMS;
   d. „Zapisz zmiany" → poczekaj na „Zmiany zostały zapisane";
   e. treść po zapisie: powtórz porównanie z 4a; dla każdego języka z `false` → „Import ICF przez interfejs" z pliku `<folder planu>/kopie/<t>__<j>.icf`.
5. `reset=true` → powiedz użytkownikowi, żeby kliknął „Wczytaj treść z szablonu domyślnego" w tej wiadomości (krok ręczny).
6. `await WT.eksportuj({shop: N, templates: [<t z planu>], rodzaj: 'weryfikacja'})` → `python wiadomosci.py weryfikuj "<folder planu>" "C:\Users\Admin\Downloads\weryfikacja_….zip"` → zrelacjonuj wynik.

## Tryb Eksport i Import Treści
1. Eksport → pliki w `Eksport i Import Treści/<sklep>/<data>/<grupa>__<template>/`: `<j>_mail.html`, `<j>_sms.txt`, tytuły w `meta.json` → `tytuly`.
2. Edycja/tłumaczenie (użytkownik albo ja na jego prośbę). Usunięcie pliku języka = nie ruszaj tego języka.
3. Podgląd zmian:
   `python -c "import sys; from wt import eksport, tresci; m=eksport.wczytaj_eksport(sys.argv[1]); [print(r['template'], r['jezyk'], sorted(r['pola'])) for r in tresci.roznice_tresci(sys.argv[1], m)]" "<katalog>"`
   → pokaż użytkownikowi; po jego „tak": `python wiadomosci.py tresci "<katalog>" --tak` → `do_importu_<data>/plan_importu.json`.
4. Dla każdej pozycji planu: aktualność w karcie panelu `await WT.odcisk(await WT.pobierzIcf('<t>', N, '<j>')) === '<odcisk_oryginalu>'` (`false` → pomiń i zgłoś), potem „Import ICF przez interfejs" z `<folder planu>/<plik>`.
5. `await WT.eksportuj({shop: N, templates: [<t z planu>], rodzaj: 'weryfikacja'})` → `python wiadomosci.py weryfikuj "<folder planu>" "C:\Users\Admin\Downloads\weryfikacja_….zip"` → zrelacjonuj. „Flaga … zmieniło się inaczej" = pominięty krok 4 „Import ICF przez interfejs" (ponowne włączenie) → wykonaj go i zweryfikuj ponownie.
6. Inny sklep niż w planie (migracja) → wymaga wyraźnej zgody użytkownika z nazwą sklepu docelowego, a PRZED importem: eksport wiadomości z planu w sklepie docelowym (`WT.eksportuj({shop: N, templates: [...]})` → `rozpakuj`) jako kopia — import nadpisuje treść nieodwracalnie i nie zostawia historii. Weryfikacja przy migracji nie zna flag sprzed importu — sprawdź włączniki ręcznie (odczyt z kroku 0).
7. Błąd jednej pozycji (np. brak komunikatu po imporcie) → najpierw krok 4 (przywróć flagi), zapisz błąd, kontynuuj pozostałe pozycje; na końcu eksport weryfikacyjny wszystkich wiadomości, których plan dotyczył.

## Import ICF przez interfejs
1. `navigate` → strona edycji wiadomości; `find` „Import ICF" → kliknij **przez `ref`** (NIE we współrzędne — obok jest „Eksport ICF", który pobiera plik do Pobranych użytkownika). Sprawdź `!!document.querySelector('input[name=idf_file]')`.
2. `find` „file input idf_file" → `file_upload` z absolutną ścieżką pliku ICF.
3. „Wgraj plik" (przez `ref`; strona się przeładuje) → wybór języka skryptem: `document.querySelector('input[type=radio][name=lang][value="<jezyk>"]').click()` → „Wybierz" (przez `ref`) → „Tak" → „Import przebiegł pomyślnie. Szablon został zmieniony.". Kliknięcie „Tak" przez `ref` bywa ignorowane — wtedy zrzut ekranu i kliknięcie we współrzędne przycisku „Tak" w oknie dialogowym.
0. **Przed importem odczytaj bieżące flagi z panelu** (nie z planu — przy migracji i po zmianach w panelu plan ma nieaktualny stan): `(await WT.pobierzEdycje('<t>', N)).formularz` → zapamiętaj `mail[<jezyk>]` i `sms`.
4. **Import ICF ZAWSZE wyłącza mail w tym języku.** Przywróć flagę do stanu odczytanego w kroku 0 — także gdy import się nie powiódł lub przerwał (sprawdź ponownie `pobierzEdycje`). Jeśli przed importem mail był włączony: `navigate` na stronę edycji → `javascript_tool`: `document.querySelector('input[type=radio][name="mail_lang[<jezyk>][active_mail]"][value="y"]').click()` → `s=document.querySelector('input[type=submit][value="Zapisz zmiany"]'); s.scrollIntoView({block:'center'}); r=s.getBoundingClientRect()` → kliknij we współrzędne `(r.left+r.width/2, r.top+r.height/2)` przeskalowane do układu zrzutu (szerokość zrzutu / `innerWidth`) — kliknięcie przez `ref` bywa ignorowane → „Zmiany zostały zapisane".
5. Jeśli „Import ICF" nie otwiera okna (strona się wczytuje) — odczekaj 2 s i kliknij ponownie; sprawdź `!!document.querySelector('input[name=idf_file]')`.

## Fakty o panelu (z testów 2026-10-13)
- Import ICF dotyczy jednego języka; ZAWSZE wyłącza mail w tym języku (niezależnie od `active` w pliku); nie zostawia wpisu w historii zmian.
- Zapis formularzem tuż po imporcie zachowuje wgraną treść (panel zapisuje tytuł bez CDATA — porównuj wartości pól, nie odcisk wgranego pliku).
- „Zapisz zmiany" potrafi przepisać HTML widocznego języka — dlatego kopie i weryfikacja treści.
- Chrome blokuje drugie automatyczne pobranie — eksport zawsze jednym ZIP-em.
