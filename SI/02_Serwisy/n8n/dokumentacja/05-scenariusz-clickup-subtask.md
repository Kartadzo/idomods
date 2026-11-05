# Scenariusz `ClickUp - SUBTASK (n8n)`

Plik: `../scenariusze/ClickUp - SUBTASK (n8n).json` (kopia sprzed poprawek: `../scenariusze/_backup/`)
ID workflow: `SAjUe2wL7g49sbsD`

## Cel

Po utworzeniu podzadania w ClickUp przepisać na nie wybrane Custom Fields z zadania nadrzędnego
(**Projekt** i **Opiekun**), żeby użytkownik nie musiał uzupełniać ich ręcznie.

## Przepływ

```
ClickUp Trigger (taskCreated, team 36829874)
  └─ pobierz dane nowego zadania        (task:get,  id = {{ $json.task_id }})
      └─ jeśli jest rodzic ...          (IF: $json.parent exists)   [tylko wyjście true]
          └─ pobierz dane rodzica       (task:get,  id = {{ $json.parent }})
              └─ Switch (po space.id)
                  ├─ 0 „klienci” (60744178)
                  │   ├─ przepisz od rodzica 'Projekt'
                  │   └─ Code in JavaScript ─┬─ przepisz od rodzica 'Opiekun'
                  │                          └─ HTTP Request            [disabled]
                  └─ 1 „wewnętrzne zadania” (60747517)
                      ├─ przepisz od rodzica 'Projekt'1
                      └─ Code in JavaScript1 ─┬─ przepisz od rodzica 'Opiekun'2
                                              └─ HTTP Request2          [disabled]
```

## Stałe (ID)

| Co | ID |
| --- | --- |
| Workspace (team) | `36829874` |
| Space „klienci” | `60744178` |
| Space „wewnętrzne zadania” | `60747517` |
| Custom Field „Opiekun” (users) — klienci | `805fca92-5634-4b72-a379-a5b9111f3f74` |
| Custom Field „Opiekun” (users) — wewnętrzne | `7e6d0b2e-0d6d-4284-af1a-63b49a9843d5` |
| Credential | `clickUpOAuth2Api` → „ClickUp: Eryk Jakubik” (`7QIUCb4UPr282M8T`) |

## Co zostało poprawione (gałąź „wewnętrzne zadania”)

### Przyczyna źródłowa

Pole **Opiekun** jest typu `users`. ClickUp zwraca je z `GET /task` jako tablicę obiektów
użytkownika, ale przy **zapisie** wymaga obiektu `{ "add": [...], "rem": [...] }`.
Scenariusz przepisywał format odczytu (`[{ "id": ... }]`) — i węzeł ClickUp, i oba obejścia
na HTTP Request wysyłały to samo złe body, więc żadna wersja nie mogła zadziałać.
Szczegóły: [03-clickup-api-custom-fields.md](03-clickup-api-custom-fields.md).

### `Code in JavaScript1`

- buduje **string** `{"add":[<userId>],"rem":[]}` (`valueJson`) — bo `Value Is JSON` w węźle ClickUp
  przepuszcza wartość przez `JSON.parse`, więc musi dostać string, nie obiekt,
- wystawia też `fieldId`, żeby ID pola miało **jedno** miejsce definicji,
- szuka pola po `id`, nie po indeksie `custom_fields[13]`,
- `return []`, gdy rodzic nie ma opiekuna **albo podzadanie już go ma** — pusta tablica zatrzymuje
  gałąź, zamiast wysyłać `null` do API (realizuje to, co obiecuje nazwa węzła IF: „nie uzupełniono pól”),
- ustawia `pairedItem: 0`, żeby nie zerwać item linkingu dla `$('pobierz dane nowego zadania').item`.

### `przepisz od rodzica 'Opiekun'2`

| | przed | po |
| --- | --- | --- |
| Field ID | wpisany na sztywno w węźle | `={{ $json.fieldId }}` |
| Value Is JSON | wyłączone | **włączone** |
| Value | `={{ $json.value }}` (tablica → złe body) | `={{ $json.valueJson }}` |
| Retry | brak | `retryOnFail`, 3 próby co 2 s (limit ClickUp: 100 żądań/min) |

Wysyłane body: `POST /task/{id}/field/7e6d0b2e-…` → `{"value":{"add":[<userId>],"rem":[]}}`.

### `HTTP Request2`

Nadal **wyłączony** (jest już zbędny), ale body poprawione do formatu `add/rem` i do nowych nazw pól —
gdyby kiedyś trzeba było wrócić do obejścia, jest sprawne.

## Znane problemy — jeszcze nie ruszone

1. **Gałąź „klienci” jest zepsuta tak samo, plus dodatkowo.** Węzeł `przepisz od rodzica 'Opiekun'`
   czyta `$json.custom_fields[13].id`, ale na jego wejściu jest wyjście `Code in JavaScript`,
   czyli `{ value: … }` — `custom_fields` tam nie istnieje, więc wyrażenie leci na `undefined`.
   Do tego ten sam zły format `[{ "id": … }]`. Lekarstwo jest identyczne jak dla gałęzi wewnętrznej
   (inne `FIELD_ID`: `805fca92-…`).
2. **`przepisz od rodzica 'Projekt'` / `'Projekt'1`** adresują pole przez `custom_fields[0]` —
   pozycja w tablicy, która zmieni się po dodaniu pola w ClickUp. Powinno być wyszukiwanie po `id`.
3. **IF „jeśli jest rodzic i nie uzupełniono pól”** sprawdza wyłącznie istnienie rodzica.
   Dla gałęzi wewnętrznej warunek „nie uzupełniono” siedzi teraz w węźle Code; dla „Projektu”
   nadal go nie ma — scenariusz nadpisze ręcznie wpisany projekt.
4. **Switch miesza źródła**: reguła 0 porównuje space **podzadania**
   (`$('pobierz dane nowego zadania').item.json.space.id`), reguła 1 space **rodzica** (`$json.space.id`).
   Zwykle to ta sama przestrzeń, ale warto ujednolicić na podzadanie.
5. **Brak wyjścia fallback w Switch** — zadania z innych przestrzeni znikają po cichu.
   Jeśli to celowe, taniej odfiltrować je już w triggerze (`filters.spaceId`).
6. **Workflow jest `active: false`** i ma `pinData` na triggerze — przed produkcją trzeba odpiąć
   dane testowe (Unpin) i aktywować.

## Test

1. Import pliku do n8n (**Import from File**) — węzły dopasują się po `id`.
2. Trigger ma przypięte dane testowe zadania `869euadpu` — **Execute Workflow** przejdzie całą ścieżkę
   bez czekania na webhook. Uwaga: to jest prawdziwy zapis do ClickUp, nie dry-run.
3. Sprawdzenie wyniku: `GET /task/{id}` → `custom_fields` → wpis o `id = 7e6d0b2e-…`
   powinien mieć `value: [{ id: <user> }]`.
4. Przypadki brzegowe do przeklikania: rodzic bez opiekuna → gałąź kończy się na węźle Code (0 itemów);
   podzadanie z już ustawionym opiekunem → to samo, brak nadpisania.
