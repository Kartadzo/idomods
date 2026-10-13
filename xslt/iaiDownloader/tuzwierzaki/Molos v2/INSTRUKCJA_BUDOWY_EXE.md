# MOLOS v2 — kompletny runbook: od zera do `dystrybucja\Molos v2.exe`

Dokument **samowystarczalny**: zawiera wszystko, co potrzebne, aby odtworzyć
`molos_app.py` oraz zbudować `dystrybucja\Molos v2.exe`, **bez zaglądania do
pozostałych plików tego folderu**. Opisane są struktura feedu dostawcy MOLOS,
schemat `config.json`, kontrakt na zmienną marż w szablonie XSLT i specyfikacja
aplikacji z krytycznymi fragmentami kodu.

Aplikacja jest bliźniacza wobec `ARA v2` — różni się dostawcą, adresem feedu,
strukturą wejściowego XML, szablonami i nazwą zmiennej marż. Sekcja 14 zbiera,
co trzeba podmienić przy kolejnej aplikacji tego typu.

---

## 1. Co powstaje

Dwa artefakty:

| Artefakt | Skąd | Rola |
|---|---|---|
| `molos_app.py` | napisany według sekcji 3–7 | źródło aplikacji GUI (Tkinter) |
| `dystrybucja\Molos v2.exe` | PyInstaller, sekcja 10 | jeden samodzielny plik (~16 MB), działa na maszynach **bez Pythona i bibliotek** |

Aplikacja: co N minut pobiera feed XML dostawcy MOLOS, wyciąga listę marek,
a dla marek zaznaczonych w GUI generuje `output.csv` z cenami powiększonymi
o ustawioną marżę. Plik CSV jest wsadem do synchronizacji w IdoSell.

Poprzednicy aplikacji — `app_xml_csv.py` i `app_xml_csv_brands.py` — to
jednorazowe skrypty CLI robiące to samo bez GUI i bez wyboru marek. Nie są
używane przez exe i nie trafiają do folderu dystrybucyjnego.

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

## 3. Dane wejściowe — feed dostawcy MOLOS

**URL** (wkompilowywany w exe jako stała `XML_URL`):

```
https://b2b.molos.com.pl/xml/bdc7f794385b9abb15db0fd437cab357/products.xml
```

**Uwaga:** to **nie** jest format IOF IdoSell. To płaski XML dostawcy o korzeniu
`/products` (ARA ma `/produkty`, więc XPath-y w szablonach są inne):

```xml
<products>
  <product>
    <producer>8in1</producer>                  <!-- marka; klucz filtrowania -->
    <symbol>3733</symbol>                      <!-- kod, trafia do kod_zewnetrzny -->
    <price_retail_net>2,65</price_retail_net>  <!-- przecinek dziesiętny -->
    <store>4</store>                           <!-- stan magazynowy -->
    ...
  </product>
</products>
```

Konsekwencje dla XSLT (już uwzględnione w szablonach z sekcji 4):
- cena wymaga `translate(..., ', PLN;', '.')` — zamiana przecinka na kropkę
  i usunięcie ewentualnego sufiksu waluty,
- `store` też może mieć przecinek,
- feed bywa niepoprawny składniowo → parser musi mieć `recover=True`.

**Rozmiar feedu: ok. 34 MB** (ok. 180 marek). Dlatego `HTTP_TIMEOUT` wynosi
tu **120 s**, a nie 30 s jak w ARA — przy 30 s pobieranie potrafi się urwać na
wolniejszym łączu. Samo pobranie przez `requests` zajmuje ok. 2 s na dobrym
łączu; parsowanie i transformacja podnoszą zużycie pamięci procesu do ~160 MB.

---

## 4. Szablony XSLT

Leżą **obok** `.py`/`.exe`, nie są pakowane do środka (sekcja 11).

### 4.1 `synch_template_brands.xml` — lista marek

Iteruje `/products/product` i emituje jedno `<marka>` na produkt (wartość
`producer`); deduplikację robi już Python.

### 4.2 `synch_template.xml` — właściwy feed do CSV

Iteruje `/products/product` ograniczone do marek obecnych w zmiennej marż.
Zawartość `<xsl:variable name='nazwa_marki_i_doliczana_marza'>` jest w czasie
działania **podmieniana w pamięci** przez aplikację (plik na dysku pozostaje
nietknięty).

**Model marży:** marża jest **doliczana od ceny detalicznej**, nie narzutem na
koszt — `cena_detaliczna = cena_zakupu / (1 - marża/100)`. Dlatego marża musi
być `< 100` (przy 100 dzielenie przez zero). Kontrola: `price_retail_net` 2,65
przy marży 50% daje `cena_detaliczna` 5,30.

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

Kanoniczna wartość w tym runbooku: **`nazwa_marki_i_doliczana_marza`**.

> **Uwaga przy przenoszeniu kodu z ARA v2:** tamten szablon ma
> `nazwa_marki_i_doliczany_marza` (`-ny-`), a MOLOS `nazwa_marki_i_doliczana_marza`
> (`-na-`). Skopiowanie `MARGIN_VAR` żywcem z ARA daje dokładnie ten błąd.

Przy tworzeniu nowego szablonu **nie używaj polskich znaków w nazwie zmiennej** —
eliminuje to klasę problemów z kodowaniem między plikiem `.py` i `.xml`.

---

## 5. `molos_app.py` — stałe i tryb „frozen”

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

Wszystkie ścieżki liczone od `BASE_DIR`. Uruchamianie przez
`python molos_app.py` działa po tej zmianie identycznie jak wcześniej.

### 5.2 Pełny zestaw stałych

```python
XML_URL = (
    'https://b2b.molos.com.pl/xml/'
    'bdc7f794385b9abb15db0fd437cab357/products.xml'
)

XSLT_MAIN   = os.path.join(BASE_DIR, 'synch_template.xml')
XSLT_BRANDS = os.path.join(BASE_DIR, 'synch_template_brands.xml')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
OUT_CSV     = os.path.join(BASE_DIR, 'output.csv')

XSL_NS        = 'http://www.w3.org/1999/XSL/Transform'
MARGIN_VAR    = 'nazwa_marki_i_doliczana_marza'      # patrz 4.3
RECORD_TAG    = 'item'
CSV_DELIMITER = ','

DEFAULT_INTERVAL_MIN = 30
MIN_INTERVAL_MIN     = 1
MAX_INTERVAL_MIN     = 1440
HTTP_TIMEOUT         = 120                            # feed ~34 MB, patrz 3
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

## 6. `molos_app.py` — warstwa danych

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
    "Acana":   { "enabled": false, "margin": 0.0  }
  }
}
```

Do CSV trafiają wyłącznie marki z `enabled: true`. Marki nieobecne w ostatnim
pobranym feedzie są **usuwane z configu przy zapisie** (GUI ostrzega o tym
przed zapisem).

### 6.2 `output.csv` — wynik

```csv
kod_zewnetrzny,cena_detaliczna,KosztWlasnySprzedazyTowarow_cenaMinimalna,idMagazynu,stanMagazynu,marka
Molos-3733-0,5.3,2.65,0,4,8in1
```

`kod_zewnetrzny` powstaje jako `Molos-` + `symbol` + `-0`. Kolumny wynikają
wyłącznie ze struktury `<item>` w `synch_template.xml` — zmiana szablonu
zmienia CSV bez zmian w kodzie Pythona.

---

## 7. `molos_app.py` — GUI i współbieżność

### 7.1 Dwa widoki jednego okna

Okno `tk.Tk` (`760x640`, `minsize 640x540`), tytuł
`MOLOS – generator output.csv`, motyw ttk `clam`, styl `Accent.TButton`
(niebieski, pogrubiony). Nagłówek: „Dostawca MOLOS” + etykieta trybu.
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

`self.jobs` / `self.results` (`queue.Queue`) + **jeden** wątek `molos-worker`
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

`run_molos_app.bat` obok `.py` (`pythonw` = bez okna konsoli):

```bat
@echo off
chcp 65001 > nul
cd /d "%~dp0"
start "" pythonw molos_app.py
```

Albo `python molos_app.py` z katalogu, w którym leżą szablony.

---

## 9. Ikona

Kopia ikony leży w tym folderze jako `app.ico`.

```powershell
# odczyt ścieżki ikony ze skrótu
$ws = New-Object -ComObject WScript.Shell
$ws.CreateShortcut("C:\...\Aplikacja.lnk").IconLocation   # np. C:\...\app.ico,0

# weryfikacja nagłówka .ico (poprawny zaczyna się od 00 00 01 00)
$b = [System.IO.File]::ReadAllBytes("C:\...\app.ico")[0..3]
if (($b -join ',') -eq '0,0,1,0') { "ICO OK" } else { "NIE jest to poprawny .ico" }
```

PyInstaller wymaga pliku **`.ico`** — nie `.lnk`, nie `.png`.

---

## 10. Build (PyInstaller)

```powershell
# --- Parametry (podmień dla nowej aplikacji) ---
$Skrypt = "molos_app.py"                                  # główny plik .py
$Nazwa  = "Molos v2"                                      # nazwa exe (bez .exe)
$Zrodlo = "C:\Users\Admin\Desktop\Domino\xslt\iaiDownloader\tuzwierzaki\Molos v2"
$Ikona  = "$Zrodlo\app.ico"
$Dyst   = "$Zrodlo\dystrybucja"                           # tu wyląduje exe
$Tmp    = "$env:TEMP\pyi_build_molos"                     # pliki robocze i .spec

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

`$Tmp` ma inną nazwę niż w ARA (`pyi_build_molos` vs `pyi_build`), żeby cache
buildów obu aplikacji się nie mieszał.

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
  Molos v2.exe
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
$exe = "C:\...\dystrybucja\Molos v2.exe"
Get-Process -Name "Molos v2" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Process -FilePath $exe | Out-Null
Start-Sleep -Seconds 20
$procs = Get-Process -Name "Molos v2" -ErrorAction SilentlyContinue
$procs | Select-Object Id,
  @{n='MB';e={[math]::Round($_.WorkingSet64/1MB,1)}},
  @{n='Title';e={$_.MainWindowTitle}} | Format-Table -AutoSize
$procs | Stop-Process -Force
```

Kryteria „OK” (wartości zmierzone dla `Molos v2.exe`):
- proces żyje po kilkunastu sekundach (nie crashuje na starcie),
- jeden z procesów ma tytuł okna `MOLOS – generator output.csv` (dowód, że GUI
  wstało),
- working set ok. **160 MB** przy 34-megabajtowym feedzie potwierdza, że
  pobranie i parsowanie XML zadziałało. Czekaj 20 s, nie 12 — feed MOLOS jest
  dwa rzędy wielkości większy niż w ARA.

**Test ten nie obejmuje generowania CSV** — ścieżka `build_main_transform()`
odpala się dopiero po zapisaniu konfiguracji. Dwa sposoby domknięcia:

1. **Ręcznie w GUI:** zaznacz jedną markę → **Zapisz** → pasek statusu pokazuje
   „Zapisano output.csv – n rekordów…”, a `output.csv` powstaje obok exe.
2. **Headless, przed buildem** — szybciej wyłapuje rozjazd nazwy zmiennej
   z sekcji 4.3:

```python
import molos_app as m
tree = m.fetch_feed()
brands = m.extract_brands(tree)                       # oczekiwane ~180 marek
rows = m.write_csv(m.build_main_transform([(brands[1], 50.0)])(tree))
print(rows)                                           # >0 = kontrakt 4.3 OK
```

---

## 13. Uwagi wdrożeniowe (przekazać z aplikacją)

- **Przenosi się cały folder dystrybucyjny** — exe razem z szablonami (exe
  szuka ich obok siebie i bez nich nie wystartuje).
- **Folder musi być zapisywalny** — aplikacja zapisuje `config.json` i
  `output.csv` obok exe. Nie umieszczać w `Program Files`; użyć np. Pulpitu
  lub `C:\MOLOS\`.
- **Aplikacja musi zostać otwarta**, żeby cykl działał — nie jest usługą ani
  zadaniem harmonogramu. Zamknięcie okna kończy odświeżanie.
- **Windows 64-bit** — zgodny z architekturą maszyny budującej.
- **Exe niepodpisany** — przy pierwszym uruchomieniu Windows SmartScreen /
  antywirus może ostrzegać; „Więcej informacji → Uruchom mimo to”. To normalne
  dla plików z PyInstallera.
- **Feed waży ~34 MB** — każdy cykl to takie pobranie. Przy ustawianiu bardzo
  krótkiego interwału (1–5 min) warto mieć to na uwadze.
- Zmiana kolumn CSV lub reguł cenowych = edycja `synch_template.xml` w folderze
  dystrybucyjnym, **bez przebudowy exe**. Wyjątek: nazwa zmiennej marż (4.3).

---

## 14. Adaptacja dla kolejnej aplikacji

Co jest zmienne, a co stałe:

| Element | Gdzie | Uwaga |
|---|---|---|
| Skrypt `.py` | plik źródłowy | główny plik podawany PyInstallerowi |
| Link do źródła danych | stała `XML_URL` w `.py` | **wkompilowany w exe** — zmień w kodzie *przed* buildem |
| Limit czasu HTTP | `HTTP_TIMEOUT` | skaluj do rozmiaru feedu (ARA: 30 s, MOLOS: 120 s przy 34 MB) |
| Szablony XSLT | folder źródłowy | kopiowane obok exe (sekcja 11) |
| Struktura wejściowego XML | XPath-y w szablonach | MOLOS: `/products/product`; ARA: `/produkty/produkt`; IdoSell IOF: `/offer/products/product` |
| Nazwa zmiennej podmienianej w pamięci | `MARGIN_VAR` + szablon | musi się zgadzać bajt w bajt (4.3) |
| Nazwa klasy aplikacji, tytuł okna, nazwa wątku | `.py` | tu: `MolosApp`, `MOLOS – generator output.csv`, `molos-worker` |
| Nazwa exe / ikona / katalog `$Tmp` | parametry buildu | `$Tmp` osobny per aplikacja |

Stałe procedury: poprawka `BASE_DIR` (5.1), wzorzec jednego trwałego wątku
roboczego (7.2), komenda PyInstallera (10), kopiowanie danych obok exe (11),
smoke test (12).

**Skrót:**
1. W nowym `.py`: poprawka `BASE_DIR`, właściwy `XML_URL`, `HTTP_TIMEOUT` pod
   rozmiar feedu, nazwy szablonów, `MARGIN_VAR` przepisany z szablonu.
2. Dostosuj XSLT do struktury nowego feedu.
3. Weryfikacja headless (12, wariant 2) — tanio wyłapuje rozjazd `MARGIN_VAR`.
4. Build komendą z sekcji 10 (podmień `$Skrypt`, `$Nazwa`, `$Zrodlo`, `$Ikona`,
   `$Tmp`).
5. Skopiuj pliki danych (sekcja 11).
6. Smoke test (12).
