# Przegląd nowości PPC — feedy i zdarzenia

Raz w miesiącu przegląd platform reklamowych i kont referencyjnych pod kątem nowych funkcji i możliwości optymalizacji **feedów** (specyfikacje, atrybuty, wymagania) i **zdarzeń** (CAPI, Events API, konwersje, consent mode, parametry). Zadanie ClickUp: [Nowe wytyczne do optymalizacji feedów i zdarzeń PPC](https://app.clickup.com/t/1ammhmkczj3).

- Status: w toku (pierwsza edycja 2026-11, termin 2026-11-17); cykl co miesiąc.
- Budżet: ok. 1 h na edycję.
- Ostatnia zmiana: 2026-11-12.
- Analiza: `ANALIZA_ppc_przeglad_nowosci.md`.

## Pliki

| Plik | Gdzie | Opis |
|---|---|---|
| `rejestr_nowosci.md` | git | rejestr narastający między edycjami, bez duplikatów |
| `raporty/<RRRR-MM>/RAPORT.md` | **lokalnie** w `Domino`, poza gitem | raport edycji: co nowego, co mamy, co dodać, co obserwować |
| `raporty/<RRRR-MM>/podzadania_clickup.txt` | lokalnie | nazwy i opisy podzadań do ręcznego utworzenia w ClickUp |
| `raporty/<RRRR-MM>/zrzuty/` | lokalnie | zrzuty z kont klientów |

Folder `raporty/` jest ignorowany przez git (reguła `SI/02_Serwisy/**/raporty/*`). Pracując w worktree, raporty zapisuj od razu w `C:\Users\Admin\Desktop\Domino\SI\02_Serwisy\PPC\Przeglad_nowosci\raporty\`.

## Źródła oficjalne (WebSearch)

Okres: ostatnie 30 dni od poprzedniej edycji (pierwsza edycja: 90 dni).

| Platforma | Gdzie szukać |
|---|---|
| Google Merchant Center | specyfikacja danych produktów (support.google.com/merchants/answer/7052112) i jej historia zmian; Merchant API — release notes (developers.google.com/merchant/api/latest-updates); zmiany zasad (support.google.com/merchants, „policy updates”) |
| Google Ads | konwersje, enhanced conversions, consent mode, Data Manager (support.google.com/google-ads/announcements, developers.google.com/google-ads/api/docs/release-notes, blog.google/products/ads-commerce) |
| Meta | specyfikacja katalogu; changelog Conversions API (developers.facebook.com/docs/marketing-api/conversions-api — changelog, developers.facebook.com/docs/graph-api/changelog); Events Manager |
| TikTok | parametry katalogu (ads.tiktok.com/help, „catalog product parameters”); Events API (business-api.tiktok.com/portal/docs — changelog) |
| OpenAI Ads | piksel `oaiq`, feed produktów (dokumentacja reklamodawcy OpenAI) |
| Pinterest | specyfikacja katalogu, Conversions API |
| Microsoft Ads | Merchant Center / feed, UET, enhanced conversions, consent mode |

Każda pozycja w rejestrze ma link do źródła. Jeśli źródło jest nieoficjalne (blog branżowy), zaznacz to w kolumnie „źródło”.

## Konta referencyjne (Claude in Chrome, tylko odczyt)

Przed wejściem przeczytaj plik klienta w `SI/Klienci/` i przestrzegaj jego zasad.

| Platforma | Konto | Czego szukać |
|---|---|---|
| GMC | shiori.pl, „brands” 5569270748 (pod CSS) | komunikaty, rekomendacje, nowe atrybuty w diagnostyce |
| Google Ads | 742-869-7103 (połączone z GMC shiori.pl) | rekomendacje, diagnostyka konwersji, consent mode, EC |
| Meta | butyolivier.pl | Events Manager: diagnostyka, jakość dopasowania (EMQ), nowe parametry; Commerce Manager |
| TikTok | butyolivier.pl | katalog, Events Manager: diagnostyka, jakość dopasowania |
| OpenAI Ads | butyolivier.pl | komunikaty, piksel, feed |

Niczego na kontach nie zmieniamy. Jedna sesja Claude in Chrome naraz.

## Kroki edycji

1. Odczytaj `rejestr_nowosci.md`: pozycje „do testu” i „obserwujemy” z poprzednich edycji (czy coś się zmieniło?).
2. Źródła oficjalne: wyszukiwanie po platformach, tylko zmiany z okresu edycji.
3. Konta referencyjne: komunikaty, rekomendacje, diagnostyka. Tylko to, co jest nowe albo wpływa na feed lub zdarzenia.
4. Porównaj z naszymi narzędziami:
   - szablony `xslt/szablony/Google.xml`, `Facebook.xml` (i inne według serwisu);
   - `SI/01_Feedy/SummonFeed/wymagania/*.md` (data przeglądu w nagłówku);
   - skille `.claude/skills/weryfikacja-fb/`, `.claude/skills/weryfikacja-gmc/` (w tym `specyfikacja_google.md`);
   - piksel ChatGPT `SI/02_Serwisy/OpenAI/Piksel_ChatGPT/`.

   Ocena: **mamy** / **warto dodać** (wysiłek S/M/L) / **obserwujemy** / **nie dotyczy**.
5. Dopisz nowe pozycje do rejestru (bez duplikatów; istniejącym aktualizuj status). Napisz `RAPORT.md` i `podzadania_clickup.txt`.
6. Zmiany w szablonach, `wymagania/*.md` i skillach tylko jako propozycje. Wprowadzamy je osobnym zadaniem, po zgodzie.

ClickUp jest tylko do odczytu. Podzadania i komentarz wkleja użytkownik.

## Kryterium nowości

Liczy się zmiana, która wpływa na **dane**: atrybuty feedu, wymagania, parametry zdarzeń, sposób przekazywania konwersji lub zgód. Zmiany samego interfejsu pomijamy.
