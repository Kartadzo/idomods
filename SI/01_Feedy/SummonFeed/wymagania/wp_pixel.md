# WP Pixel — wymagania feedu
- Źródła: https://pixel.wp.pl/docs/pl/feed/index.html
- Data przeglądu: 2026-10-27
- Format: Google RSS `g:*` (XML Google Merchant Center), akceptuje format Google: tak (inne formaty tylko po dodatkowej akceptacji)
- Szablon bazowy: `Google.xml` — WP Pixel przyjmuje wprost XML w formacie Google Merchant Center; wystarczy dodać kilka pól.

## Struktura pliku
```xml
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
  <channel>
    <item>
      <g:id/> <title/> <description/> <link/>
      <g:image_link/> <g:additional_image_link/>
      <g:brand/> <g:price/> <g:sale_price/> <g:omnibus_price/>
      <g:product_type/> <g:google_product_category/>
      <g:availability/> <g:gtin/> <g:size/> <g:item_group_id/> <g:age_group/>
    </item>
  </channel>
</rss>
```

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| `g:id` | unikalny, litery i cyfry; zgodny z ID przekazywanym przez Pixel, stały między aktualizacjami | — |
| `title` | pełna nazwa bez skrótów: rodzaj produktu + kluczowe cechy | — |
| `description` | zgodny ze stroną, tylko tekst (HTML usuwany), akapity nową linią | min. 100 znaków |
| `link` | unikalny, bezpośrednio na kartę z możliwością dodania do koszyka | — |
| `g:image_link` | zdjęcie główne (wymagania niżej) | 1 MB |
| `g:brand` | rozpoznawalna marka/producent | — |
| `g:price` | cena zgodna ze stroną | — |
| `g:sale_price` | cena promocyjna; **bez promocji = cena regularna** | — |
| `g:omnibus_price` | najniższa cena z 30 dni przed promocją | — |
| `g:product_type` | typ produktu, np. „Buty wizytowe” | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `g:google_product_category` | im precyzyjniej, tym szybsza publikacja; nazwy zbyt ogólne (marka, seria) blokują | — |
| `g:size` | każdy rozmiar jako osobny produkt, grupowane `g:item_group_id` | — |
| `g:gtin` | EAN/GTIN-13, zalecany | 13 cyfr |
| `g:additional_image_link` | jak zdjęcie główne, bez wymogu jednolitego tła | — |
| `g:availability` | np. `in stock`, zgodnie ze stroną | — |
| `g:age_group` | `newborn` / `infant` / `toddler` / `kids` / `adult` | słownik |

## Limity i formaty
- Plik na serwerze klienta, wszystkie aktualne produkty, aktualizacja min. raz na 24 h.
- Zdjęcie pionowe (zalecane): 1000×1400 px, do 1 MB, tło białe/przezroczyste/jasne neutralne. Kwadratowe: tylko packshot na białym/przezroczystym, 1000×1000 px, do 1 MB. Zakaz znaków wodnych, logotypów, haseł marketingowych, aranżacji.
- Przykład ceny w dokumentacji: `299,99 zł` (przecinek + waluta) — odbiega od zapisu Google `299.99 PLN`.

## Różnice względem szablonu bazowego
- Nowe pole `g:omnibus_price` (wymagane).
- `g:sale_price` wymagane zawsze — przy braku promocji wpisać cenę regularną (w Google zwykle pole pomijane).
- `g:product_type` i `g:brand` obowiązkowe; `description` min. 100 znaków, bez HTML.
- Do rozważenia `g:age_group`.

## Uwagi
- Strona wczytana poprawnie. Kodowanie pliku nie jest podane.
- W przykładowym XML dokumentacji `g:price` i `g:sale_price` wyglądają na zamienione (promocyjna wyższa od regularnej) — błąd przykładu.
- Format ceny (`299,99 zł` vs `299.99 PLN`) do potwierdzenia z WP — dokumentacja nie mówi wprost, czy zapis Google jest akceptowany.
