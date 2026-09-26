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

Your own non-wiki folders are **not** part of the wiki. `Workflows/` is an **infrastructure folder**, not a topic folder: it holds callable procedure pages (`type: wiki-workflow`) that are not covered by thematic evaluations or by the depth standard.

### Ingest triggers

| Command | Behavior |
|---|---|
| `ingest @citekey` | Fetches exactly this Zotero source (metadata, abstract, annotations) and processes it |
| `update wiki` | Bulk ingest: reads the last date from `[WIKI-FOLDER]/log.md`, fetches all newer Zotero entries |
| `update wiki: [topic]` | Searches Zotero for this topic/tag, processes all hits |
| `lint wiki` | Checks wiki integrity with severity classification — details in `wiki-schema.md` |
| `query wiki: [question]` | Searches `[WIKI-FOLDER]/` (index + grep), synthesizes an answer with [[Wikilinks]], offers a synthesis page |
| `verify wiki [page\|topic\|last ingest]` | Verification pass: a fresh subagent checks every statement against its source passage, flags unsubstantiated ones, removes hard fails |
| `bench wiki` | Runs the gold benchmark from `[BENCHMARK-LOCATION]/benchmark.md` (knowledge questions and out-of-scope questions) |
| `workflow: [name]` | Reads the workflow page `[WIKI-FOLDER]/Workflows/Workflow - [name].md` and works through it step by step |

### Ingest workflow (always the same, regardless of the trigger)
1. Read `[WIKI-FOLDER]/wiki-schema.md`
2. Zotero MCP server (native endpoint `http://127.0.0.1:23120/mcp`): metadata + abstract via `get_item_details` (or `get_item_abstract`); full text via `get_content` (`mode: "complete"` = entire document, no `page` parameter); annotations via `get_annotations`. For `ingest @citekey`: first `search_library` with q=citekey → `itemKey`, then `get_item_details`.
3. **Check the full-text precondition (abort criterion).** Does `get_content` actually return text? **An existing PDF attachment is not enough** — a scan without an OCR layer returns zero characters yet looks provided in the attachment list. Counter-check: `pdftotext -q <file> -`. If it is a scan: **halt the ingest** and offer OCR. If no full text is obtainable: **warn explicitly and obtain a decision**; do not quietly write from metadata (details in `wiki-schema.md`, section *Full-Text Precondition for Ingest*)
4. Read `[WIKI-FOLDER]/index.md` — check existing wiki pages
5. Identify affected concepts/entities, determine topic folders
6. Write/update wiki pages (max. ~15 per ingest), set [[Wikilinks]] and **set locators**: a `Beleg:` line inside the `[!recht]` callout for legal statements, otherwise an inline locator `(@citekey, S. N)`
7. **Verification pass:** a fresh subagent checks every statement against its source passage, flags unsubstantiated statements with `[!unbelegt]`, removes hard fails, and sets `verifiziert:` when the finding is clean (details in `wiki-schema.md`)
8. Update `[WIKI-FOLDER]/index.md`
9. Append an entry to `[WIKI-FOLDER]/log.md`

For large ingests (more than 3 sources, or a single source with more than ~50 pages of full text), decompose the workflow into sub-agents with a JSON handoff instead of loading everything into one context window (section *Ingest Decomposition* in `wiki-schema.md`).

### Evidence discipline
Every core statement carries its own locator: a `Beleg:` line inside the `[!recht]` callout for legal statements (`Beleg: @citekey S. 142 Rn. 18`), otherwise an inline locator at the end of the sentence (`(@citekey, S. 14)`). If a statement rests directly on the norm text, the norm reference in the callout suffices. The verification pass then checks every statement against its source passage. **What is checked is supportedness, not correctness.** Statements that fail the check and cannot be corrected are flagged with `[!unbelegt]` rather than silently kept; invented ECLIs, norm designations, citations, or citekeys are removed. Details in `wiki-schema.md`.

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

### Wiki MCP server
The wiki can additionally be exposed as a local MCP server: read-only, communication over stdio, no network port and no outside access. Seven tools:

| Tool | Purpose |
|---|---|
| `wiki_info` | Key figures and configuration of the wiki |
| `search_wiki` | Full-text search across all wiki pages |
| `get_page` | A single page with frontmatter and content |
| `get_norm` | Norm node for a norm reference |
| `get_backlinks` | Incoming wikilinks of a page |
| `list_unverified` | Pages without a `verifiziert:` field |
| `list_stale` | Pages with an outdated `rechtsstand:` |

Setup and details in `docs/en/08-mcp-server.md`.
