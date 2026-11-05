# Warianty elementów — link i `item_group_id`

Warianty wprowadzam w **kopii** sterownika, edytując ją po `konfiguruj.py utworz`. Opisuję je jako przekształcenia bieżącego kodu szablonu, a nie gotowe bloki, bo szablony się zmieniają. Przed edycją czytam aktualny fragment kopii (`grep -n "card/@url" <kopia>`).

## Linki

Dotyczą wszystkich elementów zbudowanych z `card/@url`:
- **Google:** `g:link`, `g:display_ads_link`, `g:mobile_link`,
- **Facebook:** `g:link`, `g:ios_url`, `g:iphone_url`, `g:ipad_url`, `g:android_url`, `g:windows_phone_url`.

`card/@url` w ofercie ma postać `https://sklep.pl/pl/products/nazwa-123.feed10000.html`. `.feed<id>` to znacznik porównywarki, z której pochodzi oferta.

| Wariant | Wynik | Zmiana w kopii |
|---|---|---|
| **A. Link porównywarki** (domyślny) | `…/nazwa-123.googleshoppingpl.html` (Google, kraj z `Kraj_dostawy`), `.googleremarketing.html` (display_ads), `.facebookads.html` (FB) | brak |
| **B. Link czysty** | `…/nazwa-123.html` | w każdym elemencie z listy zastępuję tekst sufiksu (`.googleshopping` + `translate($Kraj_dostawy…)` + `.html`, `.googleremarketing.html`, `.facebookads.html`) jednym `<xsl:text>.html</xsl:text>` |
| **C. Link z oferty** | `…/nazwa-123.feed10000.html` | `substring-before(…card/@url, '.feed')` zastępuję samym `…card/@url` i usuwam tekst sufiksu |

We wszystkich wariantach zostaje `?selected_size=<id rozmiaru>`, gdy produkt ma więcej niż jeden rozmiar. Jeśli klient chce parametry UTM, dopisuję je za `selected_size` z separatorem `?` albo `&`, zależnie od tego, czy `selected_size` wystąpił.

Wzorce B i C dla Google: `SI/archiwum/SummonFeed/Generator/parameters_templates/link_raw.xsl`, `link_default_id.xsl`.

## `g:item_group_id`

| Wariant | Logika | Domyślny w |
|---|---|---|
| **1. Tylko rozmiary** | `@id` produktu (każdy produkt to grupa swoich rozmiarów) | Google |
| **2. Rozmiary i warianty** | `group/@id`, gdy produkt należy do grupy wariantów. Gdy nie należy, a ma więcej niż jeden rozmiar, `@id`. W pozostałych przypadkach brak elementu | Facebook |

Prefiks: Facebook dodaje `group-` (`group-123`). Google nie dodaje prefiksu. Pytam o niego zawsze, gdy zmieniam wariant.

- **Google → wariant 2:** szablon ma wariant 2 zakomentowany pod `<!-- Grupuj rozmiary i warianty -->`. Usuwam aktywny blok „Grupuj tylko rozmiary” i odkomentowuję `xsl:choose` (bez gałęzi `otherwise`, chyba że klient chce `item_group_id` także dla produktów pojedynczych).
- **Facebook → wariant 1:** blok `xsl:choose` pod `<!-- Grupuj rozmiary i warianty -->` zastępuję pojedynczym `<g:item_group_id>` z `@id` (prefiks według odpowiedzi).
- W innych szablonach szukam `item_group_id` (lub odpowiednika, np. `ITEMGROUP_ID` w Heurece) i stosuję tę samą logikę.

W ofercie sprawdzam liczbę produktów z `group/@id` (raport `parametry_oferty.py`). Gdy jest 0, wariant 2 daje ten sam wynik co 1 i mówię o tym przy pytaniu.
