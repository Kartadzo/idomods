# Verbolia — wymagania feedu
- Źródła: https://www.verbolia.com/knowledge/data-feed-integration/
- Data przeglądu: 2026-10-27
- Format: własny CSV / XML / JSON (XML: `<channel>` → `<item>`, nazwy camelCase), akceptuje format Google: częściowo (strona nie wspomina o formacie Google; struktura `channel/item` jest podobna do RSS, ale nazwy pól inne)
- Szablon bazowy: `Google.xml` — najbliższy zestaw pól i struktura `channel/item`; wymaga przemianowania pól i przebudowy atrybutów.

## Pola wymagane
(domyślne nazwy Verbolii)
| pole | opis/format | limit |
|---|---|---|
| Id | unikalny identyfikator; klucz łączący, gdy jest kilka feedów | — |
| GroupId | identyfikator grupy wariantów; potrzebny, by pokazywać jeden wynik zamiast każdego koloru/rozmiaru | — |
| Category | kategoria | — |
| Brand | marka | — |
| Title | nazwa | — |
| Url | URL produktu | — |
| ImageUrl | URL zdjęcia | — |
| SalePrice | cena sprzedaży (aktualna) | — |
| OriginalPrice | cena regularna | — |
| QuantityInStock | stan magazynowy | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| AdditionalImageUrl | dodatkowe zdjęcia | — |
| Color | kolor | — |
| Size | rozmiar | — |
| Season | sezon | — |
| Badge | etykieta/odznaka | — |
| Rating | ocena | — |
| atrybuty dodatkowe | wszystko, co widać na stronach wyników sklepu (opisy, filtry, przyciski, odznaki, daty) | — |

Strona określa te pola jako dodatkowe, które mogą stać się obowiązkowe zależnie od wyglądu stron wyników klienta.

## Limity i formaty
- Dostarczenie: FTP albo URL; URL bez uwierzytelniania.
- CSV: separator pól przecinek, separator wielu wartości `|`; kolumny listy atrybutów: typ i wartość rozdzielone `:`, wpisy rozdzielone `;`; wartości z separatorami w cudzysłowach.
- XML: nazwy elementów camelCase; każdy atrybut jako osobny element `<attribute>` z jednym prostym elementem w środku — wiele wartości = powtórzony typ.
- JSON: tablica obiektów, atrybuty jako tablica obiektów `type`/`value`.
- Opinie w osobnym feedzie (rozmiar pliku); dane ogólne i atrybuty mogą być w jednym.
- Przykład XML deklaruje UTF-8; limitów rozmiaru, częstotliwości i kodowania strona nie podaje.

## Różnice względem szablonu bazowego
- Nazwy pól: `g:id`→Id, `g:item_group_id`→GroupId, `g:product_type`→Category, `g:brand`→Brand, `link`→Url, `g:image_link`→ImageUrl, `g:additional_image_link`→AdditionalImageUrl (w XML zapis camelCase, np. `imageUrl`).
- Ceny: Google ma `price` (regularna) + `sale_price` (promocyjna); Verbolia wymaga zawsze obu — `OriginalPrice` i `SalePrice` (przy braku promocji zapewne ta sama wartość — do potwierdzenia). Format ceny (z walutą czy bez) nieopisany.
- `availability` zastąpione liczbowym `QuantityInStock`.
- Brak przestrzeni `g:`; atrybuty (kolor, rozmiar, sezon…) w strukturze `<attribute>` zamiast płaskich pól.
- Pola Google typu `gtin`, `mpn`, `shipping`, `custom_label_*`, `google_product_category` nie są wymienione.

## Uwagi
- Strona wczytana poprawnie, ale nie zawiera dokładnego schematu XML (nazwy elementów w camelCase wynikają z opisu) ani informacji o formacie Google — dokładny mapping najlepiej uzgodnić z Verbolią.
