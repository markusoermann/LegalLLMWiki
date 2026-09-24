# 05 · Workflows & Triggers

All triggers are defined in `AGENTS.md`; the agent recognizes them in the chat. Before every ingest, the agent reads `[WIKI-FOLDER]/wiki-schema.md`.

| Trigger | What happens |
|---|---|
| `ingest @citekey` | Fetches exactly this Zotero source (metadata, abstract, annotations, full PDF text) and writes/updates wiki pages. |
| `update wiki` | Bulk ingest: reads the last date from `log.md`, fetches all newer Zotero entries. |
| `update wiki: [topic]` | Searches Zotero by topic/tag, processes all matches. |
| `query wiki: [question]` | Searches `[WIKI-FOLDER]/` (index + grep), synthesizes an answer with `[[Wikilinks]]`, optionally offers a synthesis page. |
| `lint wiki` | Integrity audit (broken links, orphans, missing nodes, frontmatter drift) with severity levels. |
| `verify wiki [page]` | Citation check by a fresh subagent: does the cited passage carry the claim? Argument optional (page, topic, or last ingest); runs as step 6 of every ingest anyway. (→ `07-verification.md`) |
| `bench wiki` | Measures answer quality against `[WIKI-FOLDER]/benchmark.md` (knowledge questions + out-of-scope questions). |
| `workflow: [name]` | The agent reads the workflow page in `[WIKI-FOLDER]/Workflows/` and works through it step by step. |

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
1. Read `wiki-schema.md` → 2. Zotero tools (`search_library` → `get_item_details` → `get_content` → `get_annotations`) → 3. Check `index.md` → 4. Determine topic folders → 5. Write pages (max. ~15/ingest), every key claim with a locator (`Beleg:` line or `(@citekey, S. N)`) → 6. **Verification pass** by a fresh subagent, then set `verifiziert:` → 7. Update `index.md` → 8. Append `log.md` entry.

## Maintenance
- Run `lint wiki` and `bench wiki` together at regular intervals (e.g. after every 10 ingests): one measures structure, the other answer quality.
- For changes to norms/rulings: observe the norm supersession rules in `wiki-schema.md` (mark with `[!recht]` callouts).

## Next
→ `06-legal-features.md` — the legal specifics · `07-verification.md` — citations, verification pass, and benchmark · `08-mcp-server.md` — the optional wiki MCP server.
