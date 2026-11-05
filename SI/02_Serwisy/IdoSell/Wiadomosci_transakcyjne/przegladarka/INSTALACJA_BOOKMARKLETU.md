# Instalacja bookmarkletu „Wiadomości transakcyjne"

1. Ustawień pobierania Chrome nie zmieniasz — eksport trafia do zwykłego folderu `Pobrane`
   (`C:\Users\Admin\Downloads`), a `run_wiadomosci.bat` sam go stamtąd zabiera do `_pobrane\` w projekcie.
   Jeśli w Chrome włączone jest „Pytaj, gdzie zapisać każdy plik", przy eksporcie zostaw proponowany folder `Pobrane`.
2. Pokaż pasek zakładek (Ctrl+Shift+B) → prawy klik → **Dodaj stronę…**
   - Nazwa: `Wiadomości transakcyjne`
   - URL: cała zawartość pliku `bookmarklet.txt` (Ctrl+A, Ctrl+C w Notatniku).
3. Użycie: panel → Administracja → Konfiguracja wiadomości transakcyjnych → wybierz sklep → kliknij zakładkę.
   - **Eksport wszystkich** — jeden ZIP do `Pobrane`, potem `run_wiadomosci.bat` → „Rozpakuj eksport (z Pobranych)".
   - **Zastosuj plan…** — wskaż folder planu przygotowany przez `run_wiadomosci.bat` (`zmiany_…` albo `do_importu_…`).
     Po zakończeniu pobierze się `weryfikacja_….zip` → `run_wiadomosci.bat` → „Weryfikacja po wykonaniu planu".
   - Import treści wyłącza w panelu wysyłkę maila w importowanym języku — bookmarklet sam włącza ją z powrotem
     tam, gdzie była włączona przed importem (w logu: „Ponownie włączono mail …").
4. Gdyby Chrome nie przyjął długiej zakładki: otwórz konsolę (F12 → Console), wklej zawartość `konsola.js`, Enter.
5. Po zmianie kodu: `python przegladarka\zbuduj_bookmarklet.py` i podmień URL zakładki.
