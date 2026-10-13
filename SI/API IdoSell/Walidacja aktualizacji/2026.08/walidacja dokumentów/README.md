# Walidacja aktualizacji API IdoSell

Folder służy do sprawdzania, czy ogłaszane przez IdoSell zmiany w API faktycznie
działają na panelu testowym — zanim oprzemy na nich integrację u klienta.

## Bieżąca walidacja: `orders/documents:GET` — **POTWIERDZONA** (2026-09-16)

Wynik wraz z dowodami i odkrytymi pułapkami: **[`WYNIK_orders_documents.md`](WYNIK_orders_documents.md)**.

**Teza do sprawdzenia:**

> Poprawiliśmy bramkę `orders/documents` w API. Dotychczas przy zapytaniu o kilka
> zamówień naraz odpowiedź zawierała dokument tylko dla ostatniego zamówienia z listy.
> Po zmianie API zwraca dokumenty dla każdego z przekazanych zamówień.

## Jak uruchomić

Dwuklik na **`run_walidacja.bat`** (albo `python waliduj_orders_documents.py`).

Przy pierwszym uruchomieniu skrypt zapyta o:

1. **Domenę panelu** — np. `client71.idosell.com` (bez `https://`, bez `/api/...`),
2. **Klucz API** — wartość nagłówka `X-API-KEY`.

Dane zapisują się w `../_wspolne/config.json` (plik jest w `.gitignore`) i kolejne
uruchomienia ich nie wymagają.

Następnie skrypt poprosi o **numery seryjne zamówień** do przebadania. Enter bez
wpisywania = próba automatycznego pobrania listy z bramki `orders/orders`.

> Test rozstrzyga cokolwiek tylko wtedy, gdy w puli są **co najmniej dwa zamówienia
> z wystawionym dokumentem tego samego typu**. Najpewniej jest podać numery, o których
> wiadomo, że mają faktury.

Jeśli podana pula da tylko **jedno** zamówienie z dokumentem, skrypt sam przeskanuje do
25 sąsiednich numerów seryjnych w dół, szukając drugiego z dokumentem tego samego typu.
Dzięki temu wystarczy znać jedno pewne zamówienie — w panelu testowym jest nim **1489**
(ma fakturę i korektę).

## Metodologia

1. **Baseline** — osobne żądanie na każde zamówienie. Ustala fakty: kto naprawdę ma
   dokument danego typu. Bez tego nie da się odróżnić „API gubi dokumenty" od
   „zamówienie po prostu nie ma faktury".
2. Skrypt przechodzi przez typy dokumentów, aż znajdzie taki, dla którego baseline daje
   min. 2 zamówienia z dokumentem.
3. **Test zbiorczy** — jedno żądanie o wszystkie te zamówienia naraz.
4. **Test odwrócony** — to samo z odwróconą kolejnością numerów. Gdyby API nadal zwracało
   „tylko ostatniego z listy", zestaw wyników zmieniłby się wraz z kolejnością. To
   odcina wynik fałszywie pozytywny wynikający z przypadku.
5. Raport + pełny dziennik żądań.

## Wyniki

Trafiają do `wyniki/`:

- `raport_RRRR-MM-DD_GG-MM-SS.md` — werdykt, tabela baseline, porównanie zestawów,
- `dziennik_zadan_RRRR-MM-DD_GG-MM-SS.json` — wszystkie żądania i odpowiedzi, do
  ręcznej weryfikacji raportu.

### Werdykty

| Werdykt | Znaczenie |
| --- | --- |
| `POTWIERDZONA` | Oba testy zbiorcze zwróciły komplet dokumentów — zapowiedź działa. |
| `NIEPOTWIERDZONA` | Zwrócono dokument tylko dla jednego zamówienia — stare zachowanie. |
| `CZĘŚCIOWA` | Zwrócono część dokumentów — wymaga ręcznej analizy dziennika. |
| `NIEROZSTRZYGNIĘTE` | W puli nie było 2 zamówień z dokumentem tego samego typu. |

## Uwagi techniczne

- Skrypt pyta o `returnElements` bez `pdfWithDocumentsInBase64` — dzięki temu dziennik
  nie puchnie od PDF-ów w base64. Przy odpowiedzi `422` ponawia żądanie bez tego parametru.
- Za dokument obecny uznajemy pozycję, która ma wypełnione `documentId`, `documentName`,
  `documentData` lub PDF. Pozycja zawierająca wyłącznie `errors` nie liczy się jako
  zwrócony dokument.
- Komunikaty w konsoli są bez polskich znaków — konsola Windows potrafi je kaleczyć
  przy niektórych ustawieniach. Raporty i dokumentacja mają pełną polszczyznę.

Szczegóły endpointów: `../DOKUMENTACJA_API.md`.
