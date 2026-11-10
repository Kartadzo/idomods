# Piksel ChatGPT Ads w IdoSell — gotowa kampania dodatków (ICF)

Plik: `piksel_chatgpt_ads.xml` · Autor: IdoMods.pl · Wersja 1.0

Kampania dodaje do sklepu piksel ChatGPT Ads (OpenAI) i wysyła zdarzenia:

| Zdarzenie | Kiedy |
|---|---|
| `page_viewed` | każda podstrona |
| `contents_viewed` | wejście na kartę towaru |
| `items_added` | kliknięcie „Dodaj do koszyka” na karcie towaru |
| `checkout_started` | krok „Dostawa i płatności” |
| `order_created` | potwierdzenie zamówienia i strona po płatności |

Skrypt OpenAI ładuje się dopiero po zgodzie klienta na pliki cookies reklamowe. Zdarzenia sprzed zgody czekają w pamięci strony i wysyłają się po jej wyrażeniu.

## Zanim zaczniesz

- **Pixel ID** z panelu ChatGPT Ads (Events Manager).
- W sklepie musi być włączony **baner zgód na pliki cookies**. Bez banera klient nie może wyrazić zgody, więc piksel nie wyśle żadnego zdarzenia.

## Instalacja (ok. 5 minut)

1. Panel IdoSell → **Moderacja → Wygląd sklepu → Dodatki HTML i JavaScript** → **Import ICF kampanii**.
2. Wybierz plik `piksel_chatgpt_ads.xml` → **Wgraj plik** → w okienku języka kliknij **Wybierz**.

   **Sklep w innym języku niż polski albo w kilku językach:** kod dodatków wgrywa się do polskiej wersji językowej. W każdym z 7 dodatków (**edytuj dodatki** → **edytuj**) użyj opcji **powielenia kodu we wszystkich wersjach językowych** i zapisz. Możesz też edytować tylko wybraną wersję językową. Bez tego kroku dodatki nie pojawią się w sklepie działającym w innym języku.
3. Przy nowej kampanii „[IdoMods.pl] ChatGPT Ads - piksel OpenAI” kliknij **edytuj kampanię** i uzupełnij pola:
   - **Pixel ID ChatGPT Ads** — wklej swój Pixel ID (bez niego piksel nie działa),
   - **Waluta sklepu** — kod ISO, np. `PLN`, `EUR`, `CZK` (domyślnie `PLN`).

   Kampanię zostaw na razie **nieaktywną** (tak jest po imporcie) i kliknij **Zapisz**.
4. Kliknij **edytuj dodatki** → dodatek **„[ChatGPT Ads] consent”** → sekcja **„Ustawienia dla zgody na pliki cookies”** → **Zdefiniuj nowy plik**:
   - Dostawca: `ChatGPT (OpenAI)`,
   - Kategoria: **reklamowe**,
   - Opis do polityki prywatności, np. „Piksel ChatGPT Ads (OpenAI) — pomiar skuteczności reklam w ChatGPT.”. Kliknij **Powiel we wszystkich językach** (panel wymaga opisu w każdym języku).

   Kliknij **Zapisz**. Ustawienie zapisuje się od razu.

   Ten krok jest obowiązkowy. Plik ICF nie przenosi ustawień zgód, a bez tego kroku piksel uruchamiałby się bez zgody klienta.
5. Pozostałych dodatków nie zmieniaj. Strony, regiony i wyświetlanie dynamiczne są już ustawione.
6. **Dopiero teraz** wróć do **edytuj kampanię**, zaznacz **Aktywna: tak** i kliknij **Zapisz**.

   Kolejność ma znaczenie. Sklep odświeża ustawienia dodatków z kilkuminutowym opóźnieniem (pamięć podręczna). Jeśli włączysz kampanię przed dodaniem pliku cookie, przez te kilka minut piksel może ruszać bez zgody klienta.

Zmiany w dodatkach widać w sklepie zwykle po kilku minutach.

## Sprawdzenie

1. Otwórz sklep w oknie incognito i zaakceptuj cookies reklamowe w banerze.
2. W narzędziach deweloperskich (F12) → **Sieć**, filtr `openai`: najpierw ładuje się `oaiq.min.js`, potem idą zapytania do `bzr.openai.com`.
3. Wejdź na kartę towaru i dodaj go do koszyka, a w ChatGPT Ads (Events Manager) sprawdź, czy przychodzą zdarzenia.
4. Bez zgody (albo po odrzuceniu cookies reklamowych) nie powinno być żadnych zapytań do OpenAI.

## Dobrze wiedzieć

- **Dane klienta przy zakupie** (e-mail, telefon, imię, nazwisko) skrypt OpenAI zamienia na skrót SHA-256 w przeglądarce. Do OpenAI trafia tylko skrót.
- `items_added` liczy kliknięcie przycisku, także wtedy, gdy klient nie wybrał rozmiaru albo towar jest niedostępny i sklep go nie doda. Nadwyżka jest niewielka.
- Po kliknięciu zgody w banerze piksel rusza od następnej odwiedzonej strony. Tak IdoSell wczytuje dodatki wymagające zgody.
- Wartość zakupu to wartość towarów, bez kosztu dostawy.
- Klient, który wchodzi z reklamy i od razu akceptuje cookies, zostaje powiązany z kliknięciem w reklamę także wtedy, gdy piksel ruszy dopiero na następnej stronie.
- Zakup ma identyfikator `order_<numer zamówienia>`. Ten sam format trzeba zachować, jeśli kiedyś dojdzie wysyłka zakupów z serwera (Conversions API), żeby OpenAI nie liczyło ich podwójnie.
- Niestandardowy szablon karty towaru: `items_added` szuka przycisku `#projector_button_basket` (standard IdoSell). Gdy szablon go nie ma, zdarzenie się nie wyśle. Pozostałe zdarzenia działają.
- Plików cookie w dodatku „consent” nie usuwaj ani nie zmieniaj ich kategorii na próbę. Na sklepie testowym dodatek po usunięciu pliku przestał się wyświetlać (jego kopia też). Pomogło dopiero usunięcie kampanii i ponowny import.
- Na stronach sklepu nie wklejaj osobno `oaiq('consent', false)` — kasuje identyfikator kliknięcia w reklamę (`oppref`) i zakupy przestają się łączyć z kampanią.
