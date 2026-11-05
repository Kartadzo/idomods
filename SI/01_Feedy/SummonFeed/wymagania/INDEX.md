# Wymagania feedów — indeks

Źródła: folder zakładek „wymagania feedu” (lista od użytkownika z 2026-10-27).
Każdy plik serwisu ma sekcję „Elementy do wygenerowania” z linią `dozwolone: …`. Są to elementy rekordu, które serwis obsługuje. Pozostałe usuwam z kopii sterownika (`narzedzia/przytnij.py`), żeby nie liczyć ich na próżno. Gdy sekcji brak, ustalam listę z pól wymaganych i zalecanych przy pierwszym użyciu serwisu i dopisuję ją do pliku.

Regulamin aktualizacji: gdy „Data przeglądu” w pliku serwisu jest starsza niż **90 dni**, przy najbliższym wywołaniu skilla czytam źródła ponownie i aktualizuję plik (SKILL.md, krok 0.3). Strony renderowane przez JavaScript, których WebFetch nie odczyta, czytam w Claude in Chrome.

| Serwis | Plik | Format | Akceptuje Google | Szablon bazowy | Status | Przegląd |
|---|---|---|---|---|---|---|
| Google Merchant Center | [google.md](google.md) | RSS 2.0 `g:*` | tak | Google.xml | ok | 2026-10-27 |
| Google — opinie o produktach | [google_opinie_produktow.md](google_opinie_produktow.md) | własny XML (feed/reviews) | nie | nowa struktura | ok | 2026-10-27 |
| Meta (Facebook/Instagram) | [facebook.md](facebook.md) | RSS 2.0 `g:*` | tak | Facebook.xml | częściowo — strony Meta puste przez WebFetch i w przeglądarce (JS/logowanie) | 2026-10-27 |
| Microsoft Ads | [microsoft_ads.md](microsoft_ads.md) | do ustalenia | do ustalenia | Google.xml | niedostępne — link zwraca „nie znaleziono” | 2026-10-27 |
| Pinterest | [pinterest.md](pinterest.md) | RSS 2.0/Atom, CSV, TSV | częściowo | Google.xml | ok | 2026-10-27 |
| TikTok | [tiktok.md](tiktok.md) | do ustalenia (nazwy pól jak Google, `sku_id`) | częściowo | Google.xml | ok | 2026-10-27 |
| Synerise | [synerise.md](synerise.md) | RSS/Atom `g:*` + `c:*` | tak | Google.xml (Synerise.xml do porównania) | ok | 2026-10-27 |
| edrone | [edrone.md](edrone.md) | XML GMC (zalecany), Ceneo, IAI | tak | Google.xml | ok | 2026-10-27 |
| Doofinder | [doofinder.md](doofinder.md) | XML Google Shopping, CSV, JSONL | tak | Google.xml | ok | 2026-10-27 |
| WP Pixel | [wp_pixel.md](wp_pixel.md) | RSS 2.0 `g:*` | tak | Google.xml (+ `g:omnibus_price`) | ok | 2026-10-27 |
| ExpertSender | [expertsender.md](expertsender.md) | dowolny XML/CSV, mapowanie w panelu | częściowo | Google.xml | częściowo | 2026-10-27 |
| Verbolia | [verbolia.md](verbolia.md) | własny CSV/XML/JSON (camelCase) | częściowo | Google.xml (zmiana nazw pól) | ok | 2026-10-27 |
| Favi | [favi.md](favi.md) | XML Products/Product | wg źródła nieoficjalnego tak | Google.xml | częściowo — tylko źródło nieoficjalne | 2026-10-27 |
| Samba.ai | [samba.md](samba.md) | własny XML PRODUCTS/PRODUCT | nie | samba.xml | ok | 2026-10-27 |
| Ceneo | [ceneo.md](ceneo.md) | własny XML Ceneo | nie | Ceneo.xml | ok | 2026-10-28 |
| Heureka | [heureka.md](heureka.md) | XML SHOP/SHOPITEM | nie | Glami.xml | ok | 2026-10-27 |
| Glami | [glami.md](glami.md) | XML SHOP/SHOPITEM, CSV | nie | Glami.xml | ok | 2026-10-27 |
| Idealo | [idealo.md](idealo.md) | CSV | nie | Idealo.xml | ok | 2026-10-27 |
| Skroutz | [skroutz.md](skroutz.md) | własny XML mywebstore/products | nie | Google.xml (logika pól, nowa struktura) | ok — źródło niespójne, sprawdzić walidatorem | 2026-10-27 |
| ShopMania | [shopmania.md](shopmania.md) | TXT/CSV `\|` lub XML | nie | Compari.xml | ok | 2026-10-27 |
| Hotline.ua | [hotline.md](hotline.md) | własny XML/YML/CSV | nie | Ceneo.xml | ok | 2026-10-27 |
| Billiger | [billiger.md](billiger.md) | do ustalenia | do ustalenia | Biliger.xml | niedostępne — strona JS | 2026-10-27 |
| Pazaruvaj | [pazaruvaj.md](pazaruvaj.md) | do ustalenia | do ustalenia | Compari.xml (założenie) | niedostępne — panel za logowaniem | 2026-10-27 |
| Árukereső | [arukereso.md](arukereso.md) | do ustalenia | do ustalenia | Compari.xml (założenie) | niedostępne — panel za logowaniem | 2026-10-27 |
| Vergelijk.nl | [vergelijk.md](vergelijk.md) | do ustalenia | do ustalenia | — | niedostępne — PDF nieodczytany | 2026-10-27 |
| Kainos.lt | [kainos.md](kainos.md) | do ustalenia | do ustalenia | — | niedostępne — HTTP 404 | 2026-10-27 |
| Qogita | [qogita.md](qogita.md) | do ustalenia | do ustalenia | — | niedostępne — Notion renderowany JS | 2026-10-27 |

## Linki źródłowe
- Google: https://support.google.com/merchants/answer/7052112?hl=pl#basic_product_data · https://support.google.com/merchants/answer/14819809?hl=en · https://support.google.com/merchants/answer/6324436?hl=pl · https://developers.google.com/hotels/hotel-prices/dev-guide/country-codes · https://developers.google.com/product-review-feeds/schema?hl=pl
- Meta: https://www.facebook.com/business/help/120325381656392?id=725943027795860 · https://www.facebook.com/business/help/609872007120910 · https://mypresta.eu/en/art/know-how/facebook-list-of-local-language-codes.html
- Microsoft Ads: https://help.ads.microsoft.com/apex/index/3/en/51084
- Pinterest: https://help.pinterest.com/pl/business/article/before-you-get-started-with-catalogs · https://help.pinterest.com/pl/business/article/data-source-ingestion
- TikTok: https://ads.tiktok.com/help/article/catalog-product-parameters?lang=en
- Ceneo: https://www.ceneo.pl/poradniki/Instrukcja-tworzenia-pliku-XML · https://developers.ceneo.pl/api/v3/kategorie · https://developers.ceneo.pl/api/v3/atrybuty
- Samba: https://doc.samba.ai/knowledge-base/datove-feedy/?lang=en
- Synerise: https://hub.synerise.com/developers/product-feed/
- Idealo: https://idealo.github.io/csv-importer/en/csv/
- Skroutz: https://developer.skroutz.gr/feedspec/
- Verbolia: https://www.verbolia.com/knowledge/data-feed-integration/
- Billiger: https://feedonomics.com/supported-channels/billiger-feed-specs/
- WP Pixel: https://pixel.wp.pl/docs/pl/feed/index.html
- Glami: https://www.glami.pl/info/feed/#_feed-tag-manufacturer
- Favi: https://rextheme.com/product-feed-for-favi-woocommerce-cz/
- ShopMania: https://partner.shopmania.com/cp.help?topic=20
- Hotline: https://hotline.ua/about/pricelists_specs/#tr2
- ExpertSender: https://help.expertsender.com/ecdp/product-feed/
- Vergelijk: https://sc.vergelijk.nl/webshops/en/Datafeed%20manual%20EN.pdf
- edrone: https://help.edrone.me/en/articles/8294829-product-feed-requirements#h_38614418e1 · https://help.edrone.me/pl/collections/4638275-feed-produktowy
- Doofinder: https://support.doofinder.com/managing-data/the-product-data-feed
- Qogita: https://qogita.notion.site/Qogita-Seller-Integrations-Page-1fa28b47e79b805a90c4ee1a467f8eb1
- Pazaruvaj: https://www.pazaruvaj.com/admin/FeedFormat
- Heureka: https://heureka.github.io/xml-feed-specs/
- Árukereső: https://www.arukereso.hu/admin/FeedFormat
- Kainos: https://static.kainos.lt/static/xml.pdf
