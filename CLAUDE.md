# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A working toolbox for an IdoMods / BrandsManago e-commerce consultant. It is **not a single application** — it is a collection of independent scripts, XSLT stylesheets, and one-off data jobs used to transform, migrate, and enrich product data for online shops (primarily IdoSell / IAI-Shop stores). Each subfolder is effectively its own mini-project with its own inputs, outputs, and (often) a `run*.bat` launcher.

Most code, comments, filenames, and docs are in **Polish**. Everything is **UTF-8** and must preserve Polish characters (ą ć ę ł ń ó ś ź ż). Match the existing language when editing a file — do not translate Polish comments/identifiers to English.

## Primary domains

- **`xslt/`** — the largest area. XSLT 1.0/2.0 stylesheets that transform an IAI/IdoSell **IOF "offer" XML** export into marketing feeds (Google Shopping, Facebook/Meta, TikTok, Pinterest, Segmentify, etc.). Organized **alphabetically by client** (`A/`, `B/`, `C/` … each holding per-client subfolders like `B/butyolivier/`). `xslt/szablony/` holds reusable templates; `xslt/iaiDownloader/` holds per-client feed-download + transform setups.
- **`python/`** — ETL / data-migration scripts. Each subfolder is a distinct job (CSV↔XML migration, category-ID mapping, multi-store client dedup, etc.) with sample data files and `run*.bat` wrappers. Written for **large files** using streaming (`xml.etree.ElementTree` iterparse, `csv.DictReader`, optional sqlite as an on-disk map).
- **`js/`** — standalone browser/automation snippets: GTM/Facebook Pixel tracking, cookie consent, ad injection, Facebook Ads budget watchers, Furgonetka (courier) API. Node deps in root `package.json` (express, facebook/google ads SDKs, cheerio, cron) support the automation scripts.
- **`php/`, `SQL/`** — small backend/query helpers (largely PrestaShop/IdoSell oriented).
- **`AI_Instrukcje/`** — Polish per-language convention docs (`Python/`, `JavaScript/`, `SQL/`, `XSLT/`, `PHP/`), each with `assumptions.md` + `instructions.md`. Read the relevant one before writing new code in that language.

## Running things

There is **no build, lint, or test setup** (`npm test` is a placeholder that errors). Scripts run directly:

- **Python jobs**: `python app.py` (or the co-located `run*.bat`, which supplies the exact CLI args). Auto-detect input files in the current directory when args are omitted — so run them from inside their own folder. Python 3.8+, standard library only unless a folder says otherwise.
- **XSLT**: applied with an external processor (xsltproc/libxslt or Saxon; `saxon-js` is the only devDependency). Input is the shop's `offer` XML; output is the target feed XML.
- **summonFeed generator**: `python xslt/szablony/summonFeed/summonFeed_generator.py` — interactive CLI that assembles a complete XSLT feed from building blocks. See `xslt/szablony/summonFeed/README_GENERATOR.md`.

## IAI/IdoSell input format (key to all XSLT and much of the Python)

Source XML uses `/offer/products/product`, each with `sizes/size` variants, an `iaiext:` extension namespace, and `@id` / `@currency` attributes. Feeds iterate `product` → `size` to emit one `<item>` per variant. Product attributes (gender, color, material, etc.) are matched by **Polish panel label** against pipe-delimited variable lists near the top of each stylesheet (e.g. `<xsl:variable name='gender_male'>|Męskie|</xsl:variable>`) — extend those lists rather than hardcoding new logic when a shop names a field differently.

## summonFeed generator architecture

A template-composition system (not a template engine). Two directories of paired `.json` + `.xsl` files:

- `structure_templates/` — one pair per feed type (`google`, `facebook`, `samba`). The JSON declares `insertionPoints` (`template` + `context`); the XSL is a skeleton with empty named templates.
- `parameters_templates/` — one pair per product field (`title`, `price`, `color`, …). The JSON declares which `structure`s the field applies to, its `context` (`product`/`size`/`feed`), the output element name, and the path to its XSL fragment. `helpers.xsl` holds shared named templates.

The generator loads all JSON, filters parameters to the chosen structure, prompts for any required `configVars` once, and splices the selected XSL fragments into the structure skeleton at their insertion points. Output is written to the `summonFeed/` root as `<Structure>_generated_<timestamp>.xsl`. **To add a field/structure, drop in a new `.json`+`.xsl` pair — the generator discovers them automatically; no code change needed.**

## Conventions

- Indentation: 2 spaces for XSLT/JS, 4 for Python/PHP.
- Large data artifacts (`feed*.xml`, exports, backups, source dumps, tokens) are **gitignored** — do not commit them or rely on their presence; they are per-machine working files. `Facebook_generated_*.xsl` / `Samba_generated_*.xsl` etc. are disposable generator output.
- Per-client XSLT files are near-duplicates tuned per shop — when fixing a shared bug, check whether sibling client files under other letter folders need the same change.
