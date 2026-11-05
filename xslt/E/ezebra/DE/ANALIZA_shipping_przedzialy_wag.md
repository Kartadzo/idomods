# ANALIZA: koszt dostawy wg przedziałów wagi — ezebrade_gAds.xml

Data: 2026-10-22 · Status: **czeka na akceptację i wartości**

## Cel

Zamiast jednego kosztu dostawy i jednego progu darmowej dostawy feed ma liczyć `g:shipping`
według **wagi wariantu**, w 4 przedziałach. Każdy przedział ma własny koszt dostawy
i własny próg ceny, od którego dostawa jest darmowa.

## Stan obecny (`ezebrade_gAds.xml`)

- Konfiguracja na górze pliku (l. 12–29): `kwota_dla_darmowej_dostawy` = 39, `Koszt_dostawy` = 20.00,
  opcjonalny drugi próg `kwota_dla_wiekszych_zamowien` / `Koszt_dostawy_wiekszych_zamowien`,
  tryb `*` = koszt z cennika IdoSell (`delivery_cost/prepayment/@gross`).
- Blok wyjścia (l. 773–823): `g:shipping` (price, country, handling/transit time, service)
  + `g:free_shipping_threshold` z jednym progiem.
- Waga wariantu: `size/@weight` w gramach (np. `weight="30"`), już używana w `g:shipping_weight`.

## Dane wejściowe / wyjściowe

- Wejście: `size/@weight` (g), `size/price/@gross`, waluta produktu.
- Wyjście (na każdy wariant): `g:shipping/g:price` = 0 albo koszt przedziału,
  `g:free_shipping_threshold/g:price_threshold` = próg przedziału. Pozostałe pola `g:shipping` bez zmian.

## Planowane zmiany

1. Konfiguracja: w miejsce `kwota_dla_darmowej_dostawy`, `kwota_dla_wiekszych_zamowien`,
   `Koszt_dostawy`, `Koszt_dostawy_wiekszych_zamowien` — tabela 4 przedziałów:

   ```xml
   <!-- przedział N: waga_do_N = górna granica w gramach (włącznie); ostatni przedział bez granicy -->
   <xsl:variable name="waga_do_1">…</xsl:variable>
   <xsl:variable name="koszt_dostawy_1">…</xsl:variable>
   <xsl:variable name="prog_darmowej_dostawy_1">…</xsl:variable>
   … _2, _3 …
   <xsl:variable name="koszt_dostawy_4">…</xsl:variable>
   <xsl:variable name="prog_darmowej_dostawy_4">…</xsl:variable>
   ```

2. W bloku shipping zmienna `przedzial` (1–4) z `@weight`, z niej `koszt` i `prog`;
   reszta bloku jak dziś. Tryb `*` (koszt z cennika IdoSell) zostaje jako przełącznik.
3. Test na eksporcie IOF: rozkład wariantów po przedziałach i wartości `g:shipping`.

## Założenia

- Granice „do X g włącznie”: przedział 1 = 0…waga_do_1, 2 = (waga_do_1…waga_do_2], itd., 4 = powyżej waga_do_3.
- Próg darmowej dostawy porównywany z ceną wariantu (`price/@gross`), jak dziś. Cena ≥ próg → koszt 0.
- Kwoty w walucie produktu (EUR dla DE).
- Wariant bez wagi lub z wagą 0 → przedział 1.

## Otwarte pytania

1. **Wartości** — dla 4 przedziałów: górna granica wagi (g), koszt dostawy, próg darmowej dostawy.
2. Wariant bez wagi / waga 0 — przedział 1 (najlżejszy) czy pominąć `g:shipping`?
3. Waga z `size/@weight` (waga wysyłkowa z karty) czy z parametru `Waga [g]`?
4. Usuwam drugi próg (`kwota_dla_wiekszych_zamowien`) — przedziały go zastępują. OK?
5. Przedział bez darmowej dostawy (np. najcięższy) — zostawić próg pusty, wtedy brak
   `g:free_shipping_threshold` dla tego przedziału?

## Decyzje (2026-10-22)

| Przedział | Waga do (g) | Koszt (EUR) | Próg darmowej dostawy (EUR) |
|---|---|---|---|
| 1 | 10000 | 4.49 | 39 |
| 2 | 15000 | 6.00 | 1000 |
| 3 | 25000 | 8.00 | 1000 |
| 4 | 29000 | 10.00 | 1000 |

- Brak wagi / 0 → przedział 1. Waga z `size/@weight`. Drugi próg usunięty.
- Wszystkie przedziały mają próg darmowej dostawy (używany do wyliczenia `g:shipping/g:price`).
- **`g:free_shipping_threshold` = stałe 39 EUR dla wszystkich** (prośba klienta), niezależnie od przedziału
  (wariant A). Wariant B — próg z przedziału (`prog_darmowej_dostawy_N`) — dopisany jako zakomentowany blok
  obok wariantu A; przełączenie = zamiana komentarzy.
- Waga > 29000 g → przedział 4 (założenie, brak danych o wyższym przedziale).
- `g:shipping_weight` bez zmian — poprawka tylko na prośbę klienta.

## Uwaga poza zakresem

`g:shipping_weight` (l. 826) wypisuje samą liczbę (`30`), a GMC wymaga jednostki (`30 g`).
Mogę dopisać ` g` przy okazji — do decyzji.
