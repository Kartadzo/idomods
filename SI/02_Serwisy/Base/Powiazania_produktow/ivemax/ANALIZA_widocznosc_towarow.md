# Analiza: widoczność towarów IdoSell według eksportu Shoparena i powiązań Base (IVEMAX)

## Cel

Ustawić widoczność towarów w IdoSell (sklep 1) według nowego eksportu Shoparena `eksport_shoparena/products_filtered_7078_1792656545.csv` (kolumna `active`). Towary niepowiązane z Base mają być ukryte, także te aktywne w Shoparenie.

Reguła: **widoczny = `active` 1 w Shoparenie ORAZ towar jest w pliku powiązań Base**. Każdy inny przypadek: ukryty.

## Dane wejściowe

- Eksport Shoparena: 4220 towarów (te same kody co w `shopArena - 2029-10-21.csv`, nowa jest kolumna `active`). Aktywne: 4118, nieaktywne: 102.
- Most Shoparena → IdoSell po kodzie zewnętrznym (`KZS-<kod>` / `<kod>_<data>`): 3917 starych towarów 1:1, 301 nowych (ID na żywo ze sklepu), 2 nieprzeniesione (239, 240).
- Powiązania Base: `powiazania_base_idosell.csv`, 2347 towarów IdoSell (2283 stare + 64 nowe).
- Bieżąca widoczność: odczyt na żywo przez API (eksport z 2026-10-21 posłużył do szacunku poniżej).

## Skutek (szacunek z eksportu z 2026-10-21)

Stare towary (3917):

| Shoparena | Base | Teraz | Liczba | Akcja |
|---|---|---|---|---|
| aktywny | powiązany | widoczny | 2183 | bez zmian |
| aktywny | powiązany | ukryty | 89 | **pokaż** |
| aktywny | brak | widoczny | **1348** | **ukryj** |
| aktywny | brak | ukryty | 199 | bez zmian |
| nieaktywny | powiązany | widoczny | 7 | **ukryj** |
| nieaktywny | powiązany | ukryty | 1 | bez zmian |
| nieaktywny | brak | widoczny | 26 | **ukryj** |
| nieaktywny | brak | ukryty | 64 | bez zmian |

Nowe towary (301, wszystkie teraz ukryte): 298 aktywnych w Shoparenie, z czego powiązanych z Base jest 64 → **pokaż ~64**, reszta zostaje ukryta.

Razem około: **pokaż ~153, ukryj ~1381**.

Towary IdoSell bez odpowiednika w eksporcie Shoparena (118, kod zewnętrzny spoza Shoparena lub kilka towarów na jeden kod): według reguły ukryte, chyba że są powiązane z Base.

## Planowane zmiany

`api_widocznosc.py` + `run_api_widocznosc.bat` (klient API i konfiguracja jak w poprzednich skryptach):
1. Odczyt stanu na żywo: kody zewnętrzne (`products/sizes`), istnienie i bieżąca widoczność (`products/products`).
2. Plan zmian z tabelą jak wyżej → plik `wyniki/api_widocznosc_plan_<data>.csv` (ID, nazwa, active, powiązanie, teraz, docelowo). Zatrzymanie i pytanie przed wysyłką.
3. Próba na 3 towarach (1 pokaż, 2 ukryj), odczyt kontrolny.
4. Reszta paczkami: `PUT products/products` z `productIsVisible` (y/n). Wysyłam **tylko zmiany**.
5. Dziennik `wyniki/api_widocznosc_<data>.csv` + `.jsonl`.

## Założenia

- „Powiązane z Base” = towar jest w `powiazania_base_idosell.csv` (2347). Kolizje (74) i towary bez pary (1659 po stronie BL) traktuję jak niepowiązane.
- Zmieniam tylko widoczność w sklepie. Nie ruszam widoczności w porównywarkach, statusu „towar trwały” ani stanów.
- Nie ma tłumaczeń — widoczność nie zależy od nich.

## Pytania

1. **1348 aktywnych i dziś widocznych towarów zniknie ze sklepu**, bo nie mają pary w Base. To ~1/3 oferty (strony produktów przestaną działać dla klientów i Google). Potwierdzasz?
2. Czy plik `powiazania_base_idosell.csv` został już wczytany do Base i czy mam traktować go jako wiążący? Jeśli Base zgłosił przy imporcie błędy dla części par, podeślij nowy eksport powiązań, a wezmę stan z Base.
3. Kolumna aktywności na jutro (z tłumaczeniami) — czy to właśnie ten eksport, czy przyjdzie jeszcze osobna?

## Decyzje i wynik (2026-10-22)

Decyzje użytkownika: 1) ukrycie 1348 widocznych bez pary — tak; 2) `powiazania_base_idosell.csv` jest wczytany w Base i wiąże; 3) ten eksport to zapowiadana kolumna aktywności.

Doprecyzowanie przy wykonaniu: towar powiązany z Base, którego nie ma w eksporcie Shoparena (977, 1032, 3748), zostaje bez zmian — brak informacji o aktywności.

Pole API: zapis `productInVisible` (y/n) w `PUT products/products`, odczyt `productIsVisible` w `GET products/products`.

Wynik (`api_widocznosc.py`, dziennik `wyniki/api_widocznosc_2026-10-22_102518*` — próba, `wyniki/api_widocznosc_2026-10-22_102723*` — reszta): 4321 towarów w sklepie, **zmieniono 1557** (pokazano 153, ukryto 1404), 0 błędów. Ponowny odczyt: 0 zmian do zrobienia. Widocznych jest teraz 2338.
