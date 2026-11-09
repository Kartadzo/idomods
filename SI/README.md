# SI — narzędzia i zlecenia budowane z Claude

Mapa folderu, stan projektów i zasady zakładania nowych. Struktura od 2026-11-05 (uzasadnienie: `ANALIZA_porzadki_SI.md`).

## Mapa

```
SI/
├── _wspolne/            kod współdzielony: idosell_client.py (+ config.json), zrzut.py, raport_docx.py
├── Klienci/            baza wiedzy o klientach (lokalnie, poza gitem): zasady, panele, konta, wyjątki — czytać przed zadaniem
├── 01_Feedy/            narzędzia do feedów produktowych
├── 02_Serwisy/<Serwis>/ praca związana z jedną platformą (IdoSell, Facebook, GMC, GTM, OpenAI…)
├── 03_Zewnetrzne_SI/    zewnętrzne maszyny SI (docelowo podłączone przez git)
└── archiwum/<klient lub serwis>/   zakończone projekty do wglądu
```

## Projekty

Status: **gotowe** · **w toku** · **wstrzymane** · **archiwum**. Daty z notatek projektów.

| Projekt | Folder | Status | Opis |
|---|---|---|---|
| SummonFeed (skill `/summonfeed`) | `01_Feedy/SummonFeed` | gotowe (2026-10-27) | sterownik XSLT z kopii szablonu `xslt/szablony/*.xml`, wymagania serwisów, weryfikacja lxml |
| Konwerter OpenAI Ads | `01_Feedy/OpenAI_Ads_konwerter` | gotowe (2026-09-22) | feed XML → natywny feed OpenAI Ads (CSV + JSONL), config per sklep |
| Mirakl XML → CSV | `01_Feedy/Mirakl_xml_na_csv` | w toku | płaska lista attribute/code/value; otwarte mapowanie nagłówków |
| Kategorie Heureka | `01_Feedy/Heureka_kategorie` | gotowe (2026-08-24) | mapowanie Google → Heureka CZ/SK, CATEGORYTEXT w feedzie topfit |
| Mapowanie parametrów Ceneo | `01_Feedy/Ceneo_mapowanie_parametrow` | gotowe | blok `<attrs>` i kategorie Ceneo (matfel) |
| Wiadomości transakcyjne (skill) | `02_Serwisy/IdoSell/Wiadomosci_transakcyjne` | gotowe (2026-10-14) | status, edycja działania, eksport/import treści maili i SMS |
| Edycja eksportu XML | `02_Serwisy/IdoSell/Edycja_eksportu_XML` | gotowe, nieprzetestowane ręcznie | GUI tkinter: XML + CSV → 3 struktury |
| Migracja klientów | `02_Serwisy/IdoSell/Migracja_klientow` | gotowe | konwersja eksportu klientów do importu IdoSell |
| Aktualizacja towarów (Empik) | `02_Serwisy/IdoSell/Aktualizacja_towarow` | gotowe | nazwy i opisy dla serwisu (magnicreatix.pl) |
| Walidacja aktualizacji API | `02_Serwisy/IdoSell/API_walidacja_aktualizacji` | gotowe (2026-09) | testy zmian Admin API v8; dokumentacja: `02_Serwisy/IdoSell/DOKUMENTACJA_API.md` |
| Test zdarzeń po OSCOP | `02_Serwisy/IdoSell/Test_zdarzen_OSCOP` | w toku (2026-11-05) | zdarzenia Google/Meta/TikTok w nowym procesie zamówienia; raporty `raporty/<domena>_<data>/` (megadron.pl) |
| Zmiany sterowników XSLT (eZebra) | `02_Serwisy/IdoSell/Zmiany_sterownikow/ezebra` | gotowe (2026-11-09) | folder na zadanie `<element>_<data>`: `black_days_2026-11-06` (parametr 91508 → Meta, RTB, WP/Onet), `cena_omnibus_2026-11-06` (`custom_label_3` w 5 feedach Meta); sterowniki w `xslt/E/ezebra/`, kopie w `<kraj>/old/` |
| Porównanie sterownika panel ↔ lokalnie | `02_Serwisy/IdoSell/Zmiany_sterownikow/_narzedzia/porownaj_sterownik` | gotowe (2026-11-09) | `run_porownaj.bat`: schowek z panelu vs plik w `xslt/`, werdykt, diff, podmiana z kopią w `old/`; analiza `Zmiany_sterownikow/ANALIZA_porownanie_sterownikow.md` |
| Konfiguracja dostaw | `02_Serwisy/IdoSell/Konfiguracja_dostaw` | w toku (2026-11-09) | klient → podfolder na zadanie `<element>_<data>`: `pewienpan/punkt_odbioru_2026-11-09` (niestandardowy punkt „Odbiór w punkcie”, butik Nawrot 7) |
| Weryfikacja FB (skill) | `02_Serwisy/Facebook/Weryfikacja_FB` | gotowe, cykl co 90 dni | feed, katalog, piksel/CAPI; raporty `raporty/<domena>_<data>/` |
| Weryfikacja GMC (skill) | `02_Serwisy/GMC/Weryfikacja_GMC` | gotowe, cykl co 90 dni | konto, produkty, feed, dostawy; raporty `raporty/<domena>_<data>/` |
| Piksel ChatGPT (dodatki IdoSell) | `02_Serwisy/OpenAI/Piksel_ChatGPT` | gotowe (2026-11-02) | dodatki HTML piksela `oaiq` (butyolivier.pl) + testy |
| Weryfikacja GPTAds | `02_Serwisy/OpenAI/Weryfikacja_GPTAds` | gotowe (2026-11-02) | przypisanie konwersji do kliknięć (butyolivier.pl) |
| Piksel ChatGPT przez GTM | `02_Serwisy/GTM/Piksel_ChatGPT_idomods` | w toku — czeka na publikację | import kontenera GTM dla idomods.pl |
| Śledzenie konwersji Google Ads | `02_Serwisy/Google_Ads/Sledzenie_konwersji` | gotowe (2026-10-26) | raport wycieraczkidoszyb |
| Base: powiązania (ivemax) | `02_Serwisy/Base/Powiazania_produktow/ivemax` | wstrzymane (2026-10-21) | czeka na eksport z wFirmy |
| Base: powiązania (romanetka) | `02_Serwisy/Base/Powiazania_produktow/romanetka` | wstrzymane (2026-10-27) | czeka na decyzję klienta; analiza w `02_Serwisy/Base/Analiza/` |
| Amazon: katalog | `02_Serwisy/Amazon/Katalog` | w toku | szablon TOY_BUILDING_BLOCK (magnicreatix.pl) |
| Erli | `02_Serwisy/Erli` | wiedza | zamówienia Erli ↔ IdoSell (zooart) |
| n8n + ClickUp | `02_Serwisy/n8n` | w toku | scenariusz „ClickUp - SUBTASK”, dokumentacja |
| Zadania ClickUp (skill `/zadanie`) | `02_Serwisy/ClickUp/Zadania_ClickUp` | gotowe (2026-11-05) | link ClickUp → analiza → folder → nowe okno z Claude |
| Shoparena | `02_Serwisy/Shoparena` | — | folder na przyszłe projekty |
| summonFeed — generator | `archiwum/SummonFeed/Generator` | archiwum (2026-11-05) | stary generator z klocków; wzorce linków nadal używane przez skill |

## Zasady dla nowych projektów

1. **Miejsce.** Narzędzie do feedów → `01_Feedy/<Projekt>/`. Praca na jednej platformie → `02_Serwisy/<Serwis>/<Projekt>/` (nowy serwis = nowy podfolder). Zewnętrzna maszyna SI → `03_Zewnetrzne_SI/<nazwa>/`. Jeśli nic nie pasuje — najpierw ustalamy nowe miejsce, folder nie trafia luzem do `SI/`.
2. **Klienci.** Jeden kod dla wielu sklepów → dane w `klienci/<domena>/`, raporty w `raporty/<domena>_<RRRR-MM-DD>/`. Osobna kopia skryptów per klient → folder klienta bezpośrednio w projekcie (jak `Base/Powiazania_produktow/ivemax/`).
3. **Szkielet projektu:**
   ```
   <Projekt>/
   ├── README.md            cel, jak uruchomić, status, data ostatniej zmiany
   ├── ANALIZA_<temat>.md   analiza przed kodem (może być kilka)
   ├── run.bat              uruchamianie dwuklikiem, interaktywnie
   ├── *.py / core/ / gui/
   ├── config.example.json  wzór; prawdziwy config.json tylko lokalnie
   ├── dane/                pliki wejściowe
   ├── wyniki/              pliki wyjściowe
   ├── klienci/<domena>/    gdy narzędzie obsługuje wielu klientów
   └── old/                 kopie zapasowe (zamiast *.bak i „— kopia”)
   ```
4. **Nazwy folderów:** bez spacji (`_`), bez polskich znaków, wielka litera na początku (`Weryfikacja_GMC`). Nazwy plików i treść — po polsku z ogonkami.
5. **Ścieżki w kodzie** zawsze względne od `__file__`, nigdy `C:\Users\...`. Wspólny kod:
   ```python
   _k = os.path.dirname(os.path.abspath(__file__))
   while not os.path.isdir(os.path.join(_k, "_wspolne")) and os.path.dirname(_k) != _k:
       _k = os.path.dirname(_k)
   sys.path.insert(0, os.path.join(_k, "_wspolne"))
   ```
6. **Wspólny kod** tylko w `_wspolne/`. Gdy coś kopiuję do drugiego projektu — przenoszę to do `_wspolne/`.
7. **Status** — przy zakładaniu, wstrzymaniu i zamknięciu projektu aktualizuję tabelę powyżej.
8. **Archiwum** — `archiwum/<klient lub serwis>/<projekt>/`, na prośbę lub przy zamykaniu projektu za zgodą.
9. **Zmiany istniejących sterowników XSLT** (dowolny klient) → `02_Serwisy/IdoSell/Zmiany_sterownikow/<klient>/<element>_<RRRR-MM-DD>/` (osobny podfolder na zadanie: analiza, notatki, `komentarz_clickup.txt`). Najpierw porównanie pliku lokalnego z panelem (`_narzedzia/porownaj_sterownik/run_porownaj.bat`); stare wersje sterowników → `xslt/<litera>/<klient>/<kraj>/old/` z datą.
10. **Git** — reguły tylko w `Domino\.gitignore` (ogólne dla SI: `dane/`, `wyniki/`, `config.json`, `__pycache__/`); każdy projekt na osobnej gałęzi, merge do `main` przez `/zamknij`.
