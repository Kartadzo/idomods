# Ceneo — wymagania feedu
- Źródła: https://www.ceneo.pl/poradniki/Instrukcja-tworzenia-pliku-XML · https://developers.ceneo.pl/api/v3/kategorie · https://developers.ceneo.pl/api/v3/atrybuty
- Data przeglądu: 2026-10-28 (słowniki API dodane)
- Format: własny XML Ceneo, akceptuje format Google: nie (poradnik opisuje wyłącznie format Ceneo)
- Szablon bazowy: `Ceneo.xml` — to dokładnie ten format (`<offers>` → `<o>` z atrybutami, `cat/name/imgs/desc/attrs`).

## Struktura pliku
```xml
<?xml version="1.0" encoding="utf-8"?>
<offers version="1">
  <!-- opcjonalnie (GPSR): <responsibleProducers>…</responsibleProducers> <responsiblePersons>…</responsiblePersons> -->
  <o id="" url="" price="" avail="" stock="" basket="" weight="">
    <cat><![CDATA[Dom i ogród/Ogród/…]]></cat>
    <name><![CDATA[…]]></name>
    <imgs><main url=""/><i url=""/></imgs>
    <desc><![CDATA[…]]></desc>
    <attrs>
      <a name="Producent"><![CDATA[…]]></a>
      <a name="Kod_producenta"><![CDATA[…]]></a>
      <a name="EAN"><![CDATA[…]]></a>
    </attrs>
  </o>
</offers>
```

## Pola wymagane
| pole | opis/format | limit |
|---|---|---|
| `o/@id` | unikalny identyfikator oferty; raz użytego nie wolno przypisać innemu produktowi | 100 znaków |
| `o/@url` | adres karty produktu | 1000 znaków |
| `o/@price` | cena, separator dziesiętny kropka | — |
| `o/@avail` | czas wysyłki: `1` (24 h), `3`, `7`, `14`, `90` (na zamówienie), `99` (sprawdź w sklepie), `110` (przedsprzedaż) | słownik |
| `cat` | pełna ścieżka kategorii sklepu oddzielana `/`, bez nazw promocyjnych i zbyt ogólnych | 255 znaków |
| `name` | nazwa produktu bez dopisków handlowych | 150 znaków |
| `imgs` | `main` (główne) + `i` (dodatkowe) z atrybutem `url` | URL 2048 znaków, łącznie do 20 zdjęć |
| `desc` | opis w CDATA, dozwolone tylko proste znaczniki: p, h2, h3, br, ul, ol, li, b, strong, i, em | 100 000 znaków |
| `attrs/a` | atrybuty `name=` + wartość w CDATA; integracyjne: marka, kod producenta, EAN (8 lub 13 cyfr), „wyprodukowane przez”; ISBN dla książek, kod leku dla OTC (7 cyfr) | do 500 atrybutów |

## Pola zalecane / opcjonalne istotne
| pole | opis/format | limit |
|---|---|---|
| `o/@stock` | stan magazynowy, liczba całkowita dodatnia | — |
| `o/@basket` | `1` — oferta w „Kup Teraz”, `0` — nie | 0/1 |
| `o/@weight` | waga w kg, kropka dziesiętna | — |
| atrybuty kategorii | filtry i specyfikacje z pliku atrybutów Ceneo; część oznaczona jako kluczowa i wtedy obowiązkowa | — |
| GPSR | `responsibleProducers` / `responsiblePersons` i dane bezpieczeństwa — wymagane dla „Kup Teraz” | — |
| atrybuty specjalne | etykieta energetyczna, karta informacyjna, klasa energetyczna (AGD/RTV); wyrób medyczny; znak CE (1/0 + rok); kaucja; Data Act; materiały budowlane; prekursory materiałów wybuchowych | — |

## Limity i formaty
- Kodowanie: UTF-8 (zalecane), ISO-8859-2 lub Windows-1250; opis musi mieć kodowanie zgodne z plikiem.
- Plik publiczny, bez hasła, pod stałym adresem; cena i dostępność muszą zgadzać się ze sklepem.
- Zdjęcia: duża rozdzielczość, białe tło, produkt wypełnia kadr, bez znaków wodnych i napisów, bez miniatur.
- Warianty: jeśli cena wspólna — jedna oferta, wartości wariantu rozdzielone średnikiem w atrybucie; jeśli wariant zmienia cenę — osobne oferty.
- Tryb przyrostowy: `fileVersion` w `<offers>` i `update="1"` w `<o>` (tylko id + zmienione pola); ukrycie oferty to `price="0"`.

## Słowniki API v3 (kategorie i atrybuty)
Obie strony to surowe XML-e (bez opisu endpointów), pobrane 2026-10-28:
- **Kategorie** (`/api/v3/kategorie`, ~335 KB): `ArrayOfCategory/Category` z polami `Id`, `Name`, `Subcategories` (zagnieżdżone). 3966 kategorii, 3445 liści, 26 kategorii głównych (Biuro i firma, Budowa i remont, Dla dziecka, Dom i wnętrze, …, Zdrowie). Brak pola ścieżki i rodzica — ścieżkę składa się z zagnieżdżenia (`Dla dziecka/Zabawki/Klocki`).
- **Atrybuty** (`/api/v3/atrybuty`, ~4,7 MB): to samo drzewo, a w liściach blok `Attributes/Attribute` (`Name`, `Value`, `IsKeyAttribute`). **Uwaga techniczna:** `Attributes` leży wewnątrz `Subcategories`, nie bezpośrednio w `Category`. `Value` to jedna przykładowa wartość (często pusta), nie pełny słownik. Atrybuty ma 3923 kategorii.
- Atrybuty kluczowe (`IsKeyAttribute=True`) są dla danej kategorii obowiązkowe. Najczęstsze kluczowe: Producent (3360 kategorii), Kod (3334), Kod producenta (1250), Model (1068), Rodzaj (785), Kolor (575), Pojemność, Szerokość, Przeznaczenie, Wysokość.
- Nazwy atrybutów w słowniku są ze spacjami i polskimi znakami („Kod producenta”, „Liczba elementów”, „Wiek dziecka”), a poradnik podaje atrybuty integracyjne z podkreśleniem (`Kod_producenta`). Słownik ma niespójności (literówki, spacje na końcu, „Tak”/„tak”) — nazwy kopiować dokładnie z kategorii docelowej.
- `<cat>` w pliku: poradnik każe podawać pełną ścieżkę kategorii **sklepu** z `/`. Słownik kategorii służy do doboru atrybutów kluczowych i ewentualnego mapowania ścieżki na drzewo Ceneo (np. w XSLT `choose` po kategorii sklepu), czego szablon nie robi.
- Przykład (magnicreatix, klocki magnetyczne): `Dla dziecka/Zabawki/Klocki` (Id 1054) — kluczowe: Kod, Kod producenta, Liczba elementów, Producent, Przeznaczenie, Wiek dziecka; pozostałe m.in. Rodzaj, Liczba figurek, Certyfikaty, opinie, atesty, Klocki kompatybilne z innymi zestawami, Waga.
- Do pracy ze słownikami: pobrać oba pliki (curl) do scratchpada i parsować `iterparse`/`ElementTree` (atrybuty: `Category` → `Subcategories/Attributes/Attribute`).

## Różnice względem szablonu bazowego
- Szablon `Ceneo.xml` zawiera atrybut `set` — poradnik go nie opisuje (do weryfikacji, czy nadal obsługiwany).
- Sprawdzić, czy szablon obsługuje: węzły GPSR na początku pliku, atrybut „Wyprodukowane przez”, atrybuty energetyczne/CE/kaucja, limit 20 zdjęć i 150 znaków nazwy.
- Nazwy atrybutów integracyjnych (Producent / Marka, Kod_producenta, EAN) porównać z aktualną listą Ceneo — poradnik podaje je opisowo.
- Szablon przekazuje parametry sklepu pod nazwami z panelu; nie sprawdza atrybutów kluczowych kategorii ani nazw ze słownika API (patrz „Słowniki API v3”).

## Uwagi
- Strona wczytana poprawnie.
- Poradnik nie podaje częstotliwości pobierania pliku ani maksymalnego rozmiaru; kontakt: wsparciesklepu@ceneo.pl.
- Pełna lista atrybutów kategorii: słownik `/api/v3/atrybuty` (opisany wyżej).
