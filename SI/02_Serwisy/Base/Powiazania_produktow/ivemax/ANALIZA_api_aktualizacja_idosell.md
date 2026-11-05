# Analiza: aktualizacja towarów IVEMAX przez API IdoSell

## Cel

Wgrać zmiany przez REST Admin API (`client52797.idosell.com`, v8.12), w kolejności:
1. **Kody producenta** z `aktualizacja_kod_producenta.csv` (3350 towarów).
2. **Nowe towary** z `nowe_towary_shoparena.csv` (301) — osobna analiza po zakończeniu etapu 1.

Kolejność jest celowa: przy dodawaniu nowych towarów IdoSell ostrzeże o powtórzonych kodach (EAN, kod zewnętrzny, kod producenta), o ile sklep nie ma włączonego ignorowania powtórzeń.

## Etap 1: kody producenta

**Bramka:** `PUT /api/admin/v8/products/sizes`, sprawdzona w specyfikacji panelu (`/api/doc/admin/v8/json`):
```json
{"mode": "edit",
 "sizesProductsData": [
   {"productId": 14, "sizes": [{"sizeId": "uniw", "sizeData": {"codeProducer": "7188725"}}]}
 ]}
```
Tryb `edit` zmienia tylko podane pole, a pozostałych danych rozmiaru nie rusza. Klucz przetestowany odczytem `GET products/products` (towary 14 i 790). Nic nie zostało zmienione.

**Przebieg skryptu `api_kod_producenta.py` (+ `run_api_kod_producenta.bat`):**
1. Wczytuje `aktualizacja_kod_producenta.csv`.
2. **Sprawdza stan na żywo** (`GET products/products` paczkami po 100). Pomija towar, który ma już kod producenta. Eksport jest z 16:41, a klient mógł od tego czasu zacząć uzupełniać kody ręcznie — nie nadpisuję jego pracy.
3. **Próba:** najpierw 3 towary, potem odczyt kontrolny, czy kod się zapisał. Na pełny przebieg przechodzi dopiero wtedy, gdy wszystkie 3 się zgadzają.
4. Pełny przebieg paczkami po 100 towarów (limit wyników bramki to 100), z ponawianiem przy 429/5xx.
5. Dziennik `wyniki/api_kod_producenta_<data>.csv`: ID, kod, status (`zapisano` / `pominięto - kod już jest` / `błąd: <treść z API>`), a obok surowe odpowiedzi API (`.jsonl`).

**Ryzyko — powtarzające się kody:** w pliku 341 kodów występuje w więcej niż jednym towarze (730 wierszy). To głównie pary oryginał / „ZAMIENNIK” z tym samym numerem OE. Jeśli sklep wymaga unikalnego kodu producenta, API odrzuci drugi towar z pary. Takie błędy trafią do dziennika, a skrypt idzie dalej. Po przebiegu podam listę do decyzji.

**Klucz API:** zapisany w `config.json` w tym folderze, nie w kodzie. Plik trzeba dopisać do głównego `Domino/.gitignore` (`SI/02_Serwisy/Base/Powiazania_produktow/ivemax/config.json`) — wymaga to edycji pliku poza tym folderem, dlatego proszę o zgodę.

## Wynik etapu 1 (2026-10-21, 17:54)

- Zapisano **2740** kodów producenta: 3 w próbie i 2737 w pełnym przebiegu, każdy potwierdzony odczytem kontrolnym. Błędów API: 0.
- Pominięto: 474 duplikaty (decyzja klienta), 130 zamienników z kodem oryginału, 5 kodów zajętych przez inny towar, 4 towary z już wpisanym kodem (np. 175 — wpisany ręcznie przez użytkownika).
- Dzienniki: `wyniki/api_kod_producenta_2026-10-21_175413.*` (próba) i `…_175442.*` (pełny przebieg).
- `GET products/sizes` ignoruje filtr `productIds` i zwraca cały sklep stronami (`result::page`, `result::pageNumber` ≤ 100).

## Uboczne ustalenie

W IdoSell `productDescription` (krótki opis) towaru 14 = `7188725`, czyli ten sam numer magazynowy co `short_description` w Shoparenie (= SKU wFirmy). Krótki opis jest też w eksporcie CSV, więc przy wznowieniu powiązań w Base może zastąpić most przez Shoparenę.

## Decyzje użytkownika (2026-10-21)

1. `config.json` z kluczem — tak, dopisany do głównego `.gitignore`. Używamy **drugiego klucza** (ma szersze uprawnienia).
2. Panel blokuje duplikaty kodu producenta (sprawdzone ręcznie na 175/176). **Wysyłamy tylko oryginały, a nie zamienniki.** Rozkład 341 grup z powtórzonym kodem:
   - 126 grup z dokładnie jednym oryginałem → wysyłam ten oryginał;
   - 210 grup z kilkoma oryginałami (np. 44 i 3097 — identyczna nazwa) → pomijam, decyzja klienta;
   - 5 grup z samymi zamiennikami → pomijam, decyzja klienta.
   Do wysyłki: 2620 unikalnych + 126 = **2746 towarów**. Pominięte trafiają do dziennika ze statusem `pominięto - duplikat kodu`.

## Otwarte pytania (zamknięte decyzjami powyżej)

1. Zgoda na dopisanie `config.json` do głównego `.gitignore`?
2. Czy towary z powtórzonym kodem (730) wysyłać wszystkie, czy wysłać tylko pierwszy z każdej pary, a resztę zostawić klientowi?
