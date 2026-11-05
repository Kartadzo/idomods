# ANALIZA: skill `summonfeed` — sterownik XSLT 1.0 z szablonu

## Cel
Skill (`/summonfeed <link do panelu> <id sklepu> <serwis>`) przygotowuje sterownik feedu XSLT 1.0 dla konkretnego sklepu IdoSell:
1. kopiuje bieżący szablon z `xslt/szablony/` do `SI/01_Feedy/SummonFeed/sterowniki/<domena>/`,
2. sprawdza w panelu dostępne parametry towarów i profil dostaw,
3. uzupełnia sekcję konfiguracji (zmienne na górze pliku, placeholdery `00000`),
4. wprowadza w kopii wybrane warianty elementów (link, `item_group_id`, dostawa) i zmiany wymagane przez serwis docelowy,
5. sprawdza poprawność wyniku.

Szablonów źródłowych nie edytuję. Przy każdym wywołaniu czytam ich aktualną wersję, a skill nie przechowuje ich kopii.

## Szablony i ich priorytet
| Szablon | Format | Status |
|---|---|---|
| `Google.xml` | RSS 2.0 + `g:*` | zawsze aktualny — wzorzec elementów |
| `Facebook.xml` | RSS 2.0 + `g:*` (Meta) | zawsze aktualny — wzorzec elementów |
| `Ceneo.xml` | `<offers>` Ceneo | elementy mogą być starsze niż w Google/FB |

- Serwis akceptujący format Google → `Google.xml`, potem dopasowanie do specyfikacji serwisu (usunięcie zbędnych lub dopisanie brakujących elementów).
- Pozostałe szablony (Ceneo, Glami, Idealo, Compari, Billiger, Pinterest, Synerise, samba…) też kopiuję jako bazę, gdy pasują do formatu serwisu. Skill porównuje ich elementy wspólne z Google/FB (tytuł, opis, ceny, dostępność, kolor, materiał, funkcje pomocnicze typu `wordFormat`) i proponuje listę aktualizacji. Wybrane pozycje wprowadzam w kopii i opisuję w `zmiany.md`.

## Dane wejściowe (podawane przy wywołaniu)
- Link do panelu IdoSell i ID sklepu (`shop_id` w panelu wielosklepowym), serwis docelowy.
- Logowanie do panelu robi użytkownik. W panelu działam przez Claude in Chrome **tylko w trybie odczytu**.

### Co odczytuję z panelu
- **Parametry towarów:** nazwy i ID parametrów oraz przykładowe wartości. Na tej podstawie dobieram nazwy do zmiennych: `kolor_`, `material_`, `gender_*`, `age_group_*`, `waga_`, `pojemnosc_`, `certyfikaty_`, `informacje_wyroznione_`. Jeśli kontekst parametru (`CONTEXT_COLOR`, `CONTEXT_SEX`, `CONTEXT_STATE`) jest już ustawiony, szablon go obsługuje i zmienna może zostać pusta.
- **Magazyny sprzedaży** → `sales_stocks`.
- **Domenę, język i walutę** sklepu → `<title>`, `<link>`, `<description>`, `Kraj_dostawy`.
- **Profil dostaw porównywarki** (przy trybie dynamicznym): czy ma ustawioną domyślną metodę wysyłki.
- **Cennik dostaw** (przy trybie stałym).
- Do testu transformacji próbuję użyć pliku oferty IOF ze sklepu. Pobranie zrobię dopiero po Twojej zgodzie. Zapasowo użyję `SI/01_Feedy/SummonFeed/dane/products_export.xml` (48 produktów).

## Pytania, które skill zawsze zadaje
1. **Dostawa (`g:shipping`):**
   - **dynamiczna** → `kwota_dla_darmowej_dostawy = *`. Sprawdzam w panelu, czy profil dostaw ma domyślną metodę wysyłki. Jeśli nie ma, zgłaszam, że feed nie przekaże kosztu.
   - **na sztywno** → dopytuję: najtańsza opcja (obejmuje pełny zakres produktów) czy kurier na adres. Potem wpisuję koszt, próg darmowej dostawy, czasy, dni i serwis.
   - **pominąć** → zmienne puste, element się nie generuje.
2. **Format linków** (`g:link` i pochodne):
   - link porównywarki (domyślny w szablonie): `<url>.googleshopping<kraj>.html` (Google) / `.facebookads.html` (FB) + `?selected_size=`,
   - link czysty — bez sufiksu porównywarki, z `selected_size`,
   - link dokładnie z oferty (`card/@url`).
   Warianty biorę z `SI/archiwum/SummonFeed/Generator/parameters_templates/link*.xsl`, a formę dopasowuję do bieżącego szablonu.
3. **ID grupy (`g:item_group_id`):**
   - tylko rozmiary (`@id`, domyślne w Google),
   - rozmiary i warianty (`group/@id`, w przeciwnym razie `@id` przy więcej niż jednym rozmiarze; domyślne w FB, z prefiksem `group-`),
   - z prefiksem czy bez.

Pozostałe elementy szablonu zostawiam bez zmian.

## Wymagania serwisów
`SI/01_Feedy/SummonFeed/wymagania/`:
- `INDEX.md` — 34 linki od użytkownika z przypisaniem: serwis, format (Google RSS / własny XML / CSV), szablon bazowy, link,
- `<serwis>.md` — streszczenie per serwis: wymagane i zalecane pola, limity (długość tytułu i opisu, rozmiar zdjęć), formaty wartości, różnice względem `Google.xml`.

Każde streszczenie ma pole „Data przeglądu”. Gdy od ostatniego przeglądu minęło **ponad 90 dni**, przy wywołaniu skill czyta ponownie źródła, aktualizuje streszczenie i datę, a zmiany wypisuje w podsumowaniu. Gdy brakuje streszczenia dla danego serwisu, czytam stronę z `INDEX.md` i je dopisuję.

## Dane wyjściowe
`SI/01_Feedy/SummonFeed/sterowniki/<domena>/`:
- `<domena>_<serwis>.xml` — gotowy sterownik XSLT 1.0,
- `konfiguracja.json` — odpowiedzi i wartości zmiennych (pozwala odtworzyć sterownik na nowszej wersji szablonu albo dla innego serwisu),
- `zmiany.md` — wersja szablonu (data i commit), lista podmienionych zmiennych, wybrane warianty, zmiany logiki, uwagi (np. brak parametru w panelu).

## Pliki skilla
- `.claude/skills/summonfeed/SKILL.md` — procedura krok po kroku.
- `SI/01_Feedy/SummonFeed/narzedzia/konfiguruj.py` — kopiuje szablon i podmienia wartości zmiennych z `konfiguracja.json`. Obsługuje obie formy zapisu: `<xsl:variable name='X'>…</xsl:variable>` i `select="'…'"`. Zgłasza zmienną z JSON-a, której nie ma w szablonie. Logiki nie rusza. Warianty linku i `item_group_id` wprowadzam edycją kopii (`warianty.md`).
- `SI/01_Feedy/SummonFeed/narzedzia/przytnij.py` — usuwa z kopii elementy, których serwis nie obsługuje (lista `dozwolone` w `wymagania/<serwis>.md`), razem z pustymi po nich warunkami, nieużywanymi zmiennymi lokalnymi i nazwanymi szablonami (ustalenie 2026-10-27).
- `SI/01_Feedy/SummonFeed/narzedzia/parametry_oferty.py` — raport parametrów, magazynów, grup i GTIN z oferty IOF (iterparse).
- `SI/01_Feedy/SummonFeed/narzedzia/weryfikuj.py` — kompiluje sterownik przez `lxml` (libxslt, XSLT 1.0), przepuszcza przez niego próbkę oferty i sprawdza wymagane elementy serwisu oraz pozostałe `00000`.
- `SI/01_Feedy/SummonFeed/zmienne_szablonow.md` — opis zmiennych Google, FB i Ceneo: znaczenie, format list `|…|`, wartości domyślne.
- `SI/01_Feedy/SummonFeed/wymagania/…` — jak wyżej.

Na czas prac zakładam osobną gałąź git `summonfeed-si`.

## Założenia
- Wynik zawsze XSLT 1.0. Atrybuty `tunnel="yes"` / `version="2.0"` obecne w szablonach zostawiam, bo procesor IdoSell je toleruje.
- Gdy parametru nie ma w panelu, zmienna zostaje pusta i zapisuję to w uwagach. Nie zgaduję.
- Zmiany przydatne we wszystkich sklepach opisuję w podsumowaniu jako propozycję do szablonu. Szablonu nie zmieniam.
- W panelu niczego nie zapisuję. Wgranie sterownika do porównywarki robisz Ty.
- Plik oferty jest plikiem roboczym i nie trafia do gita (reguła w głównym `.gitignore`: `SI/01_Feedy/SummonFeed/sterowniki/*/oferta*.xml`).

## Ustalenia (2026-10-27, cd.)
- Element obsługiwany przez serwis zostaje, jeśli jest w szablonie Google/FB, w wersji z tego szablonu. Elementów spoza tych szablonów nie dopisuję.
- Zmienne dopasowywane do panelu zapisuję jako `|<@id>|<@name PL>|`, a węzły menu 1 jako `|<@id>|<nazwa PL>|`. Menu 1 musi być współdzielone, co sprawdzam w `/panel/navigation.php`. Część zmiennych w szablonach nie obsługuje tego zapisu, a proponowane poprawki są w `propozycje_szablonow.md`. Rozstrzygnięte: kopii nie łatam. Nazwy zapisuję jak w panelu, bo docelowo wielkość liter nie ma znaczenia. Płeć i grupa wiekowa też mają postać `|id|nazwa|`, którą przyjmuje nowy szablon. `konfiguruj.py` odrzuca listę, gdy dana wersja szablonu porównuje zmienną przez `=`, i wtedy wpisuję pojedyncze ID. Pozostałe zmienne zostają w zapisie szablonu do czasu jego aktualizacji.

## Ustalenia (2026-10-27)
- Wynik to zawsze nowy plik do ręcznego wgrania (bez ID porównywarki).
- Dostawa na sztywno: koszt odczytuję z panelu (konfiguracja kurierów / cennik).
- Warianty linku i `item_group_id` wprowadza Claude, edytując kopię. Wzorce wariantów są w `warianty/`. `konfiguruj.py` podmienia tylko wartości zmiennych.
