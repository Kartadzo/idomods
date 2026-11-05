# ClickUp API — Custom Fields: formaty `value`

Źródła: <https://developer.clickup.com/docs/customfields> ・ <https://developer.clickup.com/reference/setcustomfieldvalue>

## Endpoint

```
POST https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}
Content-Type: application/json

{ "value": <zależne od typu pola> }
```

Alternatywa (jednym strzałem razem z innymi zmianami zadania):

```
PUT https://api.clickup.com/api/v2/task/{task_id}
{ "custom_fields": [ { "id": "<uuid>", "value": <...> } ] }
```

`field_id` to **UUID**, nie nazwa. Wyciągasz go z `GET /task/{id}` → `custom_fields[].id`
albo z `GET /list/{list_id}/field`.

## Format `value` per typ pola

| `type` | Format `value` | Uwaga |
| --- | --- | --- |
| `users` | `{ "add": [id, ...], "rem": [id, ...] }` | **obiekt, nie tablica** — `add` dopisuje, `rem` usuwa |
| `drop_down` | `"<uuid opcji>"` | ID opcji z `type_config.options[].id` |
| `labels` | `["<uuid>", "<uuid>"]` | tablica ID; **nadpisuje** dotychczasowe etykiety |
| `text` / `short_text` | `"tekst"` | |
| `number` | `123` | |
| `currency` | `80` | |
| `date` | `1508369194377` | unix ms |
| `checkbox` | `true` / `false` | |
| `url`, `email`, `phone` | `"..."` | |
| `tasks` | `{ "add": ["id"], "rem": ["id"] }` | relacja zadanie↔zadanie |
| `emoji` (rating) | `3` | |
| `location` | obiekt z `location` + `formatted_address` | |

### `users` — najczęstsza pułapka

**Odczyt** (`GET /task/{id}`) zwraca tablicę obiektów użytkownika:

```json
{ "id": "7e6d0b2e-...", "type": "users",
  "value": [ { "id": 50639757, "username": "Dominik Matyjasek", "email": "...", "initials": "DM" } ] }
```

**Zapis** wymaga zupełnie innego kształtu:

```json
{ "value": { "add": [50639757], "rem": [] } }
```

Przepisanie odczytanej wartości 1:1 (`[{ "id": 50639757 }]`) **nie zadziała** — to format odczytu,
nie zapisu. To dokładnie ten błąd był w węźle `przepisz od rodzica 'Opiekun'2`.

Wyczyszczenie pola: `{ "value": { "add": [], "rem": [<id obecnych>] } }`
(albo `DELETE /task/{task_id}/field/{field_id}`).

## Limity

Limit API ClickUp: **100 żądań/minutę na token** (plan Free/Unlimited/Business).
Każdy węzeł ClickUp = jedno żądanie na item. Przy scenariuszu odpalanym z webhooka
warto włączyć w węźle **Retry On Fail** (n8n: Settings → Retry On Fail), żeby chwilowe 429
nie ubijało całego wykonania.
