# ShopMania — wymagania feedu
- Źródła: https://partner.shopmania.com/cp.help?topic=20
- Data przeglądu: 2026-10-27
- Format: TXT/CSV rozdzielany `|` lub XML z dowolnymi nazwami tagów (byle zawierał pola obowiązkowe), akceptuje format Google: nie wspomniano (częściowo — XML o własnych tagach dopuszczalny, mapowanie Google nie potwierdzone)
- Szablon bazowy: `Compari.xml` — prosty płaski XML produktów z polami nazwanymi wprost, bez przestrzeni nazw; łatwy do przemianowania na tagi z przykładu ShopMania (zawartości szablonu nie weryfikowano). Alternatywa: `Google.xml`, jeśli ShopMania przyjmie dowolne tagi po mapowaniu w panelu.

## Struktura pliku
TXT/CSV (kolejność pól):
```
Category|Manufacturer|Model(MPN)|Merchant code|Product name|Description|Product URL|Image URL|Price|Currency|Shipping price|Availability|GTIN
```
XML (przykład ze strony):
```xml
<store>
  <products>
    <Product>
      <MPC/> <Category/> <Manufacturer/> <MPN/> <Name/> <Description/>
      <URL/> <Image/> <Price/> <Currency/> <Shipping/> <Availability/> <GTIN/>
    </Product>
  </products>
</store>
```

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| Category | pełna ścieżka od korzenia, kategorie sklepu | 255 |
| Merchant code (`MPC`) | unikalny, stały identyfikator produktu | 100 |
| Product name (`Name`) | nazwa jak w sklepie | 255 |
| Product URL (`URL`) | musi zaczynać się od `http://` (w praktyce pełny adres) | — |
| Image URL (`Image`) | duże, dobrej jakości, bez znaków wodnych, logo, tekstów | — |
| Price | z podatkami, bez dostawy, bez symbolu waluty, bez cen indywidualnych | — |
| GTIN | wymagany tylko dla książek (ISBN) | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| Manufacturer | producent/marka | 100 |
| Model (`MPN`) | kod producenta (MPN, EAN, UPC lub ISBN) | 100 |
| Description | bez HTML, JS, obrazów; bez haseł promocyjnych, rabatów, dostawy, CAPS LOCK | **200** |
| Currency | kod waluty, np. `PLN` | — |
| Shipping | koszt dostawy z podatkiem, `0.00` = darmowa; wymaga włączenia indywidualnych kosztów w panelu | — |
| Availability | `In stock`, `Available for order`, `Out of stock`, `Preorder` (inne wartości mapowane w panelu) | słownik |
| GTIN | UPC 12, EAN 13, ISBN 10/13 (preferowany 13) | — |

## Limity i formaty
- TXT/CSV: separator `|`, rekordy nową linią; puste pole jako `||`; z danych usunąć znaki nowej linii i separatory.
- Kodowanie nie jest podane.
- Ręczny feed: min. 50 produktów. Aktualizacja przy zmianie cen/stanów, co najmniej co 30 dni (inaczej zawieszenie).
- Wycofane produkty usuwać z feedu. Akceptacja 1–3 dni robocze; odrzucone linie w „Products stats”.

## Różnice względem szablonu bazowego
- Opis skrócony do 200 znaków, czysty tekst (wymaga przycinania w XSLT).
- Cena bez waluty + osobne pole `Currency`; dostępność jako słownik ShopMania.
- Tagi z przykładu (`MPC`, `MPN`, `Name`, `Image`) różnią się od etykiet w wersji CSV — trzymać się jednej konwencji.

## Uwagi
- Strona dostępna publicznie, bez logowania.
- Strona nie wspomina o formacie Google ani o kodowaniu znaków — do potwierdzenia z ShopMania.
