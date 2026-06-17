# 01 · Concept

## What is LegalWikiLLM?

A setup in which an AI agent builds and maintains a curated subject-matter wiki inside your **Obsidian vault** and keeps it queryable — optimized for **legal content**. Sources live in **Zotero**; the agent pulls them in via MCP, writes structured wiki pages, and keeps them up to date.

It follows the **LLM wiki pattern** by [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (2026): the wiki is not maintained manually by a human, but curated by an LLM according to fixed rules (`AGENTS.md` + `wiki-schema.md`). Zotero is the immutable raw-data store; the wiki is the curated knowledge layer.

## Why "legally optimized"?

- **Norm nodes** (e.g. `DSGVO Art. 6`) and **landmark decisions** (e.g. `EuGH C-300-21`) as dedicated anchor pages.
- Machine-readable frontmatter fields: `normen`, `urteile`, `rechtsgebiet`, `rang`, `ecli`, `resource`.
- **Legal hierarchy** (6 ranks) and `[!recht]` callouts beneath legally grounded statements.
- **ECLI/ELI** as stable identifiers (field `resource`).

## Architecture in one sentence

Concept pages link via `[[Wikilink]]` to norm nodes/landmark decisions — the **backlinks** of these nodes replace the SPARQL query of a classic knowledge graph. No triplestore, purely Obsidian-native.

```
Zotero (raw data)  --MCP-->  Agent  -->  Obsidian vault ([WIKI-FOLDER]/ = wiki)
                                          ├─ Concept pages ──┐
                                          ├─ Norm nodes  <───┤ Backlinks = query path
                                          └─ Landmark decisions <─┘
```

## Relationship to OKF

The schema is aligned with Google's **[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)**: every non-reserved page carries a `type` field; `resource` is the OKF recommended field for the asset URI. Details + deliberate deviations in the schema (`template/en/wiki-schema.md`, section "OKF compatibility").

## Next steps

→ `02-obsidian.md` (create the vault) · `03-zotero-mcp.md` (connect Zotero) · `04-agent-setup.md` (set up your agent).
