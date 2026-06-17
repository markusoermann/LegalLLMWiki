---
name: wiki-query
description: |
  Use when user wants to query their knowledge base: "query wiki: [question]",
  "what do I know about X", "find everything on X in the wiki", "show me what the wiki says about X",
  "search my wiki for X", "what does my wiki say about X", "search my wiki for X".
  Searches all of [WIKI-FOLDER]/ (the LLMWiki; any non-wiki folders are excluded) using
  index + grep, synthesizes an answer with [[wikilinks]], and optionally saves
  the result as a new synthesis wiki page.
---

# Wiki Query Skill

Answers questions from the LLMWiki through structured search in `[WIKI-FOLDER]/`, with optional saving as a synthesis page.

## Trigger

- `query wiki: [question]` — direct entry point
- `query wiki` — skill asks for the question
- Implicitly on: "what do I know about X", "find everything on X in the wiki", "search my wiki for X"

---

## Workflow

### Step 1 — Read the index

Read `[WIKI-FOLDER]/index.md`. Identify and note thematically relevant wiki pages.

### Step 2 — Grep search

Extract key terms from the question. Always search **German + English variants** (technical terms appear in both languages):

```bash
# Combine multiple search terms
grep -rl "Verantwortung\|accountability\|responsibility" \
  "/path/to/your/vault/[WIKI-FOLDER]/" \
  --include="*.md"
```

Actively include synonyms and related concepts (e.g. `Plattform|platform`, `Regulierung|regulation`).

### Step 3 — Merge sources

- Merge index hits + grep hits, remove duplicates
- Read pages, follow [[Wikilinks]] when thematically relevant
- **Prioritization when there are many hits:** index hits → exact grep hits → related pages
- Cap: read at most ~10–12 pages; if more, filter by relevance

### Step 4 — Synthesize the answer

Format depending on question type:

| Question type | Format |
|---|---|
| Factual question | Direct answer + evidence |
| Comparison question | Structured comparison |
| Exploratory question | Thematic overview with references |
| List question | Annotated list |

Support every central statement with a `[[Wikilink]]`. Name contradictions between sources explicitly.

### Step 5 — Synthesis page follow-up

After the answer, ask:

> "Shall I save this analysis as a synthesis page in the wiki?"

**If yes:**
1. Determine the appropriate topic from the wiki topic folders (`Ethik`, `KI`, `Jura`, etc.)
2. Filename: `Synthese - [descriptive title].md`
3. Frontmatter (mandatory):
   ```yaml
   ---
   type: wiki-page
   wiki-category: synthese
   thema: [topic]
   quellen: ["@citekey1", "@citekey2"]  # all referenced sources
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---
   ```
4. Save: `[WIKI-FOLDER]/[topic]/Synthese - [title].md`
5. Update `[WIKI-FOLDER]/index.md`
6. Append entry to `[WIKI-FOLDER]/log.md`:
   ```
   - **Query** "[question]" → created [[Synthese - title]]
   ```

**If no:** done.

---

## Quality standards

- **Substantiate:** Every factual statement with a `[[Wikilink]]` or source reference
- **Transparent:** If the wiki is incomplete on the topic → clearly say what is missing + suggest `ingest`
- **Honest:** Do not supplement from domain knowledge without labeling it — this is a wiki query, not an expertise query. Add your own knowledge only as an explicitly marked addition (`*Note: not substantiated in the wiki*`)
- **Contradictions:** Name them explicitly between sources, do not smooth them over

## Limits

- Searches only in `[WIKI-FOLDER]/` — no projects, daily notes, inbox
- Synthesizes only what is in the wiki; gaps → `ingest` hint
- Synthesis pages follow the wiki-schema depth standard (at least 3 core aspects, cross-links)
