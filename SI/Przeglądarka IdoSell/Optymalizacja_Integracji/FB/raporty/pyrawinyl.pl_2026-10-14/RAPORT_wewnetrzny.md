# Weryfikacja Meta Ads — pyrawinyl.pl — 2026-10-14 (stan bazowy)

ClickUp: [Pyrawinyl.pl FbAds - Optymalizacja katalogu i API konwersji](https://app.clickup.com/t/869c8x2g9)
Pierwsza weryfikacja w tym trybie, więc to **stan bazowy** do porównania za ~90 dni.

## Identyfikatory

| Element | Wartość |
|---|---|
| Panel IdoSell | pyrawinyl.pl/panel (techniczny: client50537.idosell.com) |
| Meta Pixel / zestaw danych | 1252442933515000 („PyraWinyl Pixel”) |
| Business Manager (portfolio „Pyra Winyl”) | business_id=1345261134266694 |
| Katalog | 1925211341430527 („Catalogue PyraWinyl”) |
| Źródło feedu w katalogu | 1552342449386375 („Catalogue PyraWinyl - IdoMods </>”), zastępowanie co godzinę |
| Feed w IdoSell | porównywarki → „Facebook ads [IdoMods]” (id serwisu 10001), plik `feed10001_….xml` |

## Panel IdoSell

| Punkt | Wynik | Status |
|---|---|---|
| Integracje FB (`social-services.php`) | Pixel WŁ, FBE2 WŁ, logowanie FB WŁ; natywny feed, pobieranie katalogów, eksport bazy — WYŁ | OK |
| Generowanie feedu | Aktywny, wygenerowany 2026-10-14 14:01:53, 3569/3569 (Google ads: 3570) | OK |
| Historia pobrań | 1042 wpisy od 2026-08-15 (retencja ~60 dni), wyłącznie „Pobranie pliku porównywarki” z `*.fbsv.net` | OK |
| Ustawienia serwisu | IOF 3.0, sterownik XSLT (66 062 zn.), eksport: magazyny własne+obce, pokazywane mimo niedostępności, info o niedostępności; **przedsprzedaż WYŁ** | Uwaga |
| XSLT — ID | 1 `<item>` na produkt (`sizes/size[position()=1]`), `g:id` = `product/@id`, `g:item_group_id` = `group/@id`. Filtr: `price/@gross > 0` i niepusta nazwa | OK |
| XSLT — dostawa | Na sztywno: `Koszt_dostawy`=13, `kwota_dla_darmowej_dostawy`=400, kraj PL | Uwaga |
| Cennik dostaw (profil STANDARD, tylko PL) | Najtańsza: InPost Paczkomaty 12,90 zł do 400 zł, 0 zł od 400,01 zł; InPost Kurier do 13,00 zł; ORLEN 15,26 / DPD 21–23 zł, darmowe od 400 zł | Baza |

## Meta — katalog

| Punkt | Wynik | Status |
|---|---|---|
| Wczytanie feedu 14.10 17:01 | 3569 zaktualizowanych, 0 usuniętych, 0 błędów | OK |
| Problemy | 996 × „Produkt niedostępny” (out of stock — świadomy eksport) | Info |
| Odrzucone | 4 × nagość na okładce: ID 414, 1761, 2543 (Jimi Hendrix „Electric Ladyland”), 3606 (Scorpions „Lovedrive”). Okładki faktycznie zawierają nagość, więc **prośby o weryfikację nie wysłano** | Info |
| Opisy | Część opisów zaczyna się od niewypełnionego szablonu „Utwór1 2:32” ×4 (np. ID 414, 1761, 3606, 3783) — do poprawy po stronie sklepu | Uwaga |
| Dopasowanie katalogu (28 dni) | 99,6% — VC 99,8%, ATC 97,7%, Purchase 92,1%; ostrzeżenie „content IDs not matching” | OK |

## Meta — zdarzenia (16.09–13.10)

| Zdarzenie | Integracja | EMQ | Liczba |
|---|---|---|---|
| ViewContent | Wiele | 6.1 (zalecana aktualizacja) | 41 426 |
| PageView | Przeglądarka | — | 29 085 |
| Search | Wiele | 6.2 (zalecana aktualizacja) | 3 021 |
| AddToCart | Wiele | 6.2 | 921 |
| Purchase | Wiele | 8.2 | 251 |
| InitiateCheckout | Wiele | 6.3 (zalecana aktualizacja) | 183 |
| AddPaymentInfo | Wiele | 6.8 | 168 |
| AddToWishlist / CompleteRegistration / Return | tylko CAPI | — | 13 / 6 / 2 |

- **Wolumen dzienny**: ~2490/dzień (16–22.09) → ~1830/dzień (07–13.10), **−26%**. Pik 24.09 (7621).
- **Purchase — piksel vs serwer**: suma z wykresu 44 (przeglądarka) vs 207 (serwer) → piksel ≈ 21%. Meta: „piksel < 25% zdarzeń CAPI”, więc nie raportuje dodatkowych konwersji.
- **Purchase — parametry CAPI**: email/fn/ln/ct/country/external_id 100%, ph 77%, UA 58%, st 58%, zp 42%, **fbp 39%**.
- **Diagnostyka (aktywne)**: `s2s_missing_ua` — 41% Purchase z serwera z IP bez User-Agent (wykryto 14.10). Sugestia Meta „Conversions API with Meta (CAPIG)” — pomijamy, bo jest natywne CAPI.
- **Deduplikacja Purchase**: event_id 100% (7 dni: 2/dzień przeglądarka, 5/dzień serwer).
- **ViewContent — parametry**: IP/UA 100%, fbp 95,7%, fbc 72,8%, email/telefon 2,3% (tylko zalogowani), brak external_id. Rekomendacje Meta: IPv6, login ID, dane adresowe — ograniczenia natywnej integracji.
- **FBE2** (sprawdzone ze względu na problem z CAPI): tylko „Wyłącz integrację” i „Konfiguracja FBE” (okno Meta). Brak ustawienia źródeł zamówień dla CAPI.

## Wnioski

1. **Proporcje CAPI/piksel w normie.** IdoSell zawsze wysyła z API więcej zdarzeń niż było działań użytkownika i polega na deduplikacji po stronie Meta. Purchase z API pochodzi z aktywacji „Meta Pixel” w panelu, a pozostałe zdarzenia API z FBE2. Brak UA i `fbp` w części Purchase oraz niski udział piksela to typowy obraz, nie błąd. **Alarm** dopiero przy wzroście zdarzeń API kilkadziesiąt lub sto razy ponad normę, wtedy zgłoszenie do IdoSell (patrz procedura).
2. **Purchase match 92,1%** (info). Prawdopodobnie przedsprzedaż (świadomie wyłączona z eksportu).
3. **Koszt dostawy w feedzie** (niski): 13,00 → 12,90 zł, poprawia użytkownik.
4. **Spadek wolumenu −26%** (info): porównać z ruchem w sklepie i budżetami kampanii.

### Stan bazowy proporcji (do porównania za 90 dni)

| Wskaźnik (16.09–13.10) | Wartość |
|---|---|
| Purchase: serwer / przeglądarka (suma z wykresu) | 207 / 44 ≈ **4,7×** |
| Purchase: średnio 7 dni z kluczem deduplikacji | serwer 5/dzień, przeglądarka 2/dzień |
| ViewContent (Wiele) / PageView (przeglądarka) | 41 426 / 29 085 ≈ **1,4×** |
| Wszystkie zdarzenia dziennie | ~1800–2500 (pik 7621 w dniu 24.09) |
| Purchase vs InitiateCheckout | 251 vs 183 |

## Parametry sklepu a konfiguracja sterownika

Porównuję tylko zmienne z początku sterownika. Logikę XSLT uznajemy za działającą, bo Meta przyjmuje feed. Źródło: drzewo `/panel/parameters.php` (38 parametrów). Liczba produktów na parametr nie była dostępna, więc podaję liczbę wartości.

**Zmienne obecne w konfiguracji:**

| Zmienna | Wartość | W sklepie | Ocena |
|---|---|---|---|
| `kolor_nazwa_w_panelu` | `\|kolor\|` | „Kolor” (wielka litera): beż, biały, czarny, czerwony, szary — sprzęt audio | Dopisać `\|Kolor\|` (1 min pracy). Mała liczba produktów, niski priorytet |
| `material_nazwa_w_panelu` | `\|materiał\|` | brak parametru | Bez zmian |
| `gender_nazwa_w_panelu` | puste | „Wariant”: damska, męska (pojedyncze produkty, odzież/merch) | Opcjonalnie `\|Wariant\|` + `gender_female=\|damska\|`, `gender_male=\|męska\|`. Mało produktów, niski priorytet |
| `age_group_*` | puste | brak | Bez zmian (płyty) |

**Nowe lub kluczowe parametry do rozważenia (wymagają nowego kodu):**

| Parametr | Wartości | Zastosowanie w Meta | Jakość / nakład |
|---|---|---|---|
| **Stan** | Nowa, Używana, Używany, CBS, Rafał do uzupełnienia | `g:condition` — kluczowe dla sklepu z używanymi płytami. Sterownik bierze stan z kontekstu `CONTEXT_STATE`, którego nie konfiguruje się zmienną; prościej przypisać w panelu kontekst „Stan” do parametru niż zmieniać XSLT | **Do sprawdzenia w pierwszej kolejności.** Wartości do uporządkowania: duplikat Używana/Używany, śmieci „CBS”, „Rafał do uzupełnienia” |
| **PYRA SZTOSY** | TAK | `custom_label` — wyróżnione produkty do osobnych zestawów i kampanii | Dobra jakość, mało kodu (wzorzec jak przy Nowość/Bestseller w `custom_label_1`) — **polecam** |
| Format | 7", 12", 12"/45 rpm, CD, REMASTERED, Usługa | `custom_label` do segmentacji (LP / single / CD) | Dobra po oczyszczeniu (REMASTERED i Usługa to nie formaty), mało kodu |
| Kondycja Płyty / Kondycja Okładki | skala Goldmine (M, NM, EX, VG+…) + „do uzupełnienia”, „oceniający do uzupełniania/uzupełnienia”, „1985”, „BRAK” | `product_detail` / tytuł — ważne dla kupujących używane płyty | Średnia jakość, wymaga sprzątania wartości i nowego kodu (`product_detail` nieobsługiwany) — średni nakład |
| Rok Wydania | 74 lata (1957…) | `product_detail` | Dobra jakość, ale wartość reklamowa niska |
| Gatunek | 477 wartości, niespójne (np. „Alleluja - Ballady Leonarda Cohena”, warianty ROCK/…) | `custom_label` / `product_type` | **Niska jakość** — sensowne dopiero po zmapowaniu na ~10 gatunków głównych, dużo pracy |
| Kraj | 70 wartości, zmieszane z latami (1973–1989) i „do uzupełnienia” | — | **Niska jakość**, nie warto |
| Artysta / Wykonawca | 1074 / dublujące się role | — | Wykonawca jest już w tytułach, `brand` = wytwórnia; nie warto |
| Sprzęt: MODEL (19), MOC, TYP, TYP NAPĘDU, IMPEDANCJA, EFEKTYWNOŚĆ, WYMIARY, MASA, WAGA, PRZETWORNIKI | po kilka–kilkanaście | MODEL → `mpn` | **Kilkanaście produktów**, nakład niewspółmierny |
| Nośnik | tylko LP | — | Pomijalny |

## Proponowane zmiany (do akceptacji, niewdrożone)

| # | Zmiana | Gdzie | Przed → po | Status |
|---|---|---|---|---|
| 1 | Koszt dostawy w XSLT | Porównywarki → Facebook ads [IdoMods] → Sterownik, `Koszt_dostawy` | `13` → `12.90` | Poprawia użytkownik |
| 2 | Eksport przedsprzedaży | Ustawienia serwisu → Eksportuj | — | Decyzja: zostawiamy |
| 3 | 4 odrzucone produkty | Commerce Manager → Produkty → Działania | — | Nie wysłano prośby (nagość faktyczna) |
| 4 | `kolor_nazwa_w_panelu` | Sterownik, zmienna | `\|kolor\|` → `\|kolor\|Kolor\|` | Propozycja |
| 5 | `custom_label` z PYRA SZTOSY | Sterownik, nowy kod | — | Propozycja |
| 6 | Kontekst „Stan” dla parametru Stan + porządek wartości | Panel → Parametry | — | Propozycja (sklep) |

## Zrzuty

`zrzuty/01…14_*.png` — kolejno: feed IdoSell, historia pobrań, profil dostaw, progi InPost, źródła danych Meta, podsumowanie feedu, przegląd katalogu, dopasowanie katalogu, dopasowanie wg zdarzeń, zdarzenia, diagnostyka, Purchase piksel vs CAPI, EMQ ViewContent, EMQ Purchase.
