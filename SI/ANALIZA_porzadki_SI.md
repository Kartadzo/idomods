# ANALIZA: porządki w folderze SI i zasady dla kolejnych projektów

Data: 2026-11-05 · wersja 2 (po decyzjach użytkownika)

## 1. Cel

Ułożyć `Domino\SI` tak, żeby od razu było widać: gdzie jest narzędzie, którego serwisu dotyczy, co jest gotowe, a co w toku. Do tego spisać stałe zasady zakładania i prowadzenia kolejnych projektów w SI.

## 2. Stan wyjściowy (co przeszkadzało)

- 16 folderów na jednym poziomie, grupowanych naraz po narzędziu, platformie, sposobie działania i kliencie.
- `summonFeed` (stary generator) obok `SummonFeed SI` (skill).
- Jedno zagadnienie rozbite (`ChatGPT/apka_generująca_katalog` + `OpenAI_Ads_Feed_przyklady`), wspólny kod w dwóch miejscach (`API IdoSell/_wspolne`, `Optymalizacja_Integracji/narzedzia`).
- Narzędzia zakopane głęboko (`Przeglądarka IdoSell/Chrome-IdoSell/IAI_Wiadomości_Transakcyjne`).
- Niespójne nazwy (spacje, ogonki, literówka `gAsd`).
- Nieaktualne ścieżki: skill `wiadomosci-transakcyjne`, `.gitignore` i globalny CLAUDE.md wskazywały nieistniejące `SI/API IdoSell/Wiadomości transakcyjne/`; główny CLAUDE.md — `xslt/szablony/summonFeed`.
- `waliduj_orders_documents.py` szukał `_wspolne` piętro za nisko (nie działał); 5 skryptów z absolutnym `C:\Users\Admin\...`.

## 3. Decyzje użytkownika (2026-11-05)

1. Obszary — tak, plus folder na **zewnętrzne maszyny SI** (w planie łączone przez git).
2. Nazwy folderów bez polskich znaków i spacji — tak.
3. Numeracja obszarów — tak.
4. Jednorazówki — zostają na miejscu (nie archiwizuję teraz).
5. Generator `summonFeed` → `archiwum/`; archiwum dzielone **na foldery klientów lub serwisów**.
6. Edycja eksportu XML → do aplikacji IdoSell; obszar **`02_Serwisy`** z podfolderem na każdy serwis (IdoSell, Shoparena, Facebook, GMC, GTM itd.).

## 4. Struktura docelowa

```
SI/
├── README.md                      mapa + tabela projektów + zasady
├── ANALIZA_porzadki_SI.md
├── _wspolne/                      kod współdzielony (idosell_client.py, config, zrzut.py, raport_docx.py)
│
├── 01_Feedy/
│   ├── SummonFeed/                ← SummonFeed SI (+ dane/products_export.xml z dawnego generatora)
│   ├── OpenAI_Ads_konwerter/      ← ChatGPT/apka_generująca_katalog (+ przyklady/ ← OpenAI_Ads_Feed_przyklady)
│   ├── Mirakl_xml_na_csv/         ← Format_Mirakl_xml_na_csv
│   ├── Heureka_kategorie/         ← Kategorie_Heureki
│   └── Ceneo_mapowanie_parametrow/← Mapowanie_Parametrów_Ceneo
│
├── 02_Serwisy/
│   ├── IdoSell/
│   │   ├── Wiadomosci_transakcyjne/     ← Przeglądarka IdoSell/Chrome-IdoSell/IAI_Wiadomości_Transakcyjne
│   │   ├── Edycja_eksportu_XML/         ← Apka_Edycji_Eksportu_XML_IdoSell
│   │   ├── Migracja_klientow/           ← Przeglądarka IdoSell/migracja_Klientów
│   │   ├── Aktualizacja_towarow/        ← IdoSell_Aktualizacja_Towarów
│   │   ├── API_walidacja_aktualizacji/  ← API IdoSell/Walidacja aktualizacji
│   │   └── DOKUMENTACJA_API.md          ← API IdoSell/DOKUMENTACJA_API.md
│   ├── Facebook/Weryfikacja_FB/         ← Optymalizacja_Integracji/FB
│   ├── GMC/Weryfikacja_GMC/             ← Optymalizacja_Integracji/GMC
│   ├── GTM/Piksel_ChatGPT_idomods/      ← ChatGPT/piksel/GTM
│   ├── OpenAI/
│   │   ├── Piksel_ChatGPT/              ← ChatGPT/piksel (dodatki IdoSell, testy)
│   │   └── Weryfikacja_GPTAds/          ← Optymalizacja_Integracji/GPTAds
│   ├── Google_Ads/Sledzenie_konwersji/  ← śledzenie konwersji gAsd
│   ├── Base/
│   │   ├── Powiazania_produktow/        ← Base/Powiązanie produktów (ivemax/, romanetka/)
│   │   └── Analiza/                     ← Base/Analiza
│   ├── Shoparena/                       nowy, pusty (README)
│   ├── Amazon/Katalog/                  ← Amazon/Katalog
│   ├── Erli/                            ← Przeglądarka IdoSell/Erli
│   └── n8n/                             ← n8n
│
├── 03_Zewnetrzne_SI/              zewnętrzne maszyny SI (README z planem podłączenia przez git)
│
└── archiwum/
    └── SummonFeed/Generator/      ← summonFeed
```

**Wnętrza projektów przenoszę bez zmian.** Porządki w środku (`*.bak`, „— kopia”, eksporty luzem → `dane/`, `old/`) robię dopiero przy kolejnej pracy nad danym projektem, bo część skryptów auto-wykrywa pliki w swoim folderze i łatwo je zepsuć.

## 5. Zasady dla kolejnych projektów (pełna wersja w `SI/README.md`)

1. **Miejsce.** Narzędzie feedowe → `01_Feedy/<Projekt>/`; praca na konkretnej platformie → `02_Serwisy/<Serwis>/<Projekt>/`; zewnętrzna maszyna SI → `03_Zewnetrzne_SI/<nazwa>/`. Nie pasuje nigdzie → pytam przed założeniem nowego obszaru/serwisu.
2. **Klienci.** Jeden kod dla wielu sklepów → dane w `klienci/<domena>/` lub raporty `raporty/<domena>_<RRRR-MM-DD>/`. Osobna kopia skryptów per klient → folder klienta bezpośrednio w projekcie (jak `Base/Powiazania_produktow/ivemax/`).
3. **Szkielet:** `README.md`, `ANALIZA_<temat>.md`, `run.bat`, kod, `config.example.json` (+ lokalny `config.json`), `dane/`, `wyniki/`, `old/`.
4. **Nazwy folderów:** bez spacji (`_`), bez ogonków, wielka litera na początku. Pliki i treść — po polsku z ogonkami.
5. **Ścieżki w kodzie** względne od `__file__`; wspólny kod z `SI/_wspolne` szukany w górę drzewa (fragment kodu w `SI/README.md`, p. 5 — moduł `sciezki.py` odpadł, bo sam musiałby najpierw znaleźć `_wspolne`), nigdy `C:\Users\...`.
6. **Wspólny kod** tylko w `SI/_wspolne/`.
7. **Status** w tabeli `SI/README.md` — aktualizuję przy zakładaniu i zamykaniu projektu.
8. **Archiwum:** `archiwum/<klient lub serwis>/<projekt>/`, przenoszę na prośbę lub przy zamykaniu projektu za zgodą.
9. **Git:** reguły tylko w `Domino\.gitignore`; projekt na osobnej gałęzi; zewnętrzne maszyny SI — docelowo submoduły/osobne repozytoria (do ustalenia przy pierwszej).

## 6. Wykonanie

1. Gałąź `porzadki-SI`.
2. Przeniesienie wg p. 4 (`git mv` dla śledzonych: summonFeed, FB, GMC, narzedzia, API IdoSell, ChatGPT; reszta zwykłym przeniesieniem — jest nieśledzona i taka zostaje).
3. Szukanie `_wspolne` w górę drzewa + poprawa importów (walidacja, 4 skrypty z `wyniki/`, `test_attrs.py`).
4. Odwołania: skille (`summonfeed`, `weryfikacja-fb`, `weryfikacja-gmc`, `wiadomosci-transakcyjne`), `.gitignore`, `Domino\CLAUDE.md`, `~/.claude/CLAUDE.md` (wyjątek Pobrane), pamięć, dokumenty w SI i `python/transform_xml — gpsr/ANALIZA_gpsr_ceneo.md`.
5. `SI/README.md`, README w `Shoparena/` i `03_Zewnetrzne_SI/`.
6. Weryfikacja: brak starych ścieżek (grep), `py_compile`, import `_wspolne`, testy wiadomości transakcyjnych, `git check-ignore` na config/danych.
7. Commit na gałęzi; merge do `main` na polecenie (`/zamknij`).

## 7. Założenia

- Nic nie usuwam.
- Zbudowane `.exe` (`dystrybucja/`, `build/`) przenoszą się z projektem; jeśli mają zaszyte ścieżki, odnotuję potrzebę przebudowy.
- W czasie porządków narzędzia z SI nie są uruchamiane.
