# n8n-mcp — serwer MCP z dokumentacją węzłów n8n

Repo: <https://github.com/czlonkowski/n8n-mcp>

## Co daje

Serwer MCP, który udostępnia asystentowi bazę wiedzy o n8n zamiast zgadywania z pamięci:

- ~2 600 węzłów (core + community) wraz z pełnym schematem właściwości,
- listę operacji i parametrów każdego węzła,
- ~2 350 gotowych szablonów workflowów,
- walidację: pojedynczego węzła (`validate_node`) i całego workflowu (`validate_workflow`),
- opcjonalnie (gdy podasz `N8N_API_URL` + `N8N_API_KEY`) — zarządzanie instancją: CRUD workflowów,
  odpalanie i podgląd wykonań, credentiale, audyt.

Najważniejsze narzędzia: `search_nodes`, `get_node`, `validate_node`, `validate_workflow`,
`search_templates`, `get_template`, `tools_documentation`.

## Stan na teraz

**Serwer nie jest podpięty w tym projekcie** — sprawdzone: brak `.mcp.json` w repo i brak `n8n-mcp`
w globalnych pakietach npm. Dlatego ta dokumentacja powstała ręcznie ze źródeł.

## Jak podpiąć (Claude Code, zasięg projektu)

```bash
claude mcp add n8n-mcp --scope project -- npx -y n8n-mcp
```

albo ręcznie plik `.mcp.json` w katalogu repo:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["-y", "n8n-mcp"],
      "env": {
        "N8N_API_URL": "https://twoja-instancja-n8n",
        "N8N_API_KEY": "..."
      }
    }
  }
}
```

Bez `N8N_API_URL`/`N8N_API_KEY` serwer działa w trybie tylko-dokumentacyjnym (wyszukiwanie węzłów,
schematy, szablony, walidacja) — do samego poprawiania eksportów JSON to wystarcza.
Klucz API generuje się w n8n: **Settings → n8n API → Create an API key**.

Alternatywy uruchomienia: `docker run ghcr.io/czlonkowski/n8n-mcp` albo hosted
(<https://dashboard.n8n-mcp.com>, darmowy próg 100 wywołań/dzień).

> Uwaga: klucz API n8n daje pełny dostęp do instancji łącznie z credentialami. Trzymamy go w `.mcp.json`
> poza gitem albo w zmiennej środowiskowej.

## Powiązane repozytoria (jeszcze nieprzejrzane)

- <https://github.com/czlonkowski/n8n-skills> — zestaw skilli do n8n od tego samego autora co `n8n-mcp`.
- <https://github.com/n8n-io/skills> — skille publikowane przez samo n8n.

Oba do rozpoznania przy okazji — mogą zastąpić albo uzupełnić ręczne notatki w tym folderze.
