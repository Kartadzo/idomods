# ANALIZA — CSV z GPSR dla Ceneo z eksportu IOF (narzędzie `transform_xml — gpsr`)

## Cel
Przygotować plik CSV z danymi GPSR (producent odpowiedzialny i podmiot odpowiedzialny) do wgrania w panelu Ceneo, spójny z feedem Ceneo ze sterownika summonFeed. Feed podaje w `attrs` tylko identyfikatory, a pełne dane trafiają do Ceneo z tego pliku. Pierwsze użycie: sklep `shop49855-1.yourtechnicaldomain.com` (sklep 1).

## Jak to działa dziś
1. `app_xml_to_xml.py` (`run_xml.bat`): dzieli eksport IOF (`source.xml` albo największy plik XML w folderze) na porcje po 12 000 produktów, przekształca je przez `formater.xslt` i scala w `output.xml` (`<item>` na producenta lub podmiot).
2. `app_xml_to_csv.py` (`run_csv.bat`): `output.xml` → `output.csv` (separator `;`), usuwa duplikaty wierszy.

Klucz łączący z feedem: kolumna „Nazwa wlasna” = `@id` z `iaiext:responsible_entity`. Sterownik Ceneo wpisuje:
- „Producent odpowiedzialny” = `iaiext:responsible_entity/producer/@id`,
- „Podmiot odpowiedzialny” = `iaiext:responsible_entity/persons/person/@id`.

## Znalezione problemy
1. **Błąd w `formater.xslt`:** gałąź „Podmiot” (`persons/person/code != ''`) bierze wszystkie pola z `producer` (`@id`, nazwa, adres, e-mail, telefon) zamiast z `persons/person`. Skutek: wiersz „Podmiot” to kopia producenta, a ID podmiotów z feedu nie występują w CSV, więc Ceneo nie połączy ofert z podmiotem odpowiedzialnym.
2. **Nagłówki:** XSLT tworzy kolumny `Nazwawlasna`, `Ulicainumer`, `Kodpocztowy`, `Telefonkontaktowy` (bez spacji), a przykładowy plik `gpsr-export (2).csv` ma nagłówki ze spacjami (`Nazwa wlasna;…;Telefon kontaktowy;Typ`). Wygląda na to, że nagłówki poprawiano ręcznie.
3. **Wiele osób:** `persons/person` może mieć kilka wpisów, a XSLT bierze tylko pierwszy (`value-of`). Sterownik Ceneo też podaje tylko pierwszą osobę.
4. **Interaktywność:** `app_xml_to_xml.py` pyta o potwierdzenie pliku (`input`), więc działa po dwukliku, zgodnie z konwencją skryptów.

## Planowane zmiany
- `formater.xslt`: gałąź „Podmiot” przepiąć na `iaiext:responsible_entity/persons/person` (`@id`, `name`, `country`, `street` + `number`, `city`, `zipcode`, `mail`, `phone`), z pętlą po wszystkich osobach.
- `app_xml_to_csv.py`: mapowanie nagłówków na postać ze spacjami, jak w przykładowym pliku (`Nazwa wlasna;Nazwa;Kraj;Ulica i numer;Miasto;Kod pocztowy;Email;Telefon kontaktowy;Typ`).
- Bez zmian w podziale na porcje i scalaniu.

## Dane wejściowe i wyjściowe
- Wejście: pełny eksport oferty IOF sklepu (XML z `iaiext:responsible_entity`). W panelu sklepu nie ma pliku oferty do pobrania bez klucza API, a próbka `SI/01_Feedy/SummonFeed/dane/products_export.xml` ma puste `responsible_entity`.
- Wyjście: `output.csv` w folderze narzędzia, do wgrania w panelu Ceneo.

## Założenia
- Format CSV Ceneo dla GPSR odpowiada przykładowemu plikowi `gpsr-export (2).csv` (separator `;`, nagłówki ze spacjami, `Typ` = Producent / Podmiot).
- Telefon normalizowany jak obecnie (bez prefiksu kraju).

## Otwarte pytania
1. **Plik IOF sklepu:** skąd go wziąć? Potrzebuję pliku z danymi GPSR (np. eksport z API albo plik wgrany przez Ciebie do tego folderu jako `source.xml`).
2. **Poprawka w miejscu czy w kopii:** poprawić `formater.xslt` i `app_xml_to_csv.py` w tym folderze (narzędzie wspólne) czy zrobić wersję dla Ceneo obok?
3. **Separator i nagłówki:** czy `;` i nagłówki ze spacjami to wymóg importu Ceneo (zgodnie z przykładowym plikiem)?
4. **Wiele osób odpowiedzialnych:** czy wystarczy pierwsza osoba (spójnie z feedem), czy eksportować wszystkie?

## Decyzje (2026-10-28)
1. Eksport IOF: `SI/01_Feedy/SummonFeed/sterowniki/magnicreatix/products_export-magnicreatix.pl-2026-10-28_14.47.xml` (36 produktów, każdy z GPSR: producent id 1, osoba id 2, bez telefonu).
2. Osobna wersja w `SI/01_Feedy/SummonFeed/sterowniki/magnicreatix/gpsr/`; narzędzie w `python/transform_xml — gpsr` zostaje bez zmian.
3. Separator i nagłówki: zostają jak w obecnym skrypcie (`;`, nagłówki z nazw elementów XSLT).
4. Tylko pierwsza osoba odpowiedzialna (`persons/person[1]`), spójnie z feedem.
Zakres zmian w wersji Ceneo: gałąź „Podmiot” w XSLT przepięta na `persons/person[1]`; skrypt XML szuka eksportu `products_export*.xml` w folderze nadrzędnym (w folderze sklepu największym XML jest podgląd sterownika).

## Zmiana decyzji (2026-10-28, później)
- GPSR budujemy na **oryginale** w tym folderze (użytkownik sam poprawił skrypt źródłowy). Kopia `SI/01_Feedy/SummonFeed/sterowniki/magnicreatix/gpsr/` jest zbędna — do usunięcia po potwierdzeniu.
