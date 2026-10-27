---
name: summonfeed
description: Przygotowanie sterownika feedu XSLT 1.0 dla sklepu IdoSell z aktualnego szablonu (xslt/szablony/Google.xml, Facebook.xml, Ceneo.xml i inne) — kopia szablonu, odczyt parametrów, magazynów i profilu dostaw z panelu przez Claude in Chrome, uzupełnienie zmiennych konfiguracyjnych, warianty linków i item_group_id, dopasowanie do wymagań serwisu, weryfikacja przez lxml. Wynik to nowy plik do ręcznego wgrania w SI/SummonFeed SI/sterowniki/<domena>/. Używaj, gdy użytkownik mówi „przygotuj sterownik/feed XSLT dla <sklep>”, „summonFeed”, „feed Google/Facebook/Ceneo/TikTok/Pinterest… dla <domena>”, „odtwórz sterownik na nowym szablonie / dla innego serwisu” albo wywołuje /summonfeed <link do panelu> <id sklepu> <serwis>.
---

# summonFeed — sterownik XSLT 1.0 z szablonu

KATALOG: `SI/SummonFeed SI/`. Specyfikacja: `ANALIZA_skill_summonFeed.md`.
Narzędzia: `narzedzia/konfiguruj.py`, `narzedzia/parametry_oferty.py`, `narzedzia/przytnij.py`, `narzedzia/weryfikuj.py`. Opis zmiennych: `zmienne_szablonow.md`. Warianty linku i grupy: `warianty.md`. Wymagania serwisów: `wymagania/INDEX.md` + `wymagania/<serwis>.md`.

## Zasady (zawsze)
- **Szablonów w `xslt/szablony/` nie edytuję.** Przy każdym wywołaniu czytam ich bieżącą wersję. Gdy szablon nie jest poprawnym XML, `konfiguruj.py` się zatrzymuje. Wtedy zgłaszam błąd użytkownikowi (linia, prawdopodobna przyczyna z `git diff`) i nie naprawiam szablonu.
- Wynik to **zawsze XSLT 1.0** i nowy plik do ręcznego wgrania. W panelu niczego nie zapisuję ani nie klikam „Zapisz”. Panel tylko czytam, a loguje się użytkownik.
- Zmiany logiki robię tylko w kopii i każdą opisuję w `zmiany.md`. Zmiana przydatna dla wszystkich sklepów trafia do podsumowania jako propozycja do szablonu.
- Gdy parametru nie ma, zmienną zostawiam pustą (`''` albo `|`) i dopisuję uwagę. Nie zgaduję.
- **Zapis zmiennych dopasowywanych do panelu:** parametry jako `|<@id>|<@name PL>|`, węzły menu 1 jako `|<@id>|<nazwa PL>|`, wartości jako `|<id>|<nazwa PL>|` (`zmienne_szablonow.md`, „Standard zapisu”). Przy ID z menu 1 sprawdzam w `/panel/navigation.php`, czy menu jest współdzielone między sklepami. Nazwa jest zapisana jak w panelu. Dotyczy to także `gender_` i `age_group_nazwa_w_panelu`. Gdy wersja szablonu porównuje zmienną jako jedną wartość, `konfiguruj.py` odrzuca listę. Wtedy wpisuję pojedyncze ID, nazwę podaję w `zmiany.md` i odnotowuję, że po aktualizacji szablonu wystarczy odtworzyć sterownik z listą. Szczegóły per zmienna są w „Standardzie zapisu”. Kopii nie łatam.
- **Elementy obsługiwane przez serwis:** element zostaje, jeśli serwis go obsługuje i jest w szablonie Google albo Facebook. W szablonie starszym aktualizuję go do wersji z Google/FB. Elementów, których nie ma w żadnym z tych dwóch szablonów (np. `g:quantity`), nie dopisuję.
- Przykładowe wartości z szablonu (`|123456789|987654321|`, `|Male|dla Panów|…|`, `|dzieci|Nastolatki|`) **zawsze** zastępuję danymi sklepu albo czyszczę.
- Python uruchamiam z katalogu `SI/SummonFeed SI/narzedzia/`, z `PYTHONIOENCODING=utf-8`.

## Szablony
| Szablon | Kiedy | Uwagi |
|---|---|---|
| `Google.xml` | Google i każdy serwis przyjmujący format Google (`wymagania/INDEX.md`, kolumna „akceptuje Google”) | wzorzec elementów |
| `Facebook.xml` | Meta | wzorzec elementów |
| `Ceneo.xml`, `Glami.xml`, `Idealo.xml`, `Compari.xml`, `Biliger.xml`, `samba.xml`, `Synerise.xml`, `Pinterest.xml`, `MCAds.xml`, `IAI_gAds.xml` | gdy format serwisu odpowiada szablonowi | starsze elementy → krok 5 |

Gdy dla serwisu nie ma pasującego szablonu, biorę `Google.xml` i dopasowuję elementy do `wymagania/<serwis>.md`.

## 0. Start
1. Argumenty: link do panelu (`https://<domena>/panel/…`), ID sklepu (`shop`), serwis. Bez któregoś z nich pytam.
2. `domena` = host sklepu. Folder: `sterowniki/<domena>/`. Jeśli jest w nim `konfiguracja.json` z poprzedniego przebiegu, proponuję **odtworzenie**: ten sam zestaw odpowiedzi na nowszej wersji szablonu albo dla innego serwisu. Pytam tylko o to, co się zmieniło lub czego brakuje.
3. **Wymagania serwisu:** `wymagania/INDEX.md` → plik serwisu. Gdy „Data przeglądu” jest starsza niż **90 dni** albo pliku brak, czytam źródła z INDEX (WebFetch; strony renderowane przez JS w Claude in Chrome), aktualizuję plik i datę, a zmiany wypisuję w podsumowaniu. Gdy strona jest niedostępna, zostawiam starą treść i zapisuję to w „Uwagach”.
4. Szablon: `python konfiguruj.py zmienne <Szablon.xml>` → lista zmiennych, commit, sha256. Ostrzegam, gdy szablon ma niezatwierdzone zmiany (`niezatwierdzone_zmiany: true`).

## 1. Panel IdoSell (Claude in Chrome, tylko odczyt)
Technika jak w skillu `weryfikacja-gmc`: zamiast `screenshot`/`get_page_text` używam `javascript_tool`, tekst odkładam do `window.__t` i czytam fragmentami. Filtr blokuje query string, więc z linków zwracam tylko `pathname`.
- Wielosklep: `/panel/config-pricecomparers.php` → `[wybierz]` przy sklepie (`?shop=<id>`).
- **Parametry:** `/panel/parameters.php`. Rozwijam `ul.list-group > li.menu_li_item a.showChildren` (pauza 500 ms), nazwę biorę z `div.showMenuSub.parameter`, wartości z `ul li`. Wypisuję kandydatów na: kolor, materiał, płeć, grupę wiekową, wagę, pojemność, certyfikaty, informacje wyróżnione oraz parametry z kontekstem (`CONTEXT_COLOR`, `CONTEXT_SEX`, `CONTEXT_STATE`).
- **Menu 1** (gdy płeć lub grupy wiekowej nie ma w parametrach). Przetestowane 2026-10-27 na `zooart6.yourtechnicaldomain.com`:
  1. `/panel/navigation.php` → lista sklepów z linkami „Menu 1…5”. Link „Menu 1” sklepu otwieram przez `location.href = <href>` (filtr ukrywa query string, ale adres `?action=menuTree&shop=<id>&tree=1&lang=pol` widać w kontekście karty).
  2. Wklejam `narzedzia/menu1.js` do `javascript_tool`. Skrypt rozwija gałęzie (`.showChildren`), zbiera węzły (`li.menu_li_item#m<ID>`, ścieżka z `.showoptions[data-path]`) i **szuka po słowach kluczowych w ścieżce węzła** (męsk/mężczy/chłop, damsk/kobie/dziewcz, unisex, noworod, niemowl, maluch/przedszkol, dzieci/dziecię, dorosł/senior). Węzły podrzędne dziedziczą trafienie rodzica. Wynik dostaję gotowy jako `|id|nazwa|…` dla zmiennych `*_id_menu`. Słowa kluczowe uzupełniam o nazwy sklepu, które widzę w `__menu1`, a listę trafień przeglądam i usuwam fałszywe trafienia.
  3. **Współdzielenie:** odczytuję menu 1 drugiego sklepu tym samym skryptem (`shop=<inny id>`). Menu jest współdzielone, gdy zbiory ID są identyczne albo strona pokazuje komunikat „Ten sklep współdzieli swoje ustawienia z …”. Gdy menu nie jest współdzielone (jak w zooart6: 26 i 65 węzłów, różne ID), konfiguracja dotyczy tylko jednego sklepu i zapisuję to w `zmiany.md`.
  4. Szablon sprawdza `iaiext:priority_menu/site/menu[1]/item/@id`. Gdy mam ofertę IOF, sprawdzam, czy znalezione ID występują w tym miejscu.
- **Magazyny:** lista magazynów sklepu → `sales_stocks`.
- **Język i waluta sklepu** → `Kraj_dostawy`, tytuł kanału.
- **Profil dostaw:** `/panel/config-shippingprofiles.php` → „Profile dostaw [wybierz]” → `[edytuj]` (klik przez `setTimeout(()=>a.click(),100)`). Odczytuję kurierów, koszty z przedpłatą, „darmowe od” i oznaczenie **domyślnej** metody w kolumnie przedpłaty.
- **Oferta IOF do testu:** jeśli w panelu jest dostępny plik oferty sklepu, pytam o zgodę na pobranie (nazwa, źródło, rozmiar) i zapisuję go jako `sterowniki/<domena>/oferta.xml`. Potem uruchamiam `python parametry_oferty.py ../sterowniki/<domena>/oferta.xml`, co daje parametry z liczbą produktów, `group/@id`, GTIN i magazyny. Bez zgody testuję na `SI/summonFeed/products_export.xml` i zaznaczam to w podsumowaniu.

## 2. Pytania (zawsze, przez AskUserQuestion, w jednym zestawie)
1. **Dostawa (`g:shipping`):**
   - **Dynamiczna** → `kwota_dla_darmowej_dostawy = *`. Sprawdzam, czy profil ma domyślną metodę wysyłki z przedpłatą. Jeśli nie ma, ostrzegam, że feed nie przekaże kosztu, i proponuję tryb na sztywno.
   - **Na sztywno** → dopytuję: najtańsza opcja (obejmująca pełny zakres produktów) czy kurier na adres. Koszt, próg darmowej dostawy i czasy odczytuję z profilu dostaw w panelu, a nazwę usługi biorę z metody.
   - **Pominąć** → `kwota_dla_darmowej_dostawy`, `Koszt_dostawy` i pozostałe zmienne dostawy puste.
2. **Format linków** (`warianty.md`): A — link porównywarki (domyślny), B — link czysty `.html`, C — link z oferty `card/@url`. Opcjonalnie UTM.
3. **ID grupy (`g:item_group_id`)** (`warianty.md`): 1 — tylko rozmiary, 2 — rozmiary i warianty. Do tego prefiks `group-` albo brak. Podaję liczbę produktów z `group/@id`, jeśli ją znam.
4. Tylko gdy dopasowanie parametrów jest niejednoznaczne: który parametr odpowiada płci, kolorowi, materiałowi itd. Podaję kandydatów z panelu.

Pozostałych elementów szablonu nie zmieniam, chyba że wymaga tego serwis (krok 4).

## 3. Konfiguracja i kopia
1. Zapisuję `sterowniki/<domena>/konfiguracja.json`:
```json
{
  "domena": "sklep.pl",
  "panel": "https://sklep.pl/panel/",
  "shop_id": "1",
  "serwis": "google",
  "szablon": "Google.xml",
  "wyjscie": "sklep.pl_google.xml",
  "odpowiedzi": {"dostawa": "dynamiczna", "linki": "A", "item_group_id": "1", "prefiks_grupy": ""},
  "dozwolone": "",
  "zmienne": {"kwota_dla_darmowej_dostawy": "*", "kolor_nazwa_w_panelu": "|kolor|", "sales_stocks": "|1|"},
  "teksty": [
    {"z": "<title>00000</title>", "na": "<title>Sklep</title>", "ile": 1},
    {"z": "https://00000/", "na": "https://sklep.pl/", "ile": 2}
  ]
}
```
   `dozwolone`: pusty ciąg oznacza pełny szablon. Lista elementów oznacza przycięcie w kroku 4. `konfiguruj.py` pomija to pole.
   Znaczenie zmiennych i pułapki (wielkość liter, pojedyncza nazwa zamiast listy): `zmienne_szablonow.md`. Wartość w zmiennej zapisanej jako `select="'…'"` nie może zawierać apostrofu.
2. `python konfiguruj.py utworz ../sterowniki/<domena>/konfiguracja.json` → kopia sterownika + `raport_konfiguracji.md`. Skrypt zatrzymuje się, gdy zmiennej nie ma w szablonie albo tekst występuje inną liczbę razy niż `ile`.
3. Warianty linku i grupy wprowadzam edycją kopii według `warianty.md`.

## 4. Dopasowanie do serwisu
1. **Generuję tylko elementy obsługiwane przez serwis.** Listę biorę z sekcji „Elementy do wygenerowania” (`dozwolone: …`) w `wymagania/<serwis>.md`. Gdy sekcji brak, ustalam listę z pól wymaganych i zalecanych, dopisuję ją do pliku i pokazuję w podsumowaniu. Najpierw uruchamiam podgląd, potem przycinam:
   `python przytnij.py ../sterowniki/<domena>/<wyjscie> --dozwolone <lista> --proba`, a potem to samo bez `--proba`.
   Skrypt usuwa elementy spoza listy, puste po nich `xsl:if`/`xsl:choose`, nieużywane zmienne lokalne i niewywoływane nazwane szablony. Zmienne globalne zostawia. Przy pełnym serwisie Google ten krok pomijam. Listę usuniętych elementów zapisuję w `zmiany.md`. Lista `dozwolone` trafia też do `konfiguracja.json` jako `"dozwolone"`, żeby odtworzenie przycięło kopię tak samo.
2. Według sekcji „Różnice względem szablonu”: zmieniam nazwy elementów, dopisuję wymagane elementy, których brakuje, i pilnuję limitów (`dlugosc_opisu`, długość tytułu). Każda zmiana trafia do `zmiany.md`.

## 5. Elementy wspólne w starszych szablonach
Gdy bazą nie jest Google ani Facebook, porównuję w kopii elementy wspólne z `Google.xml`: tytuł (`wybierzZrodloNazwy`, `nazwaTowaru`, `wordFormat`), opis (`from_parameters`, `opis_do_kropki`), ceny (`cena_serwis`, `cena_przekreslona`), dostępność (`sales_stocks`), kolor i materiał oraz named templates (`strip-tags`, `string-replace-all`, `tokenize`). Pomagają w tym komentarze z datą (`<!-- 2026.04.30 MD -->`), które pokazują, która wersja jest nowsza. Listę możliwych aktualizacji pokazuję użytkownikowi (AskUserQuestion, multiSelect). Wybrane pozycje przenoszę do kopii, dopasowując nazwy elementów do formatu serwisu, i opisuję w `zmiany.md`.

## 6. Weryfikacja
`python weryfikuj.py ../sterowniki/<domena>/<wyjscie> [--oferta ../sterowniki/<domena>/oferta.xml] --wymagane <pola wymagane serwisu> [--dozwolone <lista>] [--element o]`
- Przy przyciętym sterowniku `--dozwolone` jest obowiązkowe: każdy element spoza listy to błąd. Wartości elementów, które zostały, porównuję z wynikiem kopii sprzed przycięcia. Muszą być identyczne.
- Google/FB: domyślne `--wymagane` (id, title, description, link, image_link, price, availability) plus pola wymagane z pliku serwisu.
- Ceneo: `--element o --wymagane "@id,@url,@price,@avail,name,cat"`.
- Wymagane: wynik `OK`, brak `00000`, brak konstrukcji spoza XSLT 1.0. Ostrzeżenia omawiam w podsumowaniu.
- Ręcznie sprawdzam 2–3 rekordy z `podglad_wyniku.xml`: produkt z rozmiarami, produkt z promocją, link, `item_group_id`, `g:shipping`.
- Gdy dostępna jest oferta sklepu, porównuję liczbę rekordów z liczbą rozmiarów w ofercie.

## 7. Wynik i podsumowanie
`sterowniki/<domena>/`: `<domena>_<serwis>.xml`, `konfiguracja.json`, `raport_konfiguracji.md`, `zmiany.md`. Pliki `oferta.xml` i `podglad_wyniku.xml` są robocze i gitignorowane.
`zmiany.md`: data, wersja szablonu (commit, sha256), odpowiedzi na pytania, mapowanie parametrów (parametr z panelu → zmienna), zmiany logiki, uwagi (brak parametru, brak domyślnej metody wysyłki, test na próbce zastępczej).
Podsumowanie w czacie (krótko): ścieżka pliku, wybrane warianty, czego brakuje w danych sklepu, propozycje do szablonu, zaktualizowane wymagania.
