# Przykładowe feedy produktowe dla OpenAI Ads (ChatGPT Ads)

Wzorce plików akceptowanych przez OpenAI Ads Manager — na danych z feedu Zooart
(`feed10082`), do podmiany pod dowolny sklep IdoSell.

**XML / RSS / Atom nie są obsługiwane w żadnej ścieżce** — obecny feed Google Shopping
(`.xml`) zawsze zostanie odrzucony przy zapisie hostowanego URL-a. Stąd te przykłady.

## Pliki

| Plik | Format | Schemat | Gdzie użyć |
|---|---|---|---|
| `openai_natywny.csv` | CSV, przecinek | natywny OpenAI | hostowany URL, upload ręczny, SFTP |
| `openai_natywny.jsonl` | JSON Lines | natywny OpenAI | SFTP (format preferowany przez OpenAI) |
| `google_compat.tsv` | TSV, tabulator | profil Google-compatible | hostowany URL, upload ręczny, SFTP |
| `google_compat.txt` | TXT, tabulator | profil Google-compatible | to samo co `.tsv`, inne rozszerzenie |
| `google_compat.csv` | CSV, przecinek | profil Google-compatible | to samo co `.tsv` |
| `google_compat.tsv.gz` | TSV + gzip | profil Google-compatible | duże katalogi (gzip dozwolony dla `.txt`/`.tsv`/`.csv`) |

Parquet (+ zstd) też jest obsługiwany przy SFTP i jest formatem preferowanym dla
bardzo dużych katalogów — pomijam go tutaj, bo to plik binarny, nie wzorzec do czytania.

## Który schemat wybrać

- **Natywny OpenAI** — działa zawsze, nie wymaga zgody OpenAI. Wymaga `seller_name`
  w każdym wierszu i daje kontrolę nad `is_eligible_search` / `is_ads_eligible`.
- **Google-compatible** — pozwala wystawić kolumny bliskie feedowi Google Shopping,
  ale **musi zostać potwierdzony przez OpenAI dla konkretnego feedu**. Nazwa sprzedawcy
  brana jest z rejestracji konta (`seller_name` z pliku jest ignorowany), a wszystkie
  przyjęte produkty mają search włączony i checkout wyłączony.

OpenAI sprawdza najpierw format natywny, potem profil Google — na próbkach z pliku.
Jeden format obowiązuje dla całego uploadu, a samo rozszerzenie pliku go nie wybiera.

## Zawartość przykładów

4 wiersze: dwa realne produkty Animonda (jeden `in_stock`, jeden `out_of_stock`)
oraz grupa dwóch wariantów tego samego produktu (2 kg / 8 kg) — pokazuje grupowanie
(`group_id` + `listing_has_variations` + `variant_dict`, w profilu Google: `item_group_id` + `size`)
oraz `sale_price`.

## Reguły, które te pliki utrwalają

- UTF-8 **bez BOM**, jeden wiersz nagłówka, jeden produkt/wariant na wiersz.
- `availability`: `in_stock`, `out_of_stock`, `pre_order`, `backorder`, `unknown`
  (profil Google: `preorder` zamiast `pre_order`, bez `unknown`).
  Wartość `in stock` ze spacją — jak w obecnym XML-u — odrzuca wiersz.
- `price` jako `kwota WALUTA`, np. `4.75 PLN` — kropka dziesiętna, bez separatora tysięcy.
  Rynek PL i walutę PLN trzeba mieć skonfigurowane na koncie, inaczej domyślnym targetem
  jest US i waluta zostaje odrzucona.
- `gtin`: dokładnie 8/12/13/14 cyfr z poprawną cyfrą kontrolną, bez spacji i myślników
  (w obecnym feedzie są spacje końcowe — trzeba trimować).
- Dodatkowe zdjęcia: jedna komórka, URL-e po przecinku, bez spacji i średników;
  przecinek wewnątrz URL-a jako `%2C`. W JSONL: tablica.
- `title` ≤ 150 znaków, `description` ≤ 5 000 znaków, czysty tekst (bez HTML i CDATA).
- W CSV cytujemy komórki z przecinkiem/cudzysłowem, cudzysłów podwajamy.
  W TSV/TXT w komórkach nie może być tabulatora ani znaku nowej linii.
- `variant_dict` w CSV/TSV to zserializowany JSON w jednej komórce.
- Kolumny `custom_label_0`–`custom_label_4` służą jako filtry produktów po stronie Ads.
- Linki do kart produktów i zdjęć muszą być publiczne (HTTPS), bez loginu i hasła w URL-u.

## Źródła

- https://developers.openai.com/commerce/specs/file-upload/products
- https://developers.openai.com/ads/product-feeds
- https://developers.openai.com/commerce/specs/file-upload/overview
