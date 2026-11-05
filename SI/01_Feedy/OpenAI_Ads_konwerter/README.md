# Konwerter feedu XML → OpenAI Ads (ChatGPT Ads)

Zamienia feed produktowy XML (Google Shopping / IdoSell) na **natywny feed OpenAI**
w formatach **CSV** i **JSONL**. OpenAI nie przyjmuje XML/RSS/Atom w żadnej ścieżce —
hostowany URL z `.xml` zawsze zostanie odrzucony, stąd ta konwersja.

Wzorce docelowych plików: `przyklady/`.
Specyfikacja: <https://developers.openai.com/commerce/specs/file-upload/products>

## Uruchomienie

Dwuklik w **`run.bat`** albo `python app.py` z tego folderu. Skrypt pyta o wszystko w konsoli:

1. wybór sklepu z `config.json` (albo „nowy sklep”),
2. adres URL feedu XML (Enter = adres zapamiętany dla sklepu),
3. dane sprzedawcy — tylko przy pierwszym uruchomieniu dla danego sklepu,
4. potwierdzenie ustawień przed konwersją.

Feed jest pobierany do `katalog/_pobrane/<sklep>.xml`; przy kolejnym uruchomieniu skrypt
pyta, czy pobrać go ponownie, czy użyć kopii z dysku.

Skróty dla powtarzalnych uruchomień (opcjonalne, nie zastępują trybu interaktywnego):

```
python app.py --sklep zooart.com.pl
python app.py --url https://sklep.pl/data/export/feedXXXX.xml
python app.py --plik lokalny_feed.xml
```

## Wyjście

`katalog/<sklep>_openai_<RRRRMMDD_GGMM>.csv` oraz `.jsonl` — UTF-8 bez BOM, jeden wiersz
nagłówka, jeden produkt/wariant na wiersz. CSV nadaje się pod hostowany URL, upload ręczny
i SFTP; JSONL to format preferowany przez OpenAI przy SFTP.

Zawartość `katalog/` to duże pliki robocze — są wyłączone z gita.

### Limit 20 MB w Ads Managerze

Pliki pełne zostają na dysku do podglądu, a obok powstaje komplet **do wysyłki**, przycięty
do limitu z `ustawienia.limit_mb`:

1. **gzip** — OpenAI przyjmuje `.csv.gz` / `.jsonl.gz`; feed Zooart schodzi z 31 MB do 6,6 MB,
   czyli jeden plik mieści się w limicie z trzykrotnym zapasem.
2. **podział na części** — gdy nawet archiwum przekracza limit (albo `gzip` jest wyłączony),
   katalog jest dzielony na `_czescNzM`, każda z własnym wierszem nagłówka. Każdy produkt
   trafia dokładnie do jednej części, zgodnie z wymogiem OpenAI dla katalogu w wielu plikach
   („each product appearing once"). Przy wyłączonym gzipie feed Zooart daje 2 części CSV
   po ok. 15 MB.

Skracanie opisów (`ustawienia.max_opisu`) to ostateczność — `description` to ok. 70% objętości
pliku, ale przycięcie do 750 znaków daje dopiero ~20 MB, kosztem treści widocznej dla modelu.

## Konfiguracja (`config.json`)

Dane, których nie ma w feedzie XML, a których wymaga OpenAI. Klucz = domena sklepu.

| Pole | Znaczenie |
|---|---|
| `feed_url` | zapamiętany adres feedu (Enter przy pytaniu) |
| `seller_name` | **wymagane** przez OpenAI w każdym wierszu |
| `seller_url` | strona sklepu |
| `return_policy` | URL regulaminu zwrotów |
| `accepts_returns`, `return_deadline_in_days` | polityka zwrotów |
| `waluta` | kod ISO używany, gdy cena w feedzie nie ma waluty; niezgodność jest raportowana |
| `store_country`, `target_countries` | rynek sklepu i kraje docelowe |
| `is_eligible_search` | zwykle `true` |
| `is_eligible_checkout` | `false`, dopóki checkout nie jest skonfigurowany po stronie OpenAI |
| `is_ads_eligible` | `true` dla feedu pod ChatGPT Ads (wymaga konfiguracji konta) |

Sekcja `ustawienia` (wspólna dla wszystkich sklepów):

| Pole | Domyślnie | Znaczenie |
|---|---|---|
| `limit_mb` | `20` | maksymalny rozmiar pojedynczego pliku wysyłanego do OpenAI; `0` wyłącza kontrolę |
| `gzip` | `true` | zapisuje wersje `.gz` (zwykle jeden plik zamiast kilku części) |
| `max_opisu` | `5000` | limit długości `description`; 5000 to maksimum OpenAI |

Kraj i waluta muszą być zgodne z ustawieniami konta OpenAI Ads — przy domyślnym targecie US
waluta PLN zostanie odrzucona.

## Co robi mapowanie

| Pole OpenAI | Źródło w XML | Uwagi |
|---|---|---|
| `item_id` | `id` / `item_id` / `sku` | duplikaty pomijane |
| `title` | `title` | przycinane do 150 znaków na granicy słowa |
| `description` | `description` | HTML i encje usuwane, przycinane do 5 000 znaków |
| `url`, `image_url` | `link`, `image_link` | wymagane `http(s)` |
| `additional_image_urls` | wszystkie `additional_image_link` | jedna komórka, po przecinku, max 10, przecinek w URL-u jako `%2C` |
| `price`, `sale_price` | `price`, `sale_price` | format `kwota WALUTA`, kropka dziesiętna; `sale_price` odrzucane, gdy nie jest niższe od `price` |
| `availability` | `availability` | `in stock` → `in_stock`, `out of stock` → `out_of_stock`, nieznane → `unknown` |
| `gtin` | `gtin`, zapasowo `mpn` | trim, walidacja długości (8/12/13/14) i cyfry kontrolnej; błędne odrzucane |
| `product_category` | pierwszy `product_type` | ścieżka `Kategoria > Podkategoria` |
| `size` | `size` | wartości typu „uniwersalny” traktowane jako puste |
| `weight`, `item_weight_unit` | `unit_pricing_measure`, zapasowo `shipping_weight` | tylko jednostki wagowe (g/kg/oz/lb) |
| `group_id`, `listing_has_variations`, `variant_dict` | `item_group_id` + `size`/`color` | ustawiane **tylko** gdy grupa ma więcej niż jeden wariant (wymóg OpenAI: `group_id` ≠ `item_id`) |
| `custom_label_0`–`4` | `custom_label_0`–`4` | czyszczone z separatorów IdoSell (`\|Bestseller\|`, `Koty;`) |
| `seller_*`, `return_*`, `store_country`, `target_countries`, flagi | `config.json` | stałe dla całego sklepu |

Produkt bez któregokolwiek z pól wymaganych (`item_id`, `title`, `description`, `url`,
`brand`, `seller_name`, `image_url`, `availability`, `price`) jest pomijany, a powód trafia
do podsumowania.

## Wynik dla Zooart (feed10082, 22.09.2026)

14 557 pozycji w XML → **14 550 wierszy**, 11 s. Pominięte: 5 bez opisu, 2 bez marki.
Odrzucone 2 błędne GTIN-y, 237 uzupełnionych z `mpn`, 3 wiersze oznaczone jako warianty.

## Ograniczenia

- Wyjście jest w schemacie natywnym. Profil **Google-compatible** (kolumny `id`, `link`,
  `image_link` …) wymaga osobnej zgody OpenAI dla konkretnego feedu i nie jest tu generowany —
  wzorzec leży w `przyklady/google_compat.csv`.
- `google_product_category` z feedu IdoSell to numeryczne ID taksonomii Google; schemat
  natywny oczekuje ścieżki tekstowej, więc używany jest `product_type`.
