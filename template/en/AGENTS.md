# Vault Context

This vault is the Second Brain of **[YOUR NAME]** ([YOUR FIELD, e.g. "lawyer specializing in media and data protection law"]).

> **Note for adopters:** This file is the agnostic context/instruction file for your AI agent. Codex and OpenCode read it natively as `AGENTS.md`; for Claude Code and Gemini CLI, wire it in via the symlinks `CLAUDE.md`/`GEMINI.md → AGENTS.md` (see `template/agent-config/symlinks.sh`). Replace all `[…]` placeholders with your own details — in particular `[WIKI-FOLDER]` (see below).

## About me

[Short profile: who you are, your field, your focus areas, how you work. The agent reads this section for substantive tasks (texts, proposals, teaching). A detailed profile can optionally live in its own note.]

## Folder structure

You define your folder structure **yourself** — no particular method is prescribed. The LLMWiki needs only **one wiki folder**, whose location you are free to choose. Enter it here and replace every occurrence of `[WIKI-FOLDER]` below with this path:

- **`[WIKI-FOLDER]/`** — contains `wiki-schema.md`, `index.md`, `log.md` as well as all wiki pages (see "LLMWiki" below). Freely chosen, e.g. `Wiki/`, `Resources/`, or `.` (vault root).

All other folders are optional and entirely up to you (e.g. for an inbox, projects, daily notes, archive, attachments). The routines and rules below only apply to the extent that you maintain such folders. One common (but not required) convention is [PARA](https://fortelabs.com/blog/para/).

## Rules for this vault

- Use [[Wikilinks]] to connect notes
- Keep notes atomic: one idea per note where possible (exception: daily summaries)
- Use YAML frontmatter: tags, status (active/completed/paused), date
- File names in normal writing with spaces and capital letters: `Descriptive Name.md`
- Daily notes (if used) in the format `YYYY-MM-DD.md`
- When you create or move files, briefly explain why
- Before you delete or overwrite files, ask first
- Move/archive files only on the user's instruction, not on your own initiative
- When the user says "remember this"/"save this": substantive findings go into the wiki (`[WIKI-FOLDER]/`), vault rules into this `AGENTS.md`, everything else where it fits thematically. When in doubt, ask briefly.

## Session routines

### At session start
If you maintain a folder for unsorted notes (inbox or similar): check it for new entries, show what's there, and offer to file them.

### Context on demand
For questions like "What's current right now?" / "Where did I leave off?": read — to the extent they exist — the most recent daily notes and the active project files to give a briefing.

### At session end
Offer to: (1) note a daily summary (if you keep daily notes), (2) save new findings as wiki/note pages, (3) tidy up anything unsorted.

## LLMWiki

The folder `[WIKI-FOLDER]/` contains an LLM-maintained wiki following the Karpathy LLMWiki pattern. Zotero serves as an immutable raw-data store. The agent writes and maintains all wiki pages autonomously. Technical details in `[WIKI-FOLDER]/wiki-schema.md` — read this file on every ingest.

**Single point of truth:** The LLM wiki is the authoritative knowledge reference of this vault. Other (content-generating) skills consult it before working, use its content with priority, cite it with [[wikilinks]], and propose additions via `ingest`.

### Wiki topic folders
Create your own topic folders under `[WIKI-FOLDER]/` — one folder per field — and enter them here:
`[Topic 1]` · `[Topic 2]` · `[Topic 3]` · …

Your own non-wiki folders are **not** part of the wiki.

### Ingest triggers

| Command | Behavior |
|---|---|
| `ingest @citekey` | Fetches exactly this Zotero source (metadata, abstract, annotations) and processes it |
| `update wiki` | Bulk ingest: reads the last date from `[WIKI-FOLDER]/log.md`, fetches all newer Zotero entries |
| `update wiki: [topic]` | Searches Zotero for this topic/tag, processes all hits |
| `lint wiki` | Checks wiki integrity with severity classification — details in `wiki-schema.md` |
| `query wiki: [question]` | Searches `[WIKI-FOLDER]/` (index + grep), synthesizes an answer with [[Wikilinks]], offers a synthesis page |

### Ingest workflow (always the same, regardless of the trigger)
1. Read `[WIKI-FOLDER]/wiki-schema.md`
2. Zotero MCP server: metadata + abstract via `get_item_by_key`; full text via `get_pdf_content`; annotations via `get_item_annotations`. For `ingest @citekey`: first `search` with q=citekey → item key, then `get_item_by_key`.
3. Read `[WIKI-FOLDER]/index.md` — check existing wiki pages
4. Identify affected concepts/entities, determine topic folders
5. Write/update wiki pages (max. ~15 per ingest), set [[Wikilinks]]
6. Update `[WIKI-FOLDER]/index.md`
7. Append an entry to `[WIKI-FOLDER]/log.md`

### New topic folders
Create a new folder when a source cannot be sensibly assigned to any existing folder (at least 2–3 concepts). Then: create the hub file `[topic].md`, add the folder to the topic list in `wiki-schema.md`, to `index.md`, and to this `AGENTS.md` list, and document it in `log.md`. For borderline cases, check briefly with the user.

### Token budget
If the context limit is foreseeably about to be reached: document the state in `log.md` with `[interrupted after N sources, N pending]` and inform the user. The next session resumes seamlessly.

### Wiki page marker
All wiki pages have `type: wiki-page` in the frontmatter. Source-overview pages from the Zotero import template (`tags: [literatur]`) are **not** wiki pages.

### Norm nodes and landmark decisions
Leading norms (articles/sections) and landmark decisions get their own anchor pages (`wiki-category: entitaet`, with `rang:`; for judgments additionally `ecli:`). Concept pages link to these nodes instead of merely naming norms in the running text — the backlinks replace the SPARQL query of a classic knowledge graph. When ingesting legal sources: list the affected norms/judgments in the frontmatter fields `normen:`/`urteile:`/`rechtsgebiet:` and link to existing norm nodes. If the node is missing and the norm is cited in ≥3 pages → create the node. Relationships use a typed relation vocabulary (transposes / supersedes / specifies / applies — details in `wiki-schema.md`). **Never invent an ECLI.**

### Legal hierarchy annotation
Legally grounded statements are annotated with a `[!recht]` callout (placed *below* the statement). Format: `⚖️ Rank [N] ([norm category]) · [court/norm] → [reference]`. The rank follows the norm, not the court (6-level hierarchy table in `wiki-schema.md`). Set this only for concrete norms/decisions — not for general scholarly opinions.
