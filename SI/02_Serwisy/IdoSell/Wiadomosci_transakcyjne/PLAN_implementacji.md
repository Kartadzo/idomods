# Wiadomości transakcyjne IdoSell — plan implementacji

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Narzędzie do trzech trybów pracy z wiadomościami transakcyjnymi panelu IdoSell (Status, Edycja działania, Eksport i Import Treści) w dwóch wersjach: bookmarklet (bez Claude) i skill Claude in Chrome.

**Architecture:** Kod przeglądarkowy `przegladarka/panel_core.js` czyta panel `/panel/config-messages.php` na sesji użytkownika i zapisuje eksport jako jeden ZIP (manifest + pliki ICF) do domyślnego folderu pobierania Chrome (`C:\Users\Admin\Downloads`, bez zmiany ustawień przeglądarki); `wiadomosci.py` przy rozpakowaniu przenosi ZIP do archiwum `_pobrane/` w projekcie. Skrypt `wiadomosci.py` (pakiet `wt/`, tylko stdlib) wykonuje całą pracę na plikach: rozpakowanie, CSV konfiguracji, porównania, złożenie ICF i planów zmian, raport Status, weryfikację. Plany zmian wykonuje bookmarklet (ukryta ramka iframe sterująca formularzami panelu) albo Claude przez interfejs (`file_upload` + kliknięcia).

**Tech Stack:** Python 3.8+ (stdlib: `xml.etree`, `zipfile`, `csv`, `hashlib`, `unittest`), JavaScript ES2017 w przeglądarce Chrome (bez bibliotek), Node 18+ (`node:test`) do testów czystych funkcji JS, Claude in Chrome do wersji ze skillem.

**Spec:** `SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/ANALIZA_wiadomosci_transakcyjne.md` (szczególnie §2 fakty ze spike'u, §9 wyniki testu importu).

Wszystkie ścieżki poniżej są względne do `SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/` (dalej: **KATALOG**), chyba że zaczynają się od `.claude/` lub `.gitignore` (wtedy względem korzenia repozytorium `C:\Users\Admin\Desktop\Domino`).

## Global Constraints

- Python 3.8+, wyłącznie biblioteka standardowa; `run_wiadomosci.bat` działa po dwukliku (menu interaktywne), argumenty CLI tylko jako skrót.
- Wszystkie pliki tekstowe UTF-8; ICF/HTML/SMS czytane i zapisywane z `newline=""` (bez zmiany końców linii). CSV: UTF-8 z BOM (`utf-8-sig`), separator `;`.
- Kod, komentarze, komunikaty i identyfikatory po polsku; wcięcia 4 spacje (Python), 2 spacje (JS).
- JS na stronie panelu: panel ładuje Prototype.js — **zakaz** `Array.from`, `for…of` na `Set`/`Map`, `Array.prototype.filter/map/forEach` na wynikach DOM; tylko zwykłe pętle `for`. JSON wyłącznie przez `WT.doJson()`.
- Między żądaniami do panelu odstęp 200 ms; ponowienie przy 429/5xx (3 próby, 2 s × numer próby).
- Eksport zawsze jako **jeden** plik ZIP (Chrome blokuje drugie automatyczne pobranie).
- Folder pobierania: domyślny folder Chrome `%USERPROFILE%\Downloads` (nadpisywalny zmienną `WT_POBIERANIE`) — użytkownik nie zmienia ustawień przeglądarki. Z tego folderu narzędzie (i Claude) czyta **wyłącznie** pliki `eksport_*.zip` i `weryfikacja_*.zip` i **przenosi** je do `_pobrane/` w projekcie przed dalszą pracą; dalej wszystko dzieje się w projekcie. Pliki do importu (`file_upload`) zawsze z folderu projektu.
- Odcisk ICF = SHA-256 (hex) kanonicznej **treści**: dla każdego `<contents message_type>` pola `title` i `text_main_0` (CDATA/encje zdekodowane, sama spacja = puste) oraz zawartość `<enclosures>` — identycznie w Pythonie (`wt.icf.odcisk`) i JS (`WT.odcisk`); wspólny wektor w `testy/test_icf.py` i `przegladarka/testy/test_core.mjs` (`df229c2e…`). _Zmienione w Task 11 — pierwotna definicja (surowy tekst bez id/daty) dawała fałszywe różnice przy zmianie flag._
- Brak pliku języka w folderze wiadomości = nie ruszaj tego języka w panelu.
- Wiadomości „wycofywane” (link „Pokaż”) i kanały „nie dotyczy” są tylko do odczytu.
- Web Push: tylko odczyt (raport Status).
- Masowe „Ustaw domyślną treść wiadomości” i „Przywróć” z historii — nigdy. Reset pojedynczej wiadomości — tylko jako krok ręczny wskazany użytkownikowi.
- Import do innego sklepu/domeny niż w planie wymaga jawnego potwierdzenia (wpisanie domeny docelowej); plan konfiguracji wolno wykonać **tylko** w sklepie, z którego pochodzi eksport.
- Przed każdym zapisem w panelu ICF wszystkich języków danej wiadomości muszą być na dysku (eksport/plan).
- Dane klientów (`_pobrane/`, foldery sklepów w `Status/`, `Edycja Działania/`, `Eksport i Import Treści/`) są w `.gitignore`.
- Commity: tylko pliki z danego zadania (`git add <ścieżki>`), nigdy `git add -A` — w repozytorium są niezwiązane zmiany użytkownika.

### Kontrakt `manifest.json` (wspólny dla JS i Pythona)

```json
{
  "wersja": 1,
  "rodzaj": "eksport",
  "domena": "zooart6.yourtechnicaldomain.com",
  "shop_id": 1,
  "data_eksportu": "2026-10-13T13:05:09",
  "niekompletny": false,
  "pozostale": [],
  "jezyki": ["pol", "ukr", "eng"],
  "wiadomosci": [
    {
      "grupa": "make_order",
      "grupa_nazwa": "Złożenie zamówienia",
      "sekcja": "Zamówienia",
      "template": "order_confirmation",
      "nazwa": "Potwierdzenie wpłynięcia zamówienia",
      "edytowalna": true,
      "stan_listy": {"sms": "nie", "mail": "tak", "webpush": "nie", "braki": null},
      "formularz": {"mail": {"pol": "y", "ukr": "y", "eng": "y"}, "sms": "n", "webpush": {"pol": "n", "ukr": "n", "eng": "n"}},
      "ostatnia_edycja": {"autor": "Przemysław Kuś", "data": "2026-07-17 12:10:52"},
      "pliki": {"pol": "icf/make_order__order_confirmation/pol.icf"},
      "bledy": []
    }
  ]
}
```

- `rodzaj`: `"eksport"` albo `"weryfikacja"`. `stan_listy.*`: `"tak"`, `"nie"`, `"nie dotyczy"` albo `null` (brak kolumny); `braki`: np. `"2 z 3"` albo `null`.
- Wiadomość nieedytowalna: `edytowalna: false`, `formularz: null`, `ostatnia_edycja: null`, `pliki: {}`.
- `formularz.sms`: `"y"`/`"n"` albo `null` (brak pól SMS); `formularz.mail`: `{}` gdy brak maila.
- ZIP: `manifest.json` + pliki pod ścieżkami z `pliki`. Nazwa: `eksport_<pierwszy-człon-domeny>_shop<N>_<YYYYMMDD-HHMMSS>.zip` (albo `weryfikacja_…`).

## Review Focus

1. **Ponowne rozpakowanie tego samego eksportu** nadpisałoby pliki edytowane przez użytkownika — `rozpakuj` ma odmówić, gdy folder docelowy ma już `manifest.json` (test w Task 2).
2. **Edycja plików w Notatniku/VS Code zmienia końce linii na CRLF** — porównanie treści nie może zgłaszać zmian wyłącznie z powodu `\r\n` (test w Task 4).
3. **Excel zapisuje CSV z przecinkiem albo bez BOM, użytkownik czyści komórkę lub zostawia duplikat wiersza** — błędy mają wskazać wiersz i kolumnę, a nie zgubić zmianę po cichu (testy w Task 3).
4. **Treść zawierająca `]]>`, `&`, `<` lub polskie znaki** — podmiana w ICF musi dać poprawny XML i wierną treść (test w Task 1).
5. **Prototype.js na stronie panelu psuje `JSON.stringify` tablic (Array#toJSON)** — manifest musi mieć prawdziwe tablice JSON (test w Task 8).

---

### Task 0: Weryfikacja zachowania panelu przed zapisem (wymaga zgody użytkownika)

**Kolejność wykonania: Task 1 → … → Task 8 → Task 0 → Task 9 → Task 10 → Task 11.** Task 0 korzysta z `WT.eksportuj` (Task 8), żeby przed zapisem w panelu mieć kopię ICF wszystkich języków na dysku.

Zadanie bez kodu produkcyjnego — rozstrzyga §10 analizy i utrwala elementy DOM, na których opiera się Task 9. **Bramka:** jeśli import ICF wyłącza wysyłkę włączoną wcześniej, zatrzymaj się, dopisz wynik do analizy i zapytaj użytkownika o zmianę projektu — Task 9–11 nie startują.

**Files:**
- Modify: `ANALIZA_wiadomosci_transakcyjne.md` (nowa sekcja `## 11. Weryfikacja przed implementacją`)
- Zapis próbek: `_pobrane/task0/`

- [ ] **Step 1: Poproś użytkownika o zgodę** na import ICF w wiadomości `order_confirmation` (sklep 1, `zooart6`) i otwarcie panelu w Chrome (Claude in Chrome, `tabs_context_mcp` → nowa karta). Bez „tak” — stop.

- [ ] **Step 2: Zapisz na dysk ICF wszystkich języków.** W karcie panelu (`…/config-messages.php?populate=types&shop=1`) przez `javascript_tool` wklej zawartość `przegladarka/panel_core.js`, potem `const r = await WT.eksportuj({shop: 1, templates: ['order_confirmation']}); r.nazwa`. Następnie w KATALOGU: `python wiadomosci.py rozpakuj "%USERPROFILE%\Downloads\<nazwa>"` (ZIP zostanie przeniesiony do `_pobrane/`). Sprawdź: folder `make_order__order_confirmation` zawiera `pol.icf`, `eng.icf`, `ukr.icf`. Skopiuj `eng.icf` do `_pobrane/task0/eng.icf`.

- [ ] **Step 3: Odczytaj stan wyjściowy** przez `javascript_tool` (zwykłe pętle!): zaznaczone radio `mail_lang[*][active_mail]` i `sms_lang[active]` z `fetch` strony edycji (atrybut `checked`). Oczekiwane: mail pol/eng/ukr = `y`, sms = `n`.

- [ ] **Step 4: Import ICF `eng` (oryginał, `active=y`) na włączoną wiadomość** przez interfejs: link „Import ICF” → `file_upload` na `input[name=idf_file]` z `_pobrane/task0/<eng>.icf` → „Wgraj plik” → w kroku języka **zapisz atrybuty `name` i `value` radia „English”** (`find`/`read_page`) → „Wybierz” → **zapisz, czy przycisk „Tak” jest elementem strony (nie natywnym `confirm`)** → „Tak” → komunikat sukcesu (zapisz dokładny tekst).

- [ ] **Step 5: Sprawdź flagi po imporcie.** Oczekiwane (warunek kontynuacji): mail eng nadal `y`. Jeśli `n` → przywróć formularzem (zakładka English → „Wysyłaj ten list: tak” → „Zapisz zmiany”), dopisz wynik do analizy i **STOP** (bramka).

- [ ] **Step 6: Utrwal elementy DOM.** Z bieżącej strony odczytaj i zapisz w §11 analizy:
  - tag i treść nagłówków sekcji nad tabelami listy (`populate=list&group=make_order&shop=1`), np. `H3 "Zamówienia"`,
  - czy linki grup ustawień („Nagłówek i stopka…”) zawierają `populate=list` (jeśli tak — zanotuj, Task 8 je odfiltruje po braku tabel z kolumnami kanałów),
  - typ przycisku „Zapisz zmiany” (`input[type=submit]` czy `button`) i tekst komunikatu po zapisie („Zmiany zostały zapisane”),
  - czy po „Wgraj plik” i po „Wybierz” strona przeładowuje się (zmiana `location.href`).

- [ ] **Step 7: Dopisz §11 do analizy** w formacie:

```markdown
## 11. Weryfikacja przed implementacją (YYYY-MM-DD)

| Sprawdzane | Wynik |
| --- | --- |
| Import ICF `active=y` na włączoną wiadomość | mail eng po imporcie: y / n |
| Radio języka w imporcie | name=`…`, value=`eng` |
| Potwierdzenie „Tak” | element strony / natywny confirm |
| Komunikat sukcesu importu | „Import przebiegł pomyślnie. Szablon został zmieniony.” |
| Nagłówki sekcji listy | `H?` |
| Linki grup ustawień | zawierają / nie zawierają `populate=list` |
| „Zapisz zmiany” | `input[type=submit]` / `button`; komunikat: „Zmiany zostały zapisane” |
| Przeładowania | po „Wgraj plik”: tak/nie; po „Wybierz”: tak/nie |
```

Jeśli `value` radia języka **nie** jest kodem języka (np. `pol`/`eng`), zapisz mapowanie — Task 9 Step 3 używa `input[type=radio][value="<jezyk>"]` i trzeba go wtedy dostosować.

- [ ] **Step 8: Zamknij kartę** (`tabs_close_mcp`). Bez commita (analiza commitowana w Task 1).

---

### Task 1: Szkielet pakietu, `.gitignore` i moduł ICF

**Files:**
- Create: `wt/__init__.py`, `wt/wspolne.py`, `wt/icf.py`
- Create: `testy/__init__.py`, `testy/fixtures.py`, `testy/test_icf.py`
- Modify: `.gitignore` (korzeń repo, po linii 143)

**Interfaces:**
- Produces:
  - `wt.wspolne`: `KATALOG_GLOWNY`, `FOLDER_POBIERANIE` (folder pobierania Chrome), `FOLDER_POBRANE` (archiwum w projekcie), `FOLDER_STATUS`, `FOLDER_EDYCJA`, `FOLDER_TRESCI` (str); `przejmij(sciezka: str) -> str` (ZIP z folderu pobierania → przeniesiony do archiwum, zwraca nową ścieżkę; inne ścieżki bez zmian); `id_sklepu(domena: str, shop_id: int) -> str`; `znacznik_daty(iso: str) -> str`; `teraz_iso() -> str`; `czytaj_tekst(sciezka) -> str`; `zapisz_tekst(sciezka, tresc) -> None`; `czytaj_json(sciezka) -> Any`; `zapisz_json(sciezka, dane) -> None`.
  - `wt.icf`: `BladIcf(Exception)`; `wczytaj(xml: str) -> dict` (`{"template", "jezyk", "nazwa", "kanaly": {"mail": {pole: str}, "sms": {...}}, "zalaczniki": int}`; puste pola `" "` → `""`); `wartosc(dane: dict, kanal: str, pole: str) -> str|None`; `podmien(xml: str, kanal: str, pole: str, wartosc: str) -> str`; `odcisk(xml: str) -> str`.
  - `testy.fixtures`: `icf_xml(**opcje) -> str`, `wiadomosc(**opcje) -> dict`, `manifest(wiadomosci=None, jezyki=("pol", "eng", "ukr")) -> dict`, `zbuduj_zip(sciezka, manifest, pliki) -> None`.

- [ ] **Step 1: Dopisz do `.gitignore`** (po linii `SI/02_Serwisy/IdoSell/*/wyniki/`):

```gitignore
# Wiadomości transakcyjne - pobrane eksporty i dane sklepów klientów (per-maszyna)
SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/_pobrane/
SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/Status/*/
SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/Edycja Działania/*/
SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/Eksport i Import Treści/*/
```

Sprawdź: `git check-ignore -v "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/_pobrane/x.zip"` wypisuje regułę.

- [ ] **Step 2: Utwórz `wt/__init__.py`**

```python
"""Wiadomości transakcyjne IdoSell - praca na plikach eksportu (tylko biblioteka standardowa)."""
```

i pusty `testy/__init__.py`.

- [ ] **Step 3: Utwórz `wt/wspolne.py`**

```python
"""Wspólne pomocnicze: foldery trybów, identyfikator sklepu, zapis plików bez zmiany końców linii."""

import datetime
import json
import os
import re
import shutil
from typing import Any

# WT_KATALOG / WT_POBIERANIE pozwalają testom podmienić katalog roboczy i folder pobierania.
KATALOG_GLOWNY = os.environ.get("WT_KATALOG") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Domyślny folder pobierania Chrome - użytkownik nie musi zmieniać ustawień przeglądarki.
FOLDER_POBIERANIE = os.environ.get("WT_POBIERANIE") or os.path.join(os.path.expanduser("~"), "Downloads")
# Archiwum eksportów w projekcie - tu trafiają ZIP-y zabrane z folderu pobierania.
FOLDER_POBRANE = os.path.join(KATALOG_GLOWNY, "_pobrane")
FOLDER_STATUS = os.path.join(KATALOG_GLOWNY, "Status")
FOLDER_EDYCJA = os.path.join(KATALOG_GLOWNY, "Edycja Działania")
FOLDER_TRESCI = os.path.join(KATALOG_GLOWNY, "Eksport i Import Treści")


def id_sklepu(domena: str, shop_id: int) -> str:
    """'zooart6.yourtechnicaldomain.com', 1 -> 'zooart6_shop1'."""
    pierwszy = domena.strip().lower().split(".")[0]
    return re.sub(r"[^a-z0-9_-]", "_", pierwszy) + "_shop" + str(shop_id)


def znacznik_daty(iso: str) -> str:
    """'2026-10-13T13:05:09' -> '2026-10-13_130509' (bezpieczne w nazwach folderów)."""
    data, _, czas = iso.partition("T")
    return data + "_" + czas.replace(":", "")[:6]


def teraz_iso() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def przejmij(sciezka: str) -> str:
    """ZIP narzędzia leżący w folderze pobierania przenosi do archiwum projektu; inne ścieżki zwraca bez zmian."""
    nazwa = os.path.basename(sciezka)
    w_pobieraniu = os.path.normcase(os.path.dirname(os.path.abspath(sciezka))) == os.path.normcase(os.path.abspath(FOLDER_POBIERANIE))
    if not w_pobieraniu or not re.match(r"^(eksport|weryfikacja)_.*\.zip$", nazwa):
        return sciezka
    os.makedirs(FOLDER_POBRANE, exist_ok=True)
    rdzen, rozszerzenie = os.path.splitext(nazwa)
    cel, nr = os.path.join(FOLDER_POBRANE, nazwa), 2
    while os.path.exists(cel):
        cel = os.path.join(FOLDER_POBRANE, "%s_%d%s" % (rdzen, nr, rozszerzenie))
        nr += 1
    shutil.move(sciezka, cel)
    return cel


def czytaj_tekst(sciezka: str) -> str:
    with open(sciezka, encoding="utf-8", newline="") as plik:
        return plik.read()


def zapisz_tekst(sciezka: str, tresc: str) -> None:
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8", newline="") as plik:
        plik.write(tresc)


def czytaj_json(sciezka: str) -> Any:
    with open(sciezka, encoding="utf-8") as plik:
        return json.load(plik)


def zapisz_json(sciezka: str, dane: Any) -> None:
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8") as plik:
        json.dump(dane, plik, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Utwórz `testy/fixtures.py`** (format ICF odwzorowany z panelu, §2 analizy)

```python
"""Dane testowe: syntetyczne ICF i manifesty w formacie panelu IdoSell."""

import json
import zipfile


def icf_xml(template="order_confirmation", jezyk="pol", nazwa="Potwierdzenie wpłynięcia zamówienia",
            tytul="[iai:shop_name] – Zamówienie nr [iai:order_sn]",
            html="<p>Dziękujemy, zamówienie [iai:order_sn] przyjęte.</p>", mail_active="y",
            sms="Przyjęliśmy zamówienie [iai:order_id]. [iai:shop_name]", sms_active="n", only_ascii="y",
            z_mailem=True, z_sms=True, element_id="1791889368", opis=" 2026.10.13 13:02:48"):
    czesci = [
        '<?xml version="1.0" encoding="UTF-8"?>\n<repository file_format="ICF" version="1.0">'
        '<element id="%s">\n' % element_id,
        '<meta><title>%s</title><description>%s</description><icon encoding="base64"></icon>'
        '<language name="%s"/></meta>\n' % (nazwa, opis, jezyk),
        '<classification><type name="message_email"/></classification>\n',
        '<settings><setting type="template" value="%s"/><setting type="language" value="%s"/></settings>\n'
        % (template, jezyk),
    ]
    if z_mailem:
        czesci.append(
            '<contents message_type="mail"><content type="text_main_0"><![CDATA[%s]]></content>'
            '<content type="title"><![CDATA[%s]]></content><content type="contenttype">html</content>'
            '<content type="disposition"> </content><content type="bcc"> </content><content type="css"> </content>'
            '<content type="account"> </content><content type="default">n</content>'
            '<content type="active">%s</content><content type="additional_config"> </content></contents>\n'
            % (html, tytul, mail_active))
    if z_sms:
        czesci.append(
            '<contents message_type="sms"><content type="branding">Twoj eSklep</content>'
            '<content type="text_main_0"><![CDATA[%s]]></content><content type="name"> </content>'
            '<content type="only_ascii">%s</content><content type="type_sms">2</content>'
            '<content type="active">%s</content></contents>\n' % (sms, only_ascii, sms_active))
    czesci.append('<enclosures><enclosure id="0" name="000.png" encoding="base64">iVBORw0KGgo=</enclosure>'
                  '</enclosures>\n</element>\n</repository>')
    return "".join(czesci)


def wiadomosc(template="order_confirmation", nazwa="Potwierdzenie wpłynięcia zamówienia", grupa="make_order",
              jezyki=("pol", "eng", "ukr"), edytowalna=True, mail=None, sms="n", stan_listy=None,
              ostatnia_edycja=None):
    if not edytowalna:
        return {"grupa": grupa, "grupa_nazwa": "Złożenie zamówienia", "sekcja": "Zamówienia",
                "template": template, "nazwa": nazwa, "edytowalna": False,
                "stan_listy": stan_listy or {"sms": "nie", "mail": "tak", "webpush": "nie", "braki": None},
                "formularz": None, "ostatnia_edycja": None, "pliki": {}, "bledy": []}
    mail = mail if mail is not None else {j: "y" for j in jezyki}
    return {
        "grupa": grupa, "grupa_nazwa": "Złożenie zamówienia", "sekcja": "Zamówienia",
        "template": template, "nazwa": nazwa, "edytowalna": True,
        "stan_listy": stan_listy or {"sms": "nie" if sms == "n" else "tak", "mail": "tak", "webpush": "nie",
                                     "braki": None},
        "formularz": {"mail": dict(mail), "sms": sms, "webpush": {j: "n" for j in jezyki}},
        "ostatnia_edycja": ostatnia_edycja or {"autor": "Jan Testowy", "data": "2026-07-17 12:10:52"},
        "pliki": {j: "icf/%s__%s/%s.icf" % (grupa, template, j) for j in jezyki},
        "bledy": [],
    }


def manifest(wiadomosci=None, jezyki=("pol", "eng", "ukr")):
    return {
        "wersja": 1, "rodzaj": "eksport", "domena": "zooart6.yourtechnicaldomain.com", "shop_id": 1,
        "data_eksportu": "2026-10-13T13:05:09", "niekompletny": False, "pozostale": [],
        "jezyki": list(jezyki),
        "wiadomosci": wiadomosci if wiadomosci is not None else [wiadomosc(jezyki=jezyki)],
    }


def zbuduj_zip(sciezka, manifest_dane, pliki):
    """pliki: {sciezka_w_zip: tekst_icf}"""
    with zipfile.ZipFile(sciezka, "w") as archiwum:
        archiwum.writestr("manifest.json", json.dumps(manifest_dane, ensure_ascii=False))
        for nazwa, tresc in pliki.items():
            archiwum.writestr(nazwa, tresc.encode("utf-8"))
```

- [ ] **Step 5: Napisz testy `testy/test_icf.py`**

```python
import hashlib
import unittest
import xml.etree.ElementTree as ET

from testy import fixtures
from wt import icf


class TestWczytaj(unittest.TestCase):
    def test_pola_kanalow(self):
        dane = icf.wczytaj(fixtures.icf_xml(jezyk="eng"))
        self.assertEqual(dane["template"], "order_confirmation")
        self.assertEqual(dane["jezyk"], "eng")
        self.assertEqual(dane["kanaly"]["mail"]["active"], "y")
        self.assertEqual(dane["kanaly"]["mail"]["title"], "[iai:shop_name] – Zamówienie nr [iai:order_sn]")
        self.assertEqual(dane["kanaly"]["sms"]["active"], "n")
        self.assertEqual(dane["kanaly"]["mail"]["css"], "")   # " " w panelu = puste
        self.assertEqual(dane["zalaczniki"], 1)

    def test_brak_kanalu(self):
        dane = icf.wczytaj(fixtures.icf_xml(z_sms=False))
        self.assertNotIn("sms", dane["kanaly"])
        self.assertIsNone(icf.wartosc(dane, "sms", "text_main_0"))

    def test_nie_icf(self):
        with self.assertRaises(icf.BladIcf):
            icf.wczytaj("<html><title>Logowanie użytkownika</title></html>")
        with self.assertRaises(icf.BladIcf):
            icf.wczytaj("to nie jest xml")


class TestPodmien(unittest.TestCase):
    def test_podmienia_tylko_wskazane_pole(self):
        xml = fixtures.icf_xml()
        nowy = icf.podmien(xml, "mail", "title", "Nowy tytuł")
        dane = icf.wczytaj(nowy)
        self.assertEqual(dane["kanaly"]["mail"]["title"], "Nowy tytuł")
        self.assertEqual(dane["kanaly"]["mail"]["text_main_0"], icf.wczytaj(xml)["kanaly"]["mail"]["text_main_0"])
        # reszta pliku (sms, załączniki) bajt w bajt bez zmian
        self.assertEqual(nowy[nowy.index('<contents message_type="sms">'):], xml[xml.index('<contents message_type="sms">'):])

    def test_znaki_specjalne_i_cdata(self):
        tresc = 'Cena < 100 & "rabat" ]]> koniec – żółć'
        nowy = icf.podmien(fixtures.icf_xml(), "mail", "text_main_0", tresc)
        ET.fromstring(nowy.encode("utf-8"))   # poprawny XML
        self.assertEqual(icf.wczytaj(nowy)["kanaly"]["mail"]["text_main_0"], tresc)

    def test_pusta_wartosc_jak_w_panelu(self):
        nowy = icf.podmien(fixtures.icf_xml(), "sms", "text_main_0", "")
        self.assertIn('<content type="text_main_0"> </content>', nowy)

    def test_brak_kanalu_lub_pola(self):
        with self.assertRaises(icf.BladIcf):
            icf.podmien(fixtures.icf_xml(z_sms=False), "sms", "text_main_0", "x")
        with self.assertRaises(icf.BladIcf):
            icf.podmien(fixtures.icf_xml(), "mail", "nie_ma_takiego", "x")


class TestOdcisk(unittest.TestCase):
    def test_wektor_wspolny_z_js(self):
        self.assertEqual(icf.odcisk('<element id="5"><description>x</description></element>'),
                         "ab0b689c27f39287b842979f958747a537c71abef5268a728a1081e4f694417b")

    def test_ignoruje_id_i_date_eksportu(self):
        a = fixtures.icf_xml(element_id="1", opis=" 2026.10.13 13:00:00")
        b = fixtures.icf_xml(element_id="2", opis=" 2026.10.14 09:00:00")
        self.assertEqual(icf.odcisk(a), icf.odcisk(b))
        self.assertNotEqual(icf.odcisk(a), icf.odcisk(fixtures.icf_xml(mail_active="n")))

    def test_to_sha256(self):
        self.assertEqual(icf.odcisk("abc"), hashlib.sha256(b"abc").hexdigest())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 6: Uruchom testy — mają nie przejść**

Run (w KATALOGU): `python -m unittest testy.test_icf -v`
Expected: FAIL / ERROR — `ImportError: cannot import name 'icf' from 'wt'`.

- [ ] **Step 7: Utwórz `wt/icf.py`**

```python
"""Pliki ICF panelu IdoSell: odczyt pól, podmiana pojedynczego pola z zachowaniem reszty pliku, odcisk."""

import hashlib
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional


class BladIcf(Exception):
    """Plik nie jest poprawnym ICF albo brakuje w nim wskazanego kanału/pola."""


def wczytaj(xml: str) -> Dict:
    try:
        korzen = ET.fromstring(xml.encode("utf-8"))
    except ET.ParseError as blad:
        raise BladIcf("Niepoprawny XML ICF: %s" % blad)
    if korzen.tag != "repository" or korzen.get("file_format") != "ICF":
        raise BladIcf("To nie jest plik ICF (korzeń <%s>)" % korzen.tag)
    element = korzen.find("element")
    if element is None:
        raise BladIcf("Plik ICF bez elementu <element>")
    ustawienia = {s.get("type"): s.get("value") for s in element.findall("settings/setting")}
    kanaly = {}
    for blok in element.findall("contents"):
        pola = {}
        for pole in blok.findall("content"):
            tekst = pole.text or ""
            pola[pole.get("type")] = tekst if tekst.strip() else ""
        kanaly[blok.get("message_type")] = pola
    return {
        "template": ustawienia.get("template"),
        "jezyk": ustawienia.get("language"),
        "nazwa": (element.findtext("meta/title") or "").strip(),
        "kanaly": kanaly,
        "zalaczniki": len(element.findall("enclosures/enclosure")),
    }


def wartosc(dane: Dict, kanal: str, pole: str) -> Optional[str]:
    return dane["kanaly"].get(kanal, {}).get(pole)


def _cdata(tekst: str) -> str:
    if tekst == "":
        return " "   # panel zapisuje puste pole jako pojedynczą spację
    return "<![CDATA[" + tekst.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def podmien(xml: str, kanal: str, pole: str, wartosc_nowa: str) -> str:
    """Zmienia jedno pole w bloku kanału; reszta pliku (załączniki, nieznane pola) zostaje bajt w bajt."""
    blok = re.search(r'(<contents message_type="%s">)(.*?)(</contents>)' % re.escape(kanal), xml, re.S)
    if not blok:
        raise BladIcf("Brak kanału '%s' w ICF" % kanal)
    wnetrze = blok.group(2)
    wzor = re.compile(r'(<content type="%s">)(.*?)(</content>)' % re.escape(pole), re.S)
    if not wzor.search(wnetrze):
        raise BladIcf("Brak pola '%s' w kanale '%s'" % (pole, kanal))
    nowe_wnetrze = wzor.sub(lambda m: m.group(1) + _cdata(wartosc_nowa) + m.group(3), wnetrze, count=1)
    return xml[:blok.start(2)] + nowe_wnetrze + xml[blok.end(2):]


def odcisk(xml: str) -> str:
    """SHA-256 bez pól zmiennych przy każdym eksporcie (id elementu, data w <description>). Zgodny z WT.odcisk w JS."""
    tekst = re.sub(r'<element id="\d+">', "<element>", xml, count=1)
    tekst = re.sub(r"<description>[^<]*</description>", "<description/>", tekst, count=1)
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()
```

- [ ] **Step 8: Uruchom testy — mają przejść**

Run: `python -m unittest testy.test_icf -v`
Expected: `OK` (10 testów).

- [ ] **Step 9: Commit**

```bash
git add .gitignore "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wt" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/ANALIZA_wiadomosci_transakcyjne.md" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/PLAN_implementacji.md"
git commit -m "Wiadomości transakcyjne: szkielet pakietu wt i moduł ICF"
```

---

### Task 2: Rozpakowanie eksportu do folderów wiadomości

**Files:**
- Create: `wt/eksport.py`
- Test: `testy/test_eksport.py`

**Interfaces:**
- Consumes: `wt.icf.wczytaj`, `wt.wspolne.*`, `testy.fixtures.*`.
- Produces: `wt.eksport`: `BladEksportu(Exception)`; `wczytaj_zip(sciezka) -> (manifest: dict, pliki: {sciezka_w_zip: str})`; `scal(czesci: list) -> (manifest, pliki)`; `katalog_eksportu(manifest) -> str`; `nazwa_folderu(wiadomosc: dict) -> str` (`"<grupa>__<template>"`); `folder_wiadomosci(katalog, wiadomosc) -> str`; `rozpakuj(sciezki_zip: list, katalog_docelowy=None, nadpisz=False) -> (katalog: str, manifest: dict)`; `wczytaj_eksport(katalog) -> manifest`. Układ folderu wiadomości: `<jezyk>.icf`, `<jezyk>_mail.html` (gdy ICF ma kanał mail), `<jezyk>_sms.txt` (gdy ma sms), `meta.json` (`nazwa, grupa, grupa_nazwa, sekcja, template, domena, shop_id, data_eksportu, ostatnia_edycja, tytuly: {jezyk: str}`).

- [ ] **Step 1: Napisz testy `testy/test_eksport.py`**

```python
import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, wspolne


def _zip_z(katalog, manifest, nazwa="e.zip", pliki=None):
    if pliki is None:
        pliki = {}
        for w in manifest["wiadomosci"]:
            for j, sc in w["pliki"].items():
                pliki[sc] = fixtures.icf_xml(template=w["template"], jezyk=j)
    sciezka = os.path.join(katalog, nazwa)
    fixtures.zbuduj_zip(sciezka, manifest, pliki)
    return sciezka


class TestRozpakuj(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.k = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_uklad_folderu(self):
        m = fixtures.manifest(jezyki=("pol", "eng"))
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m)], os.path.join(self.k, "out"))
        folder = os.path.join(cel, "make_order__order_confirmation")
        self.assertEqual(sorted(os.listdir(folder)),
                         ["eng.icf", "eng_mail.html", "eng_sms.txt", "meta.json", "pol.icf", "pol_mail.html", "pol_sms.txt"])
        self.assertEqual(wspolne.czytaj_tekst(os.path.join(folder, "pol_mail.html")),
                         "<p>Dziękujemy, zamówienie [iai:order_sn] przyjęte.</p>")
        meta = wspolne.czytaj_json(os.path.join(folder, "meta.json"))
        self.assertEqual(meta["tytuly"]["eng"], "[iai:shop_name] – Zamówienie nr [iai:order_sn]")
        self.assertEqual(meta["shop_id"], 1)
        self.assertTrue(os.path.exists(os.path.join(cel, "manifest.json")))

    def test_icf_zapisany_bez_zmian(self):
        m = fixtures.manifest(jezyki=("pol",))
        xml = fixtures.icf_xml().replace("\n", "\r\n")
        sc = m["wiadomosci"][0]["pliki"]["pol"]
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m, pliki={sc: xml})], os.path.join(self.k, "out"))
        self.assertEqual(wspolne.czytaj_tekst(os.path.join(cel, "make_order__order_confirmation", "pol.icf")), xml)

    def test_bez_sms_brak_pliku_sms(self):
        m = fixtures.manifest(jezyki=("pol",))
        sc = m["wiadomosci"][0]["pliki"]["pol"]
        cel, _ = eksport.rozpakuj([_zip_z(self.k, m, pliki={sc: fixtures.icf_xml(z_sms=False)})], os.path.join(self.k, "o"))
        self.assertFalse(os.path.exists(os.path.join(cel, "make_order__order_confirmation", "pol_sms.txt")))

    def test_wycofywana_bez_folderu(self):
        m = fixtures.manifest(wiadomosci=[fixtures.wiadomosc(template="old", edytowalna=False)])
        cel, man = eksport.rozpakuj([_zip_z(self.k, m)], os.path.join(self.k, "out"))
        self.assertFalse(os.path.exists(os.path.join(cel, "make_order__old")))
        self.assertEqual(man["wiadomosci"][0]["template"], "old")

    def test_odmawia_nadpisania_edytowanego_eksportu(self):
        m = fixtures.manifest()
        z = _zip_z(self.k, m)
        cel = os.path.join(self.k, "out")
        eksport.rozpakuj([z], cel)
        with self.assertRaises(eksport.BladEksportu):
            eksport.rozpakuj([z], cel)
        eksport.rozpakuj([z], cel, nadpisz=True)   # świadome nadpisanie działa

    def test_brakujacy_plik_i_zly_icf_do_bledow(self):
        m = fixtures.manifest(jezyki=("pol", "eng"))
        w = m["wiadomosci"][0]
        cel, man = eksport.rozpakuj([_zip_z(self.k, m, pliki={w["pliki"]["pol"]: "<html>Logowanie</html>"})],
                                    os.path.join(self.k, "out"))
        bledy = man["wiadomosci"][0]["bledy"]
        self.assertEqual(len(bledy), 2)
        self.assertTrue(any(b.startswith("pol:") for b in bledy))
        self.assertTrue(any(b.startswith("eng:") for b in bledy))

    def test_zip_bez_manifestu(self):
        import zipfile
        z = os.path.join(self.k, "x.zip")
        with zipfile.ZipFile(z, "w") as a:
            a.writestr("cos.txt", "x")
        with self.assertRaises(eksport.BladEksportu):
            eksport.rozpakuj([z], os.path.join(self.k, "out"))

    def test_scalanie_czesciowych(self):
        w1 = fixtures.wiadomosc(template="a")
        w2 = fixtures.wiadomosc(template="b")
        m1 = fixtures.manifest(wiadomosci=[w1])
        m1["niekompletny"], m1["pozostale"] = True, ["b"]
        m2 = fixtures.manifest(wiadomosci=[w2])
        m2["data_eksportu"] = "2026-10-13T14:00:00"
        cel, man = eksport.rozpakuj([_zip_z(self.k, m1, "1.zip"), _zip_z(self.k, m2, "2.zip")], os.path.join(self.k, "o"))
        self.assertEqual([w["template"] for w in man["wiadomosci"]], ["a", "b"])
        self.assertFalse(man["niekompletny"])
        self.assertEqual(man["data_eksportu"], "2026-10-13T13:05:09")

    def test_scalanie_roznych_sklepow(self):
        m1 = fixtures.manifest()
        m2 = fixtures.manifest()
        m2["shop_id"] = 2
        with self.assertRaises(eksport.BladEksportu):
            eksport.rozpakuj([_zip_z(self.k, m1, "1.zip"), _zip_z(self.k, m2, "2.zip")], os.path.join(self.k, "o"))

    def test_katalog_domyslny(self):
        self.assertEqual(eksport.katalog_eksportu(fixtures.manifest()),
                         os.path.join(wspolne.FOLDER_TRESCI, "zooart6_shop1", "2026-10-13_130509"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Uruchom — FAIL**

Run: `python -m unittest testy.test_eksport -v`
Expected: ERROR `cannot import name 'eksport'`.

- [ ] **Step 3: Utwórz `wt/eksport.py`**

```python
"""Eksport z panelu (ZIP: manifest.json + ICF) -> folder per wiadomość z plikami do edycji."""

import json
import os
import zipfile
from typing import Dict, List, Optional, Tuple

from . import icf, wspolne


class BladEksportu(Exception):
    """ZIP nie jest eksportem narzędzia albo operacja zagraża plikom użytkownika."""


def wczytaj_zip(sciezka: str) -> Tuple[Dict, Dict[str, str]]:
    nazwa = os.path.basename(sciezka)
    try:
        with zipfile.ZipFile(sciezka) as archiwum:
            try:
                manifest = json.loads(archiwum.read("manifest.json").decode("utf-8"))
            except KeyError:
                raise BladEksportu("%s: brak manifest.json - to nie jest eksport narzędzia" % nazwa)
            pliki = {n: archiwum.read(n).decode("utf-8") for n in archiwum.namelist() if n.endswith(".icf")}
    except zipfile.BadZipFile:
        raise BladEksportu("%s: plik nie jest poprawnym archiwum ZIP (niedokończone pobieranie?)" % nazwa)
    if manifest.get("wersja") != 1:
        raise BladEksportu("%s: nieobsługiwana wersja manifestu: %r" % (nazwa, manifest.get("wersja")))
    return manifest, pliki


def scal(czesci: List[Tuple[Dict, Dict[str, str]]]) -> Tuple[Dict, Dict[str, str]]:
    """Łączy eksporty częściowe jednego sklepu; późniejsza część wygrywa dla tej samej wiadomości."""
    pierwszy = czesci[0][0]
    for manifest, _ in czesci[1:]:
        if (manifest["domena"], manifest["shop_id"]) != (pierwszy["domena"], pierwszy["shop_id"]):
            raise BladEksportu("Eksporty z różnych sklepów (%s/%s i %s/%s) - nie scalam"
                               % (pierwszy["domena"], pierwszy["shop_id"], manifest["domena"], manifest["shop_id"]))
    wiadomosci, pliki, jezyki = {}, {}, []
    for manifest, pliki_czesci in czesci:
        for w in manifest["wiadomosci"]:
            wiadomosci[w["template"]] = w
        pliki.update(pliki_czesci)
        for j in manifest["jezyki"]:
            if j not in jezyki:
                jezyki.append(j)
    wynik = dict(czesci[-1][0])
    wynik["wiadomosci"] = list(wiadomosci.values())
    wynik["jezyki"] = jezyki
    wynik["pozostale"] = [t for t in czesci[-1][0].get("pozostale", []) if t not in wiadomosci]
    wynik["niekompletny"] = bool(wynik["pozostale"])
    wynik["data_eksportu"] = pierwszy["data_eksportu"]
    return wynik, pliki


def katalog_eksportu(manifest: Dict) -> str:
    return os.path.join(wspolne.FOLDER_TRESCI, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                        wspolne.znacznik_daty(manifest["data_eksportu"]))


def nazwa_folderu(wiadomosc: Dict) -> str:
    return wiadomosc["grupa"] + "__" + wiadomosc["template"]


def folder_wiadomosci(katalog: str, wiadomosc: Dict) -> str:
    return os.path.join(katalog, nazwa_folderu(wiadomosc))


def wczytaj_eksport(katalog: str) -> Dict:
    return wspolne.czytaj_json(os.path.join(katalog, "manifest.json"))


def _zapisz_wiadomosc(cel: str, manifest: Dict, w: Dict, pliki: Dict[str, str]) -> None:
    folder = folder_wiadomosci(cel, w)
    tytuly = {}
    for jezyk, sciezka in w["pliki"].items():
        if sciezka not in pliki:
            w["bledy"].append("%s: brak pliku %s w ZIP" % (jezyk, sciezka))
            continue
        xml = pliki[sciezka]
        try:
            dane = icf.wczytaj(xml)
        except icf.BladIcf as blad:
            w["bledy"].append("%s: %s" % (jezyk, blad))
            continue
        wspolne.zapisz_tekst(os.path.join(folder, jezyk + ".icf"), xml)
        if "mail" in dane["kanaly"]:
            wspolne.zapisz_tekst(os.path.join(folder, jezyk + "_mail.html"), dane["kanaly"]["mail"].get("text_main_0", ""))
            tytuly[jezyk] = dane["kanaly"]["mail"].get("title", "")
        if "sms" in dane["kanaly"]:
            wspolne.zapisz_tekst(os.path.join(folder, jezyk + "_sms.txt"), dane["kanaly"]["sms"].get("text_main_0", ""))
    meta = {k: w.get(k) for k in ("nazwa", "grupa", "grupa_nazwa", "sekcja", "template", "ostatnia_edycja")}
    meta.update({"domena": manifest["domena"], "shop_id": manifest["shop_id"],
                 "data_eksportu": manifest["data_eksportu"], "tytuly": tytuly})
    wspolne.zapisz_json(os.path.join(folder, "meta.json"), meta)


def rozpakuj(sciezki_zip: List[str], katalog_docelowy: Optional[str] = None,
             nadpisz: bool = False) -> Tuple[str, Dict]:
    czesci = [wczytaj_zip(s) for s in sciezki_zip]
    manifest, pliki = scal(czesci) if len(czesci) > 1 else czesci[0]
    cel = katalog_docelowy or katalog_eksportu(manifest)
    if os.path.exists(os.path.join(cel, "manifest.json")) and not nadpisz:
        raise BladEksportu("Folder %s zawiera już rozpakowany eksport (być może z Twoimi zmianami). "
                           "Nie nadpisuję." % cel)
    for w in manifest["wiadomosci"]:
        if w.get("pliki"):
            _zapisz_wiadomosc(cel, manifest, w, pliki)
    wspolne.zapisz_json(os.path.join(cel, "manifest.json"), manifest)
    return cel, manifest
```

- [ ] **Step 4: Uruchom — PASS**

Run: `python -m unittest testy.test_eksport -v`
Expected: `OK` (10 testów).

- [ ] **Step 5: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wt/eksport.py" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_eksport.py"
git commit -m "Wiadomości transakcyjne: rozpakowanie eksportu do folderów wiadomości"
```

---

### Task 3: Konfiguracja wysyłki — CSV, różnice, plan zmian

**Files:**
- Create: `wt/konfiguracja.py`
- Test: `testy/test_konfiguracja.py`

**Interfaces:**
- Consumes: `wt.eksport.folder_wiadomosci`, `wt.icf.odcisk`, `wt.wspolne.*`.
- Produces: `wt.konfiguracja`: `TAK="tak"`, `NIE="nie"`, `ND="nie dotyczy"`; `BladKonfiguracji(Exception)`; `kolumny(manifest) -> list[str]`; `wiersze(manifest) -> Iterator[dict]`; `sciezka_csv(manifest) -> str`; `zapisz_csv(manifest, sciezka) -> None`; `roznice(manifest, sciezka_csv) -> (zmiany: list[dict], bledy: list[str])` — zmiana: `{"template", "nazwa", "grupa", "mail": {jezyk: "y"|"n"}, "sms": "y"|"n"|None, "reset": bool}`; `zapisz_plan(manifest, katalog_eksportu, zmiany, katalog_planu) -> str` (ścieżka `plan_konfiguracji.json`; kopie ICF w `katalog_planu/kopie/<template>__<jezyk>.icf`, bez kopii dla `reset=True`).

Format `plan_konfiguracji.json`:

```json
{"wersja": 1, "rodzaj": "konfiguracja", "domena": "...", "shop_id": 1, "data_eksportu": "...",
 "zmiany": [{"template": "order_confirmation", "nazwa": "...", "grupa": "make_order",
             "mail": {"eng": "n"}, "sms": null, "reset": false,
             "oczekiwane": {"mail": {"pol": "y", "eng": "n", "ukr": "y"}, "sms": "n"},
             "kopie": {"pol": {"plik": "order_confirmation__pol.icf", "odcisk": "<sha256>"}}}]}
```

- [ ] **Step 1: Napisz testy `testy/test_konfiguracja.py`**

```python
import csv
import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, icf, konfiguracja as k, wspolne


def _manifest():
    return fixtures.manifest(wiadomosci=[
        fixtures.wiadomosc(template="order_confirmation", nazwa="Potwierdzenie", jezyki=("pol", "eng")),
        fixtures.wiadomosc(template="panel_only", nazwa="Z panelu", jezyki=("pol", "eng"), sms=None,
                           stan_listy={"sms": "nie dotyczy", "mail": "tak", "webpush": "nie", "braki": None}),
        fixtures.wiadomosc(template="old", nazwa="Wycofana", edytowalna=False),
    ], jezyki=("pol", "eng"))


class TestCsv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "konf.csv")
        self.m = _manifest()
        k.zapisz_csv(self.m, self.csv)

    def tearDown(self):
        self.tmp.cleanup()

    def _wiersze(self):
        with open(self.csv, encoding="utf-8-sig", newline="") as p:
            return list(csv.DictReader(p, delimiter=";"))

    def _zapisz(self, wiersze, kodowanie="utf-8-sig", sep=";"):
        with open(self.csv, "w", encoding=kodowanie, newline="") as p:
            w = csv.DictWriter(p, fieldnames=list(wiersze[0].keys()), delimiter=sep)
            w.writeheader()
            w.writerows(wiersze)

    def test_zawartosc_csv(self):
        wiersze = self._wiersze()
        self.assertEqual(list(wiersze[0].keys()), ["grupa", "template", "nazwa", "mail_pol", "mail_eng", "sms", "reset_domyslna"])
        self.assertEqual([w["template"] for w in wiersze], ["order_confirmation", "panel_only"])   # bez wycofanej
        self.assertEqual(wiersze[0]["mail_eng"], "tak")
        self.assertEqual(wiersze[0]["sms"], "nie")
        self.assertEqual(wiersze[1]["sms"], "nie dotyczy")
        with open(self.csv, "rb") as p:
            self.assertTrue(p.read().startswith(b"\xef\xbb\xbf"))   # BOM dla Excela

    def test_brak_zmian(self):
        self.assertEqual(k.roznice(self.m, self.csv), ([], []))

    def test_zmiana_maila_i_sms(self):
        w = self._wiersze()
        w[0]["mail_eng"], w[0]["sms"] = "NIE ", "tak"
        self._zapisz(w)
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(bledy, [])
        self.assertEqual(zmiany, [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "grupa": "make_order",
                                   "mail": {"eng": "n"}, "sms": "y", "reset": False}])

    def test_zmiana_nie_dotyczy_to_blad(self):
        w = self._wiersze()
        w[1]["sms"] = "tak"
        self._zapisz(w)
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(zmiany, [])
        self.assertEqual(len(bledy), 1)
        self.assertIn("wiersz 3", bledy[0])
        self.assertIn("sms", bledy[0])

    def test_pusta_lub_zla_wartosc(self):
        w = self._wiersze()
        w[0]["mail_pol"], w[0]["mail_eng"] = "", "może"
        self._zapisz(w)
        zmiany, bledy = k.roznice(self.m, self.csv)
        self.assertEqual(zmiany, [])
        self.assertEqual(len(bledy), 2)
        self.assertTrue(all("dozwolone: tak / nie" in b for b in bledy))

    def test_duplikat_wiersza(self):
        w = self._wiersze()
        self._zapisz(w + [dict(w[0])])
        _, bledy = k.roznice(self.m, self.csv)
        self.assertTrue(any("powtórzona" in b for b in bledy))

    def test_nieznana_wiadomosc(self):
        w = self._wiersze()
        w[0]["template"] = "old"
        self._zapisz(w)
        _, bledy = k.roznice(self.m, self.csv)
        self.assertTrue(any("'old'" in b for b in bledy))

    def test_csv_z_przecinkiem_i_bez_bom(self):
        self._zapisz(self._wiersze(), kodowanie="utf-8", sep=",")
        with self.assertRaises(k.BladKonfiguracji) as kontekst:
            k.roznice(self.m, self.csv)
        self.assertIn("średnik", str(kontekst.exception))

    def test_reset(self):
        w = self._wiersze()
        w[0]["reset_domyslna"] = "tak"
        self._zapisz(w)
        zmiany, _ = k.roznice(self.m, self.csv)
        self.assertTrue(zmiany[0]["reset"])


class TestPlan(unittest.TestCase):
    def test_plan_z_kopiami(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = _manifest()
            w = m["wiadomosci"][0]
            katalog = os.path.join(tmp, "eksport")
            for j in ("pol", "eng"):
                wspolne.zapisz_tekst(os.path.join(eksport.folder_wiadomosci(katalog, w), j + ".icf"),
                                     fixtures.icf_xml(jezyk=j))
            zmiany = [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "grupa": "make_order",
                       "mail": {"eng": "n"}, "sms": None, "reset": False}]
            sciezka = k.zapisz_plan(m, katalog, zmiany, os.path.join(tmp, "plan"))
            plan = wspolne.czytaj_json(sciezka)
            z = plan["zmiany"][0]
            self.assertEqual(plan["rodzaj"], "konfiguracja")
            self.assertEqual(z["oczekiwane"], {"mail": {"pol": "y", "eng": "n"}, "sms": "n"})
            self.assertEqual(z["kopie"]["eng"]["plik"], "order_confirmation__eng.icf")
            kopia = os.path.join(tmp, "plan", "kopie", "order_confirmation__eng.icf")
            self.assertEqual(z["kopie"]["eng"]["odcisk"], icf.odcisk(wspolne.czytaj_tekst(kopia)))

    def test_reset_bez_kopii(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = _manifest()
            zmiany = [{"template": "order_confirmation", "nazwa": "P", "grupa": "make_order",
                       "mail": {}, "sms": None, "reset": True}]
            plan = wspolne.czytaj_json(k.zapisz_plan(m, os.path.join(tmp, "e"), zmiany, os.path.join(tmp, "p")))
            self.assertEqual(plan["zmiany"][0]["kopie"], {})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Uruchom — FAIL**

Run: `python -m unittest testy.test_konfiguracja -v`
Expected: ERROR `cannot import name 'konfiguracja'`.

- [ ] **Step 3: Utwórz `wt/konfiguracja.py`**

```python
"""Edycja działania: CSV z bieżącym stanem wysyłki, porównanie z poprawionym CSV, plan zmian dla panelu."""

import csv
import io
import os
import shutil
from typing import Dict, Iterator, List, Tuple

from . import eksport, icf, wspolne

TAK, NIE, ND = "tak", "nie", "nie dotyczy"


class BladKonfiguracji(Exception):
    """CSV nie da się odczytać jako plik konfiguracji tego eksportu."""


def kolumny(manifest: Dict) -> List[str]:
    return ["grupa", "template", "nazwa"] + ["mail_" + j for j in manifest["jezyki"]] + ["sms", "reset_domyslna"]


def _tekst(flaga: str) -> str:
    return TAK if flaga == "y" else NIE


def wiersze(manifest: Dict) -> Iterator[Dict[str, str]]:
    for w in manifest["wiadomosci"]:
        if not w["edytowalna"] or not w.get("formularz"):
            continue
        formularz, stan = w["formularz"], w["stan_listy"]
        wiersz = {"grupa": w["grupa"], "template": w["template"], "nazwa": w["nazwa"]}
        for j in manifest["jezyki"]:
            if stan.get("mail") == ND or j not in formularz["mail"]:
                wiersz["mail_" + j] = ND
            else:
                wiersz["mail_" + j] = _tekst(formularz["mail"][j])
        wiersz["sms"] = ND if (stan.get("sms") == ND or formularz.get("sms") is None) else _tekst(formularz["sms"])
        wiersz["reset_domyslna"] = NIE
        yield wiersz


def sciezka_csv(manifest: Dict) -> str:
    return os.path.join(wspolne.FOLDER_EDYCJA, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                        "konfiguracja_" + wspolne.znacznik_daty(manifest["data_eksportu"]) + ".csv")


def zapisz_csv(manifest: Dict, sciezka: str) -> None:
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.DictWriter(plik, fieldnames=kolumny(manifest), delimiter=";")
        pisarz.writeheader()
        for wiersz in wiersze(manifest):
            pisarz.writerow(wiersz)


def _wczytaj_csv(manifest: Dict, sciezka: str) -> csv.DictReader:
    with open(sciezka, encoding="utf-8-sig", newline="") as plik:
        tresc = plik.read()
    naglowek = tresc.split("\n", 1)[0]
    if ";" not in naglowek:
        raise BladKonfiguracji("Nagłówek CSV nie zawiera średnika - zapisz plik w Excelu jako "
                               "'CSV UTF-8 (rozdzielany przecinkami)' z separatorem średnik albo popraw separator.")
    czytnik = csv.DictReader(io.StringIO(tresc), delimiter=";")
    brak = [c for c in kolumny(manifest) if c not in (czytnik.fieldnames or [])]
    if brak:
        raise BladKonfiguracji("Brak kolumn w CSV: " + ", ".join(brak))
    return czytnik


def roznice(manifest: Dict, sciezka: str) -> Tuple[List[Dict], List[str]]:
    stan = {w["template"]: w for w in wiersze(manifest)}
    zmiany, bledy, widziane = [], [], set()
    for nr, wiersz in enumerate(_wczytaj_csv(manifest, sciezka), start=2):
        template = (wiersz.get("template") or "").strip()
        if not template:
            continue
        if template not in stan:
            bledy.append("wiersz %d: nieznana lub nieedytowalna wiadomość '%s'" % (nr, template))
            continue
        if template in widziane:
            bledy.append("wiersz %d: wiadomość '%s' powtórzona - liczy się pierwsze wystąpienie" % (nr, template))
            continue
        widziane.add(template)
        przed = stan[template]
        zmiana = {"template": template, "nazwa": przed["nazwa"], "grupa": przed["grupa"],
                  "mail": {}, "sms": None, "reset": False}
        for kolumna in kolumny(manifest)[3:]:
            surowa = wiersz.get(kolumna) or ""
            nowa, stara = surowa.strip().lower(), przed[kolumna]
            if kolumna == "reset_domyslna":
                if nowa not in (TAK, NIE, ""):
                    bledy.append("wiersz %d (%s): reset_domyslna = '%s' - dozwolone: tak / nie" % (nr, template, surowa))
                zmiana["reset"] = nowa == TAK
                continue
            if nowa == stara:
                continue
            if stara == ND:
                bledy.append("wiersz %d (%s): %s = 'nie dotyczy' w panelu - nie da się zmienić" % (nr, template, kolumna))
                continue
            if nowa not in (TAK, NIE):
                bledy.append("wiersz %d (%s): %s = '%s' - dozwolone: tak / nie" % (nr, template, kolumna, surowa))
                continue
            flaga = "y" if nowa == TAK else "n"
            if kolumna == "sms":
                zmiana["sms"] = flaga
            else:
                zmiana["mail"][kolumna[len("mail_"):]] = flaga
        if zmiana["mail"] or zmiana["sms"] is not None or zmiana["reset"]:
            zmiany.append(zmiana)
    return zmiany, bledy


def zapisz_plan(manifest: Dict, katalog_eksportu: str, zmiany: List[Dict], katalog_planu: str) -> str:
    po_template = {w["template"]: w for w in manifest["wiadomosci"]}
    plan = {"wersja": 1, "rodzaj": "konfiguracja", "domena": manifest["domena"], "shop_id": manifest["shop_id"],
            "data_eksportu": manifest["data_eksportu"], "zmiany": []}
    for zmiana in zmiany:
        w = po_template[zmiana["template"]]
        oczekiwane = {"mail": dict(w["formularz"]["mail"]), "sms": w["formularz"].get("sms")}
        oczekiwane["mail"].update(zmiana["mail"])
        if zmiana["sms"] is not None:
            oczekiwane["sms"] = zmiana["sms"]
        kopie = {}
        if not zmiana["reset"]:
            for jezyk in w["pliki"]:
                zrodlo = os.path.join(eksport.folder_wiadomosci(katalog_eksportu, w), jezyk + ".icf")
                if not os.path.exists(zrodlo):
                    continue
                nazwa = "%s__%s.icf" % (zmiana["template"], jezyk)
                os.makedirs(os.path.join(katalog_planu, "kopie"), exist_ok=True)
                shutil.copyfile(zrodlo, os.path.join(katalog_planu, "kopie", nazwa))
                kopie[jezyk] = {"plik": nazwa, "odcisk": icf.odcisk(wspolne.czytaj_tekst(zrodlo))}
        pozycja = dict(zmiana)
        pozycja.update({"oczekiwane": oczekiwane, "kopie": kopie})
        plan["zmiany"].append(pozycja)
    sciezka = os.path.join(katalog_planu, "plan_konfiguracji.json")
    wspolne.zapisz_json(sciezka, plan)
    return sciezka
```

- [ ] **Step 4: Uruchom — PASS**

Run: `python -m unittest testy.test_konfiguracja -v`
Expected: `OK` (11 testów).

- [ ] **Step 5: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wt/konfiguracja.py" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_konfiguracja.py"
git commit -m "Wiadomości transakcyjne: CSV konfiguracji wysyłki i plan zmian"
```

---

### Task 4: Treści — wykrycie zmian w plikach i złożenie ICF do importu

**Files:**
- Create: `wt/tresci.py`
- Test: `testy/test_tresci.py`

**Interfaces:**
- Consumes: `wt.eksport.folder_wiadomosci`, `wt.icf.wczytaj/podmien/odcisk`, `wt.wspolne.*`.
- Produces: `wt.tresci`: `bez_cr(s) -> str`; `roznice_tresci(katalog_eksportu, manifest) -> list[dict]` — pozycja `{"template", "nazwa", "grupa", "jezyk", "icf": sciezka, "pola": {"mail.text_main_0"|"mail.title"|"sms.text_main_0": nowa}, "przed": {to samo: stara}}`; `zloz(manifest, roznice, katalog_planu) -> str` (ścieżka `plan_importu.json`, pliki `katalog_planu/<template>__<jezyk>.icf`).

Format `plan_importu.json`:

```json
{"wersja": 1, "rodzaj": "import", "domena": "...", "shop_id": 1, "data_eksportu": "...",
 "pozycje": [{"template": "...", "nazwa": "...", "jezyk": "eng", "plik": "order_confirmation__eng.icf",
              "odcisk_oryginalu": "<sha256>", "oczekiwane": {"mail.title": "..."}, "przed": {"mail.title": "..."}}],
 "oczekiwane_flagi": {"order_confirmation": {"mail": {"pol": "y", "eng": "y"}, "sms": "n"}}}
```

- [ ] **Step 1: Napisz testy `testy/test_tresci.py`**

```python
import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, icf, tresci, wspolne


class TestTresci(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.m = fixtures.manifest(jezyki=("pol", "eng"))
        pliki = {}
        for j in ("pol", "eng"):
            pliki[self.m["wiadomosci"][0]["pliki"][j]] = fixtures.icf_xml(jezyk=j, html="<p>A</p>\n<p>B</p>")
        zip_ = os.path.join(self.tmp.name, "e.zip")
        fixtures.zbuduj_zip(zip_, self.m, pliki)
        self.kat, self.m = eksport.rozpakuj([zip_], os.path.join(self.tmp.name, "e"))
        self.folder = os.path.join(self.kat, "make_order__order_confirmation")

    def tearDown(self):
        self.tmp.cleanup()

    def test_bez_zmian(self):
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_crlf_to_nie_zmiana(self):
        sciezka = os.path.join(self.folder, "eng_mail.html")
        wspolne.zapisz_tekst(sciezka, wspolne.czytaj_tekst(sciezka).replace("\n", "\r\n"))
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_zmiana_tresci_tytulu_i_sms(self):
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_mail.html"), "<p>Thank you</p>\r\n")
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_sms.txt"), "Order [iai:order_id] received")
        meta = wspolne.czytaj_json(os.path.join(self.folder, "meta.json"))
        meta["tytuly"]["eng"] = "Your order [iai:order_sn]"
        wspolne.zapisz_json(os.path.join(self.folder, "meta.json"), meta)
        wynik = tresci.roznice_tresci(self.kat, self.m)
        self.assertEqual(len(wynik), 1)
        self.assertEqual(wynik[0]["jezyk"], "eng")
        self.assertEqual(wynik[0]["pola"], {"mail.text_main_0": "<p>Thank you</p>\n",
                                            "sms.text_main_0": "Order [iai:order_id] received",
                                            "mail.title": "Your order [iai:order_sn]"})
        self.assertEqual(wynik[0]["przed"]["mail.text_main_0"], "<p>A</p>\n<p>B</p>")

    def test_brak_pliku_jezyka_nie_rusza(self):
        os.remove(os.path.join(self.folder, "pol_mail.html"))
        os.remove(os.path.join(self.folder, "pol_sms.txt"))
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_kanal_nie_dotyczy_pominiety(self):
        self.m["wiadomosci"][0]["stan_listy"]["sms"] = "nie dotyczy"
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_sms.txt"), "zmiana")
        self.assertEqual(tresci.roznice_tresci(self.kat, self.m), [])

    def test_zloz(self):
        wspolne.zapisz_tekst(os.path.join(self.folder, "eng_mail.html"), "<p>Nowa</p>")
        roznice = tresci.roznice_tresci(self.kat, self.m)
        plan_dir = os.path.join(self.tmp.name, "plan")
        plan = wspolne.czytaj_json(tresci.zloz(self.m, roznice, plan_dir))
        poz = plan["pozycje"][0]
        self.assertEqual(plan["rodzaj"], "import")
        self.assertEqual(poz["plik"], "order_confirmation__eng.icf")
        nowy = wspolne.czytaj_tekst(os.path.join(plan_dir, poz["plik"]))
        self.assertEqual(icf.wczytaj(nowy)["kanaly"]["mail"]["text_main_0"], "<p>Nowa</p>")
        self.assertEqual(icf.wczytaj(nowy)["kanaly"]["mail"]["active"], "y")   # flaga bez zmian
        oryginal = wspolne.czytaj_tekst(os.path.join(self.folder, "eng.icf"))
        self.assertEqual(poz["odcisk_oryginalu"], icf.odcisk(oryginal))
        self.assertEqual(plan["oczekiwane_flagi"]["order_confirmation"], {"mail": {"pol": "y", "eng": "y"}, "sms": "n"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Uruchom — FAIL**

Run: `python -m unittest testy.test_tresci -v`
Expected: ERROR `cannot import name 'tresci'`.

- [ ] **Step 3: Utwórz `wt/tresci.py`**

```python
"""Eksport i Import Treści: które pliki użytkownik zmienił i złożenie z nich ICF do importu."""

import os
from typing import Dict, List

from . import eksport, icf, wspolne

ND = "nie dotyczy"


def bez_cr(tekst: str) -> str:
    return tekst.replace("\r\n", "\n")


def _jak_oryginal(nowa: str, stara: str) -> str:
    """Zachowuje styl końców linii z panelu - edytor użytkownika mógł zamienić \\n na \\r\\n."""
    return nowa if "\r\n" in stara else bez_cr(nowa)


def roznice_tresci(katalog_eksportu: str, manifest: Dict) -> List[Dict]:
    wynik = []
    for w in manifest["wiadomosci"]:
        if not w["edytowalna"] or not w.get("pliki"):
            continue
        folder = eksport.folder_wiadomosci(katalog_eksportu, w)
        sciezka_meta = os.path.join(folder, "meta.json")
        tytuly = wspolne.czytaj_json(sciezka_meta).get("tytuly", {}) if os.path.exists(sciezka_meta) else {}
        for jezyk in w["pliki"]:
            sciezka_icf = os.path.join(folder, jezyk + ".icf")
            if not os.path.exists(sciezka_icf):
                continue
            dane = icf.wczytaj(wspolne.czytaj_tekst(sciezka_icf))
            pola, przed = {}, {}
            kandydaci = (("mail", "text_main_0", jezyk + "_mail.html"), ("sms", "text_main_0", jezyk + "_sms.txt"))
            for kanal, pole, nazwa_pliku in kandydaci:
                plik = os.path.join(folder, nazwa_pliku)
                if kanal not in dane["kanaly"] or w["stan_listy"].get(kanal) == ND or not os.path.exists(plik):
                    continue
                nowa, stara = wspolne.czytaj_tekst(plik), dane["kanaly"][kanal].get(pole, "")
                if bez_cr(nowa) != bez_cr(stara):
                    pola[kanal + "." + pole] = _jak_oryginal(nowa, stara)
                    przed[kanal + "." + pole] = stara
            if "mail" in dane["kanaly"] and w["stan_listy"].get("mail") != ND and jezyk in tytuly:
                stary_tytul = dane["kanaly"]["mail"].get("title", "")
                if tytuly[jezyk] != stary_tytul:
                    pola["mail.title"] = tytuly[jezyk]
                    przed["mail.title"] = stary_tytul
            if pola:
                wynik.append({"template": w["template"], "nazwa": w["nazwa"], "grupa": w["grupa"], "jezyk": jezyk,
                              "icf": sciezka_icf, "pola": pola, "przed": przed})
    return wynik


def zloz(manifest: Dict, roznice: List[Dict], katalog_planu: str) -> str:
    po_template = {w["template"]: w for w in manifest["wiadomosci"]}
    plan = {"wersja": 1, "rodzaj": "import", "domena": manifest["domena"], "shop_id": manifest["shop_id"],
            "data_eksportu": manifest["data_eksportu"], "pozycje": [], "oczekiwane_flagi": {}}
    for r in roznice:
        oryginal = wspolne.czytaj_tekst(r["icf"])
        nowy = oryginal
        for klucz, wartosc in r["pola"].items():
            kanal, pole = klucz.split(".", 1)
            nowy = icf.podmien(nowy, kanal, pole, wartosc)
        nazwa = "%s__%s.icf" % (r["template"], r["jezyk"])
        wspolne.zapisz_tekst(os.path.join(katalog_planu, nazwa), nowy)
        plan["pozycje"].append({"template": r["template"], "nazwa": r["nazwa"], "jezyk": r["jezyk"], "plik": nazwa,
                                "odcisk_oryginalu": icf.odcisk(oryginal), "oczekiwane": r["pola"], "przed": r["przed"]})
        formularz = po_template[r["template"]]["formularz"]
        plan["oczekiwane_flagi"][r["template"]] = {"mail": dict(formularz["mail"]), "sms": formularz.get("sms")}
    sciezka = os.path.join(katalog_planu, "plan_importu.json")
    wspolne.zapisz_json(sciezka, plan)
    return sciezka
```

- [ ] **Step 4: Uruchom — PASS**

Run: `python -m unittest testy.test_tresci -v`
Expected: `OK` (6 testów).

- [ ] **Step 5: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wt/tresci.py" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_tresci.py"
git commit -m "Wiadomości transakcyjne: wykrycie zmian treści i złożenie ICF do importu"
```

---

### Task 5: Raport Status z kontrolą jakości

**Files:**
- Create: `wt/status.py`
- Test: `testy/test_status.py`

**Interfaces:**
- Consumes: `wt.eksport.folder_wiadomosci`, `wt.icf.wczytaj/wartosc`, `wt.wspolne.*`.
- Produces: `wt.status`: `zmienne(tekst) -> set[str]`; `dlugosc_sms(tekst, only_ascii) -> (dlugosc: int, limit: int)`; `kontrola(manifest, katalog) -> list[dict]` (`{"template", "nazwa", "jezyk", "rodzaj": "kopia"|"zmienne"|"pusta"|"sms", "opis"}`); `raport(manifest, katalog) -> str` (Markdown); `sciezka_raportu(manifest) -> str`; `zapisz_raport(manifest, katalog) -> str`.

- [ ] **Step 1: Napisz testy `testy/test_status.py`**

```python
import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, status


def _eksport(tmp, icf_per_jezyk, wiadomosc=None, jezyki=("pol", "eng", "ukr")):
    w = wiadomosc or fixtures.wiadomosc(jezyki=jezyki)
    m = fixtures.manifest(wiadomosci=[w, fixtures.wiadomosc(template="old", edytowalna=False)], jezyki=jezyki)
    pliki = {w["pliki"][j]: xml for j, xml in icf_per_jezyk.items()}
    zip_ = os.path.join(tmp, "e.zip")
    fixtures.zbuduj_zip(zip_, m, pliki)
    return eksport.rozpakuj([zip_], os.path.join(tmp, "e"))


class TestFunkcje(unittest.TestCase):
    def test_zmienne(self):
        self.assertEqual(status.zmienne("Nr [iai:order_sn] [iai:if_prepaid-begin]x[iai:if_prepaid-end]"),
                         {"[iai:order_sn]", "[iai:if_prepaid-begin]", "[iai:if_prepaid-end]"})

    def test_dlugosc_sms(self):
        self.assertEqual(status.dlugosc_sms("a" * 10, "n"), (10, 160))
        self.assertEqual(status.dlugosc_sms("zażółć", "n"), (6, 70))
        self.assertEqual(status.dlugosc_sms("zażółć łódź", "y"), (11, 160))   # panel konwertuje do ASCII


class TestKontrola(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _problemy(self, icf_per_jezyk, **kw):
        katalog, m = _eksport(self.tmp.name, icf_per_jezyk, **kw)
        return status.kontrola(m, katalog)

    def test_kopia_tytulu_z_pol(self):
        p = self._problemy({
            "pol": fixtures.icf_xml(jezyk="pol"),
            "eng": fixtures.icf_xml(jezyk="eng", tytul="Order [iai:order_sn]", html="<p>Thanks [iai:order_sn]</p>",
                                    sms="Order [iai:order_id] [iai:shop_name]"),
            "ukr": fixtures.icf_xml(jezyk="ukr", html="<p>Дякуємо [iai:order_sn]</p>", sms="Замовлення [iai:order_id] [iai:shop_name]"),
        })
        kopie = [x for x in p if x["rodzaj"] == "kopia"]
        self.assertEqual(len(kopie), 1)
        self.assertEqual(kopie[0]["jezyk"], "ukr")
        self.assertIn("tytuł maila", kopie[0]["opis"])
        self.assertIn("pol", kopie[0]["opis"])

    def test_pol_identyczny_z_eng_zglaszany_raz_przy_eng(self):
        xml = fixtures.icf_xml()
        p = self._problemy({"pol": xml, "eng": xml.replace('value="pol"', 'value="eng"')}, jezyki=("pol", "eng"),
                           wiadomosc=fixtures.wiadomosc(jezyki=("pol", "eng")))
        self.assertEqual({x["jezyk"] for x in p if x["rodzaj"] == "kopia"}, {"eng"})

    def test_brakujaca_zmienna(self):
        p = self._problemy({"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Order",
                                                                              html="<p>x [iai:order_sn]</p>", sms="x [iai:order_id] [iai:shop_name]")},
                           jezyki=("pol", "eng"), wiadomosc=fixtures.wiadomosc(jezyki=("pol", "eng")))
        zm = [x for x in p if x["rodzaj"] == "zmienne"]
        self.assertEqual(len(zm), 1)
        self.assertIn("[iai:order_sn]", zm[0]["opis"])
        self.assertIn("tytuł", zm[0]["opis"])

    def test_pusta_tresc_przy_wlaczonej_wysylce(self):
        p = self._problemy({"pol": fixtures.icf_xml(html="")}, jezyki=("pol",), wiadomosc=fixtures.wiadomosc(jezyki=("pol",)))
        self.assertTrue(any(x["rodzaj"] == "pusta" and "treść maila" in x["opis"] for x in p))

    def test_dlugi_sms(self):
        w = fixtures.wiadomosc(jezyki=("pol",), sms="y")
        p = self._problemy({"pol": fixtures.icf_xml(sms="ą" * 80, only_ascii="n")}, jezyki=("pol",), wiadomosc=w)
        self.assertTrue(any(x["rodzaj"] == "sms" and "80 znaków > 70" in x["opis"] for x in p))


class TestRaport(unittest.TestCase):
    def test_raport(self):
        with tempfile.TemporaryDirectory() as tmp:
            katalog, m = _eksport(tmp, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng"),
                                        "ukr": fixtures.icf_xml(jezyk="ukr")})
            m["wiadomosci"][0]["nazwa"] = "Nazwa | z kreską"
            tekst = status.raport(m, katalog)
            self.assertIn("# Status wiadomości transakcyjnych — zooart6.yourtechnicaldomain.com, sklep 1", tekst)
            self.assertIn("| Wiadomości ogółem | 2 |", tekst)
            self.assertIn("| Wycofywane (tylko podgląd) | 1 |", tekst)
            self.assertIn("| Mail włączony — pol | 1 |", tekst)
            self.assertIn("Nazwa \\| z kreską", tekst)
            self.assertIn("2026-07-17 12:10:52 (Jan Testowy)", tekst)
            self.assertIn("## Kontrola jakości", tekst)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Uruchom — FAIL**

Run: `python -m unittest testy.test_status -v`
Expected: ERROR `cannot import name 'status'`.

- [ ] **Step 3: Utwórz `wt/status.py`**

```python
"""Raport Status: stan wysyłki, braki, ostatnia edycja i kontrola jakości treści."""

import os
import re
import unicodedata
from typing import Dict, List, Tuple

from . import eksport, icf, wspolne

WZOR_ZMIENNEJ = re.compile(r"\[iai:[^\]\s]+\]")
# Podstawowy alfabet GSM 03.38 - spoza niego SMS idzie w UCS-2 (70 znaków na segment).
GSM7 = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡"
           "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
POLA = (("mail", "title", "tytuł maila"), ("mail", "text_main_0", "treść maila"), ("sms", "text_main_0", "treść SMS"))
ETYKIETY = {"kopia": "Kopie tłumaczeń (treść identyczna z PL lub EN)", "zmienne": "Niezgodne zmienne [iai:…]",
            "pusta": "Pusta treść przy włączonej wysyłce", "sms": "SMS dłuższy niż jeden segment"}


def _norm(tekst) -> str:
    return re.sub(r"\s+", " ", tekst or "").strip()


def zmienne(tekst) -> set:
    return set(WZOR_ZMIENNEJ.findall(tekst or ""))


def _na_ascii(tekst: str) -> str:
    tekst = tekst.replace("ł", "l").replace("Ł", "L")
    return unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode("ascii")


def dlugosc_sms(tekst: str, only_ascii) -> Tuple[int, int]:
    tekst = _na_ascii(tekst) if only_ascii == "y" else tekst
    limit = 160 if all(znak in GSM7 for znak in tekst) else 70
    return len(tekst), limit


def _wzorce_kopii(jezyk: str) -> Tuple[str, ...]:
    if jezyk == "pol":
        return ()
    if jezyk == "eng":
        return ("pol",)
    return ("pol", "eng")


def kontrola(manifest: Dict, katalog: str) -> List[Dict]:
    problemy = []
    for w in manifest["wiadomosci"]:
        if not w["edytowalna"] or not w.get("pliki"):
            continue
        folder = eksport.folder_wiadomosci(katalog, w)
        tresci = {}
        for jezyk in w["pliki"]:
            sciezka = os.path.join(folder, jezyk + ".icf")
            if os.path.exists(sciezka):
                tresci[jezyk] = icf.wczytaj(wspolne.czytaj_tekst(sciezka))

        def dodaj(jezyk, rodzaj, opis):
            problemy.append({"template": w["template"], "nazwa": w["nazwa"], "jezyk": jezyk, "rodzaj": rodzaj, "opis": opis})

        wzorzec_zmiennych = "pol" if "pol" in tresci else (sorted(tresci)[0] if tresci else None)
        for jezyk, dane in tresci.items():
            for wzorzec in _wzorce_kopii(jezyk):
                if wzorzec not in tresci:
                    continue
                for kanal, pole, etykieta in POLA:
                    a = _norm(icf.wartosc(dane, kanal, pole))
                    if a and a == _norm(icf.wartosc(tresci[wzorzec], kanal, pole)):
                        dodaj(jezyk, "kopia", "%s identyczna z %s" % (etykieta, wzorzec))
            if jezyk != wzorzec_zmiennych:
                for kanal, pole, etykieta in POLA:
                    if kanal not in dane["kanaly"]:
                        continue
                    wzor = zmienne(icf.wartosc(tresci[wzorzec_zmiennych], kanal, pole))
                    jest = zmienne(icf.wartosc(dane, kanal, pole))
                    if wzor - jest:
                        dodaj(jezyk, "zmienne", "%s: brakuje %s (są w %s)" % (etykieta, ", ".join(sorted(wzor - jest)), wzorzec_zmiennych))
                    if jest - wzor:
                        dodaj(jezyk, "zmienne", "%s: nadmiarowe %s (nie ma ich w %s)" % (etykieta, ", ".join(sorted(jest - wzor)), wzorzec_zmiennych))
            formularz = w["formularz"] or {}
            if formularz.get("mail", {}).get(jezyk) == "y" and "mail" in dane["kanaly"]:
                for pole, etykieta in (("title", "tytuł maila"), ("text_main_0", "treść maila")):
                    if not _norm(icf.wartosc(dane, "mail", pole)):
                        dodaj(jezyk, "pusta", "mail włączony, %s pusta" % etykieta)
            if "sms" in dane["kanaly"]:
                tekst_sms = icf.wartosc(dane, "sms", "text_main_0") or ""
                if formularz.get("sms") == "y" and not _norm(tekst_sms):
                    dodaj(jezyk, "pusta", "SMS włączony, treść SMS pusta")
                if _norm(tekst_sms):
                    dlugosc, limit = dlugosc_sms(tekst_sms, icf.wartosc(dane, "sms", "only_ascii"))
                    if dlugosc > limit:
                        dodaj(jezyk, "sms", "%d znaków > %d (więcej niż 1 SMS; bez rozwinięcia zmiennych)" % (dlugosc, limit))
    return problemy


def _kom(tekst) -> str:
    return str(tekst if tekst is not None else "").replace("|", "\\|")


def _flaga(wartosc) -> str:
    return {"y": "tak", "n": "nie"}.get(wartosc, "n.d.")


def raport(manifest: Dict, katalog: str) -> str:
    jezyki = manifest["jezyki"]
    wszystkie = manifest["wiadomosci"]
    edytowalne = [w for w in wszystkie if w["edytowalna"] and w.get("formularz")]
    problemy = kontrola(manifest, katalog)
    linie = ["# Status wiadomości transakcyjnych — %s, sklep %s" % (manifest["domena"], manifest["shop_id"]), "",
             "Eksport: %s · Raport: %s" % (manifest["data_eksportu"], wspolne.teraz_iso()), ""]
    if manifest.get("niekompletny"):
        linie += ["> **Uwaga:** eksport niekompletny — brakuje %d wiadomości (sesja wygasła). "
                  "Uruchom eksport ponownie i rozpakuj obie części razem." % len(manifest.get("pozostale", [])), ""]
    linie += ["## Podsumowanie", "", "| | Liczba |", "| --- | --- |",
              "| Wiadomości ogółem | %d |" % len(wszystkie),
              "| Edytowalne | %d |" % len(edytowalne),
              "| Wycofywane (tylko podgląd) | %d |" % (len(wszystkie) - len([w for w in wszystkie if w["edytowalna"]]))]
    for j in jezyki:
        linie.append("| Mail włączony — %s | %d |" % (j, sum(1 for w in edytowalne if w["formularz"]["mail"].get(j) == "y")))
    linie.append("| SMS włączony | %d |" % sum(1 for w in edytowalne if w["formularz"].get("sms") == "y"))
    for j in jezyki:
        linie.append("| Web Push włączony — %s | %d |" % (j, sum(1 for w in edytowalne if (w["formularz"].get("webpush") or {}).get(j) == "y")))
    linie += ["| Z brakami szablonów | %d |" % sum(1 for w in wszystkie if w["stan_listy"].get("braki")),
              "| Problemy kontroli jakości | %d |" % len(problemy), "",
              "## Wiadomości", "",
              "| Grupa | Wiadomość | " + " | ".join("Mail " + j for j in jezyki) + " | SMS | Web Push | Braki | Ostatnia edycja |",
              "| --- | --- | " + " | ".join("---" for _ in jezyki) + " | --- | --- | --- | --- |"]
    for w in wszystkie:
        f = w.get("formularz") or {}
        nazwa = _kom(w["nazwa"]) + ("" if w["edytowalna"] else " _(wycofywana)_")
        maile = [_flaga((f.get("mail") or {}).get(j)) if f else _kom(w["stan_listy"].get("mail")) for j in jezyki]
        webpush = ", ".join(j for j, v in sorted((f.get("webpush") or {}).items()) if v == "y") or "—"
        edycja = w.get("ostatnia_edycja")
        linie.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            _kom(w.get("grupa_nazwa") or w["grupa"]), nazwa, " | ".join(maile),
            _flaga(f.get("sms")) if f else _kom(w["stan_listy"].get("sms")), webpush,
            _kom(w["stan_listy"].get("braki") or "—"),
            "%s (%s)" % (_kom(edycja["data"]), _kom(edycja["autor"])) if edycja else "—"))
    linie += ["", "> Import ICF nie zostawia wpisu w historii zmian panelu — data ostatniej edycji pomija importy.",
              "", "## Kontrola jakości", ""]
    if not problemy:
        linie.append("Brak problemów.")
    for rodzaj in ("kopia", "zmienne", "pusta", "sms"):
        grupa = [p for p in problemy if p["rodzaj"] == rodzaj]
        if not grupa:
            continue
        linie += ["### %s (%d)" % (ETYKIETY[rodzaj], len(grupa)), ""]
        linie += ["- **%s** (`%s`), %s: %s" % (_kom(p["nazwa"]), p["template"], p["jezyk"], p["opis"]) for p in grupa]
        linie.append("")
    bledy = [(w, b) for w in wszystkie for b in w.get("bledy", [])]
    if bledy:
        linie += ["## Błędy eksportu", ""] + ["- **%s** (`%s`): %s" % (_kom(w["nazwa"]), w["template"], b) for w, b in bledy]
    return "\n".join(linie) + "\n"


def sciezka_raportu(manifest: Dict) -> str:
    return os.path.join(wspolne.FOLDER_STATUS, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                        "status_" + wspolne.znacznik_daty(manifest["data_eksportu"]) + ".md")


def zapisz_raport(manifest: Dict, katalog: str) -> str:
    sciezka = sciezka_raportu(manifest)
    wspolne.zapisz_tekst(sciezka, raport(manifest, katalog))
    return sciezka
```

- [ ] **Step 4: Uruchom — PASS**

Run: `python -m unittest testy.test_status -v`
Expected: `OK` (8 testów).

- [ ] **Step 5: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wt/status.py" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_status.py"
git commit -m "Wiadomości transakcyjne: raport Status z kontrolą jakości"
```

---

### Task 6: Weryfikacja po imporcie i po zmianach konfiguracji

**Files:**
- Create: `wt/weryfikacja.py`
- Test: `testy/test_weryfikacja.py`

**Interfaces:**
- Consumes: `wt.eksport.folder_wiadomosci`, `wt.icf.*`, `wt.tresci.bez_cr`, `wt.wspolne.*`; formaty `plan_importu.json` (Task 4) i `plan_konfiguracji.json` (Task 3).
- Produces: `wt.weryfikacja`: stałe `OK="OK"`, `BEZ_ZMIAN="nie zmieniło się"`, `INACZEJ="zmieniło się inaczej"`, `BRAK="brak w eksporcie weryfikacyjnym"`; `weryfikuj(plan, manifest_po, katalog_po) -> list[dict]` (`{"template", "nazwa", "jezyk", "co", "wynik", "szczegoly"}`); `raport(plan, wyniki) -> str`; `nazwa_raportu(plan) -> str` (`import_<teraz>.md` / `konfiguracja_<teraz>.md`).

- [ ] **Step 1: Napisz testy `testy/test_weryfikacja.py`**

```python
import os
import tempfile
import unittest

from testy import fixtures
from wt import eksport, icf, weryfikacja as wer


def _po(tmp, xml_per_jezyk, mail=None, sms="n", jezyki=("pol", "eng")):
    w = fixtures.wiadomosc(jezyki=jezyki, mail=mail, sms=sms)
    m = fixtures.manifest(wiadomosci=[w], jezyki=jezyki)
    m["rodzaj"] = "weryfikacja"
    zip_ = os.path.join(tmp, "w.zip")
    fixtures.zbuduj_zip(zip_, m, {w["pliki"][j]: x for j, x in xml_per_jezyk.items()})
    return eksport.rozpakuj([zip_], os.path.join(tmp, "po"))


def _plan_importu(oczekiwane, przed, flagi=None):
    return {"wersja": 1, "rodzaj": "import", "domena": "zooart6.yourtechnicaldomain.com", "shop_id": 1,
            "data_eksportu": "2026-10-13T13:05:09",
            "pozycje": [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "jezyk": "eng",
                         "plik": "order_confirmation__eng.icf", "odcisk_oryginalu": "x",
                         "oczekiwane": oczekiwane, "przed": przed}],
            "oczekiwane_flagi": {"order_confirmation": flagi or {"mail": {"pol": "y", "eng": "y"}, "sms": "n"}}}


class TestImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_ok(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Nowy")})
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        self.assertEqual([w["wynik"] for w in wyniki], [wer.OK])

    def test_nie_zmienilo_sie_i_inaczej(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Stary", sms="Inny")})
        plan = _plan_importu({"mail.title": "Nowy", "sms.text_main_0": "Nowy SMS"}, {"mail.title": "Stary", "sms.text_main_0": "Stary SMS"})
        wyniki = {w["co"]: w["wynik"] for w in wer.weryfikuj(plan, m, katalog)}
        self.assertEqual(wyniki["mail.title"], wer.BEZ_ZMIAN)
        self.assertEqual(wyniki["sms.text_main_0"], wer.INACZEJ)

    def test_import_wylaczyl_wysylke(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml(), "eng": fixtures.icf_xml(jezyk="eng", tytul="Nowy")},
                         mail={"pol": "y", "eng": "n"})
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        flagi = [w for w in wyniki if w["co"] == "flaga mail eng"]
        self.assertEqual(flagi[0]["wynik"], wer.INACZEJ)

    def test_brak_w_eksporcie(self):
        katalog, m = _po(self.tmp.name, {"pol": fixtures.icf_xml()})
        wyniki = wer.weryfikuj(_plan_importu({"mail.title": "Nowy"}, {"mail.title": "Stary"}), m, katalog)
        self.assertEqual(wyniki[0]["wynik"], wer.BRAK)


class TestKonfiguracja(unittest.TestCase):
    def test_flagi_i_kopie(self):
        with tempfile.TemporaryDirectory() as tmp:
            xml_pol, xml_eng = fixtures.icf_xml(), fixtures.icf_xml(jezyk="eng")
            katalog, m = _po(tmp, {"pol": xml_pol, "eng": fixtures.icf_xml(jezyk="eng", html="<p>przepisane</p>")},
                             mail={"pol": "y", "eng": "n"})
            plan = {"wersja": 1, "rodzaj": "konfiguracja", "domena": "zooart6.yourtechnicaldomain.com", "shop_id": 1,
                    "data_eksportu": "2026-10-13T13:05:09",
                    "zmiany": [{"template": "order_confirmation", "nazwa": "Potwierdzenie", "grupa": "make_order",
                                "mail": {"eng": "n"}, "sms": None, "reset": False,
                                "oczekiwane": {"mail": {"pol": "y", "eng": "n"}, "sms": "n"},
                                "kopie": {"pol": {"plik": "a", "odcisk": icf.odcisk(xml_pol)},
                                          "eng": {"plik": "b", "odcisk": icf.odcisk(xml_eng)}}}]}
            wyniki = {(w["co"], w["jezyk"]): w["wynik"] for w in wer.weryfikuj(plan, m, katalog)}
            self.assertEqual(wyniki[("flaga mail eng", "eng")], wer.OK)
            self.assertEqual(wyniki[("flaga mail pol", "pol")], wer.OK)
            self.assertEqual(wyniki[("treść", "pol")], wer.OK)
            self.assertEqual(wyniki[("treść", "eng")], wer.INACZEJ)


class TestRaport(unittest.TestCase):
    def test_raport(self):
        plan = _plan_importu({}, {})
        wyniki = [{"template": "t", "nazwa": "N", "jezyk": "eng", "co": "mail.title", "wynik": wer.OK, "szczegoly": ""},
                  {"template": "t", "nazwa": "N", "jezyk": "eng", "co": "sms.text_main_0", "wynik": wer.INACZEJ, "szczegoly": "jest: x"}]
        tekst = wer.raport(plan, wyniki)
        self.assertIn("OK: 1", tekst)
        self.assertIn("Problemy: 1", tekst)
        self.assertTrue(wer.nazwa_raportu(plan).startswith("import_"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Uruchom — FAIL**

Run: `python -m unittest testy.test_weryfikacja -v`
Expected: ERROR `cannot import name 'weryfikacja'`.

- [ ] **Step 3: Utwórz `wt/weryfikacja.py`**

```python
"""Weryfikacja planu po wykonaniu w panelu: porównanie eksportu weryfikacyjnego z oczekiwanym stanem."""

import os
from typing import Dict, List, Optional

from . import eksport, icf, tresci, wspolne

OK = "OK"
BEZ_ZMIAN = "nie zmieniło się"
INACZEJ = "zmieniło się inaczej"
BRAK = "brak w eksporcie weryfikacyjnym"


def _icf_po(katalog_po: str, wiadomosc: Optional[Dict], jezyk: str) -> Optional[str]:
    if wiadomosc is None:
        return None
    sciezka = os.path.join(eksport.folder_wiadomosci(katalog_po, wiadomosc), jezyk + ".icf")
    return wspolne.czytaj_tekst(sciezka) if os.path.exists(sciezka) else None


def _wynik(template, nazwa, jezyk, co, wynik, szczegoly=""):
    return {"template": template, "nazwa": nazwa, "jezyk": jezyk, "co": co, "wynik": wynik, "szczegoly": szczegoly}


def _flagi(template, nazwa, oczekiwane: Dict, wiadomosc: Optional[Dict], zmienione: Dict) -> List[Dict]:
    """zmienione: {jezyk: flaga} zamówione w planie - dla nich BEZ_ZMIAN zamiast INACZEJ, gdy panel ich nie przyjął."""
    wyniki = []
    formularz = (wiadomosc or {}).get("formularz") or {}
    for jezyk, flaga in sorted(oczekiwane.get("mail", {}).items()):
        jest = (formularz.get("mail") or {}).get(jezyk)
        if jest == flaga:
            wynik = OK
        else:
            wynik = BEZ_ZMIAN if jezyk in zmienione else INACZEJ
        wyniki.append(_wynik(template, nazwa, jezyk, "flaga mail " + jezyk, wynik, "oczekiwano %s, jest %s" % (flaga, jest)))
    if oczekiwane.get("sms") is not None:
        jest = formularz.get("sms")
        wynik = OK if jest == oczekiwane["sms"] else (BEZ_ZMIAN if "sms" in zmienione else INACZEJ)
        wyniki.append(_wynik(template, nazwa, "*", "flaga sms", wynik, "oczekiwano %s, jest %s" % (oczekiwane["sms"], jest)))
    return wyniki


def weryfikuj(plan: Dict, manifest_po: Dict, katalog_po: str) -> List[Dict]:
    po = {w["template"]: w for w in manifest_po["wiadomosci"]}
    wyniki = []
    if plan["rodzaj"] == "import":
        for p in plan["pozycje"]:
            xml = _icf_po(katalog_po, po.get(p["template"]), p["jezyk"])
            if xml is None:
                wyniki.append(_wynik(p["template"], p["nazwa"], p["jezyk"], "plik ICF", BRAK))
                continue
            dane = icf.wczytaj(xml)
            for klucz, oczekiwana in p["oczekiwane"].items():
                kanal, pole = klucz.split(".", 1)
                jest = tresci.bez_cr(icf.wartosc(dane, kanal, pole) or "")
                if jest == tresci.bez_cr(oczekiwana):
                    wynik = OK
                elif jest == tresci.bez_cr(p["przed"].get(klucz, "")):
                    wynik = BEZ_ZMIAN
                else:
                    wynik = INACZEJ
                wyniki.append(_wynik(p["template"], p["nazwa"], p["jezyk"], klucz, wynik,
                                     "" if wynik == OK else "jest: %s" % jest[:120]))
        for template, oczekiwane in plan["oczekiwane_flagi"].items():
            nazwa = (po.get(template) or {}).get("nazwa", template)
            wyniki += [w for w in _flagi(template, nazwa, oczekiwane, po.get(template), {}) if w["wynik"] != OK]
    else:
        for z in plan["zmiany"]:
            w_po = po.get(z["template"])
            zmienione = dict(z["mail"])
            if z["sms"] is not None:
                zmienione["sms"] = z["sms"]
            wyniki += _flagi(z["template"], z["nazwa"], z["oczekiwane"], w_po, zmienione)
            for jezyk, kopia in sorted(z["kopie"].items()):
                xml = _icf_po(katalog_po, w_po, jezyk)
                if xml is None:
                    wyniki.append(_wynik(z["template"], z["nazwa"], jezyk, "treść", BRAK))
                    continue
                zgodna = icf.odcisk(xml) == kopia["odcisk"]
                wyniki.append(_wynik(z["template"], z["nazwa"], jezyk, "treść", OK if zgodna else INACZEJ,
                                     "" if zgodna else "treść różni się od kopii sprzed zmiany"))
            if z["reset"]:
                wyniki.append(_wynik(z["template"], z["nazwa"], "*", "reset do treści domyślnej", BEZ_ZMIAN,
                                     "krok ręczny - sprawdź w panelu"))
    return wyniki


def nazwa_raportu(plan: Dict) -> str:
    return "%s_%s.md" % ("import" if plan["rodzaj"] == "import" else "konfiguracja",
                         wspolne.znacznik_daty(wspolne.teraz_iso()))


def raport(plan: Dict, wyniki: List[Dict]) -> str:
    problemy = [w for w in wyniki if w["wynik"] != OK]
    linie = ["# Weryfikacja: %s — %s, sklep %s" % ("import treści" if plan["rodzaj"] == "import" else "zmiany konfiguracji",
                                                  plan["domena"], plan["shop_id"]), "",
             "Sprawdzono: %s · OK: %d · Problemy: %d" % (wspolne.teraz_iso(), len(wyniki) - len(problemy), len(problemy)), "",
             "| Wiadomość | Język | Co | Wynik | Szczegóły |", "| --- | --- | --- | --- | --- |"]
    for w in sorted(wyniki, key=lambda x: (x["wynik"] == OK, x["template"], x["jezyk"], x["co"])):
        linie.append("| %s (`%s`) | %s | %s | %s | %s |" % (
            w["nazwa"].replace("|", "\\|"), w["template"], w["jezyk"], w["co"],
            "**%s**" % w["wynik"] if w["wynik"] != OK else w["wynik"], w["szczegoly"].replace("|", "\\|")))
    return "\n".join(linie) + "\n"
```

- [ ] **Step 4: Uruchom — PASS**

Run: `python -m unittest testy.test_weryfikacja -v`
Expected: `OK` (6 testów).

- [ ] **Step 5: Uruchom cały zestaw** — `python -m unittest discover -s testy -t . -v` → `OK`.

- [ ] **Step 6: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wt/weryfikacja.py" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_weryfikacja.py"
git commit -m "Wiadomości transakcyjne: weryfikacja planów po wykonaniu w panelu"
```

---

### Task 7: `wiadomosci.py` — menu interaktywne, skróty CLI i `.bat`

**Files:**
- Create: `wiadomosci.py`, `run_wiadomosci.bat`
- Test: `testy/test_cli.py`

**Interfaces:**
- Consumes: wszystkie moduły `wt.*`.
- Produces: polecenia CLI (używane przez skill w Task 10): `rozpakuj <zip>...`, `status <katalog_eksportu>`, `konfiguracja <katalog_eksportu>`, `zmiany <katalog_eksportu> [csv]`, `tresci <katalog_eksportu>`, `weryfikuj <katalog_planu> <zip>`. Flaga `--tak` pomija pytania o potwierdzenie (dla skilla, po akceptacji w rozmowie). Kod wyjścia 0 = sukces, 1 = błąd danych, 2 = złe argumenty.

- [ ] **Step 1: Napisz test `testy/test_cli.py`** (CLI uruchamiane w podprocesie z `WT_KATALOG` w katalogu tymczasowym)

```python
import os
import subprocess
import sys
import tempfile
import unittest

from testy import fixtures

SKRYPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiadomosci.py")


def uruchom(katalog, *argumenty):
    env = dict(os.environ, WT_KATALOG=katalog, WT_POBIERANIE=os.path.join(katalog, "Downloads"), PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, SKRYPT] + list(argumenty), capture_output=True, text=True,
                          encoding="utf-8", env=env, stdin=subprocess.DEVNULL)


class TestCli(unittest.TestCase):
    def test_pelny_przebieg(self):
        with tempfile.TemporaryDirectory() as k:
            m = fixtures.manifest(jezyki=("pol", "eng"))
            w = m["wiadomosci"][0]
            zip_ = os.path.join(k, "eksport.zip")
            fixtures.zbuduj_zip(zip_, m, {w["pliki"][j]: fixtures.icf_xml(jezyk=j) for j in ("pol", "eng")})

            r = uruchom(k, "rozpakuj", zip_)
            self.assertEqual(r.returncode, 0, r.stderr)
            katalog = os.path.join(k, "Eksport i Import Treści", "zooart6_shop1", "2026-10-13_130509")
            self.assertTrue(os.path.exists(os.path.join(katalog, "manifest.json")))

            r = uruchom(k, "status", katalog)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(k, "Status", "zooart6_shop1", "status_2026-10-13_130509.md")))

            r = uruchom(k, "konfiguracja", katalog)
            self.assertEqual(r.returncode, 0, r.stderr)
            csv_ = os.path.join(k, "Edycja Działania", "zooart6_shop1", "konfiguracja_2026-10-13_130509.csv")
            with open(csv_, encoding="utf-8-sig") as p:
                tekst = p.read()
            with open(csv_, "w", encoding="utf-8-sig") as p:
                p.write(tekst.replace("tak;tak;nie", "tak;nie;nie", 1))
            r = uruchom(k, "zmiany", katalog, "--tak")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("mail eng: tak -> nie", r.stdout)

            with open(os.path.join(katalog, "make_order__order_confirmation", "eng_sms.txt"), "w", encoding="utf-8") as p:
                p.write("Nowy SMS")
            r = uruchom(k, "tresci", katalog, "--tak")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("plan_importu.json", r.stdout)

    def test_zip_z_folderu_pobierania_przeniesiony_do_archiwum(self):
        with tempfile.TemporaryDirectory() as k:
            m = fixtures.manifest(jezyki=("pol",))
            pobieranie = os.path.join(k, "Downloads")
            os.makedirs(pobieranie)
            nazwa = "eksport_zooart6_shop1_20261013-130509.zip"
            fixtures.zbuduj_zip(os.path.join(pobieranie, nazwa), m, {m["wiadomosci"][0]["pliki"]["pol"]: fixtures.icf_xml()})
            obcy = os.path.join(pobieranie, "faktura.zip")
            with open(obcy, "wb") as p:
                p.write(b"x")
            r = uruchom(k, "rozpakuj", os.path.join(pobieranie, nazwa))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(os.path.exists(os.path.join(pobieranie, nazwa)))
            self.assertTrue(os.path.exists(os.path.join(k, "_pobrane", nazwa)))
            self.assertTrue(os.path.exists(obcy))   # inne pliki z Pobranych nietknięte

    def test_zle_argumenty(self):
        with tempfile.TemporaryDirectory() as k:
            self.assertEqual(uruchom(k, "nieznane").returncode, 2)
            self.assertEqual(uruchom(k, "status", os.path.join(k, "brak")).returncode, 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Uruchom — FAIL**

Run: `python -m unittest testy.test_cli -v`
Expected: FAIL (`returncode` 2 — `can't open file ... wiadomosci.py`).

- [ ] **Step 3: Utwórz `wiadomosci.py`**

```python
"""Wiadomości transakcyjne IdoSell - praca na plikach eksportu.

Uruchom bez argumentów (albo dwuklikiem run_wiadomosci.bat), żeby dostać menu.
Skróty: rozpakuj <zip>... | status <katalog> | konfiguracja <katalog> | zmiany <katalog> [csv]
        | tresci <katalog> | weryfikuj <katalog_planu> <zip>     (+ --tak = bez pytań o potwierdzenie)
"""

import glob
import os
import sys

from wt import eksport, icf, konfiguracja, status, tresci, weryfikacja, wspolne

POTWIERDZAJ = "--tak" not in sys.argv


class BladUzycia(Exception):
    pass


def pytaj_tak(pytanie: str) -> bool:
    if not POTWIERDZAJ:
        return True
    return input(pytanie + " [t/N]: ").strip().lower() in ("t", "tak", "y")


def wybierz(opcje, opis, wiele=False):
    if not opcje:
        print("Brak: " + opis)
        return [] if wiele else None
    for nr, (etykieta, _) in enumerate(opcje, start=1):
        print("  %d) %s" % (nr, etykieta))
    odp = input("%s (numer%s, Enter = anuluj): " % (opis, "y po przecinku" if wiele else "")).strip()
    try:
        numery = [int(x) for x in odp.split(",") if x.strip()]
        wybrane = [opcje[n - 1][1] for n in numery if 1 <= n <= len(opcje)]
    except ValueError:
        wybrane = []
    if wiele:
        return wybrane
    return wybrane[0] if wybrane else None


def eksporty():
    pliki = sorted(glob.glob(os.path.join(wspolne.FOLDER_TRESCI, "*", "*", "manifest.json")), reverse=True)
    return [(os.path.relpath(os.path.dirname(p), wspolne.FOLDER_TRESCI), os.path.dirname(p)) for p in pliki]


def zipy(przedrostek):
    """ZIP-y narzędzia: najpierw nowe z folderu pobierania Chrome, potem archiwum _pobrane w projekcie."""
    wynik = []
    for folder, etykieta in ((wspolne.FOLDER_POBIERANIE, "Pobrane"), (wspolne.FOLDER_POBRANE, "archiwum")):
        pliki = sorted(glob.glob(os.path.join(folder, przedrostek + "*.zip")), key=os.path.getmtime, reverse=True)
        wynik += [("[%s] %s" % (etykieta, os.path.basename(p)), p) for p in pliki]
    return wynik


def _manifest(katalog):
    if not os.path.exists(os.path.join(katalog, "manifest.json")):
        raise BladUzycia("W %s nie ma manifest.json - to nie jest rozpakowany eksport." % katalog)
    return eksport.wczytaj_eksport(katalog)


def cmd_rozpakuj(sciezki):
    for s in sciezki:
        eksport.wczytaj_zip(s)   # najpierw sprawdź, czy to eksport narzędzia - dopiero potem przenoś
    sciezki = [wspolne.przejmij(s) for s in sciezki]
    katalog, manifest = eksport.rozpakuj(sciezki)
    bledy = sum(len(w.get("bledy", [])) for w in manifest["wiadomosci"])
    print("[OK] Rozpakowano %d wiadomości do: %s" % (len(manifest["wiadomosci"]), katalog))
    if bledy:
        print("[!] Błędów eksportu: %d - szczegóły w raporcie Status." % bledy)
    if manifest.get("niekompletny"):
        print("[!] Eksport niekompletny (brakuje %d wiadomości) - uruchom eksport ponownie i rozpakuj oba ZIP-y razem."
              % len(manifest["pozostale"]))
    return katalog


def cmd_status(katalog):
    manifest = _manifest(katalog)
    sciezka = status.zapisz_raport(manifest, katalog)
    problemy = status.kontrola(manifest, katalog)
    print("[OK] Raport Status: %s" % sciezka)
    print("     Wiadomości: %d, problemy kontroli jakości: %d" % (len(manifest["wiadomosci"]), len(problemy)))


def cmd_konfiguracja(katalog):
    manifest = _manifest(katalog)
    sciezka = konfiguracja.sciezka_csv(manifest)
    if os.path.exists(sciezka) and not pytaj_tak("Plik %s istnieje (może z Twoimi zmianami). Nadpisać?" % sciezka):
        print("Anulowano.")
        return
    konfiguracja.zapisz_csv(manifest, sciezka)
    print("[OK] CSV konfiguracji: %s" % sciezka)
    print("     Zmień wartości tak/nie, zapisz (CSV UTF-8, średnik) i wybierz 'Zmiany konfiguracji'.")


def cmd_zmiany(katalog, sciezka_csv=None):
    manifest = _manifest(katalog)
    sciezka_csv = sciezka_csv or konfiguracja.sciezka_csv(manifest)
    zmiany, bledy = konfiguracja.roznice(manifest, sciezka_csv)
    for b in bledy:
        print("[!] " + b)
    if not zmiany:
        print("Brak zmian do wprowadzenia.")
        return 1 if bledy else 0
    stan = {w["template"]: w["formularz"] for w in manifest["wiadomosci"] if w.get("formularz")}
    print("Zmiany (%d wiadomości):" % len(zmiany))
    for z in zmiany:
        opisy = ["mail %s: %s -> %s" % (j, "tak" if stan[z["template"]]["mail"].get(j) == "y" else "nie",
                                        "tak" if f == "y" else "nie") for j, f in sorted(z["mail"].items())]
        if z["sms"] is not None:
            opisy.append("sms: %s -> %s" % ("tak" if stan[z["template"]]["sms"] == "y" else "nie", "tak" if z["sms"] == "y" else "nie"))
        if z["reset"]:
            opisy.append("RESET do treści domyślnej (krok ręczny w panelu)")
        print("  - %s (%s): %s" % (z["nazwa"], z["template"], "; ".join(opisy)))
    if bledy and not pytaj_tak("Są błędy w CSV (powyżej) - wiersze z błędami zostaną pominięte. Kontynuować?"):
        return 1
    if not pytaj_tak("Przygotować plan zmian?"):
        print("Anulowano.")
        return 0
    katalog_planu = os.path.join(wspolne.FOLDER_EDYCJA, wspolne.id_sklepu(manifest["domena"], manifest["shop_id"]),
                                 "zmiany_" + wspolne.znacznik_daty(wspolne.teraz_iso()))
    sciezka = konfiguracja.zapisz_plan(manifest, katalog, zmiany, katalog_planu)
    print("[OK] Plan: %s" % sciezka)
    print("     Bookmarklet -> 'Zastosuj plan' -> wskaż folder %s" % katalog_planu)
    return 0


def cmd_tresci(katalog):
    manifest = _manifest(katalog)
    roznice = tresci.roznice_tresci(katalog, manifest)
    if not roznice:
        print("Brak zmian w plikach treści.")
        return
    print("Zmienione treści (%d):" % len(roznice))
    for r in roznice:
        print("  - %s (%s), %s: %s" % (r["nazwa"], r["template"], r["jezyk"], ", ".join(sorted(r["pola"]))))
    if not pytaj_tak("Złożyć ICF do importu?"):
        print("Anulowano.")
        return
    katalog_planu = os.path.join(katalog, "do_importu_" + wspolne.znacznik_daty(wspolne.teraz_iso()))
    sciezka = tresci.zloz(manifest, roznice, katalog_planu)
    print("[OK] Plan: %s" % sciezka)
    print("     Bookmarklet -> 'Zastosuj plan' -> wskaż folder %s" % katalog_planu)


def cmd_weryfikuj(katalog_planu, sciezka_zip):
    plany = [p for p in ("plan_importu.json", "plan_konfiguracji.json") if os.path.exists(os.path.join(katalog_planu, p))]
    if not plany:
        raise BladUzycia("W %s nie ma plan_importu.json ani plan_konfiguracji.json." % katalog_planu)
    plan = wspolne.czytaj_json(os.path.join(katalog_planu, plany[0]))
    eksport.wczytaj_zip(sciezka_zip)
    sciezka_zip = wspolne.przejmij(sciezka_zip)
    katalog_po, manifest_po = eksport.rozpakuj([sciezka_zip], os.path.join(katalog_planu, "po"), nadpisz=True)
    wyniki = weryfikacja.weryfikuj(plan, manifest_po, katalog_po)
    sciezka = os.path.join(katalog_planu, weryfikacja.nazwa_raportu(plan))
    wspolne.zapisz_tekst(sciezka, weryfikacja.raport(plan, wyniki))
    problemy = [w for w in wyniki if w["wynik"] != weryfikacja.OK]
    print("[OK] Raport weryfikacji: %s" % sciezka)
    print("     OK: %d, problemy: %d" % (len(wyniki) - len(problemy), len(problemy)))
    for w in problemy:
        print("  [!] %s (%s) %s %s: %s %s" % (w["nazwa"], w["template"], w["jezyk"], w["co"], w["wynik"], w["szczegoly"]))
    return 1 if problemy else 0


def plany():
    wzory = [os.path.join(wspolne.FOLDER_EDYCJA, "*", "zmiany_*"), os.path.join(wspolne.FOLDER_TRESCI, "*", "*", "do_importu_*")]
    katalogi = sorted([k for w in wzory for k in glob.glob(w) if os.path.isdir(k)], key=os.path.getmtime, reverse=True)
    return [(os.path.relpath(k, wspolne.KATALOG_GLOWNY), k) for k in katalogi]


def menu():
    pozycje = [
        ("Rozpakuj eksport (z Pobranych)", lambda: cmd_rozpakuj(wybierz(zipy("eksport_"), "Które ZIP-y (części jednego eksportu)", wiele=True) or _anuluj())),
        ("Raport Status", lambda: cmd_status(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Edycja działania: utwórz CSV ze stanu", lambda: cmd_konfiguracja(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Edycja działania: różnice i plan zmian", lambda: cmd_zmiany(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Treści: różnice i ICF do importu", lambda: cmd_tresci(wybierz(eksporty(), "Który eksport") or _anuluj())),
        ("Weryfikacja po wykonaniu planu", lambda: cmd_weryfikuj(wybierz(plany(), "Który plan") or _anuluj(),
                                                                 wybierz(zipy("weryfikacja_"), "Który ZIP weryfikacji") or _anuluj())),
    ]
    while True:
        print("\n=== Wiadomości transakcyjne IdoSell ===")
        for nr, (etykieta, _) in enumerate(pozycje, start=1):
            print("  %d) %s" % (nr, etykieta))
        print("  0) Wyjście")
        odp = input("Wybór: ").strip()
        if odp in ("0", ""):
            return
        if not odp.isdigit() or not 1 <= int(odp) <= len(pozycje):
            continue
        try:
            pozycje[int(odp) - 1][1]()
        except _Anulowano:
            print("Anulowano.")
        except (BladUzycia, eksport.BladEksportu, konfiguracja.BladKonfiguracji, icf.BladIcf, OSError) as blad:
            print("[BŁĄD] %s" % blad)


class _Anulowano(Exception):
    pass


def _anuluj():
    raise _Anulowano()


POLECENIA = {
    "rozpakuj": (lambda a: cmd_rozpakuj(a), 1, None),
    "status": (lambda a: cmd_status(a[0]), 1, 1),
    "konfiguracja": (lambda a: cmd_konfiguracja(a[0]), 1, 1),
    "zmiany": (lambda a: cmd_zmiany(a[0], a[1] if len(a) > 1 else None), 1, 2),
    "tresci": (lambda a: cmd_tresci(a[0]), 1, 1),
    "weryfikuj": (lambda a: cmd_weryfikuj(a[0], a[1]), 2, 2),
}


def main(argv):
    argumenty = [a for a in argv if a != "--tak"]
    if not argumenty:
        menu()
        return 0
    nazwa, reszta = argumenty[0], argumenty[1:]
    if nazwa not in POLECENIA:
        print(__doc__)
        return 2
    funkcja, minimum, maksimum = POLECENIA[nazwa]
    if len(reszta) < minimum or (maksimum is not None and len(reszta) > maksimum):
        print(__doc__)
        return 2
    try:
        wynik = funkcja(reszta)
        return wynik if isinstance(wynik, int) else 0
    except (BladUzycia, eksport.BladEksportu, konfiguracja.BladKonfiguracji, icf.BladIcf, OSError) as blad:
        print("[BŁĄD] %s" % blad)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Utwórz `run_wiadomosci.bat`**

```bat
@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python wiadomosci.py %*
echo.
pause
```

- [ ] **Step 5: Uruchom — PASS**

Run: `python -m unittest testy.test_cli -v`
Expected: `OK` (3 testy). Potem cały zestaw: `python -m unittest discover -s testy -t .` → `OK`.

- [ ] **Step 6: Sprawdź menu ręcznie** — `echo 0 | python wiadomosci.py` wypisuje menu i kończy z kodem 0.

- [ ] **Step 7: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/wiadomosci.py" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/run_wiadomosci.bat" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_cli.py"
git commit -m "Wiadomości transakcyjne: menu interaktywne i skróty CLI"
```

---

### Task 8: `panel_core.js` — czyste funkcje i eksport z panelu

**Files:**
- Create: `przegladarka/panel_core.js`
- Test: `przegladarka/testy/test_core.mjs`

**Interfaces:**
- Produces (obiekt `WT` — `window.WT` w przeglądarce, `module.exports` w Node):
  - czyste: `crc32(Uint8Array) -> number`; `zbudujZip([{nazwa: string, dane: string|Uint8Array}]) -> Uint8Array`; `normalizujIcf(xml) -> string`; `odcisk(xml) -> Promise<string>`; `parsujStan(tekst) -> {stan: 'tak'|'nie'|'nie dotyczy'|null, braki: string|null}`; `parametr(href, nazwa) -> string|null`; `doJson(obiekt) -> string`; `terazIso() -> string`.
  - panel: `BLAD_SESJI` (string); `pobierzTekst(url) -> Promise<string>`; `pobierzGrupy(shop) -> Promise<[{grupa, nazwa}]>`; `pobierzListe(grupa, shop) -> Promise<[wiadomość bez formularza]>`; `pobierzEdycje(template, shop) -> Promise<{jezyki, formularz, ostatnia_edycja}>`; `pobierzIcf(template, shop, jezyk) -> Promise<string>`; `eksportuj({shop, templates?, rodzaj?, onPostep?}) -> Promise<{nazwa, manifest}>` (pobiera ZIP); `pobierzPlik(nazwa, Uint8Array) -> void`; `shopZAdresu() -> number`.

- [ ] **Step 1: Napisz testy `przegladarka/testy/test_core.mjs`**

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const WT = require('../panel_core.js');

test('crc32 — wektor standardowy', () => {
  assert.equal(WT.crc32(new TextEncoder().encode('123456789')), 0xCBF43926);
});

test('odcisk zgodny z Pythonem (wt.icf.odcisk)', async () => {
  assert.equal(await WT.odcisk('<element id="5"><description>x</description></element>'),
    'ab0b689c27f39287b842979f958747a537c71abef5268a728a1081e4f694417b');
});

test('parsujStan', () => {
  assert.deepEqual(WT.parsujStan(' tak '), { stan: 'tak', braki: null });
  assert.deepEqual(WT.parsujStan('nie dotyczy'), { stan: 'nie dotyczy', braki: null });
  assert.deepEqual(WT.parsujStan('takdo uzupełnienia szablony: (2 z 3)'), { stan: 'tak', braki: '2 z 3' });
  assert.deepEqual(WT.parsujStan('nie'), { stan: 'nie', braki: null });
  assert.deepEqual(WT.parsujStan(''), { stan: null, braki: null });
});

test('parametr z adresu', () => {
  const href = '/panel/config-messages.php?populate=edit&template=order_confirmation&shop=1';
  assert.equal(WT.parametr(href, 'template'), 'order_confirmation');
  assert.equal(WT.parametr(href, 'shop'), '1');
  assert.equal(WT.parametr(href, 'group'), null);
});

test('doJson odporny na Array#toJSON z Prototype.js', () => {
  Array.prototype.toJSON = function () { return 'ZEPSUTE'; };
  try {
    assert.equal(WT.doJson({ a: [1, 'ż'] }).replace(/\s/g, ''), '{"a":[1,"ż"]}');
    assert.equal(typeof Array.prototype.toJSON, 'function');   // przywrócone
  } finally {
    delete Array.prototype.toJSON;
  }
});

test('zbudujZip czytelny dla Pythona (zipfile)', () => {
  const zip = WT.zbudujZip([{ nazwa: 'manifest.json', dane: '{"wersja":1}' }, { nazwa: 'icf/ą__b/pol.icf', dane: '<x>żółć</x>' }]);
  const katalog = mkdtempSync(join(tmpdir(), 'wt-'));
  const sciezka = join(katalog, 'test.zip');
  writeFileSync(sciezka, zip);
  const py = spawnSync('python', ['-I', '-c',
    'import sys,zipfile;z=zipfile.ZipFile(sys.argv[1]);assert z.testzip() is None;' +
    'sys.stdout.buffer.write(z.read("icf/ą__b/pol.icf"))', sciezka]);
  assert.equal(py.status, 0, py.stderr.toString());
  assert.equal(py.stdout.toString('utf8'), '<x>żółć</x>');
});
```

- [ ] **Step 2: Uruchom — FAIL**

Run (w KATALOGU): `node --test przegladarka/testy/`
Expected: FAIL `Cannot find module '../panel_core.js'`.

- [ ] **Step 3: Utwórz `przegladarka/panel_core.js`**

```js
/* Wiadomości transakcyjne IdoSell — rdzeń przeglądarkowy.
 * Działa na stronie /panel/config-messages.php na sesji zalogowanego użytkownika (bookmarklet, skill)
 * oraz w Node (testy czystych funkcji).
 * UWAGA: panel ładuje Prototype.js — tylko zwykłe pętle for, bez Array.from / for..of na Set / filter / map;
 * JSON wyłącznie przez WT.doJson().
 */
(function (root) {
  'use strict';
  var WT = {};
  var SCIEZKA = '/panel/config-messages.php';
  var ODSTEP_MS = 200;
  WT.BLAD_SESJI = 'SESJA_WYGASLA';

  // ---------- czyste funkcje ----------

  var TABLICA_CRC = null;
  WT.crc32 = function (bajty) {
    if (!TABLICA_CRC) {
      TABLICA_CRC = [];
      for (var n = 0; n < 256; n++) {
        var c = n;
        for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
        TABLICA_CRC[n] = c >>> 0;
      }
    }
    var crc = 0xFFFFFFFF;
    for (var i = 0; i < bajty.length; i++) crc = TABLICA_CRC[(crc ^ bajty[i]) & 0xFF] ^ (crc >>> 8);
    return (crc ^ 0xFFFFFFFF) >>> 0;
  };

  function utf8(tekst) { return new TextEncoder().encode(tekst); }

  // ZIP bez kompresji (metoda 0 „store"), nazwy plików w UTF-8 (bit 11), data 1980-01-01.
  WT.zbudujZip = function (pliki) {
    var czesci = [], centralne = [], przesuniecie = 0;
    for (var i = 0; i < pliki.length; i++) {
      var nazwa = utf8(pliki[i].nazwa);
      var dane = typeof pliki[i].dane === 'string' ? utf8(pliki[i].dane) : pliki[i].dane;
      var crc = WT.crc32(dane);
      var lok = new DataView(new ArrayBuffer(30));
      lok.setUint32(0, 0x04034b50, true); lok.setUint16(4, 20, true); lok.setUint16(6, 0x0800, true);
      lok.setUint16(8, 0, true); lok.setUint16(10, 0, true); lok.setUint16(12, 0x21, true);
      lok.setUint32(14, crc, true); lok.setUint32(18, dane.length, true); lok.setUint32(22, dane.length, true);
      lok.setUint16(26, nazwa.length, true); lok.setUint16(28, 0, true);
      czesci.push(new Uint8Array(lok.buffer), nazwa, dane);
      var cen = new DataView(new ArrayBuffer(46));
      cen.setUint32(0, 0x02014b50, true); cen.setUint16(4, 20, true); cen.setUint16(6, 20, true);
      cen.setUint16(8, 0x0800, true); cen.setUint16(10, 0, true); cen.setUint16(12, 0, true);
      cen.setUint16(14, 0x21, true); cen.setUint32(16, crc, true); cen.setUint32(20, dane.length, true);
      cen.setUint32(24, dane.length, true); cen.setUint16(28, nazwa.length, true);
      cen.setUint32(42, przesuniecie, true);
      centralne.push(new Uint8Array(cen.buffer), nazwa);
      przesuniecie += 30 + nazwa.length + dane.length;
    }
    var rozmiarCen = 0;
    for (var j = 0; j < centralne.length; j++) { czesci.push(centralne[j]); rozmiarCen += centralne[j].length; }
    var kon = new DataView(new ArrayBuffer(22));
    kon.setUint32(0, 0x06054b50, true); kon.setUint16(8, pliki.length, true); kon.setUint16(10, pliki.length, true);
    kon.setUint32(12, rozmiarCen, true); kon.setUint32(16, przesuniecie, true);
    czesci.push(new Uint8Array(kon.buffer));
    var dlugosc = 0;
    for (var a = 0; a < czesci.length; a++) dlugosc += czesci[a].length;
    var wynik = new Uint8Array(dlugosc), poz = 0;
    for (var b = 0; b < czesci.length; b++) { wynik.set(czesci[b], poz); poz += czesci[b].length; }
    return wynik;
  };

  WT.normalizujIcf = function (xml) {
    return xml.replace(/<element id="\d+">/, '<element>').replace(/<description>[^<]*<\/description>/, '<description/>');
  };

  WT.odcisk = function (xml) {
    return crypto.subtle.digest('SHA-256', utf8(WT.normalizujIcf(xml))).then(function (bufor) {
      var b = new Uint8Array(bufor), s = '';
      for (var i = 0; i < b.length; i++) s += (b[i] < 16 ? '0' : '') + b[i].toString(16);
      return s;
    });
  };

  WT.parsujStan = function (tekst) {
    var t = (tekst || '').replace(/\s+/g, ' ').trim();
    var braki = t.match(/do uzupełnienia szablony:\s*\((\d+ z \d+)\)/);
    var stan = /^nie dotyczy/.test(t) ? 'nie dotyczy' : /^tak/.test(t) ? 'tak' : /^nie/.test(t) ? 'nie' : null;
    return { stan: stan, braki: braki ? braki[1] : null };
  };

  WT.parametr = function (href, nazwa) {
    var m = (href || '').match(new RegExp('[?&]' + nazwa + '=([^&#]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  };

  // Prototype.js dodaje Array#toJSON / String#toJSON, co psuje JSON.stringify — zdejmujemy je na czas serializacji.
  WT.doJson = function (obiekt) {
    var a = Array.prototype.toJSON, s = String.prototype.toJSON;
    delete Array.prototype.toJSON; delete String.prototype.toJSON;
    try { return JSON.stringify(obiekt, null, 2); }
    finally { if (a) Array.prototype.toJSON = a; if (s) String.prototype.toJSON = s; }
  };

  function dwa(n) { return (n < 10 ? '0' : '') + n; }
  WT.terazIso = function () {
    var d = new Date();
    return d.getFullYear() + '-' + dwa(d.getMonth() + 1) + '-' + dwa(d.getDate()) + 'T' +
      dwa(d.getHours()) + ':' + dwa(d.getMinutes()) + ':' + dwa(d.getSeconds());
  };

  // ---------- odczyt panelu ----------

  function czekaj(ms) { return new Promise(function (ok) { setTimeout(ok, ms); }); }
  function html(tekst) { return new DOMParser().parseFromString(tekst, 'text/html'); }
  function tekstEl(e) { return ((e && e.textContent) || '').replace(/\s+/g, ' ').trim(); }
  WT.tekstEl = tekstEl;

  function bladSesji() {
    var e = new Error('Sesja panelu wygasła — zaloguj się i uruchom ponownie.');
    e.kod = WT.BLAD_SESJI;
    return e;
  }

  WT.pobierzTekst = async function (url) {
    for (var proba = 1; ; proba++) {
      var r = await fetch(url, { credentials: 'include' });
      var t = await r.text();
      if ((r.status === 429 || r.status >= 500) && proba < 3) { await czekaj(2000 * proba); continue; }
      if (r.status >= 400) throw new Error('HTTP ' + r.status + ' dla ' + url.split('?')[0]);
      if (/<title>\s*Logowanie u/.test(t)) throw bladSesji();
      await czekaj(ODSTEP_MS);
      return t;
    }
  };

  WT.shopZAdresu = function () {
    return parseInt(WT.parametr(location.search, 'shop') || '1', 10);
  };

  WT.pobierzGrupy = async function (shop) {
    var d = html(await WT.pobierzTekst(SCIEZKA + '?populate=types&shop=' + shop));
    var linki = d.querySelectorAll('a[href*="populate=list"]'), wynik = [], byly = {};
    for (var i = 0; i < linki.length; i++) {
      var g = WT.parametr(linki[i].getAttribute('href'), 'group');
      if (!g || byly[g]) continue;
      byly[g] = true;
      var wiersz = linki[i].closest('tr');
      wynik.push({ grupa: g, nazwa: tekstEl(wiersz ? wiersz.querySelector('td') : linki[i]) });
    }
    return wynik;
  };

  function naglowekSekcji(tabela) {
    for (var e = tabela; e && e.tagName !== 'BODY'; e = e.parentElement) {
      for (var s = e.previousElementSibling; s; s = s.previousElementSibling) {
        if (/^H[1-6]$/.test(s.tagName)) return tekstEl(s);
        if (s.tagName === 'TABLE') break;
      }
    }
    return '';
  }

  function wierszeTabeli(tabela) {
    return tabela.querySelectorAll(':scope > tr, :scope > tbody > tr, :scope > thead > tr');
  }

  WT.pobierzListe = async function (grupa, shop) {
    var d = html(await WT.pobierzTekst(SCIEZKA + '?populate=list&group=' + encodeURIComponent(grupa) + '&shop=' + shop));
    var tabele = d.querySelectorAll('table'), wynik = [], byly = {};
    var kanaly = ['sms', 'mail', 'webpush'];
    for (var i = 0; i < tabele.length; i++) {
      var wiersze = wierszeTabeli(tabele[i]);
      if (!wiersze.length) continue;
      var naglowki = wiersze[0].querySelectorAll('th, td'), kol = {};
      for (var k = 0; k < naglowki.length; k++) {
        var h = tekstEl(naglowki[k]);
        if (/SMS/.test(h)) kol.sms = k; else if (/Web Push/i.test(h)) kol.webpush = k; else if (/e-mail/i.test(h)) kol.mail = k;
      }
      if (kol.mail === undefined && kol.sms === undefined) continue;
      var sekcja = naglowekSekcji(tabele[i]);
      for (var r = 1; r < wiersze.length; r++) {
        var a = wiersze[r].querySelector('a[href*="template="]');
        if (!a) continue;
        var template = WT.parametr(a.getAttribute('href'), 'template');
        if (!template || byly[template]) continue;
        byly[template] = true;
        var komorki = wiersze[r].querySelectorAll('td'), stan = { braki: null };
        for (var c = 0; c < kanaly.length; c++) {
          var idx = kol[kanaly[c]];
          if (idx === undefined || !komorki[idx]) { stan[kanaly[c]] = null; continue; }
          var s = WT.parsujStan(tekstEl(komorki[idx]));
          stan[kanaly[c]] = s.stan;
          if (s.braki) stan.braki = s.braki;
        }
        wynik.push({ grupa: grupa, sekcja: sekcja, template: template, nazwa: tekstEl(komorki[0]),
          edytowalna: /Edytuj/.test(tekstEl(a)), stan_listy: stan });
      }
    }
    return wynik;
  };

  WT.pobierzEdycje = async function (template, shop) {
    var d = html(await WT.pobierzTekst(SCIEZKA + '?populate=edit&template=' + encodeURIComponent(template) + '&shop=' + shop));
    var jezyki = [], formularz = { mail: {}, sms: null, webpush: {} };
    var pola = d.querySelectorAll('input[name]');
    for (var i = 0; i < pola.length; i++) {
      var n = pola[i].getAttribute('name');
      var m = n.match(/^(mail|sms|webpush)_lang\[([a-z]{3})\]/);
      if (m && jezyki.indexOf(m[2]) < 0) jezyki.push(m[2]);
      if (pola[i].type !== 'radio' || !pola[i].hasAttribute('checked')) continue;
      var v = pola[i].getAttribute('value');
      var mm = n.match(/^mail_lang\[([a-z]{3})\]\[active_mail\]$/);
      if (mm) formularz.mail[mm[1]] = v;
      if (n === 'sms_lang[active]') formularz.sms = v;
      var mw = n.match(/^webpush_lang\[([a-z]{3})\]\[active\]$/);
      if (mw) formularz.webpush[mw[1]] = v;
    }
    var ostatnia = null, komorki = d.querySelectorAll('td, th');
    for (var k = 0; k < komorki.length; k++) {
      if (tekstEl(komorki[k]) !== 'Data modyfikacji') continue;
      var wiersz = komorki[k].closest('tr'), nast = wiersz ? wiersz.nextElementSibling : null;
      var td = nast ? nast.querySelectorAll('td') : [];
      if (td.length >= 2 && /^\d{4}-\d{2}-\d{2}/.test(tekstEl(td[1]))) ostatnia = { autor: tekstEl(td[0]), data: tekstEl(td[1]) };
      break;
    }
    return { jezyki: jezyki, formularz: formularz, ostatnia_edycja: ostatnia };
  };

  WT.adresIcf = function (template, shop, jezyk) {
    return SCIEZKA + '?populate=edit&template=' + encodeURIComponent(template) + '&shop=' + shop +
      '&story_id=&action=exportIDF&language=' + jezyk;
  };

  WT.pobierzIcf = async function (template, shop, jezyk) {
    var t = await WT.pobierzTekst(WT.adresIcf(template, shop, jezyk));
    if (t.indexOf('file_format="ICF"') < 0) throw new Error('Odpowiedź nie jest plikiem ICF');
    return t;
  };

  WT.pobierzPlik = function (nazwa, bajty) {
    var url = URL.createObjectURL(new Blob([bajty], { type: 'application/zip' }));
    var a = document.createElement('a');
    a.href = url; a.download = nazwa;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  };

  WT.eksportuj = async function (opcje) {
    var shop = opcje.shop, filtr = opcje.templates || null, postep = opcje.onPostep || function () {};
    var rodzaj = opcje.rodzaj || 'eksport';
    var manifest = { wersja: 1, rodzaj: rodzaj, domena: location.hostname, shop_id: shop, data_eksportu: WT.terazIso(),
      niekompletny: false, pozostale: [], jezyki: [], wiadomosci: [] };
    var pliki = [], lista = [];
    var grupy = await WT.pobierzGrupy(shop);
    for (var g = 0; g < grupy.length; g++) {
      postep('Lista: ' + grupy[g].nazwa);
      var wiersze = await WT.pobierzListe(grupy[g].grupa, shop);
      for (var i = 0; i < wiersze.length; i++) {
        wiersze[i].grupa_nazwa = grupy[g].nazwa;
        if (!filtr || filtr.indexOf(wiersze[i].template) >= 0) lista.push(wiersze[i]);
      }
    }
    for (var n = 0; n < lista.length; n++) {
      var w = lista[n];
      w.formularz = null; w.ostatnia_edycja = null; w.pliki = {}; w.bledy = [];
      try {
        if (w.edytowalna) {
          postep((n + 1) + '/' + lista.length + ': ' + w.nazwa);
          var e = await WT.pobierzEdycje(w.template, shop);
          w.formularz = e.formularz; w.ostatnia_edycja = e.ostatnia_edycja;
          for (var j = 0; j < e.jezyki.length; j++) {
            var jez = e.jezyki[j];
            if (manifest.jezyki.indexOf(jez) < 0) manifest.jezyki.push(jez);
            try {
              var xml = await WT.pobierzIcf(w.template, shop, jez);
              var sciezka = 'icf/' + w.grupa + '__' + w.template + '/' + jez + '.icf';
              pliki.push({ nazwa: sciezka, dane: xml });
              w.pliki[jez] = sciezka;
            } catch (bladJ) {
              if (bladJ.kod === WT.BLAD_SESJI) throw bladJ;
              w.bledy.push(jez + ': ' + bladJ.message);
            }
          }
        }
      } catch (blad) {
        if (blad.kod !== WT.BLAD_SESJI) { w.bledy.push(blad.message); manifest.wiadomosci.push(w); continue; }
        manifest.niekompletny = true;
        for (var r = n; r < lista.length; r++) manifest.pozostale.push(lista[r].template);
        postep('Sesja wygasła — zapisuję eksport częściowy (' + n + '/' + lista.length + ').');
        break;
      }
      manifest.wiadomosci.push(w);
    }
    pliki.unshift({ nazwa: 'manifest.json', dane: WT.doJson(manifest) });
    var nazwa = rodzaj + '_' + location.hostname.split('.')[0] + '_shop' + shop + '_' +
      manifest.data_eksportu.replace(/[-:]/g, '').replace('T', '-') + '.zip';
    WT.pobierzPlik(nazwa, WT.zbudujZip(pliki));
    postep('Gotowe: ' + nazwa + (manifest.niekompletny ? ' (NIEKOMPLETNY)' : ''));
    return { nazwa: nazwa, manifest: manifest };
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = WT;
  else root.WT = WT;
})(typeof window !== 'undefined' ? window : globalThis);
```

- [ ] **Step 4: Uruchom — PASS**

Run: `node --test przegladarka/testy/`
Expected: `# pass 6`, `# fail 0`.

- [ ] **Step 5: Test na panelu (tylko odczyt)** — Claude in Chrome, karta z `…/config-messages.php?populate=types&shop=1` na `zooart6`: wklej przez `javascript_tool` zawartość `panel_core.js`, potem `const g = await WT.pobierzGrupy(1); const l = await WT.pobierzListe('make_order', 1); const e = await WT.pobierzEdycje('order_confirmation', 1); ({grupy: g.length, lista: l.length, sekcja: l[0].sekcja, e})`.
Expected: `grupy` ≥ 15 (więcej = linki grup ustawień też pasują do `populate=list`; to nieszkodliwe, bo ich strony nie mają tabel z kolumnami kanałów — zanotuj liczbę w Task 0 Step 6), `lista` = 11, `sekcja` = „Zamówienia” albo `''` (gdy nagłówki sekcji nie są `H1–H6` — pole jest informacyjne; zanotuj w Task 0 Step 6), `e.formularz.mail` = `{pol: 'y', ukr: 'y', eng: 'y'}`, `e.ostatnia_edycja.data` zaczyna się od `2026-`. Potem `await WT.eksportuj({shop: 1, templates: ['order_confirmation']})` → w `%USERPROFILE%\Downloads` pojawia się `eksport_zooart6_shop1_*.zip`; `python wiadomosci.py rozpakuj "%USERPROFILE%\Downloads\eksport_zooart6_shop1_<data>.zip"` → `[OK] Rozpakowano 1 wiadomości`, a ZIP jest już w `_pobrane/`, nie w Pobranych. Usuń ten testowy folder eksportu po sprawdzeniu.

- [ ] **Step 6: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/przegladarka/panel_core.js" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/przegladarka/testy/test_core.mjs"
git commit -m "Wiadomości transakcyjne: rdzeń przeglądarkowy i eksport z panelu"
```

---

### Task 9: Sterowanie formularzami, bookmarklet i instrukcja instalacji

**Files:**
- Modify: `przegladarka/panel_core.js` (dopisanie sekcji „zapis w panelu” przed blokiem `module.exports`)
- Create: `przegladarka/bookmarklet_ui.js`, `przegladarka/zbuduj_bookmarklet.py`, `przegladarka/INSTALACJA_BOOKMARKLETU.md`
- Generated (gitignore nie dotyczy, commitujemy): `przegladarka/bookmarklet.txt`, `przegladarka/konsola.js`
- Test: `testy/test_bookmarklet.py`

**Interfaces:**
- Consumes: `WT.*` z Task 8; formaty planów z Task 3 i 4; elementy DOM z Task 0 §11.
- Produces: `WT.importujIcf({shop, template, jezyk, nazwaPliku, xml}) -> Promise<string>` (komunikat sukcesu); `WT.zapiszFlagi({shop, template, mail: {jezyk: 'y'|'n'}, sms: 'y'|'n'|null}) -> Promise<void>`; `WT.zastosujPlan(plan, mapaPlikow: {nazwa: File}, opcje: {shop, loguj}) -> Promise<{wykonane, pominiete, reczne: string[]}>`; `WTUI.pokaz()` (menu bookmarkletu).

- [ ] **Step 1: Dopisz do `panel_core.js`** (przed `if (typeof module !== 'undefined' …)`):

```js
  // ---------- zapis w panelu (tylko bookmarklet: ukryta ramka iframe z formularzami panelu) ----------

  WT.ramka = function () {
    var f = document.getElementById('wt-ramka');
    if (!f) {
      f = document.createElement('iframe');
      f.id = 'wt-ramka';
      f.style.cssText = 'position:fixed;left:-5000px;top:0;width:1300px;height:900px;border:0;';
      document.body.appendChild(f);
    }
    return f;
  };
  function dok() { var f = WT.ramka(); return f.contentDocument; }

  async function czekajNa(warunek, ms, opis) {
    var koniec = Date.now() + (ms || 20000);
    while (Date.now() < koniec) {
      var w = null;
      try { w = warunek(); } catch (e) { w = null; }
      if (w) return w;
      await czekaj(200);
    }
    throw new Error('Panel nie odpowiedział: ' + (opis || 'element'));
  }

  function widocznyZTekstem(d, selektor, wzor) {
    if (!d) return null;
    var e = d.querySelectorAll(selektor);
    for (var i = 0; i < e.length; i++) {
      var t = tekstEl(e[i]) || e[i].value || '';
      if (wzor.test(t) && e[i].offsetParent !== null) return e[i];
    }
    return null;
  }

  function sprawdzSesje(d) {
    if (d && /^\s*Logowanie u/.test(d.title || '')) throw bladSesji();
  }

  async function zaladuj(url) {
    var f = WT.ramka(), stary = f.contentDocument;
    f.src = url;
    var d = await czekajNa(function () {
      var n = dok();
      return n && n !== stary && n.readyState === 'complete' && n.location.href !== 'about:blank' ? n : null;
    }, 60000, 'wczytanie strony');
    sprawdzSesje(d);
    return d;
  }

  function adresEdycji(template, shop) {
    return SCIEZKA + '?populate=edit&template=' + encodeURIComponent(template) + '&shop=' + shop;
  }

  WT.importujIcf = async function (p) {
    var d = await zaladuj(adresEdycji(p.template, p.shop));
    var link = widocznyZTekstem(d, 'a', /^Import ICF$/);
    if (!link) throw new Error('Brak linku „Import ICF" (wiadomość wycofywana?)');
    // Panel bywa jeszcze w trakcie wczytywania i ignoruje pierwsze kliknięcie (ANALIZA §11) — ponawiamy do 3 razy.
    var pole = null;
    for (var proba = 0; proba < 3 && !pole; proba++) {
      link.click();
      try { pole = await czekajNa(function () { return dok().querySelector('input[type=file][name=idf_file]'); }, 5000, 'okno importu'); }
      catch (e) { if (proba === 2) throw e; }
    }
    var dt = new DataTransfer();
    dt.items.add(new File([p.xml], p.nazwaPliku, { type: 'text/xml' }));
    pole.files = dt.files;
    (await czekajNa(function () { return widocznyZTekstem(dok(), 'button, input[type=submit], input[type=button]', /^Wgraj plik$/); },
      15000, 'przycisk „Wgraj plik"')).click();
    var radio = await czekajNa(function () {
      return dok().querySelector('input[type=radio][name=lang][value="' + p.jezyk + '"]');
    }, 30000, 'wybór języka ' + p.jezyk);
    radio.click();
    (await czekajNa(function () { return widocznyZTekstem(dok(), 'button, input[type=submit], input[type=button]', /^Wybierz$/); },
      15000, 'przycisk „Wybierz"')).click();
    (await czekajNa(function () { return widocznyZTekstem(dok(), 'button, input[type=submit], input[type=button]', /^Tak$/); },
      30000, 'potwierdzenie „Tak"')).click();
    var komunikat = await czekajNa(function () {
      var t = tekstEl(dok().body);
      var m = t.match(/Import przebiegł pomyślnie[^.]*\./);
      return m ? m[0] : null;
    }, 30000, 'komunikat po imporcie');
    return komunikat;
  };

  WT.zapiszFlagi = async function (p) {
    var d = await zaladuj(adresEdycji(p.template, p.shop));
    function ustaw(nazwa, wartosc) {
      var r = d.querySelector('input[type=radio][name="' + nazwa + '"][value="' + wartosc + '"]');
      if (!r) throw new Error('Brak pola ' + nazwa + ' w formularzu ' + p.template);
      r.click();
    }
    for (var j in p.mail) if (Object.prototype.hasOwnProperty.call(p.mail, j)) ustaw('mail_lang[' + j + '][active_mail]', p.mail[j]);
    if (p.sms) ustaw('sms_lang[active]', p.sms);
    var zapisz = widocznyZTekstem(d, 'input[type=submit], button', /^Zapisz zmiany$/);
    if (!zapisz) throw new Error('Brak przycisku „Zapisz zmiany"');
    zapisz.click();
    await czekajNa(function () {
      var n = dok();
      return n !== d && n.readyState === 'complete' && /Zmiany zostały zapisane/.test(tekstEl(n.body)) ? n : null;
    }, 60000, 'potwierdzenie zapisu');
  };

  async function aktualny(template, shop, kopie) {
    for (var jezyk in kopie) {
      if (!Object.prototype.hasOwnProperty.call(kopie, jezyk)) continue;
      if (await WT.odcisk(await WT.pobierzIcf(template, shop, jezyk)) !== kopie[jezyk].odcisk) return jezyk;
    }
    return null;
  }

  WT.zastosujPlan = async function (plan, mapa, opcje) {
    var shop = opcje.shop, loguj = opcje.loguj || function () {};
    var innyCel = plan.domena !== location.hostname || String(plan.shop_id) !== String(shop);
    var wynik = { wykonane: 0, pominiete: 0, reczne: [], templates: [] };
    // Import ICF zawsze wyłącza mail w importowanym języku (ANALIZA §11) — włączamy z powrotem,
    // jeśli przed importem był włączony. Zapis formularzem po imporcie zachowuje wgraną treść.
    async function wlaczPoImporcie(template, jezyk, oczekiwane) {
      if (!oczekiwane || !oczekiwane.mail || oczekiwane.mail[jezyk] !== 'y') return;
      var mail = {};
      mail[jezyk] = 'y';
      await WT.zapiszFlagi({ shop: shop, template: template, mail: mail, sms: null });
      loguj('Ponownie włączono mail ' + jezyk + ' (import ICF wyłącza wysyłkę): ' + template);
    }
    async function plik(nazwa) {
      if (!mapa[nazwa]) throw new Error('W wybranym folderze brakuje pliku ' + nazwa);
      return await mapa[nazwa].text();
    }
    if (plan.rodzaj === 'konfiguracja') {
      if (innyCel) throw new Error('Plan konfiguracji pochodzi z ' + plan.domena + ' sklep ' + plan.shop_id + ' — wykonuj go tylko tam.');
      for (var i = 0; i < plan.zmiany.length; i++) {
        var z = plan.zmiany[i];
        var zmieniony = await aktualny(z.template, shop, z.kopie);
        if (zmieniony) { wynik.pominiete++; loguj('POMINIĘTO ' + z.nazwa + ': treść ' + zmieniony + ' zmieniona w panelu po eksporcie'); continue; }
        var jestFlag = false;
        for (var k in z.mail) if (Object.prototype.hasOwnProperty.call(z.mail, k)) jestFlag = true;
        if (jestFlag || z.sms) { await WT.zapiszFlagi({ shop: shop, template: z.template, mail: z.mail, sms: z.sms }); loguj('Zapisano flagi: ' + z.nazwa); }
        for (var jezyk in z.kopie) {
          if (!Object.prototype.hasOwnProperty.call(z.kopie, jezyk)) continue;
          var teraz = await WT.pobierzIcf(z.template, shop, jezyk);
          if (await WT.odcisk(teraz) === z.kopie[jezyk].odcisk) continue;
          await WT.importujIcf({ shop: shop, template: z.template, jezyk: jezyk, nazwaPliku: z.kopie[jezyk].plik, xml: await plik(z.kopie[jezyk].plik) });
          loguj('Przywrócono treść ' + jezyk + ' (zapis formularzem ją zmienił): ' + z.nazwa);
          await wlaczPoImporcie(z.template, jezyk, z.oczekiwane);
        }
        if (z.reset) wynik.reczne.push(z.nazwa + ' (' + z.template + '): „Wczytaj treść z szablonu domyślnego"');
        wynik.wykonane++; wynik.templates.push(z.template);
      }
    } else if (plan.rodzaj === 'import') {
      for (var p = 0; p < plan.pozycje.length; p++) {
        var poz = plan.pozycje[p];
        if (!innyCel) {
          var obecny = await WT.odcisk(await WT.pobierzIcf(poz.template, shop, poz.jezyk));
          if (obecny !== poz.odcisk_oryginalu) { wynik.pominiete++; loguj('POMINIĘTO ' + poz.nazwa + ' ' + poz.jezyk + ': zmieniona w panelu po eksporcie'); continue; }
        }
        var komunikat = await WT.importujIcf({ shop: shop, template: poz.template, jezyk: poz.jezyk, nazwaPliku: poz.plik, xml: await plik(poz.plik) });
        loguj('Zaimportowano ' + poz.nazwa + ' ' + poz.jezyk + ': ' + komunikat);
        await wlaczPoImporcie(poz.template, poz.jezyk, plan.oczekiwane_flagi[poz.template]);
        wynik.wykonane++;
        if (wynik.templates.indexOf(poz.template) < 0) wynik.templates.push(poz.template);
      }
    } else {
      throw new Error('Nieznany rodzaj planu: ' + plan.rodzaj);
    }
    if (wynik.templates.length) {
      loguj('Eksport weryfikacyjny…');
      await WT.eksportuj({ shop: shop, templates: wynik.templates, rodzaj: 'weryfikacja', onPostep: loguj });
    }
    return wynik;
  };
```

- [ ] **Step 2: Utwórz `przegladarka/bookmarklet_ui.js`**

```js
/* Menu bookmarkletu: Eksport / Eksport wybranych / Zastosuj plan. Wymaga WT z panel_core.js. */
(function (root) {
  'use strict';
  var WTUI = {};

  function el(tag, styl, tekst) {
    var e = document.createElement(tag);
    if (styl) e.style.cssText = styl;
    if (tekst) e.textContent = tekst;
    return e;
  }

  WTUI.pokaz = function () {
    if (!/\/panel\/config-messages\.php/.test(location.pathname)) {
      alert('Otwórz w panelu: Administracja → Konfiguracja wiadomości transakcyjnych, wybierz sklep i uruchom zakładkę ponownie.');
      return;
    }
    var stare = document.getElementById('wt-menu');
    if (stare) stare.remove();
    var okno = el('div', 'position:fixed;top:20px;right:20px;width:460px;max-height:85vh;overflow:auto;z-index:2147483647;' +
      'background:#fff;border:2px solid #1a7f4b;border-radius:8px;padding:14px;font:13px/1.4 Arial,sans-serif;color:#222;' +
      'box-shadow:0 6px 24px rgba(0,0,0,.25)');
    okno.id = 'wt-menu';
    okno.appendChild(el('div', 'font-weight:bold;font-size:15px;margin-bottom:8px', 'Wiadomości transakcyjne'));
    var shopWiersz = el('div', 'margin-bottom:8px', 'Sklep (shop): ');
    var shop = el('input', 'width:50px');
    shop.value = String(WT.shopZAdresu());
    shopWiersz.appendChild(shop);
    okno.appendChild(shopWiersz);
    var log = el('pre', 'white-space:pre-wrap;background:#f4f4f4;padding:8px;max-height:300px;overflow:auto;margin:8px 0 0');
    function loguj(t) { log.textContent += t + '\n'; log.scrollTop = log.scrollHeight; }
    function przycisk(tekst, akcja) {
      var b = el('button', 'margin:0 6px 6px 0;padding:6px 10px;cursor:pointer', tekst);
      b.onclick = async function () {
        var wszystkie = okno.querySelectorAll('button');
        for (var i = 0; i < wszystkie.length; i++) wszystkie[i].disabled = true;
        try { await akcja(); } catch (e) { loguj('BŁĄD: ' + e.message); }
        finally { for (var j = 0; j < wszystkie.length; j++) wszystkie[j].disabled = false; }
      };
      okno.appendChild(b);
      return b;
    }
    var nr = function () { return parseInt(shop.value, 10) || 1; };
    przycisk('Eksport wszystkich', function () { return WT.eksportuj({ shop: nr(), onPostep: loguj }); });
    przycisk('Eksport wybranych…', function () {
      var t = prompt('Kody wiadomości (template), oddzielone przecinkami:', '');
      if (!t) return Promise.resolve();
      var lista = t.split(','), templates = [];
      for (var i = 0; i < lista.length; i++) if (lista[i].trim()) templates.push(lista[i].trim());
      return WT.eksportuj({ shop: nr(), templates: templates, onPostep: loguj });
    });
    var wybor = el('input');
    wybor.type = 'file'; wybor.webkitdirectory = true; wybor.multiple = true; wybor.style.display = 'none';
    okno.appendChild(wybor);
    przycisk('Zastosuj plan…', function () {
      return new Promise(function (ok) {
        wybor.value = '';
        wybor.onchange = async function () {
          try { await zastosuj(wybor.files); } catch (e) { loguj('BŁĄD: ' + e.message); }
          ok();
        };
        wybor.click();
      });
    });
    przycisk('Zamknij', function () { okno.remove(); return Promise.resolve(); });
    okno.appendChild(log);
    document.body.appendChild(okno);

    async function zastosuj(pliki) {
      var mapa = {};
      for (var i = 0; i < pliki.length; i++) mapa[pliki[i].name] = pliki[i];
      var nazwa = mapa['plan_importu.json'] ? 'plan_importu.json' : (mapa['plan_konfiguracji.json'] ? 'plan_konfiguracji.json' : null);
      if (!nazwa) throw new Error('W folderze nie ma plan_importu.json ani plan_konfiguracji.json');
      var plan = JSON.parse(await mapa[nazwa].text());
      var opis = [];
      if (plan.rodzaj === 'import') for (var p = 0; p < plan.pozycje.length; p++) opis.push('• ' + plan.pozycje[p].nazwa + ' — ' + plan.pozycje[p].jezyk);
      else for (var z = 0; z < plan.zmiany.length; z++) opis.push('• ' + plan.zmiany[z].nazwa);
      var innyCel = plan.domena !== location.hostname || String(plan.shop_id) !== String(nr());
      var pytanie = (plan.rodzaj === 'import' ? 'Import treści' : 'Zmiany konfiguracji') + ' (' + opis.length + '):\n' +
        opis.slice(0, 30).join('\n') + (opis.length > 30 ? '\n…' : '') + '\n\nWykonać?';
      if (innyCel) {
        var wpis = prompt('UWAGA: plan pochodzi z ' + plan.domena + ' (sklep ' + plan.shop_id + '), a jesteś w ' +
          location.hostname + ' (sklep ' + nr() + ').\nŻeby wgrać tutaj, wpisz domenę docelową: ' + location.hostname);
        if (wpis !== location.hostname) { loguj('Anulowano (inny sklep).'); return; }
      }
      if (!confirm(pytanie)) { loguj('Anulowano.'); return; }
      var wynik = await WT.zastosujPlan(plan, mapa, { shop: nr(), loguj: loguj });
      loguj('Wykonane: ' + wynik.wykonane + ', pominięte: ' + wynik.pominiete);
      for (var r = 0; r < wynik.reczne.length; r++) loguj('RĘCZNIE: ' + wynik.reczne[r]);
      loguj('Zweryfikuj: run_wiadomosci.bat → „Weryfikacja po wykonaniu planu".');
    }
  };

  root.WTUI = WTUI;
})(window);
```

- [ ] **Step 3: Sprawdź zgodność z §11 analizy** — radio języka `name=lang`, `value=<kod>` (już w kodzie Step 1); „Wgraj plik"/„Wybierz" to `input[type=submit|button]`, „Tak" to `button` — `widocznyZTekstem` obsługuje oba (tekst albo `value`). Bez zmian w kodzie.

- [ ] **Step 4: Napisz test `testy/test_bookmarklet.py`**

```python
import os
import subprocess
import sys
import unittest
import urllib.parse

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKRYPT = os.path.join(KATALOG, "przegladarka", "zbuduj_bookmarklet.py")


class TestBookmarklet(unittest.TestCase):
    def test_budowanie(self):
        r = subprocess.run([sys.executable, SKRYPT], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(KATALOG, "przegladarka", "bookmarklet.txt"), encoding="utf-8") as p:
            zakladka = p.read().strip()
        self.assertTrue(zakladka.startswith("javascript:"))
        kod = urllib.parse.unquote(zakladka[len("javascript:"):])
        self.assertIn("WT.eksportuj", kod)
        self.assertIn("WTUI.pokaz()", kod)
        self.assertNotIn("module.exports = WT;\n  else", kod.replace("\r", ""))   # wariant przeglądarkowy
        with open(os.path.join(KATALOG, "przegladarka", "konsola.js"), encoding="utf-8") as p:
            self.assertIn("WTUI.pokaz()", p.read())
        node = subprocess.run(["node", "--check", os.path.join(KATALOG, "przegladarka", "konsola.js")],
                              capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Uruchom — FAIL** — `python -m unittest testy.test_bookmarklet -v` → FAIL (`can't open file … zbuduj_bookmarklet.py`).

- [ ] **Step 6: Utwórz `przegladarka/zbuduj_bookmarklet.py`**

```python
"""Skleja panel_core.js + bookmarklet_ui.js w zakładkę (bookmarklet.txt) i wariant do konsoli (konsola.js)."""

import os
import re
import urllib.parse

TU = os.path.dirname(os.path.abspath(__file__))


def czytaj(nazwa):
    with open(os.path.join(TU, nazwa), encoding="utf-8") as plik:
        return plik.read()


def main():
    rdzen = czytaj("panel_core.js")
    # W zakładce zawsze wariant przeglądarkowy: bez gałęzi module.exports.
    rdzen = re.sub(r"if \(typeof module !== 'undefined' && module\.exports\) module\.exports = WT;\s*else root\.WT = WT;",
                   "root.WT = WT;", rdzen)
    kod = rdzen + "\n" + czytaj("bookmarklet_ui.js") + "\nWTUI.pokaz();\n"
    with open(os.path.join(TU, "konsola.js"), "w", encoding="utf-8") as plik:
        plik.write(kod)
    zakladka = "javascript:" + urllib.parse.quote("(function(){" + kod + "})();", safe="")
    with open(os.path.join(TU, "bookmarklet.txt"), "w", encoding="utf-8") as plik:
        plik.write(zakladka + "\n")
    print("[OK] bookmarklet.txt (%d znaków) i konsola.js" % len(zakladka))


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Uruchom — PASS** — `python -m unittest testy.test_bookmarklet -v` → `OK`; `node --test przegladarka/testy/` → nadal `# fail 0`.

- [ ] **Step 8: Utwórz `przegladarka/INSTALACJA_BOOKMARKLETU.md`**

```markdown
# Instalacja bookmarkletu „Wiadomości transakcyjne"

1. Ustawień pobierania Chrome nie zmieniasz — eksport trafia do zwykłego folderu `Pobrane`
   (`C:\Users\Admin\Downloads`), a `run_wiadomosci.bat` sam go stamtąd zabiera do `_pobrane\` w projekcie.
   Jeśli w Chrome włączone jest „Pytaj, gdzie zapisać każdy plik", przy eksporcie zostaw proponowany folder `Pobrane`.
2. Pokaż pasek zakładek (Ctrl+Shift+B) → prawy klik → **Dodaj stronę…**
   - Nazwa: `Wiadomości transakcyjne`
   - URL: cała zawartość pliku `bookmarklet.txt` (Ctrl+A, Ctrl+C w Notatniku).
3. Użycie: panel → Administracja → Konfiguracja wiadomości transakcyjnych → wybierz sklep → kliknij zakładkę.
   - **Eksport wszystkich** — jeden ZIP do `Pobrane`, potem `run_wiadomosci.bat` → „Rozpakuj eksport (z Pobranych)".
   - **Zastosuj plan…** — wskaż folder planu przygotowany przez `run_wiadomosci.bat` (`zmiany_…` albo `do_importu_…`).
     Po zakończeniu pobierze się `weryfikacja_….zip` → `run_wiadomosci.bat` → „Weryfikacja po wykonaniu planu".
4. Gdyby Chrome nie przyjął długiej zakładki: otwórz konsolę (F12 → Console), wklej zawartość `konsola.js`, Enter.
5. Po zmianie kodu: `python przegladarka\zbuduj_bookmarklet.py` i podmień URL zakładki.
```

- [ ] **Step 9: Test bookmarkletu na panelu — tylko eksport (odczyt).** Użytkownik dodaje zakładkę (Step 8), otwiera `…/config-messages.php?populate=types&shop=1` i klika „Eksport wybranych…” z `order_confirmation`. Expected: ZIP w `%USERPROFILE%\Downloads`; `run_wiadomosci.bat` → „Rozpakuj eksport (z Pobranych)" pokazuje go jako `[Pobrane] eksport_…zip`, rozpakowanie → OK, ZIP przeniesiony do `_pobrane/`. Zapis (Zastosuj plan) testujemy dopiero w Task 11.

- [ ] **Step 10: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/przegladarka" "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/testy/test_bookmarklet.py"
git commit -m "Wiadomości transakcyjne: bookmarklet z eksportem i wykonaniem planów"
```

---

### Task 10: Skill Claude in Chrome

**Files:**
- Create: `.claude/skills/wiadomosci-transakcyjne/SKILL.md` (korzeń repozytorium)

**Interfaces:**
- Consumes: `przegladarka/konsola.js` / `panel_core.js` (eksport przez `javascript_tool`), polecenia CLI z Task 7, formaty planów z Task 3–4.

- [ ] **Step 1: Utwórz `.claude/skills/wiadomosci-transakcyjne/SKILL.md`**

````markdown
---
name: wiadomosci-transakcyjne
description: Status, edycja działania (które maile/SMS w jakich językach są wysyłane) oraz eksport i import treści wiadomości transakcyjnych w panelu IdoSell przez Claude in Chrome. Używaj, gdy użytkownik prosi o raport wiadomości transakcyjnych, włączenie/wyłączenie wiadomości, eksport/import/tłumaczenie treści wiadomości albo migrację wiadomości między sklepami.
---

# Wiadomości transakcyjne IdoSell

Folder narzędzia: `SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/` (dalej KATALOG). Specyfikacja: `ANALIZA_wiadomosci_transakcyjne.md`.

## Zasady bezpieczeństwa (zawsze)
- Panel: `https://<domena>/panel/config-messages.php`. Użytkownik loguje się sam; ja nie wpisuję haseł.
- Przed KAŻDYM zapisem w panelu: eksport ICF wiadomości na dysk (krok „Eksport") i zgoda użytkownika na listę zmian.
- Nigdy: „Ustaw domyślną treść wiadomości" (masowe), „Przywróć" z historii, wiadomości „wycofywane", Web Push.
- Zapis w panelu wykonuję przez interfejs (`file_upload` + kliknięcia), nie przez `fetch` POST.
- JS na stronie panelu: tylko zwykłe pętle (Prototype.js psuje `Array.from`, `filter`, iterację `Set`).
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
6. Inny sklep niż w planie (migracja) → wymaga wyraźnej zgody użytkownika z nazwą sklepu docelowego.

## Import ICF przez interfejs
1. `navigate` → strona edycji wiadomości; `find` „Import ICF" → kliknij (jeśli `ref` nie zadziała — kliknij we współrzędne z zrzutu).
2. `find` „file input idf_file" → `file_upload` z absolutną ścieżką pliku ICF.
3. „Wgraj plik" (strona się przeładuje) → wybór języka (`input[name=lang][value=<jezyk>]`) → „Wybierz" → „Tak" → „Import przebiegł pomyślnie. Szablon został zmieniony." → „OK".
4. **Import ICF ZAWSZE wyłącza mail w tym języku.** Jeśli przed importem mail był włączony (`oczekiwane_flagi` / `oczekiwane` w planie): `navigate` na stronę edycji → `javascript_tool`: `document.querySelector('input[type=radio][name="mail_lang[<jezyk>][active_mail]"][value="y"]').click()` → przewiń do „Zapisz zmiany" i kliknij we współrzędne widocznego przycisku (kliknięcie przez `ref` bywa ignorowane) → „Zmiany zostały zapisane".
5. Jeśli „Import ICF" nie otwiera okna (strona się wczytuje) — odczekaj 2 s i kliknij ponownie; sprawdź `!!document.querySelector('input[name=idf_file]')`.

## Fakty o panelu (z testów 2026-10-13)
- Import ICF dotyczy jednego języka; ZAWSZE wyłącza mail w tym języku (niezależnie od `active` w pliku); nie zostawia wpisu w historii zmian.
- Zapis formularzem tuż po imporcie zachowuje wgraną treść (panel zapisuje tytuł bez CDATA — porównuj wartości pól, nie odcisk wgranego pliku).
- „Zapisz zmiany" potrafi przepisać HTML widocznego języka — dlatego kopie i weryfikacja treści.
- Chrome blokuje drugie automatyczne pobranie — eksport zawsze jednym ZIP-em.
````

- [ ] **Step 2: Sprawdź, że skill się ładuje** — w nowej sesji Claude Code w repozytorium skill `wiadomosci-transakcyjne` jest na liście dostępnych skilli (system-reminder). Jeśli nie — popraw frontmatter (`name`, `description`).

- [ ] **Step 3: Commit**

```bash
git add ".claude/skills/wiadomosci-transakcyjne/SKILL.md"
git commit -m "Wiadomości transakcyjne: skill Claude in Chrome"
```

---

### Task 11: Test całościowy na panelu testowym (wymaga zgody użytkownika)

**Files:**
- Modify: `ANALIZA_wiadomosci_transakcyjne.md` (sekcja `## 12. Test całościowy`)
- Modify: `C:\Users\Admin\.claude\projects\C--Users-Admin-Desktop-Domino\memory\project-wiadomosci-transakcyjne.md` (stan projektu)

- [ ] **Step 1: Zgoda użytkownika** na: wyłączenie i ponowne włączenie maila eng w `order_confirmation` oraz import zmienionego tytułu eng (i powrót) — sklep 1, `zooart6`. Bez „tak" — stop.

- [ ] **Step 2: Status** — bookmarklet „Eksport wszystkich" → `run_wiadomosci.bat` → Rozpakuj → Raport Status. Expected: raport z ~144 wiadomościami, w sekcji „Kopie tłumaczeń" pozycja „Potwierdzenie wpłynięcia zamówienia, ukr: tytuł maila identyczny z pol".

- [ ] **Step 3: Edycja działania (bookmarklet)** — CSV → `mail_eng` = `nie` dla `order_confirmation` → „Zmiany konfiguracji" → bookmarklet „Zastosuj plan" → `weryfikuj`. Expected: `flaga mail eng: OK`, `treść *: OK` (albo zalogowane „Przywrócono treść …" i potem OK). Potem to samo z `mail_eng` = `tak` (przywrócenie).

- [ ] **Step 4: Import treści (skill)** — w eksporcie zmień `meta.json` → `tytuly.eng` (dopisz „ [TEST]") → `tresci --tak` → import przez interfejs wg skilla → `weryfikuj`. Expected: `mail.title: OK`, brak problemów z flagami. Potem przywróć oryginalny tytuł tą samą ścieżką.

- [ ] **Step 5: Dopisz `## 12. Test całościowy`** do analizy: data, każdy krok z wynikiem weryfikacji (OK / problemy), odstępstwa od planu. Zaktualizuj pamięć projektu (stan: zaimplementowane, co przetestowane).

- [ ] **Step 6: Commit**

```bash
git add "SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/ANALIZA_wiadomosci_transakcyjne.md"
git commit -m "Wiadomości transakcyjne: wyniki testu całościowego"
```
