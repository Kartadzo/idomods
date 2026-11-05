# Favi — wymagania feedu
- Źródła: https://rextheme.com/product-feed-for-favi-woocommerce-cz/ (artykuł dostawcy wtyczki WooCommerce, nie oficjalna dokumentacja Favi)
- Data przeglądu: 2026-10-27
- Format: własny XML (`Products`/`Product`), akceptuje format Google: według artykułu tak (Favi ma przyjmować m.in. Google Shopping, Zbozi, Ceneo, Compari, Árukereső) — nie potwierdzone u źródła
- Szablon bazowy: `Google.xml` — najprostsza ścieżka, jeśli Favi rzeczywiście przyjmuje feed Google (wg artykułu). Dla natywnego formatu Favi najbliższy jest prawdopodobnie `Compari.xml` (płaska lista produktów z polami identifier/name/product_url/price/image_url/category/description/delivery_time) — nie zweryfikowano zawartości szablonu.

## Struktura pliku
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Products>
  <Product>
    <Identifier/> <GroupId/> <Name/> <Product_url/> <Price/>
    <Image_url/> <Image_url_2/> … <Image_url_9/>
    <Category/> <Description/> <Manufacturer/>
    <Delivery_Time/> <Delivery_Cost/> <EAN_code/>
    <!-- atrybuty nazwa/wartość (materiał, kolor, typ) — konkretna składnia nie podana -->
  </Product>
</Products>
```

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| `Identifier` | unikalny ID produktu | — |
| `Name` | konkretna nazwa; dla wariantów z cechą wariantu | nie podano |
| `Product_url` | karta produktu z przyciskiem zakupu; bez spacji i znaków diakrytycznych | — |
| `Price` | cena regularna brutto, bez separatora tysięcy | — |
| `Image_url` | zdjęcie główne | min. 400×400 px |
| `Category` | kategoria z listy Favi (mapowanie) | — |
| `Description` | opis konkretnego produktu; tylko p, b, strong, i, em, ul, ol, li, br; bez linków, kontaktów, e-maili | nie podano |
| `Delivery_Time` | `0` (ten sam dzień), `1`, `2`, `3` | słownik |
| `GroupId` | ID produktu nadrzędnego, łączy warianty | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `Manufacturer` | producent | — |
| `Delivery_Cost` | koszt dostawy; dla darmowej słowo „FREE” lub odpowiedniki językowe | — |
| `Image_url_2` … `Image_url_9` | zdjęcia dodatkowe | do 8 |
| atrybuty | pary nazwa/wartość; artykuł zaleca nie więcej niż 5 | ~5 |
| `EAN_code` | EAN, jeśli dostępny | — |

## Limity i formaty
- UTF-8. Brak informacji o limitach rozmiaru pliku i liczby produktów.
- Zdjęcia: realny produkt bez grafik, znaków wodnych i tekstów promocyjnych, bez innych obiektów, zgodne kolorystycznie, min. 400×400 px.

## Różnice względem szablonu bazowego
- Względem `Google.xml`: inne nazwy elementów (wielka litera, podkreślniki), brak `g:`, zdjęcia jako numerowane `Image_url_N` zamiast powtarzalnego `additional_image_link`, `Delivery_Time` jako skala 0–3 zamiast `availability`, kategoria z listy Favi.

## Uwagi
- **Źródło nieoficjalne** (RexTheme) — dane mogą być nieaktualne. Oficjalne warunki i lista kategorii są w centrum pomocy Favi (podlinkowane w artykule, nie przeglądane).
- Niespójności w artykule: korzeń raz `products`, raz `Products`; różne ceny w przykładach; błędnie zamknięta sekcja CDATA w `Category`. Składnia atrybutów nie jest pokazana jednoznacznie.
- Przed wdrożeniem warto potwierdzić u Favi, czy feed Google jest akceptowany — byłby najprostszą drogą.
