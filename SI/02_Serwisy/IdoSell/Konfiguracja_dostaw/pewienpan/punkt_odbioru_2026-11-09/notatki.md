# Notatki: punkt odbioru „Butik Pewien Pan Łódź” (pewienpan.pl)
Data: 2026-11-09 · panel `shop=1` · dostawa 100105

## Stan „przed” (odczyt, bez zmian)

### Panel
- Ścieżka: `deliveries-notes.php?idr=1143020003&companyKey=shopPickUpPoints` → „Sieć punktów odbioru 1 (Polska)” → [punkty odbioru] → `shop-pickup-points.php?action=edit&pickupPointId=1&delivery=100105`.
- Kurierzy własnych punktów (Polska): Sieć punktów odbioru 1–4. Dostawa 100105 = **Sieć punktów odbioru 1 (Polska)**, nazwa w sklepie „Butik Pewien Pan Łódź”.
- Lista punktów sieci 1: jeden punkt.

| Pole | Wartość |
|---|---|
| ID | 1 |
| Nazwa (pol) | Butik Pewien Pan Łódź |
| Nazwa (eng) | Pewien Pan Shop |
| Opis lokalizacji (pol) | Ulica Nawrot na odcinku pomiędzy ul. Piotrkowską a Sienkiewicza - tuż obok dużego parkingu po prawej stronie. |
| Opis lokalizacji (eng) | (pusty) |
| Ulica | Nawrot 7 |
| Kod pocztowy | 90-060 |
| Miasto | Łódź |
| Region administracyjny | Nie wybrano |
| Kraj | Polska |
| Współrzędne | **(0, 0)**; mapa w formularzu się nie wczytuje („Ups... Coś poszło nie tak”) |
| Aktywny | tak |
| Pobranie | tak; gotówka, karta płatnicza |
| Kod zewnętrznego systemu | BUTIK PEWIEN PAN |
| Godziny | pn–pt 10:00–18:00, sob 10:00–14:00, nd zamknięty |
| Telefon | **brak takiego pola w formularzu punktu** |

- Konfiguracja dostawy 100105: Nazwa „Butik Pewien Pan Łódź”. „Komentarz - przedpłata”, „Komentarz - pobranie” i `[iai:deliverer_explanation]` są puste. Dane nadawcy: „Dane kontaktowe” (nie magazyn).
- Konsola panelu (formularz punktu): `This site overrides Array.from() with an implementation that doesn't support iterables, which could cause Google Maps JavaScript API v3 to not work correctly.` Mapa w panelu nie działa z powodu skryptu panelu, więc znacznika nie da się przesunąć.

### Strona sklepu (Chrome DevTools MCP, osobny profil)
- Koszyk: Mucha wiązana - czarna (ID 1653), **2 szt.**, 258,00 zł. Zamówienia nie składałem.
- `order1.php`: opcja „Butik Pewien Pan Łódź” (wartość `100105-1`), gratis, bez adresu i telefonu. Zrzut: `przed_order1_butik.jpeg`.
- „Przejdź dalej” → `pickup-sites.php` „Potwierdzam punkt odbioru”. **Mapa Google się wczytuje**, `BillingNotEnabledMapError` już nie występuje. Zrzut: `przed_pickup_sites.jpeg`.
- Pole adresu jest wstępnie wypełnione adresem z profilu przeglądarki. Wyszukanie „Nawrot 7, Łódź” → „Wystąpił błąd. Proszę odświeżyć stronę i spróbować ponownie”.
  - Konsola: `Geocoding Service: This API key is not authorized to use this service or API` → klucz Google klienta nie ma włączonego **Geocoding API**.
  - Skutek: zapytanie GraphQL `pickupPoints(courierId: 100105, location: {latitude: ,longitude: })` z pustymi współrzędnymi → `Syntax Error`. „Szukaj w tym obszarze” daje ten sam błąd.
- Ręczne zapytanie GraphQL (tylko odczyt, współrzędne Łodzi) zwraca punkt `id 1`: Nawrot 7, 90-060 Łódź, `coordinates 0,0`. Pole `location` = opis lokalizacji + godziny pracy. Telefonu brak.

## Wnioski
1. Adres Nawrot 7 jest już wpisany w punkcie. Magazyny nie biorą w tym udziału.
2. Klient sklepu nie widzi punktu, bo wyszukiwanie na mapie pada (brak Geocoding API w kluczu klienta), a punkt i tak ma współrzędne 0,0.
3. Telefonu nie da się wpisać w osobne pole punktu. Można go dodać w opisie lokalizacji (trafia do `location` widocznego przy punkcie) lub w komentarzu dostawy 100105.
