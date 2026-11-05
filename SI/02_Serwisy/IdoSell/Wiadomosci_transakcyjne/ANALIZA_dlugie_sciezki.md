# Analiza: błąd WinError 206 (za długa ścieżka) w wersji dystrybucyjnej

Data: 2026-10-14 · Status: **zaakceptowana i wykonana 2026-10-14** (gałąź `wiadomosci-dlugie-sciezki`, bez commita).
Wynik: `.exe` przebudowany; ZIP alpha-teile rozpakowany w folderze dystrybucji (136 wiadomości, 707 plików,
najdłuższa ścieżka 256 znaków); raport Status identyczny jak dla starego układu folderów (133 problemy — cecha sklepu).
Uwaga z wykonania: `TemporaryDirectory.cleanup` też nie usuwa ścieżek > 260 — stąd `ignore_cleanup_errors` przy weryfikacji.
Gałąź `wiadomosci-transakcyjne` z §4 już nie istnieje (narzędzie jest nieśledzone na `main`) — założona nowa.

## 1. Co się dzieje

Rozpakowanie `eksport_alpha-teile_shop1_20261014-120404.zip` w `.exe` kończy się błędem
`[WinError 206] Nazwa pliku lub jej rozszerzenie są za długie`.

Przyczyna: klasyczny limit Windows **MAX_PATH = 260 znaków** (dla folderu praktycznie 248). Program nie włącza
obsługi długich ścieżek, a Windows 10 domyślnie jej nie ma (wymaga klucza w rejestrze `LongPathsEnabled`).

Policzone na tym eksporcie:

| Element ścieżki | Znaki |
| --- | --- |
| `C:\Users\Admin\Desktop\Domino\SI\...\dystrybucja\Wiadomosci_transakcyjne\Eksport i Import Treści\alpha-teile_shop1\2026-10-14_120404` | 192 |
| `\make_order__order_confirmation_request_wholesale_from_panel` | +60 → **252** (folder > 248 → błąd) |
| `\pol_mail.html` | +14 → 266 |
| najdłuższa wiadomość: `subscriptions__subscription_upcoming_payment_after_amount_change` | 64 |
| weryfikacja: `...\do_importu_<data>\po\<wiadomość>\pol.icf` | **~350** |

Wniosek: problem nie dotyczy „niektórych eksportów”, tylko **sklepów z długimi nazwami szablonów** (hurt, subskrypcje)
w połączeniu z **głęboko położonym folderem programu**. Wersja deweloperska ma o 36 znaków krótszą bazę, więc
rozpakowanie przechodzi, ale weryfikacja importu (`po\`) też by tam padła. U użytkownika — instrukcja poleca Pulpit
albo Dokumenty, a nazwa sklepu i ścieżka profilu mogą być dłuższe — błąd jest realny.

## 2. Wejście / wyjście

- Wejście: ZIP-y eksportu/weryfikacji z bookmarkletu (bez zmian).
- Wyjście: te same pliki co dziś, ale w ścieżkach mieszczących się w limicie; program nie wywraca się na długich ścieżkach.

## 3. Planowane zmiany (trzy warstwy)

1. **Program odporny na długie ścieżki** (`wt/wspolne.py`): na Windows `KATALOG_GLOWNY` dostaje prefiks
   rozszerzonej ścieżki `\\?\` — wszystkie foldery trybów pochodzą z niego, więc zapis/odczyt/`exists`/`glob`
   przestają podlegać limitowi 260 bez zmian w pozostałych modułach. Funkcja `pokaz()` usuwa prefiks w komunikatach
   dla użytkownika (żeby w konsoli było `C:\...`, a nie `\\?\C:\...`). Do sprawdzenia testem: `glob` i `relpath`
   z prefiksem `\\?\` (znak `?` to metaznak glob — w części dysku Python go nie interpretuje, ale zweryfikuję).
2. **Krótsze ścieżki, żeby pliki dało się otworzyć w Notatniku/Eksploratorze i wskazać w Chrome**
   (sam prefiks `\\?\` nie pomaga edytorom użytkownika):
   - folder wiadomości = sam `template` zamiast `grupa__template` (szablony są unikalne w sklepie — w tym eksporcie
     136/136; grupa jest w `meta.json` i w raporcie Status). Najdłuższy folder spada z 64 do ~50 znaków.
     Zgodność wstecz: `folder_wiadomosci()` używa starej nazwy, jeśli taki folder już istnieje w rozpakowanym eksporcie.
   - weryfikacja: eksport „po” rozpakowywany do **folderu tymczasowego** (usuwany po raporcie) zamiast
     `do_importu_<data>\po\` — raport weryfikacji zostaje w folderze planu jak dziś.
3. **Ostrzeżenie zamiast zaskoczenia**: przy starcie, gdy ścieżka folderu programu przekracza ~100 znaków,
   program wypisze: „Folder programu leży głęboko (N znaków) — przy sklepach z długimi nazwami wiadomości pliki mogą
   się nie otwierać w Notatniku. Najlepiej przenieś folder np. do `C:\Wiadomosci_transakcyjne`.” Ta sama wskazówka
   trafi do `INSTRUKCJA.html` (krok 1 + tabela problemów), a przykład folderu wiadomości zmieni się na `order_confirmation`.

Pliki: `wt/wspolne.py`, `wt/eksport.py`, `wiadomosci.py`, `dokumentacja/INSTRUKCJA.html`, testy w `testy/`
(nowy test: rozpakowanie przy bazie ~200 znaków + zgodność ze starą nazwą folderu). Na koniec przebudowa
`zbuduj_dystrybucje.bat` i sprawdzenie `.exe` na tym ZIP-ie z `_pobrane` w obecnym (głębokim) folderze dystrybucji.

## 4. Założenia

- Pracuję na gałęzi `wiadomosci-transakcyjne` (tam jest narzędzie; na `main` folder jest nieśledzony).
- Bookmarklet (JS) bez zmian — nazwy plików w ZIP i w planach importu (`template__jezyk.icf`) zostają.
- Częściowo rozpakowany folder `dystrybucja\...\Eksport i Import Treści\alpha-teile_shop1\2026-10-14_120404\`
  (bez `manifest.json`) usunę przed testem — to pozostałość po nieudanej próbie.

## 5. Wątpliwości (domyślnie przyjmuję jak w §3)

1. Folder wiadomości bez prefiksu grupy — w Eksploratorze wiadomości przestaną być pogrupowane alfabetycznie
   wg grupy (`make_order__…`, `subscriptions__…`). Alternatywa: zostawić grupę, a skracać tylko warstwą 1 i 3.
2. Folder `po\` z weryfikacji znika z dysku — jeśli był Ci potrzebny do ręcznego porównania, mogę go zostawić,
   ale w krótszym miejscu (`_pobrane\weryfikacja_<data>\`).
