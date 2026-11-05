# ExpertSender — wymagania feedu
- Źródła: https://help.expertsender.com/ecdp/product-feed/ , https://help.expertsender.com/pl/ecdp/product-feed/
- Data przeglądu: 2026-10-27
- Format: dowolny XML lub CSV mapowany ręcznie w panelu ECDP (wskazanie węzła produktu i przypisanie pól), akceptuje format Google: częściowo (strona tego nie mówi; mapowanie pozwala wskazać `item` i pola `g:*`, ale wymagane są pola spoza standardu Google)
- Szablon bazowy: `Google.xml` — zawiera większość pól systemowych; trzeba dodać cenę Omnibus i zmienić dostępność na true/false.

## Pola wymagane
(atrybuty systemowe — nazwy w ECDP stałe, w feedzie dowolne, bo mapowane)
| pole | opis/format | limit |
|---|---|---|
| ID produktu | tekst, unikalny w sklepie | — |
| Nazwa | tekst | — |
| URL produktu | URL | — |
| URL obrazka | URL obrazka | — |
| Cena | kwota dziesiętna, cena standardowa | — |
| Bieżąca cena (Sale price) | kwota dziesiętna, cena widoczna dla klienta (np. po rabacie) | — |
| Cena Omnibus | kwota dziesiętna, najniższa cena z 30 dni przed promocją | — |
| Dostępność | logiczne, wyłącznie `true` / `false` | — |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| Kategoria | tekst (może być liczba); poziomy rozdzielane `>` | — |
| atrybuty niestandardowe | definiowane w ECDP przed importem; nazwy muszą się zgadzać w feedzie, na stronie i w ECDP | max 20 na jednostkę biznesową |

Typy atrybutów niestandardowych: Tekst (do 256 znaków), Tekst długi (do 2048, bez segmentacji), Liczba całkowita, Kwota (double), Data `DD-MM-RRRR`, Data i godzina `DD-MM-RRRR gg:mm`, Tak/Nie (`true`/`false`), URL i Obraz (do 256 znaków), Zbiór (lista rozdzielana `,` lub `>`).

## Limity i formaty
- Plik XML lub CSV, nieskompresowany, publicznie dostępny pod URL w domenie sklepu (HTTP/HTTPS).
- XML: przy imporcie wybiera się walutę dla Ceny i Bieżącej ceny oraz węzeł produktu (zwykle `product` w `feed`) — ceny należy więc podawać jako liczby bez waluty.
- CSV: separator tab / przecinek / średnik, opcjonalny nagłówek, konfigurowalne znaki cudzysłowu, escape, komentarza i kodowanie (zalecane UTF-8).
- Harmonogram: co 3 h albo własny (co godzinę, dziennie, CRON).
- Produkt nieobecny w kolejnym imporcie jest usuwany z katalogu.
- Najczęstszy błąd: dostępność jako 1/0 lub tak/nie zamiast true/false.

## Różnice względem szablonu bazowego
- `g:availability` (`in stock`/`out of stock`) → wartość `true`/`false`.
- `g:price` / `g:sale_price` z walutą → same liczby (waluta wybierana w panelu); bieżąca cena wymagana zawsze, także bez promocji (wtedy zapewne równa cenie — do potwierdzenia).
- Nowe pole: cena Omnibus (w IdoSell dostępna w eksporcie jako najniższa cena z 30 dni) — brak w `Google.xml`.
- Kategoria z `>` — zgodna z `g:product_type`.
- Pola Google typu `gtin`, `shipping`, `custom_label_*` niepotrzebne, chyba że jako atrybuty niestandardowe (limit 20).

## Uwagi
- Na stronie nie ma sekcji o nazwie „Parametry produktu” (ani w wersji EN, ani PL); najbliższe treści to „Dodaj cechy produktów” oraz wymagania importu XML/CSV — na nich oparto streszczenie.
- Strona nie zawiera przykładowego XML, informacji o wariantach ani limitach rozmiaru pliku.
