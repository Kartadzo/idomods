# ivemax.com — wiadomości transakcyjne: stan przed migracją
Panel `client52797.idosell.com`, sklep 1 · eksport tylko do odczytu 2026-11-12 11:34 (skill `/wiadomosci-transakcyjne`, tryb Status) · pełny raport: `status_2026-11-12_113445.md`, tabela: `status_2026-11-12_113445.csv`. Pliki eksportu (ICF, HTML): `SI/02_Serwisy/IdoSell/Wiadomosci_transakcyjne/Eksport i Import Treści/client52797_shop1/2026-11-12_113445/`.

## Najważniejsze

1. **Treści to czysty standard IdoSell.** W 136 wiadomościach nie ma marki „Ivemax”/„VIKI” ani żadnych zmian pod klienta. Ostatnie edycje pochodzą od „Support” IdoSell: 2016 (szablony bazowe) i 08.2025 (25 wiadomości, aktualizacja standardu). Odpowiada to na pytanie z ticketu z 22.09: **IdoSell niczego pod ivemax nie ustawiał**, poza domyślnym szablonem.
2. **Klienci zagraniczni dostaną maile po polsku.** Dla FR, ES, NL, SV i IT treści są kopią PL (1386 pozycji „identyczna z PL lub EN” w kontroli jakości), a maile w tych językach są **włączone** (72 wiadomości na język). Do czasu tłumaczeń to realne ryzyko przy zamówieniach z FR, NL, AT i DE. EN i DE mają treści standardowe IdoSell w swoich językach.
3. **16 wiadomości ma wyłączony mail PL, a włączony EN/DE**, w tym ważne dla obsługi zamówień:
   - Rozliczenie zamówienia: **Przyjęcie wpłaty**, Anulowanie niezaksięgowanej przedpłaty, Zablokowanie/Włączenie wpłaty zaliczki;
   - Realizacja: **Podziękowanie za zakupy i informacja o dostarczeniu paczki**, Zmiana statusu na Reklamację, na Zwrot; Zwrot anulowany przez klienta;
   - Klienci: Potwierdzenie zmian w koncie, Konto przy zakupach bez rejestracji, Zmiana danych przez obsługę;
   - Prośba o potwierdzenie zamówienia wprowadzonego przez panel (×2), Zmiana ceny produktu obserwowanego, Polecenie produktu/sklepu.

   Do decyzji: które z nich włączyć w PL. Zestaw wygląda na domyślny układ IdoSell, a nie na świadomy wybór.
4. **SMS:** włączone tylko 2 (PIN do logowania, kody autoryzacyjne). Brak nadawcy SMS (branding) w konfiguracji kont.
5. **Zmienne:** 177 niezgodności `[iai:…]` między językami, głównie w SMS DE/EN (inne zmienne niż w PL). Ma to znaczenie dopiero po włączeniu SMS lub przy tłumaczeniach.
6. **Błąd eksportu:** „Kody autoryzacyjne w sklepie” (`mfa_otp_shop_pin`) dla FR, ES, NL, SV, IT. Panel zwraca HTTP 500 przy eksporcie ICF. Pozostałe języki tej wiadomości są w eksporcie.
7. **Nadawca:** wszystkie wiadomości wychodzą z konta `shop@shop52797-1.yourtechnicaldomain.com` (jedyne konto e-mail w panelu). Patrz `../stan_panelu.md`.

## Liczby

| | Liczba |
|---|---|
| Wiadomości | 136 (112 edytowalnych, 24 wycofywane) |
| Mail włączony: PL / EN / DE | 72 / 87 / 87 |
| Mail włączony: FR, ES, NL, SV, IT | po 72 (treść = PL) |
| SMS włączony | 2 |
| Web Push | 0 |
| Wiadomości z brakami szablonów („6 z 8”) | 20 |

## Przygotowanie do pracy nad treściami (bez zmian w panelu)

- Eksport z 12.11 to **kopia stanu wyjściowego**. Każda późniejsza edycja i import porównuje się z nim (odciski treści).
- Kolejność proponowana po decyzji klienta i dostępie do tłumaczeń:
  1. Decyzja, które wiadomości wysyłamy (CSV `konfiguracja` w skillu). Najpierw włączenie brakujących PL z punktu 3.
  2. Branding PL: nagłówek i stopka (logo, dane kontaktowe, adres nadawcy w domenie ivemax.com po ustawieniu poczty).
  3. Tłumaczenia FR/ES/NL/SV/IT (i przegląd EN/DE). Aplikacja „Idomods Translator” jest już podpięta do panelu (klucz Admin API aktywny 12.11). Tłumaczenie skillem przez pliki `<j>_mail.html` → plan importu → import ICF.
  4. Do tego czasu rozważyć **wyłączenie maili FR/ES/NL/SV/IT** albo ukrycie tych języków na froncie (decyzja klienta, pytanie 8 w `../komentarz_clickup.txt`).
- Zgodnie z zasadą klienta edycja i tłumaczenia czekają na zielone światło dla aplikacji do tłumaczeń.
