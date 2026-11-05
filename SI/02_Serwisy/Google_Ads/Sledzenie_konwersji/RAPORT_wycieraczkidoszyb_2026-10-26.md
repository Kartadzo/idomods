# wycieraczkidoszyb.pl — Google Ads: diagnoza niedziałającej integracji (2026-10-26)

Panel: abcwycieraczki.pl/panel, sklep `shop=2` (wycieraczkidoszyb.pl).
Kampania dodatków: `campaign=19` „[IdoMods.pl] Google Ads - Kod konwersji oraz kod remarketingu z konwersjami rozszerzonymi”.
Wzorzec, który działa: `shop=1` (abcwycieraczki.pl), `campaign=18`.

## Przyczyna główna: brak treści dodatków w wersji językowej `zul`

Sklep wycieraczkidoszyb.pl działa na wersji językowej **`zul`** (ścieżki `/gfx/zul/`, URL-e `zul_m_…`).
Dodatek HTML renderuje się tylko w tej wersji językowej, w której ma treść.

| Dodatek (id) | `pol` | `zul` | Na stronie sklepu |
|---|---|---|---|
| 33 [gAds] header gtag.js | 386 zn. | **0** | brak |
| 36 [gAds] Konwersja rozszerzona | 846 zn. | **0** | brak |
| 34 [gAds] "Zakup" conversion tag | 598 zn. | **0** | brak |
| 35 [gAds] page_view product | 264 zn. | **0** | brak |
| 37 [gAds] Cart | 424 zn. | **0** | brak |
| 11 google-site-verification (kontrola) | 0 | 189 zn. | **jest** |
| 7 GWT (kontrola) | 189 zn. | 0 | brak |

Dowód: w HTML sklepu są tylko znaczniki `<!--6|2|6-->`, `<!--12|2|11-->`, `<!--11|2|10-->`, `<!--19|2|15-->`.
Z kampanii 19 nie renderuje się nic, na żadnej podstronie. Na abcwycieraczki.pl (wersja `pol`) dodatek 27 renderuje się z `AW-724342151`.
Ustawienia wszystkich 5 dodatków w c18 i c19 są identyczne (kod, region, podstrony, urządzenia, auto_block) — różnica to wyłącznie język sklepu.

**Naprawa:** w każdym z 5 dodatków kampanii 19 wkleić ten sam kod do zakładki wersji `zul` (albo przełączyć dodatek na wspólną treść dla wszystkich języków, jeśli panel na to pozwala).

## Przyczyna dodatkowa: spacja w etykiecie konwersji

Parametr kampanii `conversion_label` = `" Fl0-CMLj1aUdEIGF0soD"` (21 znaków, spacja na początku).
`send_to` przyjmie postać `AW-961839745/ Fl0-…` i Google Ads nie dopasuje akcji konwersji.

**Naprawa:** usunąć spację → `Fl0-CMLj1aUdEIGF0soD`.

## Do decyzji: stara konwersja na tym samym koncie

Kampania `campaign=5` „Kod google zam” (dodatek 5, aktywny, strona po złożeniu zamówienia, wersja `zul`)
wysyła starą konwersję `conversion.js` na **to samo konto** `961839745`, etykieta `LWxyCJ-6rwsQgYXSygM`.
Po uruchomieniu nowej kampanii zakup będzie raportowany przez dwie akcje konwersji. Jeśli obie są „podstawowe” w Google Ads — podwójne liczenie.
Rekomendacja: po potwierdzeniu, że nowa konwersja wpada, wyłączyć kampanię 5 lub ustawić starą akcję jako „dodatkową”.

## Co działa poprawnie

- Systemowa integracja IdoSell w `<head>`: `gtag config AW-17813761056` (z `allow_enhanced_conversions`) i `G-G3CPTH3BC9`, remarketing `viewthroughconversion/17813761056` leci.
- Consent Mode v2: `default denied` → `update granted` po zgodzie.
- Uwaga: `AW-17813761056` (integracja systemowa) ≠ `AW-961839745` (kampania dodatków). Warto potwierdzić, które konto Google Ads jest docelowe.

## Weryfikacja po poprawce

1. Strona główna wycieraczkidoszyb.pl: w źródle znacznik `<!--33|2|19-->` i `gtag/js?id=AW-961839745`.
2. Karta towaru / koszyk: dodatki 35 i 37.
3. Zamówienie testowe (tani produkt, minimalna ilość) → na stronie po zamówieniu dodatki 34 i 36, w Google Ads Tag Assistant zdarzenie `conversion` z `send_to` bez spacji.
