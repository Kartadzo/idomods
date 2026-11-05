# Węzeł ClickUp (`n8n-nodes-base.clickUp`, typeVersion 1)

Docs: <https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.clickup/>
Źródło: `packages/nodes-base/nodes/ClickUp/ClickUp.node.ts` w repo n8n.

## Uwierzytelnianie

Dwa tryby: `accessToken` (personal API token) i `oAuth2`. W naszych scenariuszach:
`"authentication": "oAuth2"` + credential `clickUpOAuth2Api`.

Ten sam credential da się użyć w węźle **HTTP Request**:
`authentication: "predefinedCredentialType"` + `nodeCredentialType: "clickUpOAuth2Api"` —
przydatne, gdy węzeł ClickUp nie obsługuje potrzebnego formatu body.

## Zasoby i operacje (skrót)

`task` (create, get, getAll, update, delete, **setCustomField**, member:getAll),
`taskList`, `taskTag`, `taskDependency`, `checklist`, `checklistItem`, `comment`, `folder`,
`goal`, `goalKeyResult`, `list`, `spaceTag`, `timeEntry`, `timeEntryTag`.

## `task: setCustomField` — jak faktycznie działa

Parametry: **Task ID** (`task`), **Field ID** (`field`), **Value Is JSON** (`jsonParse`, domyślnie `false`), **Value** (`value`).

Kod węzła (n8n master):

```ts
const value = this.getNodeParameter('value', i) as string;
const jsonParse = this.getNodeParameter('jsonParse', i) as boolean;

const body: IDataObject = {};
body.value = value;
if (jsonParse) {
  body.value = validateJSON(body.value);            // validateJSON = JSON.parse w try/catch
  if (body.value === undefined) {
    throw new NodeOperationError(this.getNode(), 'Value is invalid JSON!', { itemIndex: i });
  }
} else {
  if (!isNaN(body.value)) { body.value = parseInt(body.value, 10); }   // liczby -> int
}
await clickupApiRequest.call(this, 'POST', `/task/${taskId}/field/${fieldId}`, body);
```

### Wnioski praktyczne (pułapki)

1. **`Value Is JSON = true` wymaga STRINGA.** `validateJSON` to `JSON.parse`. Jeśli podasz wyrażenie,
   które rozwiązuje się do prawdziwej tablicy/obiektu, `JSON.parse` dostaje `"[object Object]"`,
   rzuca wyjątek → węzeł kończy się błędem **„Value is invalid JSON!”**.
   Poprawnie: w węźle Code zwróć `JSON.stringify(...)` i wstaw `={{ $json.valueJson }}`.
2. **`Value Is JSON = false` wysyła wartość „jak jest”**, a dodatkowo *stringi wyglądające jak liczba
   zamienia na int* (`parseInt`). Dla pól tekstowych, w których liczba ma zostać tekstem, to zmienia typ.
3. Węzeł **nie zna typów pól ClickUp** — nie zbuduje za Ciebie `{ "add": [...] }` dla pola typu `users`
   ani nie sprawdzi, czy ID opcji istnieje. Format `value` musi być zgodny z API ClickUp —
   patrz [03-clickup-api-custom-fields.md](03-clickup-api-custom-fields.md).
4. Endpoint to zawsze `POST /task/{task_id}/field/{field_id}`. Węzeł **nie obsługuje**
   parametrów zapytania `custom_task_ids` i `team_id` — przy Custom Task IDs trzeba użyć HTTP Request.
5. Odpowiedź ClickUp dla tego endpointu to `{}` — brak potwierdzenia wartości. Weryfikacja tylko
   przez ponowny `task: get`.

## `task: get`

`GET /task/{id}` — zwraca m.in. `id`, `name`, `parent` (ID zadania nadrzędnego albo `null`),
`space.id`, `list.id`, `folder.id`, `assignees[]`, `custom_fields[]`.

`custom_fields[]` to **pełna lista pól z listy, także pustych** — element ma `id`, `name`, `type`,
`type_config`, a klucz `value` **istnieje tylko wtedy, gdy pole ma wartość**.
Dlatego `custom_fields[13].value` bywa `undefined` i wysypuje wyrażenie.

> **Nie indeksuj `custom_fields` po pozycji** (`custom_fields[0]`, `custom_fields[13]`).
> Kolejność zależy od listy i zmienia się po dodaniu/przestawieniu pola w ClickUp.
> Szukaj po `id` pola: `custom_fields.find(f => f.id === FIELD_ID)`.

## ClickUp Trigger (`n8n-nodes-base.clickUpTrigger`)

Docs: <https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.clickuptrigger/>

Parametry: `team` (Workspace ID), `events[]` (np. `taskCreated`, `taskUpdated`, `taskDeleted`),
`filters` (m.in. `listId`, `folderId`, `spaceId`).

Payload webhooka jest **chudy** — dla `taskCreated` dostajesz `event`, `task_id`, `team_id`,
`webhook_id`, `history_items[]`. **Nie ma tam pól zadania** — po dane trzeba dobić `task: get`.

Filtr `spaceId` w samym triggerze pozwala odciąć niepotrzebne zdarzenia u źródła, zamiast
filtrować je później węzłem Switch (mniej wykonań, mniej zużytego limitu API).
