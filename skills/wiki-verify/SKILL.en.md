---
name: wiki-verify
description: |
  Use when the user wants to verify that wiki claims are actually supported by their sources,
  or wants to measure wiki answer quality: "verify wiki", "verify wiki [page]",
  "check the citations in my wiki", "are these claims supported", "bench wiki",
  "run the benchmark", "how well does my wiki answer questions",
  "prüf die Belege", "Belegprüfung", "stimmen die Belege im Wiki",
  "sind die Aussagen belegt", "Benchmark laufen lassen", "Verifikations-Pass".
  Runs a fresh-subagent verification pass that checks whether each claim on a wiki page is
  carried by its cited source passage (supportedness, not correctness), marks unsupported
  claims, removes fabricated identifiers, and logs the result. Also runs the gold benchmark.
---

# Wiki Verify Skill

Two functions: the **evidence check** of individual pages (`verify wiki`) and the **benchmark** of answer quality (`bench wiki`). Both write their result to `[WIKI-FOLDER]/log.md`.

Full specification: `[WIKI-FOLDER]/wiki-schema.md`, sections *Verification Pass* and *Benchmark Specification*. The procedure can additionally be kept as a process page in the wiki (e.g. [[Workflow - Belegprüfung]]).

> **Note on terminology:** Callout names (`[!recht]`, `[!unbelegt]`) and frontmatter field names (`verifiziert`, `quellen`, `normen`, `urteile`, `ecli`) stay German in both language variants, because they produce the actual markup in the vault and must match the schema.

## Trigger

| Trigger | Function |
|---|---|
| `verify wiki` | asks what to check |
| `verify wiki [page name]` | checks one page |
| `verify wiki [topic]` | checks all pages of a topic folder |
| `verify wiki letzter Ingest` | checks the pages of the latest `log.md` entry |
| `bench wiki` | runs `[WIKI-FOLDER]/benchmark.md` |

Independently of these triggers, the evidence check runs automatically as the closing step of every ingest.

---

## Part 1 — Evidence check

### Principle

**What is checked is supportedness, not correctness.** The check establishes one thing only: whether the cited source passage carries the claim. Whether the claim is true is not judged, because legal interpretation has no machine-checkable standard of truth. A verifier ruling on correctness would cast a presumption into a test routine and produce false confidence, which would be hard to notice precisely because it carries a seal of approval.

### Step 1: Fresh subagent

The actual check runs in a **subagent without the writing context**. This is the core of the procedure, not a formality: whoever wrote the text reads it against the source as confirmation, not as verification.

The subagent receives: page path, page content, frontmatter. It does **not** receive: the reasoning behind how the page was written, or the ingest history.

### Step 2: Collect what is to be checked

Extract from the page:

- `Beleg:` lines from `[!recht]` callouts
- inline evidence locators of the form `(@citekey, S. N)`
- `quellen:`, `normen:`, `urteile:`, `ecli:` from the frontmatter
- **claims that would need evidence but carry none** — often the most productive item

### Step 3: Return to the sources

Zotero MCP (default endpoint `http://127.0.0.1:23120/mcp`, see `docs/en/03-zotero-mcp.md`):

- `search_fulltext` with a characteristic phrase from the claim, to locate the passage
- `get_content` targeted at the section (`mode: "standard"` is usually enough)
- `get_annotations` for your own highlights

Check norms and decisions against the official source: EUR-Lex/ELI for EU law, gesetze-im-internet.de for German federal law, the ECLI resolver for decisions. For other jurisdictions, use the respective official source of record.

### Step 4: Classify

| Finding | Meaning | Consequence |
|---|---|---|
| `belegt` (substantiated) | the passage carries the claim | nothing |
| `nicht belegt` (not substantiated) | the passage exists, it does not carry the claim | max. 2 repair attempts (fix the locator, look for a better passage), then `[!unbelegt]` |
| `widersprochen` (contradicted) | the source says something else | correct it in the same run, log the correction |
| `nicht prüfbar` (not checkable) | no full text available | claim stays, do **not** set `verifiziert:` |

### Step 5: Hard fail

Four findings lead to **immediate removal without a repair attempt**:

1. fabricated or unfindable **ECLI**
2. fabricated **norm designation** (the article/section does not exist in the cited statute)
3. fabricated **source of record** (volume, page, marginal number not verifiable)
4. fabricated **citekey** (not present in Zotero)

These are removed, not flagged. The schema rule "never invent an ECLI" was an instruction to the writing agent; here it becomes a check performed by a different one. Instructions enforce nothing, checks do.

### Step 6: Flag

Claims that fail get a callout. They do not disappear silently, and they do not remain standing without comment:

```markdown
> [!unbelegt] ⚠️ Not substantiated — checked YYYY-MM-DD
> The cited source @citekey does not carry this statement at the passage given.
> Either correct the locator, supply a source, or remove the statement.
```

### Step 7: Close out

- no open findings → set `verifiziert: YYYY-MM-DD` in the frontmatter
- an open `[!unbelegt]` finding → do **not** set the field
- advance `updated:` if the text was changed

`log.md` entry:

```
- **Verification** [[Page name]] — 14 statements: 12 substantiated, 1 corrected, 1 not substantiated, 0 hard fail
```

### Output format

```markdown
## Evidence check — [page] — YYYY-MM-DD

**Result:** 12/14 substantiated · 1 corrected · 1 not substantiated · 0 hard fail
**Status:** `verifiziert:` not set (open finding)

### Corrected (1)
- "[claim]" — locator said @citekey p. 88, correct is p. 91

### Not substantiated (1)
- "[claim]" — @citekey does not carry the claim at any findable passage

### Hard fail (0)
```

---

## Part 2 — Benchmark

### Procedure

1. Read `[WIKI-FOLDER]/benchmark.md`
2. Answer every question from **Block A** through the `wiki-query` workflow, **without the gold answer being in context**. In practice: one subagent per question, receiving only the question.
3. Do the same for every question from **Block B**. The expected answer there is the refusal.
4. Check the answers against the gold answers

### Scoring

| Criterion | Meaning |
|---|---|
| **substantively correct** | hits the core of the gold answer |
| **correctly substantiated** | points to the stated evidence page |
| **partial hit** | substantively correct, but without evidence |
| **no hit** | substantively correct, but from model knowledge instead of from the wiki |

The last case matters: an answer that is right but does not come from the wiki measures the model, not the wiki. It does not count.

For **Block B**, a correct refusal counts as passed, even if explicitly marked model knowledge was added. The question is failed when model knowledge is presented as wiki content.

### Output

```markdown
## Benchmark — YYYY-MM-DD

**Block A (knowledge):** 13/15 correct, 11 of them correctly substantiated
**Block B (out of scope):** 5/5 correctly refused

### Failures
- A7 — answer did not state the date, evidence page correct
- A12 — answer from model knowledge, no wiki evidence

### Comparison with the previous run
Block A: 13/15 (previously 12/15) · Block B: 5/5 (unchanged)
```

`log.md` entry:

```
- **Bench** — knowledge 13/15 correct (11 substantiated), out-of-scope 5/5 refused
```

A drop after a schema change is a finding about the schema change, not about the question set.

---

## Limits

- The skill checks **supportedness**, not substantive correctness. It does not replace legal review.
- Without full text in Zotero no check is possible. Marking a page as checked when it could not be checked would be worse than no check at all.
- Pages whose `updated:` predates the introduction of the evidence layer (`[EINFÜHRUNGSDATUM]`, enter your own date) are grandfathered in and are only checked on an explicit trigger.
- The benchmark measures the wiki, not the model. It is meaningful only as long as the gold answers track the state of the wiki.
