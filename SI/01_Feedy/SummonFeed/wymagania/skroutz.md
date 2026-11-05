# Skroutz — wymagania feedu
- Źródła: https://developer.skroutz.gr/feedspec/ (zwrócił pustą treść), https://developer.skroutz.gr/products/xml_feed/ (właściwa specyfikacja, podlinkowana z https://developer.skroutz.gr/)
- Data przeglądu: 2026-10-27
- Format: własny XML Skroutz, akceptuje format Google: nie wynika ze specyfikacji (nie wspomina o Google; wymaga „dowolnego szablonu” z kompletem atrybutów — de facto własny XML)
- Szablon bazowy: `Google.xml` jako źródło logiki pól (id, title, link, image, price, availability, brand, mpn, gtin, size, color, item_group_id) — strukturę i nazwy elementów trzeba przepisać na płaski XML Skroutz. Żaden z szablonów nie odpowiada formatowi 1:1.

## Struktura pliku
```xml
<?xml version="1.0" encoding="UTF-8"?>
<mywebstore>
  <created_at>2026-10-27 12:00</created_at>
  <products>
    <product>
      <id/> <name/> <link/> <image/> <additionalimage/>
      <category/> <price_with_vat/> <vat/>
      <manufacturer/> <mpn/> <ean/>
      <availability/> <size/> <color/> <weight/>
      <description/> <quantity/>
      <specifications><spec name=""/></specifications>
      <variations>
        <variation>
          <variationid/> <link/> <availability/> <manufacturersku/>
          <ean/> <price_with_vat/> <size/> <quantity/>
        </variation>
      </variations>
    </product>
  </products>
</mywebstore>
```
Przykłady używają CDATA dla tekstów (nie jest to wymóg wprost).

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| `created_at` | data wygenerowania pliku (przykład `RRRR-MM-DD GG:MM`) | — |
| `id` | unikalne, stałe przez cały cykl życia, nie używać ponownie | 200 znaków |
| `name` | producent, model, kolor itp.; bez gwarancji, dostawy, promocji; produkty używane z informacją o stanie | 300 znaków |
| `link` | https, karta produktu (nie kategoria), bez URL-encodingu | 1000 znaków |
| `image` | https, publiczne, bez znaków wodnych i ramek, min. jeden bok > 1000 px, bez AVIF | 400 znaków |
| `category` | pełna ścieżka, np. `Komputery > Dyski zewnętrzne` | 250 znaków |
| `price_with_vat` | cena brutto w EUR, 2 miejsca po przecinku, jedna dla wszystkich | decimal |
| `vat` | stawka VAT 0 lub 1–100 | decimal |
| `availability` | `In Stock` / `Available from 1 to 3 days` / `Available from 4 to 6 days` / `Available up to 12 days` | 60 znaków |
| `manufacturer` | rzeczywisty producent, musi występować też w nazwie | 100 znaków |
| `mpn` | MPN lub ISBN (książki) — wymagany we wszystkich kategoriach | 80 znaków |
| `ean` | EAN/kod kreskowy — wymagany we wszystkich kategoriach | 13 cyfr |
| `description` | specyfikacja i zastosowanie produktu | 10 000 znaków |
| `quantity` | stan; 0 przy braku; dla produktów z rozmiarami suma rozmiarów | 0–10 000 000 |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `additionalimage` | powtarzalne, unikalne; wymagane dla mody z rozmiarami | do 15, 400 znaków |
| `size` | wymagane dla produktów z rozmiarami; lista po przecinku (`S,M,L`), zakres `5.5-6.5`, para `5.5/42` | 500 znaków |
| `color` | zgodny ze zdjęciem; wymagany w modzie; każdy kolor = osobny produkt z innym id | 100 znaków |
| `weight` | gramy domyślnie, można `3.2 kg`; wymagane, gdy koszty wysyłki zależą od wagi | decimal |
| `shipping` | koszt dostawy niezależny od lokalizacji, 0 = darmowa (tylko model z przekierowaniem) | decimal |
| `variations/variation` | warianty rozmiarowe: `variationid` (np. `12431.XL`), `availability`, `size` (64), `quantity` wymagane; `price_with_vat`, `link`, `manufacturersku`, `ean` opcjonalne (część w becie) | — |
| `specifications/spec@name` | dodatkowe cechy; nie dublować pól dedykowanych | — |
| `wholesale_price`, `season`, `size_fit`, `outlet`, `author`, `expiration_date`, `country_of_origin` | opcjonalne pola uzupełniające | — |
| `instock` | Y/N — wycofane (XSD nadal go wymaga) | — |

## Limity i formaty
- Kodowanie zadeklarowane w nagłówku musi zgadzać się z rzeczywistym (przykład UTF-8).
- Plik > 10 MB musi być spakowany zip/gzip.
- Bez duplikatów id; XML poprawny i walidowalny (walidator: validator.skroutz.gr).
- Bez uwierzytelniania — dostęp przez whitelistę IP SkroutzBot / Skroutz ImageBot; pełny łańcuch certyfikatów HTTPS.
- Regeneracja co najmniej raz na dobę.

## Różnice względem szablonu bazowego
- Brak przestrzeni nazw `g:` i RSS — płaskie elementy z małych liter w `mywebstore/products/product`.
- Warianty rozmiarowe zagnieżdżone w `variations` jednego produktu (Google: osobne itemy + `item_group_id`); kolor nadal jako osobne produkty.
- Cena brutto bez waluty + osobne pole `vat`; dostępność jako słownik tekstów Skroutz zamiast `in stock`.
- Dodatkowe wymagane: `quantity`, `mpn` i `ean` we wszystkich kategoriach, `created_at`.

## Uwagi
- Podany link `/feedspec/` zwrócił pustą stronę (prawdopodobnie przekierowanie lub render JS) — treść pobrana z `/products/xml_feed/`.
- Specyfikacja jest niespójna: XSD używa `storedata` i `uid`, przykłady `mywebstore` i `id`; cena raz `price`, raz `price_with_vat`; dodatkowe zdjęcie `additional_image` / `additionalimage` / `additional_imageurl`. Przed wdrożeniem sprawdzić walidatorem, którą wersję przyjmuje.
- Ceny w EUR — dla sklepów IdoSell potrzebna waluta EUR w eksporcie.
