# 05 · Workflows & Triggers

All triggers are defined in `AGENTS.md`; the agent recognizes them in the chat. Before every ingest, the agent reads `[WIKI-FOLDER]/wiki-schema.md`.

| Trigger | What happens |
|---|---|
| `ingest @citekey` | Fetches exactly this Zotero source (metadata, abstract, annotations, full PDF text) and writes/updates wiki pages. |
| `update wiki` | Bulk ingest: reads the last date from `log.md`, fetches all newer Zotero entries. |
| `update wiki: [topic]` | Searches Zotero by topic/tag, processes all matches. |
| `query wiki: [question]` | Searches `[WIKI-FOLDER]/` (index + grep), synthesizes an answer with `[[Wikilinks]]`, optionally offers a synthesis page. |
| `lint wiki` | Integrity audit (broken links, orphans, missing nodes, frontmatter drift) with severity levels. |

## Typical flow

```
1. Add the source to Zotero (note the citekey)
2. In the agent:  ingest @mustermann2024
   → Agent reads the Zotero entry, identifies concepts/normen/urteile,
     writes wiki pages into the appropriate topic folders, sets [[Wikilinks]],
     updates index.md + log.md
3. Later:  query wiki: What does my wiki say about data minimization?
   → Answer from frontmatter (normen/urteile) + backlinks
```

## Ingest flow (internal, always the same)
1. Read `wiki-schema.md` → 2. Zotero tools (`search` → `get_item_by_key` → `get_pdf_content` → `get_item_annotations`) → 3. Check `index.md` → 4. Determine topic folders → 5. Write pages (max. ~15/ingest) → 6. Update `index.md` → 7. Append `log.md` entry.

## Maintenance
- Run `lint wiki` regularly (e.g. after every 10 ingests).
- For changes to norms/rulings: observe the norm supersession rules in `wiki-schema.md` (mark with `[!recht]` callouts).

## Next
→ `06-legal-features.md` — the legal specifics.
