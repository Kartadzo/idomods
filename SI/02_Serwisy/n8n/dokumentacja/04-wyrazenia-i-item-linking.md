# Wyrażenia n8n, typy i item linking

## Odwołania do danych

| Zapis | Znaczenie |
| --- | --- |
| `$json` | JSON **bieżącego** itemu (wyjście węzła bezpośrednio poprzedzającego) |
| `$('Nazwa węzła').item` | item z podanego węzła **powiązany** z bieżącym (przez item linking) |
| `$('Nazwa węzła').first()` / `.last()` | pierwszy / ostatni item danego węzła — bez śledzenia powiązań |
| `$('Nazwa węzła').all()[i]` | item po indeksie |
| `$input.all()` / `$input.first()` | wejście węzła Code (tryb *Run Once for All Items*) |

`$('Nazwa węzła')` odwołuje się **po nazwie z kanwy**. Zmiana nazwy węzła psuje każde takie wyrażenie
w całym workflow — n8n nie aktualizuje ich automatycznie w zaimportowanym JSON-ie.

## Typ zwracany przez wyrażenie

Gdy **cała** wartość parametru to jedno wyrażenie (`={{ $json.value }}`), n8n zachowuje natywny typ —
tablica zostaje tablicą, obiekt obiektem. Gdy wyrażenie jest **wplecione w tekst**
(`=abc {{ $json.value }}`), wynik jest zawsze stringiem, a obiekt zamienia się w `[object Object]`.

Konsekwencja dla węzła ClickUp `setCustomField` z `Value Is JSON = true`: taki parametr trafia do
`JSON.parse()`. Musi więc być **stringiem z JSON-em**, a nie gotowym obiektem.
Bezpieczny wzorzec — string budujemy w węźle Code:

```js
return [{ json: { valueJson: JSON.stringify({ add: [123], rem: [] }) }, pairedItem: 0 }];
```

a w węźle ClickUp: `Value = {{ $json.valueJson }}`.

## Item linking (`pairedItem`)

Docs: <https://docs.n8n.io/build/work-with-data/reference-data/link-data-items/preserving-linking-in-the-code-node.md>

`$('Węzeł').item` działa dzięki „nitce” prowadzącej od bieżącego itemu wstecz. Węzeł Code, który
**tworzy nowe itemy** (a nie modyfikuje wejściowych), tę nitkę zrywa, jeśli nie ustawisz `pairedItem`:

```js
return [{ json: { ... }, pairedItem: 0 }];   // 0 = indeks itemu wejściowego, z którego to powstało
```

Bez tego dalsze węzły rzucą **„Info for expression missing from previous node”**.
n8n radzi sobie automatycznie tylko przy **jednym** itemie wejściowym — czyli scenariusz odpalany
z webhooka „przypadkiem” działa, ale przestanie po pierwszym uruchomieniu wsadowym.
`pairedItem` warto ustawiać zawsze.

Druga wersja błędu — **„Multiple matching items for expression”** — pojawia się, gdy nitka wskazuje
na kilka itemów (po Merge / Aggregate / Summarize). Wtedy zamiast `.item` używa się `.first()`
albo `.all()[i]`.

## Zatrzymanie gałęzi: `return []`

Węzeł Code, który zwróci **pustą tablicę**, nie przekazuje żadnego itemu dalej — kolejne węzły
w tej gałęzi się nie wykonują. To czystszy sposób na „nie ma czego przepisać” niż przepuszczanie
`null` i łapanie błędu z API. Alternatywa, gdy warunek ma być widoczny na kanwie: węzeł **Filter**.

## Węzły IF / Switch (typeVersion 2.x / 3.x)

Docs: <https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.switch/>

- **IF** → dwa wyjścia: `true` (index 0) i `false` (index 1). Podłączenie tylko wyjścia `true`
  jest poprawne — gałąź `false` po prostu kończy wykonanie.
- **Switch** w trybie *Rules* → jedno wyjście na regułę, w kolejności reguł; `renameOutput`/`outputKey`
  nadaje im nazwy. Domyślnie item leci **tylko pierwszą pasującą** gałęzią —
  opcja `Send data to all matching outputs` to zmienia. Opcja `Fallback Output` dokłada wyjście
  dla itemów, które nie pasują do żadnej reguły (domyślnie takie itemy **znikają bez śladu**).
- `typeValidation: "strict"` (domyślne w wersji 2+) porównuje **z typami** — `"60744178"` (string)
  ≠ `60744178` (number). Przy porównaniach ID z API warto wymuszać string: `{{ String($json.space.id) }}`.
