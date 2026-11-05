# Analiza: nowe towary z Shoparena do IdoSell (IVEMAX)

## Cel

Towary przeniesiono z Shoparena do IdoSell rok temu. Od tego czasu w Shoparenie dochodziły nowe pozycje, których w IdoSell nie ma. Trzeba przygotować plik z tymi towarami, żeby je dodać do IdoSell, a potem powiązać w Base z wFirmą.

## Dane wejściowe

- `shopArena - 2029-10-21.csv` — 4220 produktów.
- `products_export-shop52797-…csv` — 4035 towarów IdoSell. Most do Shoparena przez `size@code_external` = `KZS-<product_code>` albo `<product_code>`.

## Ustalenia

- W IdoSell brakuje **303** produktów z Shoparena.
- Migracja: najnowszy znacznik czasu w kodach IdoSell to **2025-07-26**, a najwyższy numer porządkowy to 7253. **301** z brakujących powstało później (numery 7254–7551 albo kody z datą 2025-09-06 … 2026-09-12). Pozostałe **2** to stare pozycje: `239` (lusterko lewe, stan 0) i `240` (lusterko prawe). Chyba świadomie nieprzeniesione, choć do sprawdzenia.
- 80 z nich ma numer części, który występuje już w nazwie jakiegoś towaru IdoSell. Mogą to być duplikaty albo warianty, np. oryginał i zamiennik. Oznaczę je w raporcie, nie usuwam.
- Kategorie: wszystkie 106 kategorii nowych towarów mają odpowiednik w IdoSell (`A > B` w Shoparenie = `A/B` w IdoSell, potwierdzone na przeniesionych towarach).
- Dane są kompletne: cena, zdjęcie i producent są przy każdym z 303 produktów (Iveco 283, Naveco 5, „zamiennik” 5…). Stan > 0 ma 292.

## Planowane wyjście

Skrypt `nowe_towary_shoparena.py` + `run_nowe_towary.bat` w tym folderze:

1. `nowe_towary_import_idosell.csv` — plik importu do IdoSell (nagłówki IOF jak w eksporcie panelu, separator `,`), na każdy towar:
   - nazwa, opis, krótki opis, kategoria (`/` zamiast `>`), producent, cena brutto, jednostka, waga, zdjęcia (URL-e z ivemax.com),
   - `size@code_external` = `KZS-<product_code>` — ta sama konwencja co przy migracji, żeby most do Shoparena działał dalej,
   - `size@code_producer` = numer części z nazwy, ale tylko gdy jest jeden (zgodnie z decyzją przy kodach producenta).
2. `nowe_towary_raport.csv` — lista 303 pozycji: kod Shoparena, nazwa, kategoria, cena, stan, flaga „numer części już w IdoSell (towar …)”, flaga „sprzed migracji”.

## Założenia

- Bez `@id` — towary są nowe, ID nada IdoSell.
- SEO (`seo_title`, `seo_description`, `seo_url`) przenoszę, jeśli import panelu ma na nie kolumny.

## Decyzje użytkownika (2026-10-21) — zmieniają plan powyżej

1. Zakres: **301 towarów**, bez 2 starych (239, 240). Możliwe duplikaty zostają, ale z flagą.
2. Stan magazynowy **pomijamy** — stany przyjdą z wFirmy przez powiązanie w Base.
3. Zamiast pliku importu z nagłówkami IOF: **sama lista CSV**. Użytkownik wgra ją do panelu własną aplikacją „downloader”. Wyjście to jeden plik `nowe_towary_shoparena.csv`: kolumny Shoparena bez `stock` + pomocnicze `kategoria_idosell`, `kod_zewnetrzny` (`KZS-…`), `kod_producenta` (tylko gdy w nazwie jest jeden numer), `uwagi` (numer części już w IdoSell → ID towaru).

## Otwarte pytania (zamknięte decyzjami powyżej)

1. **Zakres:** wszystkie 303, czy bez 2 starych (239, 240) i/lub bez 80 możliwych duplikatów?
2. **Stan magazynowy:** przenosić stan z Shoparena, czy pominąć? Docelowo stany ma podawać wFirma przez Base.
3. **Format:** plik importu do panelu IdoSell (jak wyżej), czy wystarczy sama lista do wglądu? Importu nowych towarów przez CSV w panelu nie mam przetestowanego — przed całością proponuję próbę na 2–3 towarach.
