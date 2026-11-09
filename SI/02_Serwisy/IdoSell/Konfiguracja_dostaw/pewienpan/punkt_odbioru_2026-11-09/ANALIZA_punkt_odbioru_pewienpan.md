# ANALIZA: adres punktu odbioru „odbiór z butiku” (pewienpan.pl)
Zadanie ClickUp: [PewienPan.pl - problem z mapą Google](https://app.clickup.com/t/869ffngm5) · Klient: pewienpan.pl · Data: 2026-11-09

| | |
|---|---|
| Status / typ | w trakcie · WYCENA |
| Termin | 09.11.2026 (minął); czas mocno przekroczony (5,9 h przy limicie 1 h), więc działam krótko |
| Zlecająca | Katarzyna Woźniak (komentarz 09.11) |

## Cel
Przy dostawie „odbiór z butiku” klient sklepu ma widzieć punkt odbioru z adresem **ul. Nawrot 7** i telefonem **786 086 977**. **Danych magazynów nie zmieniamy.**

Według użytkownika jest to dostawa z niestandardowych punktów odbioru dla metody wysyłkowej „Odbiór w punkcie” (Polska). W tej metodzie można wprowadzić własne punkty.

Poboczne: pierwotny problem z mapą Google (`BillingNotEnabledMapError`, płatności w Google Cloud). Sprawdzam tylko, czy mapa już się wczytuje.

## Dane wejściowe i wyjściowe
**Wejście:**
- Panel `pewienpan.pl/panel`, `shop=1`.
- Link od Pawła Gacy z ClickUp: `deliveries-notes.php?delivery=100105&idr=1143020003&shop=1`, czyli uwagi do dostawy 100105.
- Metoda „Odbiór w punkcie” (Polska) z niestandardowymi punktami odbioru.
- Załącznik z komentarza 09.11: `image.png`, 72 KB. Pobieram go tylko za zgodą użytkownika, adres można zobaczyć na stronie.

**Wyjście:**
- Wyjaśnienie, skąd bierze się obecny adres i telefon.
- Niestandardowy punkt z adresem Nawrot 7 i telefonem, dodany lub poprawiony **po zgodzie użytkownika**.
- `komentarz_clickup.txt` w tym folderze.

## Plan
1. **Panel, Claude in Chrome, tylko odczyt:**
   - metoda „Odbiór w punkcie” (Polska) i lista jej niestandardowych punktów (nazwa, adres, telefon, godziny, współrzędne, przypisanie do sklepu);
   - uwagi do dostawy 100105 (link Pawła);
   - które pole decyduje o adresie widocznym w koszyku.

   Stan „przed” zapisuję w `notatki.md`.
2. **Strona sklepu, Chrome DevTools MCP** (osobny profil): koszyk z tanim produktem, 1 szt., krok wyboru dostawy. Sprawdzam, jaki adres widać i czy mapa Google się wczytuje. **Bez składania zamówienia.**
3. **Propozycja zmiany** (najpewniej nowy lub poprawiony niestandardowy punkt „Butik Pewien Pan Łódź”: ul. Nawrot 7, Łódź, tel. 786 086 977). Uzgadniam z użytkownikiem:
   - pozostałe pola: kod pocztowy, godziny otwarcia, współrzędne do mapy;
   - czy stary punkt wyłączyć.
4. **Zmiana w panelu po wyraźnej zgodzie**, a po niej kontrola w koszyku (DevTools). Zrzut „przed” i „po” do `notatki.md`.
5. **`komentarz_clickup.txt`:** źródło adresu, co zmieniono i stan mapy Google.

## Założenia
- Adres pochodzi z niestandardowego punktu metody „Odbiór w punkcie”, a nie z magazynu, zgodnie z informacją użytkownika. Krok 1 to potwierdzi.
- Miasto: Łódź (wątek ClickUp: „Butik Pewien Pan Łódź”). Kod pocztowy i godziny do potwierdzenia.
- Zmiana w panelu jest odwracalna, a stan „przed” zapisuję.

## Otwarte pytania
- Kod pocztowy i godziny otwarcia butiku: z obecnego punktu, ze strony sklepu czy od klienta?
- Czy po dodaniu nowego punktu stary ma zostać wyłączony, czy poprawiamy istniejący?
- Mapa Google: jeśli nadal pokazuje `BillingNotEnabledMapError`, nie naprawiamy tego. Opisuję to w komentarzu (po stronie klienta: płatności w Google Cloud dla klucza Maps).

## Zasady sesji
- ClickUp tylko do odczytu. Komentarz zapisuję w `komentarz_clickup.txt`, wkleja go użytkownik.
- Git: gałąź `punkt_odbioru_pewienpan` (wariant „nowy problem”). `/zapisz` i `/zamknij` wykonuje użytkownik, sesja realizująca nie commituje.
- Przed zmianą w panelu: potwierdzenie użytkownika (globalny CLAUDE.md).
- Przeglądarka: tak, jedna sesja z Claude in Chrome naraz.
- Strona sklepu (koszyk, mapa): **tylko przez Chrome DevTools MCP** (`mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`, osobny profil), nie przez Claude in Chrome. Zamówienia **nie składam**. Gdyby jednak było potrzebne: tani produkt, 1 szt., „przelew zwykły”, nigdy za pobraniem, i dopiero po zgodzie.
- Panel zostaje w Claude in Chrome.

## Stan
- 2026-11-09: analiza wstępna (sesja /zadanie). Użytkownik: dostawa z niestandardowych punktów odbioru metody „Odbiór w punkcie” (Polska), można dodać własne punkty.
- 2026-11-09: odczyt panelu i sklepu (notatki.md). Wdrożone: telefon w opisie punktu i komentarz dostawy 100105. Współrzędne punktu (0,0) czekają na support IdoSell.
