# Pazaruvaj — wymagania feedu
- Źródła: https://www.pazaruvaj.com/admin/FeedFormat
- Data przeglądu: 2026-10-27
- Format: nie ustalono (specyfikacja za logowaniem), akceptuje format Google: nie ustalono
- Szablon bazowy: `Compari.xml` — Pazaruvaj (BG), Árukereső (HU) i Compari (RO) to serwisy jednej grupy z jednakowo zbudowanym panelem partnera (`/admin/FeedFormat`, sekcja `#feed-format`), więc najpewniej dzielą format feedu. To wniosek z budowy serwisów, nie z treści specyfikacji.

## Struktura pliku
Nie ustalono — strona odsyła do sekcji „ФАЙЛ НА ПРОДУКТИТЕ” (`/admin/#feed-format`) w panelu partnera wymagającym logowania.

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| — | brak danych ze źródła | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| — | brak danych ze źródła | — |

## Limity i formaty
Brak danych o polach. Strona publiczna podaje tylko wymagania wobec partnera: działający sklep, e-mail i telefon, możliwość wystawiania faktur firmowych, plik eksportu produktów zgodny z instrukcją z panelu, dostawa na terenie Bułgarii.

## Różnice względem szablonu bazowego
Nie da się ocenić bez specyfikacji. Podobieństwa grupy: patrz `arukereso.md` — ten sam układ panelu i adresu specyfikacji; Compari jest trzecim serwisem tej grupy.

## Uwagi
- **Wymaga logowania** — specyfikacja pól niedostępna publicznie; treści nie zgadywano.
- Operator może odrzucić pliki z towarami używanymi, odnowionymi lub z uszkodzonym opakowaniem.
- Do uzupełnienia: odczyt sekcji feed-format po zalogowaniu (Claude in Chrome) lub wklejenie jej treści.
