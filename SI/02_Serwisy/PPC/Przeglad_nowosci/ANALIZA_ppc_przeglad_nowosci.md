# ANALIZA: miesięczny przegląd nowości w feedach i zdarzeniach PPC
Zadanie ClickUp: [Nowe wytyczne do optymalizacji feedów i zdarzeń PPC](https://app.clickup.com/t/1ammhmkczj3) · Klient: wewnętrzne (BrandsManago / IdoMods, lista „[PPC] Rozwój Techniczny”) · Data: 2026-11-12

## Cel
Raz w miesiącu przeglądam platformy reklamowe i konta referencyjne pod kątem nowych funkcji i możliwości optymalizacji:
- **feedów**: specyfikacje produktów, nowe atrybuty, wymagania;
- **zdarzeń**: CAPI, Events API, konwersje, consent mode, nowe parametry.

Każde znalezisko to propozycja podzadania w ClickUp. Jeśli warto, trafia potem do naszych narzędzi:
- szablony summonFeed `xslt/szablony/*.xml` i `SI/01_Feedy/SummonFeed/wymagania/`;
- skille `/weryfikacja-fb` i `/weryfikacja-gmc`;
- piksel ChatGPT.

Wzór z opisu zadania: wcześniejsze testy w Meta CAPI. Budżet: ok. 1 h na edycję. Termin pierwszej edycji: 2026-11-17.

## Dane wejściowe i wyjściowe
Wejście:
- **źródła oficjalne** (WebSearch). Okres: ostatnie 30 dni, w pierwszej edycji 90 dni.
  - Google Merchant Center: specyfikacja produktów, Merchant API, zmiany zasad;
  - Google Ads: konwersje, enhanced conversions, consent mode, Data Manager;
  - Meta: specyfikacja katalogu, changelog Conversions API, Events Manager;
  - TikTok: katalog, Events API;
  - OpenAI Ads: piksel `oaiq`, feed;
  - Pinterest, Microsoft Ads;
- **konta referencyjne** (Claude in Chrome, tylko odczyt; zatwierdził użytkownik 2026-11-12):

  | Platforma | Konto | Czego szukam |
  |---|---|---|
  | GMC | shiori.pl, konto „brands” 5569270748 (pod CSS) | komunikaty i rekomendacje |
  | Google Ads | 742-869-7103 (połączone z GMC shiori.pl, według `SI/Klienci/shiori.pl.md`) | rekomendacje, diagnostyka konwersji |
  | Meta | butyolivier.pl | Events Manager: diagnostyka, jakość dopasowania, nowe parametry; Commerce |
  | OpenAI Ads | butyolivier.pl | |
  | TikTok | butyolivier.pl (wskazał użytkownik 2026-11-12) | katalog, Events Manager: diagnostyka, jakość dopasowania |

- **nasze narzędzia do porównania**: `xslt/szablony/Google.xml`, `Facebook.xml`, `SI/01_Feedy/SummonFeed/wymagania/*.md` (daty przeglądów), listy kontrolne skilli w `.claude/skills/weryfikacja-fb/`, `.claude/skills/weryfikacja-gmc/`.

Wyjście (w tym folderze; w gicie tylko `rejestr_nowosci.md` i `README.md`. Raporty zostają lokalnie w Domino, bo ignoruje je reguła `.gitignore` `SI/02_Serwisy/**/raporty/*`. Decyzja użytkownika z 2026-11-12: bez wyjątku w `.gitignore`):
- `rejestr_nowosci.md`: rejestr narastający między edycjami, bez duplikatów. Kolumny: data, platforma, nowość, źródło (link), wpływ (feed / zdarzenia), docelowe narzędzie, status (nowe / do testu / wdrożone / odrzucone / obserwujemy), edycja;
- `raporty/2026-11/RAPORT.md`: co nowego, co już mamy, co warto dodać, co tylko obserwować;
- `raporty/2026-11/podzadania_clickup.txt`: gotowe nazwy i opisy podzadań. Tworzy je użytkownik, bo ClickUp jest tylko do odczytu;
- `README.md`: jak przeprowadzić kolejną edycję (lista źródeł, konta, kroki, budżet czasu).

Zrzuty i dane z kont klientów (jeśli powstaną) zapisuję od razu w `Domino`, poza gitem (`raporty/<RRRR-MM>/zrzuty/` w `.gitignore`).

## Plan
1. `README.md` + szkielet `rejestr_nowosci.md`.
2. Źródła oficjalne: wyszukiwanie po platformach, tylko zmiany z okresu edycji, każda z linkiem do źródła.
3. Konta referencyjne (Claude in Chrome): komunikaty, rekomendacje i diagnostyka. Odnotowuję tylko to, co jest nowe albo dotyczy feedu lub zdarzeń.
4. Ocena względem szablonów i skilli: mamy / warto dodać (z szacunkiem wysiłku) / obserwujemy.
5. Raport + `podzadania_clickup.txt`. Proponowane zmiany w `wymagania/*.md`, szablonach lub skillach tylko jako propozycje; wprowadzam je dopiero po zgodzie, jako osobne zadanie.

## Założenia
- Niczego na kontach nie zmieniam: tylko odczyt.
- Nowość liczy się, gdy wpływa na feed albo zdarzenia (dane, atrybuty, parametry, wymagania). Zmiany interfejsu bez wpływu na dane pomijam.
- Szablony `xslt/szablony/` nie są edytowane w tym zadaniu. Zmiany w nich wymagają osobnej zgody (zasada summonFeed).
- Zasady klientów z `SI/Klienci/` obowiązują także przy przeglądzie ich kont: shiori.pl (struktura kont GMC bez zmian, CSS Homebook) i butyolivier.pl (plik klienta, jeśli istnieje).

## Otwarte pytania
- ~~Konto TikTok~~ → butyolivier.pl (2026-11-12).
- Czy miesięczny przegląd ma zastąpić 90-dniowy przegląd `wymagania/*.md` w summonFeed? Decyzja użytkownika po pierwszej edycji.

## Zasady sesji
- ClickUp tylko do odczytu; komentarz → `komentarz_clickup.txt` (wkleja użytkownik), podzadania → `podzadania_clickup.txt`.
- Git: worktree .worktrees/ppc_przeglad_nowosci, gałąź ppc_przeglad_nowosci; nie przełączaj gałęzi; /zapisz i /zamknij wykonuje użytkownik w tym oknie. Dane klienta (pliki ignorowane przez git: eksporty, pliki od klienta, raporty z danymi, zrzuty) zapisuj na bieżąco w Domino pod tą samą ścieżką względną (C:\Users\Admin\Desktop\Domino\<ścieżka>), nie w worktree. Gdy narzędzie zapisze je w worktree, przenieś je do Domino zaraz po wygenerowaniu. W worktree zostają tylko pliki do commita.
- Przed kodem: potwierdzenie tej analizy przez użytkownika (globalny CLAUDE.md).
- Przeglądarka: tak (konta GMC, Google Ads, Events Manager, OpenAI Ads przez Claude in Chrome) — jedna sesja z Claude in Chrome naraz.
- Zamówienie testowe i sprawdzanie zdarzeń na stronie sklepu: nie w planie. Jeśli okaże się potrzebne do testu nowości, robię to **tylko przez Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`, osobny profil) i po zgodzie.
  - Zamówienie: tani produkt, 1 szt., płatność „przelew zwykły”, nigdy za pobraniem (globalny CLAUDE.md).
  - Panele i platformy reklamowe zostają w Claude in Chrome.
- Przed przeglądem kont: przeczytaj `SI/Klienci/shiori.pl.md` (i plik butyolivier.pl, jeśli jest) i przestrzegaj zasad klienta.

## Stan
- 2026-11-12: analiza wstępna (sesja /zadanie). Konta referencyjne zatwierdzone przez użytkownika.
- 2026-11-12: raporty (`raporty/<RRRR-MM>/RAPORT.md`, `podzadania_clickup.txt`) zapisuję lokalnie w `Domino/SI/02_Serwisy/PPC/Przeglad_nowosci/raporty/`, poza gitem. Konto TikTok: butyolivier.pl.
- 2026-11-12: plan zatwierdzony przez użytkownika („ok”; uwaga użytkownika: wiadomość z akceptacją nie pochodzi z sesji w tym folderze). Start realizacji.
- 2026-11-12: `README.md`, `rejestr_nowosci.md` (12 pozycji + stan bazowy). Źródła oficjalne przejrzane (GMC, Merchant API, Google Ads, Meta, TikTok, OpenAI, Pinterest, Microsoft). Konta:
  - GMC shiori.pl „brands” przejrzane (tekstem; zrzuty ekranu w GMC się nie udały — strona stale „zajęta”);
  - Google Ads 742-869-7103 niedostępne z loginu w Chrome (brak na liście kont i pod MCC 436-334-4317);
  - Meta / OpenAI Ads / TikTok butyolivier.pl: brak identyfikatorów kont (w Chrome otwiera się konto ZooArt w Events Managerze i onboarding BrandsManago w OpenAI Ads). Pytanie do użytkownika.
- 2026-11-12: dostęp do kont uzupełnił użytkownik (Google Ads przez `ocid`, Meta `business_id`, OpenAI — przełącznik konta, TikTok `org_id`). Przegląd kont zakończony (tylko odczyt, bez zrzutów — narzędzie zrzutów zgłaszało „strona zajęta”). Rejestr: 17 pozycji + stan bazowy. `RAPORT.md` i `podzadania_clickup.txt` (7 propozycji) zapisane lokalnie w `Domino/.../raporty/2026-11/`. Edycja 2026-11 gotowa do akceptacji.
- 2026-11-12 15:3x: odpowiedzi użytkownika naniesione (rejestr #1, #13, #15, #16, nowa #18); `/weryfikacja-fb` uzupełniony o komunikaty diagnostyki i krok „API konwersji z Meta” (za zgodą: „sprawdzaj w ustawieniach”).
- 2026-11-12: „API konwersji z Meta” — włączenie 2026-11-16, kontrola co 1 h; punkt 5 powiązany z ustaleniem gotowca ICF (brak page_viewed na stronie akceptacji baneru).
- 2026-11-12: edycja 2026-11 zamknięta (/zamknij). Otwarte sprawy jako podzadania: włączenie „API konwersji z Meta” 2026-11-16, piksel ChatGPT (pkt 5), raport GMC w /weryfikacja-gmc (pkt 2).
