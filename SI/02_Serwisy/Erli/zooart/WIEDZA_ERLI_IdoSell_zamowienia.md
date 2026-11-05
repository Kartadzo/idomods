# ERLI ↔ IdoSell: zamówienia, które nie przechodzą do sklepu

Źródło: analiza zadania ClickUp „ZooArt.com.pl - Integracja z erli” (1ammhmkbwdm), 2026-11-04.

## Gdzie co jest

### Panel ERLI (manager sklepu)
- Adres: `https://erli.pl/manager-sklepu/<id_sklepu>/...` (ZooArt: `15852`).
  - Nie `erli.pl/svc/shop-panel` (404). Z `erli.pl/moje-konto` nie ma linku do panelu, to widok kupującego.
- Lista zamówień: `/manager-sklepu/<id>/zamowienia`. Pierwsza strona nie zawiera starszych zamówień.
- Karta zamówienia: `/manager-sklepu/<id>/zamowienia/<numer_erli>`, np. `.../zamowienia/261029x17273`.
  - Treść ładuje się dynamicznie, odczyt dopiero po kilku sekundach.
  - Na karcie: data zakupu, status płatności, status zamówienia (pole `data-e2e="order-status-manual-select"`), dostawa, płatność, **zwroty płatności**, produkty z polem „Zewnętrzne ID”.
- Konfiguracja integracji: `/manager-sklepu/<id>/integracja`. Pokazuje:
  - adres sklepu i login użytkownika API IdoSell (ZooArt: `Marketplace10045`);
  - czy pobierane są zestawy;
  - sposób liczenia stanu: **wszystkie magazyny** albo wybrane.
  - Na stronie widnieje też hasło integracji kurierskiej. Nie kopiować go do notatek ani raportów.
- Dostawy i cenniki: `/manager-sklepu/<id>/dostawy`.

### Panel IdoSell
- Logi API: `/panel/api.php?shop=<n>` → „Zapis żądań i odpowiedzi do API” → `/panel/api-listener.php?shop=<n>&api=<api|marketplace-api|customer-api>`.
  - Zapis jest **domyślnie wyłączony**, można go włączyć maksymalnie na 24 h (86400 s).
  - Logi są kasowane miesiąc po zakończeniu zapisu albo przy starcie kolejnego.
  - Bez włączonego zapisu nie da się odtworzyć, co API odpowiedziało ERLI.
- `/panel/users-api.php` (klucze Admin API) zawiera sekrety. Nie czytać tekstu tej strony.
- Zestaw: karta towaru `/panel/product.php?idt=<id>`, zakładka „Zestawy i kolekcje” (`#mainTabs-tab-content-6`). Pokazuje składniki, ilości i stany per magazyn.
- Wyszukiwarka `orders-search.php?text=...` **nie znajduje zamówień po numerze ERLI**. ERLI nie jest marketplace’em natywnym IdoSell, nie ma go na liście „Konto w serwisie”.

## Format danych
- „Zewnętrzne ID” produktu w ERLI = `<id_towaru_IdoSell>-<rozmiar>`, np. `91502-uniw`.
- Numer zamówienia ERLI zaczyna się od daty: `RRMMDD x <nr>`, np. `261029x17273` = 29.10.2026.

## Mail „Wystąpił błąd zewnętrzny związany z API sklepu”
- Ten komunikat jest ogólny: oznacza, że API IdoSell odrzuciło utworzenie zamówienia.
- Podpowiedź z maila ERLI o powiązaniu metod dostawy z przewoźnikami to tylko jedna z możliwych przyczyn.

### Na co patrzeć po kolei
1. **Czy towar to zestaw** i czy składniki się nie powtarzają.
   - ZooArt 91502 „Mix smaków 24x400g”: składnik 91172 dodany dwa razy (4 × 6 szt., w tym 12 szt. jednego smaku).
2. **Stan składników per magazyn.**
   - ERLI z opcją „wszystkie magazyny” sumuje stany i pokazuje towar jako dostępny.
   - Wystarczyć może dopiero suma, przy niedoborze w głównym magazynie. ZooArt: Moszczanka 11 + RED WATER 1 = 12, przy potrzebnych 12.
   - To hipoteza, nie potwierdzono jej w logu API.
3. **Metoda dostawy** z zamówienia: czy jest powiązana z przewoźnikiem IdoSell.
4. **Stan płatności w ERLI przed wznowieniem eksportu.**
   - ZooArt: płatność zwrócono 5 dni później, a status nadal „Gotowe do realizacji”.
   - Po zwrocie nie wznawiać eksportu.
5. Jeśli przyczyna nadal jest niejasna: włączyć zapis żądań API w IdoSell, wznowić eksport w ERLI i odczytać odpowiedź.

## Stan sprawy ZooArt (2026-11-04)
- Do decyzji klienta:
  - poprawa składu zestawu 91502 (który smak miał być czwarty);
  - wstrzymanie zestawu w ERLI albo uzupełnienie 91172 w Moszczance.
- Do sprawdzenia, jeśli klient zechce: inne zestawy wystawione w ERLI pod kątem zduplikowanych składników.
