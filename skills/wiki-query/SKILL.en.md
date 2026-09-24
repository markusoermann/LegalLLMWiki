---
name: wiki-query
description: |
  Use when user wants to query their knowledge base: "query wiki: [question]",
  "what do I know about X", "find everything on X in the wiki", "show me what the wiki says about X",
  "search my wiki for X", "what does my wiki say about X", "search my wiki for X".
  Searches all of [WIKI-FOLDER]/ (the LLMWiki; any non-wiki folders are excluded) using
  the wiki MCP server when connected, plus index + grep, synthesizes an answer with
  [[wikilinks]] and a mandatory evidence-status line, and optionally saves
  the result as a new synthesis wiki page.
---

# Wiki Query Skill

Answers questions from the LLMWiki through structured search in `[WIKI-FOLDER]/`, with optional saving as a synthesis page.

> **Single point of truth:** This wiki is the authoritative knowledge reference of the vault. Other (content-generating) skills — teaching materials, assessment, research — consult it through this workflow **before** producing content, and cite it with [[wikilinks]]. Keep answers consistent and citable.

## Trigger

- `query wiki: [question]` — direct entry point
- `query wiki` — skill asks for the question
- Implicitly on: "what do I know about X", "find everything on X in the wiki", "search my wiki for X"

---

## Workflow

### Step 1 — Read the index

Read `[WIKI-FOLDER]/index.md`. Identify and note thematically relevant wiki pages.

### Step 2 — Search

**Preferred, whenever the wiki MCP server is connected:** `search_wiki` for full-text search, `get_norm` for norm references (returns the norm node plus every page carrying that norm in its `normen:` frontmatter), and `get_backlinks` for the neighbourhood of a page. These tools evaluate the frontmatter, which grep cannot do, and return markedly more complete hits for norm questions.

**Without the MCP server: grep search.**

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

#### Mandatory: evidence-status block

Every answer ends with an evidence status. It visibly separates what comes from the wiki from what does not:

```markdown
**Belegstatus:** 6 claims substantiated from the wiki (4 pages) · 1 claim added from model knowledge (marked above) · Gap: no wiki page on [sub-aspect]
```

Without this block the answer is not finished. A knowledge query whose answer does not reveal which part is substantiated creates the appearance of substantiation for the whole.

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

## Refusal is a correct answer

**"There is nothing on this in the wiki" is a full and desirable result.** It is not a defeat, and it must not be papered over with a plausible-sounding substitute answer.

The most dangerous answer this skill can give is not the wrong one, but the substantively right one that comes from model knowledge and looks like substantiated wiki knowledge. It is dangerous because it makes the wiki answerable for something that was never written into it and never checked. Whoever goes looking for the evidence page afterwards finds nothing and can no longer trace the error.

Concretely:

- If index, MCP search and grep return **no relevant page**, the answer is: "There is nothing on this in the wiki",
  followed by whatever lies closest in substance, plus an `ingest` suggestion.
- If the wiki covers the question only **partially**, name the boundary: which part is substantiated and which is not.
- Model knowledge may be added, but **only** with `*Note: not substantiated in the wiki*`, and never as the
  main answer without a preceding refusal.
- A source reference is **never** reconstructed. No page number, no citekey, no ECLI and no source of record
  that is not in the wiki.

This discipline is measured: Block B of `[BENCHMARK-LOCATION]/benchmark.md` contains questions on areas of law the wiki
demonstrably does not cover. The correct answer there is the refusal in every case (see the `wiki-verify` skill).

## Limits

- Searches only in `[WIKI-FOLDER]/` — no projects, daily notes, inbox
- Synthesizes only what is in the wiki; gaps → `ingest` hint
- Synthesis pages follow the wiki-schema depth standard (at least 3 core aspects, cross-links)
