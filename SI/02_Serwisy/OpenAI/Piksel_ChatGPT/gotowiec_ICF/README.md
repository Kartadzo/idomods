# Gotowiec ICF — piksel ChatGPT Ads (YouTube IdoMods)

Kampania dodatków IdoSell z pikselem ChatGPT Ads (`oaiq`) jako plik ICF do importu w dowolnym sklepie. Pixel ID, waluta i wariant wartości zakupu to zmienne w edycji kampanii.

Status: gotowe do publikacji (2026-11-10). Zadanie: [IdoMods YouTube - Pixel pod GPT Ads](https://app.clickup.com/t/36829874/1ammhmkcve9).

## Pliki

| Plik | Co to |
|---|---|
| `piksel_chatgpt_ads.xml` | gotowiec do importu (dla widzów) |
| `INSTRUKCJA.md` | instrukcja dla widzów: import, zmienne, plik cookie, sprawdzenie |
| `zbuduj_icf.py` | buduje XML z `../dodatki/0*.html`: Pixel ID i PLN → `[config:…]`, `oppref` z `document.referrer` w `consent`, kwota zakupu `[iai:products_worth_cpa2]`; opcjonalny kod języka (`python zbuduj_icf.py gre`, tylko wewnętrznie) |
| `test_gotowca.js` | test XML: zmienne, brak danych butyolivier, logika na makiecie (`../test/test_dodatkow.js`) |
| `komentarz_clickup.txt` | komentarz do zadania (wkleja użytkownik) |
| `ANALIZA_piksel_chatgpt_gotowiec.md` | analiza, decyzje, wyniki testów |
| `zrodlo/` | eksport ICF kampanii z butyolivier.pl (poza gitem) |

## Zmiana dodatków

Poprawiasz kod w `../dodatki/` → `python zbuduj_icf.py` → `node test_gotowca.js` (musi być „WSZYSTKO OK”). Builder przerywa pracę, jeśli nie znajdzie fragmentu do podmiany, i wtedy trzeba go poprawić.
