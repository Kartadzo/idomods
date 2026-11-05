# Dokumentacja robocza: n8n + ClickUp

Notatki referencyjne do pracy nad scenariuszami n8n w tym folderze.
Wszystko poniżej jest **zweryfikowane w źródłach** (kod węzła n8n, docs.n8n.io, developer.clickup.com),
a nie odtworzone z pamięci — przy każdej sekcji jest link do źródła.

## Spis

| Plik | Zawartość |
| --- | --- |
| [01-n8n-mcp-setup.md](01-n8n-mcp-setup.md) | Serwer `n8n-mcp` (czlonkowski) — co daje, jak podpiąć do Claude Code |
| [02-wezel-clickup.md](02-wezel-clickup.md) | Węzeł `n8n-nodes-base.clickUp` — operacje, pułapka `Value Is JSON` |
| [03-clickup-api-custom-fields.md](03-clickup-api-custom-fields.md) | Formaty `value` dla każdego typu Custom Field w API ClickUp |
| [04-wyrazenia-i-item-linking.md](04-wyrazenia-i-item-linking.md) | `$json`, `$('Węzeł').item`, `pairedItem`, typy zwracane przez wyrażenia |
| [05-scenariusz-clickup-subtask.md](05-scenariusz-clickup-subtask.md) | Mapa scenariusza `ClickUp - SUBTASK (n8n)`: ID, przepływ, znane błędy |

## Struktura folderu

```
SI/02_Serwisy/n8n/
  scenariusze/      # eksporty JSON workflowów z n8n (źródło prawdy)
  dokumentacja/     # to, co czytasz
```

## Zasada pracy z eksportami

Plik JSON w `scenariusze/` to eksport z n8n (**Download** w menu workflowu). Zmiany nanosimy w pliku,
a do n8n wgrywamy przez **Import from File** — n8n dopasuje węzły po `id`, więc pozycje na kanwie
i połączenia zostają. Nazwy węzłów są jednocześnie kluczami w sekcji `connections`
i w wyrażeniach `$('nazwa węzła')` — **zmiana nazwy węzła wymaga podmiany w obu miejscach**.

## Dodatkowe źródła (do przejrzenia)

- <https://github.com/czlonkowski/n8n-mcp> — serwer MCP z bazą węzłów i walidacją workflowów
  (szczegóły: [01-n8n-mcp-setup.md](01-n8n-mcp-setup.md))
- <https://github.com/czlonkowski/n8n-skills> — skille do n8n od autora `n8n-mcp`
- <https://github.com/n8n-io/skills> — oficjalne skille n8n
- <https://docs.n8n.io/> — dokumentacja n8n (wersje markdown: dopisz `.md` do URL-a strony;
  indeks: `https://docs.n8n.io/sitemap.md`)
- <https://developer.clickup.com/> — API ClickUp v2
