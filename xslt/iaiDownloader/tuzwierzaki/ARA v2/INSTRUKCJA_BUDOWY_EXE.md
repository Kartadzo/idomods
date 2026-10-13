# ARA v2 — kompletny runbook: od zera do `dystrybucja\ARA v2.exe`

Dokument **samowystarczalny**: zawiera wszystko, co potrzebne, aby odtworzyć
`ara_app.py` oraz zbudować `dystrybucja\ARA v2.exe`, **bez zaglądania do
pozostałych plików tego folderu**. Wklejone są pełne treści obu szablonów XSLT,
schemat `config.json`, struktura feedu wejściowego i specyfikacja aplikacji z
krytycznymi fragmentami kodu.

Dokument służy też jako wzorzec dla **kolejnej aplikacji tego typu**, różniącej
się skryptem `.py`, linkiem do źródła danych, szablonami, nazwą i ikoną —
sekcja 12 zbiera, co trzeba podmienić.

---

## 1. Co powstaje

Dwa artefakty:

| Artefakt | Skąd | Rola |
|---|---|---|
| `ara_app.py` | napisany według sekcji 3–7 | źródło aplikacji GUI (Tkinter) |
| `dystrybucja\ARA v2.exe` | PyInstaller, sekcja 9 | jeden samodzielny plik, działa na maszynach **bez Pythona i bibliotek** |

Aplikacja: co N minut pobiera feed XML dostawcy ARA, wyciąga listę marek,
a dla marek zaznaczonych w GUI generuje `output.csv` z cenami powiększonymi
o ustawioną marżę. Plik CSV jest wsadem do synchronizacji w IdoSell.

---

## 2. Wymagania środowiska (jednorazowo na maszynie budującej)

- **Python 64-bit** (referencyjnie 3.11) — exe dziedziczy architekturę maszyny
  budującej, więc buduj pod docelowy system (Windows 64-bit).
- Tkinter musi być w instalacji Pythona (standardowo jest w instalatorze
  python.org dla Windows).

```powershell
python -m pip install --upgrade pyinstaller lxml requests
python -m PyInstaller --version    # weryfikacja (referencyjnie 6.14.2)
```

Zależności runtime: `requests` (HTTP), `lxml` (parsowanie XML + XSLT 1.0),
`tkinter` + `csv`, `json`, `queue`, `threading` ze standardowej biblioteki.

> `lxml` jest wymagany, bo `xml.etree` nie umie XSLT. Transformacja to XSLT 1.0,
> więc `lxml`/libxslt wystarcza (Saxon niepotrzebny).

---

## 3. Dane wejściowe — feed dostawcy ARA

**URL** (wkompilowywany w exe jako stała `XML_URL`; parametry `_gl` to
pozostałość po sesji GA, działa też bez nich):

```
https://ara.waw.pl/wymiana/ara.xml?_gl=1*14loj5u*_ga*MjIwMDk5NDAuMTc1MjUwMTk4MQ..*_ga_2QRB642E1C*czE3NTI1MDE5ODAkbzEkZzEkdDE3NTI1MDIwNjUkajU5JGwwJGgxNzk4NjM0OTUw
```

**Uwaga:** to **nie** jest format IOF IdoSell. To płaski XML dostawcy:

```xml
<produkty>
  <produkt>
    <producent>4DOGS</producent>            <!-- marka; klucz filtrowania -->
    <kod_kreskowy>5904181401012</kod_kreskowy>
    <cena_tylko_brutto>11,85 PLN</cena_tylko_brutto>  <!-- przecinek + " PLN" -->
    <stan>4</stan>
    ...
  </produkt>
</produkty>
```

Konsekwencje dla XSLT (już uwzględnione w szablonach z sekcji 4):
- cena wymaga `translate(..., ', PLN;', '.')` — zamiana przecinka na kropkę
  i usunięcie sufiksu waluty,
- `stan` też może mieć przecinek,
- feed bywa niepoprawny składniowo → parser musi mieć `recover=True`.

---

## 4. Szablony XSLT (pełna treść — utwórz oba pliki)

Leżą **obok** `.py`/`.exe`, nie są pakowane do środka (sekcja 10).

### 4.1 `synch_template_brands.xml` — lista marek

Emituje jedno `<marka>` na produkt; deduplikację robi już Python.

```xml
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:iof="http://www.iai-shop.com/developers/iof.phtml"
                xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                xmlns:php="http://php.net/xsl">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />

    <xsl:template match="/">
        <rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
            <channel>
                <xsl:for-each select="/produkty/produkt">
                    <item>
                        <marka>
                            <xsl:value-of select="producent/." />
                        </marka>
                    </item>
                </xsl:for-each>
            </channel>
        </rss>
    </xsl:template>
</xsl:stylesheet>
```

### 4.2 `synch_template.xml` — właściwy feed do CSV

Zawartość `<xsl:variable name='nazwa_marki_i_doliczany_marza'>` jest w czasie
działania **podmieniana w pamięci** przez aplikację (plik na dysku pozostaje
nietknięty) — wartości poniżej to tylko przykład/fallback.

```xml
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:iof="http://www.iai-shop.com/developers/iof.phtml"
                xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml"
                xmlns:php="http://php.net/xsl">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" />

    <xsl:variable name='nazwa_marki_i_doliczany_marza'>
        |4DOGS|50%|
        |8in1|10%|
    </xsl:variable>

    <xsl:template match="/">
        <rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
            <channel>
                <xsl:for-each select="/produkty/produkt[
                        contains($nazwa_marki_i_doliczany_marza, concat('|',producent/.,'|'))]">
                    <xsl:variable name='doliczana_marza_procent'>
                        <xsl:value-of select="substring-before(substring-after($nazwa_marki_i_doliczany_marza, concat('|',producent/.,'|')), '%')" />
                    </xsl:variable>
                    <xsl:variable name='doliczana_marza_doObliczen'>
                        <xsl:value-of select="1 - (number($doliczana_marza_procent) div 100)" />
                    </xsl:variable>
                    <item>
                        <kodProducenta>
                            <xsl:value-of select="kod_kreskowy/." />
                        </kodProducenta>
                        <cena_detaliczna>
                            <xsl:value-of select="format-number(number(translate(cena_tylko_brutto/., ', PLN;', '.')) div $doliczana_marza_doObliczen, '#.##')" />
                        </cena_detaliczna>
                        <KosztWlasnySprzedazyTowarow_cenaMinimalna>
                            <xsl:value-of select="format-number(number(translate(cena_tylko_brutto/., ', PLN;', '.')), '#.##')" />
                        </KosztWlasnySprzedazyTowarow_cenaMinimalna>
                        <idMagazynu><![CDATA[0]]></idMagazynu>
                        <stanMagazynu>
                            <xsl:choose>
                                <xsl:when test="number(translate(stan/., ',', '.')) > 1">
                                    <xsl:value-of select="number(translate(stan/., ',', '.'))" />
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="0" />
                                </xsl:otherwise>
                            </xsl:choose>
                        </stanMagazynu>
                        <marka>
                            <xsl:value-of select="producent/." />
                        </marka>
                    </item>
                </xsl:for-each>
            </channel>
        </rss>
    </xsl:template>
</xsl:stylesheet>
```

**Model marży:** marża jest **doliczana od ceny detalicznej**, nie narzutem na
koszt — `cena_detaliczna = cena_zakupu / (1 - marża/100)`. Dlatego marża musi
być `< 100` (przy 100 dzielenie przez zero).

**Format zmiennej marż** — jedna para na linię, potokowa (`|`) delimitacja
umożliwia dopasowanie całej nazwy marki:

```
|4DOGS|50%|
|8in1|10%|
```

### 4.3 Nazwa zmiennej — twardy kontrakt

Stała `MARGIN_VAR` w Pythonie musi być **bajt w bajt** równa atrybutowi `name`
zmiennej w `synch_template.xml`. Jeśli się rozjadą, aplikacja w trybie pracy
cyklicznej rzuca `RuntimeError: W szablonie synch_template.xml nie znaleziono
zmiennej "..."` (i nic nie zapisze), choć pobieranie listy marek nadal działa —
błąd ujawnia się dopiero po zapisaniu konfiguracji.

Kanoniczna wartość w tym runbooku: **`nazwa_marki_i_doliczany_marza`**
(bez znaków diakrytycznych). Przy tworzeniu nowego szablonu **nie używaj
polskich znaków w nazwie zmiennej** — eliminuje to klasę problemów z
kodowaniem między plikiem `.py` i `.xml`.

---

## 5. `ara_app.py` — stałe i tryb „frozen”

Nagłówek pliku (`#!/usr/bin/env python3`, `# -*- coding: utf-8 -*-`, docstring
po polsku), potem importy: `csv, io, json, os, queue, sys, threading, time,
tkinter as tk`, `from tkinter import messagebox, ttk`, `requests`,
`from lxml import etree`.

### 5.1 `BASE_DIR` — poprawka WYMAGANA dla exe

Po spakowaniu `--onefile` `__file__` wskazuje **tymczasowy** katalog
rozpakowania (`_MEIPASS`), a nie folder z exe. Aplikacja czyta **i zapisuje**
pliki obok siebie, więc bez tej poprawki exe nie znajdzie szablonów i nie
zapisze wyników:

```python
if getattr(sys, 'frozen', False):          # uruchomienie jako spakowany .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:                                       # uruchomienie jako .py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

Wszystkie ścieżki liczone od `BASE_DIR`. Uruchamianie przez `python ara_app.py`
działa po tej zmianie identycznie jak wcześniej.

### 5.2 Pełny zestaw stałych

```python
XML_URL = ( ... )                                    # patrz sekcja 3

XSLT_MAIN   = os.path.join(BASE_DIR, 'synch_template.xml')
XSLT_BRANDS = os.path.join(BASE_DIR, 'synch_template_brands.xml')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
OUT_CSV     = os.path.join(BASE_DIR, 'output.csv')

XSL_NS        = 'http://www.w3.org/1999/XSL/Transform'
MARGIN_VAR    = 'nazwa_marki_i_doliczany_marza'      # patrz 4.3
RECORD_TAG    = 'item'
CSV_DELIMITER = ','

DEFAULT_INTERVAL_MIN = 30
MIN_INTERVAL_MIN     = 1
MAX_INTERVAL_MIN     = 1440
HTTP_TIMEOUT         = 30
```

Paleta kolorów GUI (stałe `C_*`), jasny motyw:

```python
C_BG='#f4f6f8'; C_CARD='#ffffff'; C_LINE='#dfe4ea'; C_TEXT='#1f2933'
C_MUTED='#6b7684'; C_ACCENT='#0b6bcb'
C_NEW_BG='#fff6e0'; C_NEW_FG='#9a6700'      # znacznik „NOWA”
C_GONE_BG='#fdeced'; C_GONE_FG='#b3261e'    # marki nieobecne w feedzie
C_OK='#1a7f4b'; C_ERR='#b3261e'; C_ROW_ALT='#fafbfc'
```

---

## 6. `ara_app.py` — warstwa danych

Siedem funkcji modułowych, bez stanu globalnego.

**`_parser()`** → `etree.XMLParser(encoding='utf-8', recover=True)`.
`recover=True` jest konieczne — feed dostawcy bywa niepoprawny.

**`fetch_feed()`** — `requests.get(XML_URL, timeout=HTTP_TIMEOUT)`,
`raise_for_status()`, `etree.parse(io.BytesIO(resp.content), _parser())`.
Parsujemy z bajtów, nie z `resp.text` — deklaracja XML rozstrzyga kodowanie.

**`extract_brands(xml_tree)`** — transformacja `synch_template_brands.xml`,
potem zebranie `.//*[local-name()="marka"]`, `strip()`, zbiór, sortowanie
`key=lambda s: s.lower()`. **Marki zawierające `|` są pomijane** — pionowa
kreska jest separatorem w zmiennej XSLT i taki rekord zepsułby dopasowanie.

**`build_margin_variable(enabled)`** — składa treść zmiennej z par
`(marka, marża)`; puste stringi na początku i końcu dają wiodący/kończący
znak nowej linii:

```python
lines = ['']
for brand, margin in enabled:
    lines.append('|{}|{:g}%|'.format(brand, margin))
lines.append('')
return '\n'.join(lines)
```

`{:g}` daje `50` zamiast `50.0` — XSLT porównuje tekstowo, więc format ma
znaczenie.

**`build_main_transform(enabled)`** — wczytuje `synch_template.xml`, szuka
**wśród dzieci korzenia** elementu `{XSL_NS}variable` o `name == MARGIN_VAR`,
usuwa jego dzieci, wstawia nowy `text`, zwraca `etree.XSLT(tree)`. Jeśli
zmiennej nie ma → `RuntimeError` z nazwą pliku i zmiennej (sekcja 4.3).
Podmiana odbywa się **tylko w drzewie w pamięci** — plik na dysku nietknięty.

**`write_csv(result_tree)`** → liczba rekordów. Nagłówki to nazwy
bezpośrednich dzieci **pierwszego** `<item>` (kolejność zachowana, duplikaty
odfiltrowane); wartości pobierane per kolumna przez
`./*[local-name()="..."]`, brak elementu → puste pole. Brak rekordów →
zapisuje **pusty plik** i zwraca 0. Zapis: `newline=''`,
`encoding='utf-8'`, `csv.writer(delimiter=',')`.

**`load_config()`** → `(interwał, {marka: {'enabled': bool, 'margin': float}})`.
Odporna na wszystko: brak pliku, `OSError`, niepoprawny JSON, zła wartość
interwału → zwraca `(DEFAULT_INTERVAL_MIN, {})`. Interwał docinany do
`[MIN, MAX]`. Wpisy marek nie będące dict-ami — pomijane; nieparsowalna marża
→ `0.0`.

**`save_config(interval, brands)`** — `json.dump(..., ensure_ascii=False,
indent=2)`. `ensure_ascii=False` jest istotne: nazwy marek mają polskie znaki.

### 6.1 `config.json` — schemat

Tworzy się sam przy pierwszym zapisie; brak pliku = konfiguracja domyślna.

```json
{
  "interval_minutes": 60,
  "brands": {
    "4DOGS":   { "enabled": true,  "margin": 50.0 },
    "8in1":    { "enabled": true,  "margin": 50.0 },
    "ADBI":    { "enabled": false, "margin": 0.0  }
  }
}
```

Do CSV trafiają wyłącznie marki z `enabled: true`. Marki nieobecne w ostatnim
pobranym feedzie są **usuwane z configu przy zapisie** (GUI ostrzega o tym
przed zapisem).

### 6.2 `output.csv` — wynik

```csv
kodProducenta,cena_detaliczna,KosztWlasnySprzedazyTowarow_cenaMinimalna,idMagazynu,stanMagazynu,marka
5904181401012,23.7,11.85,0,4,4DOGS
```

Kolumny wynikają wyłącznie ze struktury `<item>` w `synch_template.xml` —
zmiana szablonu zmienia CSV bez zmian w kodzie Pythona.

---

## 7. `ara_app.py` — GUI i współbieżność

### 7.1 Dwa widoki jednego okna

Okno `tk.Tk` (`760x640`, `minsize 640x540`), tytuł
`ARA – generator output.csv`, motyw ttk `clam`, styl `Accent.TButton`
(niebieski, pogrubiony). Nagłówek: „Dostawca ARA” + etykieta trybu.
Stopka: pasek statusu kolorowany (`C_MUTED` / `C_OK` / `C_ERR` / `C_ACCENT`).

Oba widoki budowane raz w `_build_ui()`, przełączane
`pack()` / `pack_forget()`; `self.mode ∈ {'edit', 'running'}`.

**Widok „konfiguracja” (`edit`)** — lista marek do zaznaczenia:
- pole „Szukaj” z `trace_add('write', ...)` → filtrowanie w locie,
- przewijalny kontener `ScrollFrame` (Canvas + Scrollbar + wewnętrzna ramka;
  `<MouseWheel>` bindowany na `<Enter>`, odbindowany na `<Leave>`, żeby kółko
  nie przewijało listy, gdy kursor jest poza nią),
- wiersz `BrandRow` = Checkbutton + nazwa marki + `ttk.Spinbox` (0–99, krok 5)
  + `%`; wyłączona marka ma **zablokowany** spinbox i wyszarzoną nazwę
  (`_sync_state()` jako `command` checkbuttona),
- naprzemienne tła wierszy (`C_CARD` / `C_ROW_ALT`),
- **trzy sekcje w tej kolejności:** „Nowe marki od ostatniej konfiguracji (n)”
  (żółte, z odznaką `NOWA`), „Nieobecne w feedzie – zostaną zapomniane po
  zapisie (n)” (czerwone, przekreślone, tylko gdy pole szukania jest puste),
  „Znane marki (n)”,
- licznik pod listą: `Marek w feedzie: n | nowych: n | do zapomnienia: n`,
- przed pierwszym udanym pobraniem: „Pobieranie listy marek…”,
- przycisk **Zapisz**.

**Widok „praca cykliczna” (`running`)**:
- duży licznik odliczania `MM:SS` (`Consolas 30 bold`) — „Do następnego
  odświeżenia”,
- `Spinbox` interwału (1–1440 min, krok 5) + przycisk **Zastosuj**,
- przycisk **Odśwież teraz**,
- `ttk.Treeview` (kolumny „Marka”, „Doliczana marża”, `selectmode='none'`) —
  podgląd zapisanej konfiguracji, tylko włączone marki,
- etykieta „Ostatni zapis: HH:MM:SS (n rekordów)”,
- przycisk **Edytuj** → powrót do konfiguracji.

### 7.2 Jeden trwały wątek roboczy — nie zmieniać

`self.jobs` / `self.results` (`queue.Queue`) + **jeden** wątek `ara-worker`
(`daemon=True`) startowany w `__init__`.

> **Powód:** osobny wątek na każdy cykl powodował **zakleszczenie libxml2 przy
> trzeciej z kolei transformacji XSLT**. Cała praca z `lxml` musi zostać na tym
> jednym wątku. Wątek nie dotyka widgetów — wynik wraca kolejką `results`,
> którą wątek główny odpytuje w `_poll_queue()` co 100 ms.

Zlecenie: krotka `(generate, enabled, initial)`; sentinel `None` kończy wątek.
Pętla wątku łapie `Exception` i wkłada je do `results` — komunikat trafia na
pasek statusu, aplikacja nie ubija się na błędzie sieci.

```python
def _job_worker(self):
    while True:
        job = self.jobs.get()
        if job is None:
            return
        generate, enabled, initial = job
        try:
            tree = fetch_feed()
            brands = extract_brands(tree)
            rows = None
            if generate:
                rows = write_csv(build_main_transform(enabled)(tree))
            self.results.put((brands, rows, initial, None))
        except Exception as exc:
            self.results.put((None, None, initial, exc))
```

### 7.3 Harmonogram i porządkowanie `after()`

Pomocnik `_schedule(key, delay_ms, callback)` zapamiętuje uchwyt pod **stałym
kluczem** — cykliczne callbacki nadpisują swój wpis, więc słownik nie puchnie
przy długiej pracy. Trzy pętle startowane w `__init__`:
`start` (200 ms, pierwsze pobranie z `initial=True`), `poll` (100 ms),
`tick` (1000 ms).

`_on_close()` (`WM_DELETE_WINDOW`): flaga `_closing`, `after_cancel` wszystkich
uchwytów (łapiąc `tk.TclError`), sentinel `None` do `jobs`, `quit()`,
`destroy()`. Wątki są demonami, więc nie wstrzymają wyjścia z procesu —
anulowanie callbacków chroni przed odpaleniem ich na zniszczonych widgetach.

### 7.4 Reguły zachowania (łatwe do przeoczenia)

- W trybie `edit` cykl pobiera **tylko** feed (odświeżenie listy marek);
  `output.csv` generowany jest wyłącznie w trybie `running`.
- Gdy cykl trwa (`busy`), kolejne zlecenie ustawia flagę `_rerun` i wykonuje
  się zaraz po zakończeniu bieżącego — wejście w edycję nigdy nie zostaje bez
  świeżej listy.
- W trybie `edit` lista jest przerysowywana **tylko gdy zestaw marek się
  zmienił** (albo przy pierwszym pobraniu) — inaczej odświeżanie w tle
  przestawiałoby widok pod palcami użytkownika.
- Przed zniszczeniem widgetów listy stan jest przepisywany do `brands_cfg`
  (`_harvest_rows(strict=False)`) — filtrowanie i przerysowanie nie gubią
  zmian; `strict=True` (przy zapisie) zwraca wiersz z błędną marżą.
- Marża: przecinek dopuszczalny, `%` obcinane, puste pole = `0.0`, zakres
  `0 ≤ x < 100`, poza zakresem → `messagebox` + fokus na winnym spinboksie.
- Zapis bez żadnej zaznaczonej marki → `askyesno` „output.csv będzie pusty”.
- „Zastosuj” interwał: waliduje `[1, 1440]`, zapisuje config i **przelicza
  termin następnego cyklu** od teraz.
- `_tick`: przy `00:00` odpala cykl, o ile `busy` jest wolne.
- `main()` **przed** utworzeniem okna sprawdza istnienie obu szablonów; brak →
  `messagebox.showerror` na ukrytym rootcie + `sys.exit(1)`. To zabezpieczenie
  przed uruchomieniem exe wyrwanego z folderu dystrybucyjnego.

---

## 8. Uruchomienie w trybie dev

`run_ara_app.bat` obok `.py` (`pythonw` = bez okna konsoli):

```bat
@echo off
chcp 65001 > nul
cd /d "%~dp0"
start "" pythonw ara_app.py
```

Albo `python ara_app.py` z katalogu, w którym leżą szablony.

---

## 9. Ikona

Ikonę wzięto z ikony skrótu `Aplikacja.lnk` → plik `app.ico`.

```powershell
# odczyt ścieżki ikony ze skrótu
$ws = New-Object -ComObject WScript.Shell
$ws.CreateShortcut("C:\...\Aplikacja.lnk").IconLocation   # np. C:\...\app.ico,0

# weryfikacja nagłówka .ico (poprawny zaczyna się od 00 00 01 00)
$b = [System.IO.File]::ReadAllBytes("C:\...\app.ico")[0..3]
if (($b -join ',') -eq '0,0,1,0') { "ICO OK" } else { "NIE jest to poprawny .ico" }
```

PyInstaller wymaga pliku **`.ico`** — nie `.lnk`, nie `.png`. Kopia ikony leży
w tym folderze jako `app.ico`.

---

## 10. Build (PyInstaller)

```powershell
# --- Parametry (podmień dla nowej aplikacji) ---
$Skrypt = "ara_app.py"                                   # główny plik .py
$Nazwa  = "ARA v2"                                        # nazwa exe (bez .exe)
$Ikona  = "C:\Users\Admin\Desktop\facebook_google_v4_formatowanie-danych-main\data\app.ico"
$Zrodlo = "C:\Users\Admin\Desktop\Domino\xslt\iaiDownloader\tuzwierzaki\ARA v2"
$Dyst   = "$Zrodlo\dystrybucja"                           # tu wyląduje exe
$Tmp    = "$env:TEMP\pyi_build"                           # pliki robocze i .spec

# --- Build ---
Set-Location $Zrodlo
python -m PyInstaller --onefile --windowed --name $Nazwa --icon $Ikona `
  --distpath $Dyst --workpath "$Tmp\build" --specpath $Tmp `
  --hidden-import lxml._elementpath --noconfirm $Skrypt
```

| Flaga | Po co |
|---|---|
| `--onefile` | jeden samodzielny plik exe (~16 MB) |
| `--windowed` | aplikacja GUI (Tkinter) — bez okna konsoli. **Dla aplikacji konsolowej pomiń.** |
| `--name` | nazwa pliku wynikowego |
| `--icon` | ikona exe (`.ico`) |
| `--distpath` | katalog wynikowy (kierujemy prosto do folderu dystrybucyjnego) |
| `--workpath` / `--specpath` | pliki robocze i `.spec` poza projektem (czysty katalog źródłowy) |
| `--hidden-import lxml._elementpath` | asekuracyjnie dla `lxml`. **Pomiń, jeśli skrypt nie używa `lxml`.** |
| `--noconfirm` | nadpisuje poprzedni wynik bez pytania |

> Certyfikaty CA (HTTPS przez `requests`) oraz Tkinter/`lxml` są dociągane
> automatycznie przez wbudowane hooki PyInstallera — nie trzeba nic dodawać.

Jeśli w katalogu został `__pycache__`, można go usunąć — nie wpływa na build.

---

## 11. Folder dystrybucyjny

Szablony XSLT **kopiujemy obok exe**, a nie pakujemy przez `--add-data`,
ponieważ:
- `config.json` i `output.csv` są **zapisywane** w czasie działania (muszą
  leżeć w zapisywalnym folderze obok exe, a `_MEIPASS` znika po zamknięciu),
- szablony bywają edytowane bez przebudowy exe.

```powershell
$DaneDoKopii = @("synch_template.xml", "synch_template_brands.xml")
New-Item -ItemType Directory -Force $Dyst | Out-Null
foreach ($f in $DaneDoKopii) {
  Copy-Item (Join-Path $Zrodlo $f) (Join-Path $Dyst $f) -Force
}
```

Zawartość gotowego folderu:

```
dystrybucja\
  ARA v2.exe
  synch_template.xml
  synch_template_brands.xml
```

**Czego NIE kopiować:** `config.json` (tworzy się sam), `output.csv` i kopie
zapasowe (pliki generowane/robocze), `app_xml_csv*.py` (jednorazowe skrypty
CLI, poprzednicy aplikacji — nie są używane przez exe).

---

## 12. Smoke test

Udany build ≠ działający exe. Dla aplikacji `--onefile` GUI powstają **dwa**
procesy (bootloader + właściwa aplikacja z oknem):

```powershell
$exe = "C:\...\dystrybucja\ARA v2.exe"
Get-Process -Name "ARA v2" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Process -FilePath $exe | Out-Null
Start-Sleep -Seconds 12
$procs = Get-Process -Name "ARA v2" -ErrorAction SilentlyContinue
$procs | Select-Object Id,
  @{n='MB';e={[math]::Round($_.WorkingSet64/1MB,1)}},
  @{n='Title';e={$_.MainWindowTitle}} | Format-Table -AutoSize
$procs | Stop-Process -Force
```

Kryteria „OK”:
- proces żyje po kilkunastu sekundach (nie crashuje na starcie),
- jeden z procesów ma **tytuł okna** aplikacji (dowód, że GUI wstało),
- podwyższony working set (rzędu 100+ MB przy `lxml` + pobrany feed)
  potwierdza, że pobranie i parsowanie XML zadziałało.

**Test ten nie obejmuje generowania CSV** — ścieżka `build_main_transform()`
odpala się dopiero po zapisaniu konfiguracji. Domknij weryfikację ręcznie:
zaznacz jedną markę → **Zapisz** → sprawdź, że pasek statusu pokazuje
„Zapisano output.csv – n rekordów…” i że `output.csv` powstał obok exe.
To jedyny moment, w którym wychodzi rozjazd nazwy zmiennej z sekcji 4.3.

---

## 13. Uwagi wdrożeniowe (przekazać z aplikacją)

- **Przenosi się cały folder dystrybucyjny** — exe razem z szablonami (exe
  szuka ich obok siebie i bez nich nie wystartuje).
- **Folder musi być zapisywalny** — aplikacja zapisuje `config.json` i
  `output.csv` obok exe. Nie umieszczać w `Program Files`; użyć np. Pulpitu
  lub `C:\ARA\`.
- **Aplikacja musi zostać otwarta**, żeby cykl działał — nie jest usługą ani
  zadaniem harmonogramu. Zamknięcie okna kończy odświeżanie.
- **Windows 64-bit** — zgodny z architekturą maszyny budującej.
- **Exe niepodpisany** — przy pierwszym uruchomieniu Windows SmartScreen /
  antywirus może ostrzegać; „Więcej informacji → Uruchom mimo to”. To normalne
  dla plików z PyInstallera.
- Zmiana kolumn CSV lub reguł cenowych = edycja `synch_template.xml` w folderze
  dystrybucyjnym, **bez przebudowy exe**. Wyjątek: nazwa zmiennej marż (4.3).

---

## 14. Adaptacja dla kolejnej aplikacji

Co jest zmienne, a co stałe:

| Element | Gdzie | Uwaga |
|---|---|---|
| Skrypt `.py` | plik źródłowy | główny plik podawany PyInstallerowi |
| Link do źródła danych | stała `XML_URL` w `.py` | **wkompilowany w exe** — zmień w kodzie *przed* buildem |
| Szablony XSLT | folder źródłowy | kopiowane obok exe (sekcja 11) |
| Struktura wejściowego XML | XPath-y w szablonach | ARA: `/produkty/produkt`; IdoSell IOF: `/offer/products/product` |
| Nazwa zmiennej podmienianej w pamięci | `MARGIN_VAR` + szablon | musi się zgadzać bajt w bajt (4.3) |
| Nazwa exe / ikona | parametry buildu | opcjonalne |

Stałe procedury: poprawka `BASE_DIR` (5.1), wzorzec jednego trwałego wątku
roboczego (7.2), komenda PyInstallera (10), kopiowanie danych obok exe (11),
smoke test (12).

**Skrót:**
1. W nowym `.py`: poprawka `BASE_DIR`, właściwy `XML_URL`, nazwy szablonów.
2. Dostosuj XSLT do struktury nowego feedu; ustaw `MARGIN_VAR` zgodnie z nim.
3. Build komendą z sekcji 10 (podmień `$Skrypt`, `$Nazwa`, `$Zrodlo`, `$Ikona`).
4. Skopiuj pliki danych (sekcja 11).
5. Smoke test + ręczna weryfikacja zapisu CSV (sekcja 12).
