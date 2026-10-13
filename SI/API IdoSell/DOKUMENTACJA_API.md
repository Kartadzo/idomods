# API IdoSell — notatki robocze dla projektów w tym folderze

Baza wiedzy o REST API panelu administracyjnego IdoSell (Admin API v8), zbierana pod
kolejne projekty integracyjne. Dokumentacja producenta: <https://idosell.readme.io/>

---

## 1. Podstawy

| Element | Wartość |
| --- | --- |
| Base URL | `https://{domena}/api/admin/v{wersja}` |
| Przykład | `https://client71.idosell.com/api/admin/v8/orders/documents` |
| Aktualna wersja | `v8` |
| Format | JSON (żądanie i odpowiedź) |
| Uwierzytelnianie | nagłówek `X-API-KEY: <klucz>` **albo** `Authorization: Bearer <JWT>` |

`{domena}` to adres panelu sklepu — **nie** adres sklepowy witryny. W dokumentacji
występuje jako placeholder `clientXXX.idosell.com`.

Pełną specyfikację OpenAPI konkretnego sklepu można pobrać pod:
`https://{domena}/api/doc/admin/v{X}/json` — warto to robić przed każdym nowym projektem,
bo odzwierciedla realny stan bramek danego panelu, a nie ogólną dokumentację.

### Tablice w query stringu — najważniejsza pułapka

Parametry tablicowe przekazuje się jako **jedną wartość rozdzieloną przecinkami**:

```
?orderSerialNumber=1489,1484,1473&documentType=vat_invoice
```

Specyfikacja OpenAPI sklepu opisuje je jako `style: form, explode: false`, co dokładnie
to oznacza. **Powtórzony klucz nie działa** i — co najgorsze — *nie zgłasza błędu*:

```
?returnElements=documentId&returnElements=orderSerialNumber   ->  {"orderSerialNumber": 1489}
?returnElements=orderSerialNumber&returnElements=documentId   ->  {"documentId": "FV/5/PL/2609"}
```

Backend bierze wyłącznie **ostatnią** wartość, resztę cicho gubi, i nadal zwraca `200`.
Zweryfikowane eksperymentalnie 2026-09-16 na panelu testowym.

To jest prawdopodobne źródło mitu „API zwraca dokument tylko dla ostatniego zamówienia" —
integracja wysyłająca powtórzone klucze faktycznie dostanie dokument jednego zamówienia,
niezależnie od wersji API.

Przykłady w dokumentacji na readme.io pokazują formę z powtórzonym kluczem — **jest myląca**.
Źródłem prawdy jest `https://{domena}/api/doc/admin/v{X}/json`.

### Kody odpowiedzi

| Kod | Znaczenie |
| --- | --- |
| 200 | OK |
| 207 | Multi-Status — część elementów zwrócona, część z błędem w polu `errors` |
| 401 | Błąd uwierzytelnienia (zły/nieaktywny klucz) |
| 403 | Brak uprawnień aplikacji do danej bramki |
| 404 | Nie znaleziono |
| 422 | Nieprawidłowy format lub nieznana wartość parametru |
| 429 | Przekroczony limit żądań — ponawiać z odstępem |
| 5xx | Błąd serwera — ponawiać z odstępem |

**207 jest istotny**: odpowiedź może być częściowo poprawna. Nie należy traktować
`kod != 200` jako braku danych — trzeba zawsze przejrzeć treść.

---

## 2. `orders/documents` — GET

Pobranie dokumentów sprzedaży (faktury, paragony, WZ itd.) dla wskazanych zamówień.

**Ścieżka:** `GET /api/admin/v8/orders/documents`

### Parametry

| Parametr | Typ | Wymagany | Uwagi |
| --- | --- | --- | --- |
| `orderSerialNumber` | tablica liczb | tak | numery **seryjne** zamówień (nie `orderId`) |
| `documentType` | string | tak | jedna wartość na żądanie — patrz lista niżej |
| `returnElements` | tablica stringów | nie | ogranicza zwracane pola; bez tego odpowiedź zawiera PDF-y w base64 i potrafi być bardzo ciężka |

`returnElements` działa jako **whitelist**: odpowiedź zawiera wyłącznie wymienione pola.
Jeśli zapomnisz o `orderSerialNumber`, nie przypiszesz dokumentu do zamówienia — przy
zapytaniu o kilka zamówień naraz odpowiedź staje się bezużyteczna. Zawsze dopisuj
`orderSerialNumber` (i przekazuj listę przez przecinki — patrz pułapka wyżej).

### Dopuszczalne `documentType`

`sales_confirmation`, `vat_invoice`, `corrective_vat_invoice`, `advance_vat_invoice`,
`final_advance_vat_invoice`, `pro_forma_invoice`, `advance_pro_forma_invoice`,
`final_advance_pro_forma_invoice`, `delivery_note`, `fiscal_receipt`, `fiscal_invoice`,
`other`.

Filtr jest jednowartościowy — żeby zebrać różne typy dokumentów, trzeba wykonać
osobne żądanie na każdy typ.

### Struktura odpowiedzi

```json
{
  "documents": [
    {
      "orderSerialNumber": 12,
      "documentType": "vat_invoice",
      "id": 1,
      "documentId": "FV/2025/001",
      "documentName": "Faktura VAT",
      "ksefNumber": "5265877635-20250729-01004014E040-00",
      "ksefDocumentStatus": "completed",
      "pdfWithDocumentsInBase64": "JVBERi0xLjQK...",
      "documentPurchaseDate": "2025-01-15",
      "documentIssuedDate": "2025-01-15",
      "orderPaymentDate": "2025-01-16",
      "documentData": "...",
      "correctedInvoiceId": "FV/2025/000",
      "errors": { "faultCode": 0, "faultString": "" }
    }
  ],
  "errors": { "faultCode": 0, "faultString": "" }
}
```

### Jak wygląda brak dokumentu

Sprawdzone na panelu testowym:

- Żaden z pytanych zamówień nie ma dokumentu danego typu → `{"documents": []}`.
- W zapytaniu o kilka zamówień te bez dokumentu są **po prostu pomijane** — nie ma dla nich
  wpisu ani sekcji `errors`. Odpowiedź może więc mieć mniej elementów niż numerów w żądaniu
  i nadal być poprawna.
- Nie wolno zakładać, że pozycja *n* odpowiedzi dotyczy *n*-tego numeru z żądania — trzeba
  mapować po `orderSerialNumber`.

### Pułapka: `returnElements` psuje odpowiedź dla korekt

Dla `documentType=corrective_vat_invoice` użycie `returnElements` gubi dane — API zwraca
pustą listę zamiast obiektu dokumentu albo obiekt bez `documentId`, mimo że dokument
istnieje i **to samo zapytanie bez `returnElements` zwraca go w komplecie**:

```
documentType=corrective_vat_invoice&returnElements=documentId          ->  {"documents": [[]]}
documentType=corrective_vat_invoice   (bez returnElements)             ->  pełny FK/3/PL/2609
```

Dla `vat_invoice` i `sales_confirmation` `returnElements` działa poprawnie.
**Wniosek roboczy: przy korektach nie używaj `returnElements`** i filtruj pola po swojej
stronie. Zgłoszone jako obserwacja z 2026-09-16 — warto sprawdzić ponownie po aktualizacjach API.

### Zapowiedziana zmiana (walidowana w `Walidacja aktualizacji/`)

> Poprawiliśmy bramkę `orders/documents` w API. Dotychczas przy zapytaniu o kilka
> zamówień naraz odpowiedź zawierała dokument tylko dla ostatniego zamówienia z listy.
> Po zmianie API zwraca dokumenty dla każdego z przekazanych zamówień.

**Status weryfikacji: POTWIERDZONA** — test z 2026-09-16 na panelu `zooart6.iai-shop.com`
(nr klienta 7496). Jedno żądanie o zamówienia `1489,1484,1473,1472` zwróciło **5 faktur
dla 4 zamówień**, komplet w obu kolejnościach numerów. Szczegóły i surowy dziennik:
`Walidacja aktualizacji/wyniki/`.

Implikacja dla integracji: wsadowe pobieranie faktur można robić jednym żądaniem na paczkę
zamówień zamiast pętli N żądań — **pod warunkiem** przekazania numerów przez przecinki
i umieszczenia `orderSerialNumber` w `returnElements`. Przy powtórzonych kluczach dostaniemy
dokument jednego zamówienia i będzie to wyglądało na niedziałającą poprawkę.

**Jedno zamówienie może mieć wiele dokumentów tego samego typu** — w teście zamówienie 1473
zwróciło dwie faktury (`FV/2/PL/2609` i `FV/3/PL/2609`). Odpowiedź to płaska lista, nie mapa
„zamówienie → dokument"; grupuj po `orderSerialNumber` i nie zakładaj jednego wpisu na zamówienie.
Kolejność elementów odpowiedzi podąża za kolejnością numerów w żądaniu.

---

## 3. `orders/orders` — GET

**Ścieżka:** `GET /api/admin/v8/orders/orders`

| Parametr | Typ | Uwagi |
| --- | --- | --- |
| `ordersIds` | tablica | ID zamówień |
| `ordersSerialNumbers` | tablica | numery seryjne, maks. 100 pozycji |
| `orderExternalId` | tablica | ID z systemu zewnętrznego, maks. 100 pozycji |

Kluczowe pola odpowiedzi: `orderId`, `orderSerialNumber`, `orderStatus`, `clientResult`,
`orderDetails`, `productsResults`, `dispatch`. Pole `resultsNumberAll` podaje liczbę
wszystkich znalezionych wyników.

**`orderId` ≠ `orderSerialNumber`.** `orders/documents` oczekuje numeru **seryjnego**.

---

## 4. Wzorzec pracy w tym folderze

```
SI/API IdoSell/
├── DOKUMENTACJA_API.md          <- ten plik
├── _wspolne/
│   ├── idosell_client.py        <- klient HTTP wielokrotnego użytku
│   └── config.json              <- domena + klucz API (gitignorowany)
└── <Nazwa projektu>/
    ├── <skrypt>.py              <- importuje klienta z ../_wspolne
    ├── run_*.bat                <- działa po dwukliku
    └── wyniki/                  <- raporty i surowe odpowiedzi
```

### `idosell_client.py`

Tylko biblioteka standardowa (`urllib`) — brak zależności do instalowania, skrypty
ruszają po dwukliku na czystym Pythonie 3.8+.

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_wspolne"))
from idosell_client import IdoSellClient, wczytaj_konfiguracje

cfg = wczytaj_konfiguracje()          # przy braku config.json pyta i zapisuje
api = IdoSellClient(cfg["domena"], cfg["api_key"])

kod, dane = api.get("orders/documents", {
    "orderSerialNumber": [12, 15, 18],   # lista -> sklejana przecinkami (explode: false)
    "documentType": "vat_invoice",
    "returnElements": ["orderSerialNumber", "documentId", "documentName"],
})
```

Klient sam ponawia żądania przy 429 i 5xx (3 próby, rosnący odstęp) oraz zwraca treść
także dla odpowiedzi 4xx — bo tam siedzi opis problemu.

### Zasady

- **Klucz API nigdy nie trafia do repozytorium.** Siedzi w `_wspolne/config.json`,
  wpisanym do `.gitignore`. W kodzie i raportach nie wklejamy go w URL-e.
- Testy prowadzimy na panelu testowym, nie na produkcji klienta.
- Każdy projekt archiwizuje surowe odpowiedzi — bez nich raport jest nieweryfikowalny.
- `returnElements` bez `pdfWithDocumentsInBase64`, dopóki PDF-y nie są faktycznie
  potrzebne; inaczej odpowiedzi rosną do megabajtów na dokument.

---

## 5. Do sprawdzenia / luki w wiedzy

- Konkretne limity `429` (ile żądań na minutę) — dokumentacja publiczna ich nie podaje,
  a w teście (ok. 60 żądań pod rząd) limit się nie odezwał.
- Czy `orders/orders` bez parametrów zwraca stronicowaną listę i jak sterować stronami —
  dokumentacja nie opisuje parametrów paginacji, mimo że zwraca `resultsNumberAll`.
- Czy błąd `returnElements` przy `corrective_vat_invoice` dotyczy też innych typów
  korygujących (`advance_*`, `final_advance_*`) — nie było ich na panelu testowym.
- Górny limit liczby numerów w jednym żądaniu `orders/documents` (dla `orders/orders`
  dokumentacja podaje 100 — dla dokumentów nie jest to nigdzie określone).

---

## 6. Historia walidacji

| Data | Co sprawdzano | Werdykt |
| --- | --- | --- |
| 2026-09-16 | `orders/documents:GET` zwraca dokumenty dla wszystkich przekazanych zamówień | **POTWIERDZONA** |

Szczegóły: `Walidacja aktualizacji/`.
