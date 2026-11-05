# Árukereső — wymagania feedu
- Źródła: https://www.arukereso.hu/admin/FeedFormat
- Data przeglądu: 2026-10-27
- Format: nie ustalono (specyfikacja za logowaniem), akceptuje format Google: nie ustalono
- Szablon bazowy: `Compari.xml` — Árukereső (HU), Pazaruvaj (BG) i Compari (RO) to jedna grupa porównywarek z identyczną strukturą panelu partnera; format feedu najpewniej wspólny. Wniosek z budowy serwisów, nie z treści specyfikacji.

## Struktura pliku
Nie ustalono — odnośniki „Terméklista feltöltés” prowadzą do `/admin/Login#feed-format` i `/admin/#feed-format`, czyli do panelu wymagającego logowania.

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| — | brak danych ze źródła | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| — | brak danych ze źródła | — |

## Limity i formaty
Brak danych o polach. Strona publiczna mówi tylko, że wszystkie trzy modele rozliczeń (PPC, MPO, MPH) wymagają poprawnej listy produktów, a PPC — listy zaakceptowanej.

## Różnice względem szablonu bazowego
Nie da się ocenić bez specyfikacji.

### Podobieństwa w grupie (Árukereső / Pazaruvaj / Compari)
- Ten sam adres specyfikacji `/admin/FeedFormat` i ta sama kotwica `#feed-format` w panelu partnera na obu sprawdzonych domenach.
- Obie strony publiczne nie ujawniają pól i odsyłają do panelu.
- Compari nie był sprawdzany w tym przeglądzie (brak linku w zadaniu) — założenie wspólnego formatu dla całej trójki wymaga potwierdzenia po zalogowaniu.
- Artykuł o Favi (patrz `favi.md`) wymienia Compari i Árukereső jako formaty akceptowane przez Favi, co sugeruje, że jest to rozpoznawalny, ustandaryzowany format.

## Uwagi
- **Wymaga logowania** — specyfikacja pól niedostępna publicznie; treści nie zgadywano.
- Do uzupełnienia: odczyt sekcji feed-format po zalogowaniu (Claude in Chrome) lub wklejenie jej treści; wtedy porównać z `Compari.xml`.
