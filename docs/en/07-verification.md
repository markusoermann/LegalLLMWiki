# 07 · Verification, Citations & Benchmark

`lint wiki` checks **structure**: broken links, orphans, missing nodes, frontmatter drift. It does not check whether a sentence is actually carried by the source cited beneath it. That gap is what the **verification pass** closes.

## The citation layer

`quellen:` cites a page as a whole. That is not enough for a check: what gets verified is a passage, not an entire PDF. Every key claim therefore carries its own **locator**.

| Mechanism | Where | For what |
|---|---|---|
| `Beleg:` line | inside the `[!recht]` callout, directly below the title line | legal claims taken from secondary sources (interpretation, doctrinal dispute, figures) |
| Inline locator | at the end of the sentence | non-legal key claims taken from a source |
| `[!unbelegt]` callout | below the claim | a finding that failed the check |
| `verifiziert:` | frontmatter | date of the last passed verification pass |

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6 Abs. 1 lit. f
> Beleg: @kuehling2024 S. 142 Rn. 18
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

```markdown
The effect is measurable in the data from 2023 onward (@mustermann2026, S. 14).
```

If a claim rests directly on the text of the norm itself, the `Beleg:` line is omitted: the norm reference in the title line **is** the locator. The inline format is `(@citekey, S. N)`, `(@citekey, Abschn. N)`, or `(@citekey)` for sources without pagination; greppable via `\(@[a-z]`.

```
> [!unbelegt] ⚠️ Not substantiated — checked YYYY-MM-DD
> The cited source @citekey does not carry this statement at the passage given.
> Either correct the locator, supply a source, or remove the statement.
```

The callout is an open finding, not a permanent state: `lint wiki` reports `[!unbelegt]` findings older than 30 days as a warning.

## Verification pass

The pass runs automatically as **step 7 of every ingest** and on the trigger `verify wiki [page|topic|last ingest]`.

The check is performed by a **fresh subagent without the writing context**. Whoever wrote the text cannot check it impartially; that is the core of the procedure, not a formality. The subagent receives the page path, all locators, and the fields `normen:`/`urteile:`/`ecli:`, looks up the passages via the Zotero MCP server (primarily `get_content`; `search_fulltext` only when the original wording is known, since it matches substrings rather than term combinations), and classifies each claim:

| Finding | Meaning | Consequence |
|---|---|---|
| `belegt` | the cited passage carries the claim | nothing |
| `nicht belegt` | the passage exists but does not carry the claim | max. 2 repair attempts (fix the locator, find a better passage), then `[!unbelegt]` |
| `widersprochen` | the source says something different | correct the claim in the same run, note the correction in `log.md` |
| `nicht prüfbar` | no full text available | the claim stays, `verifiziert:` is **not** set, `log.md` note `[kein Volltext]` |

**Hard fail (immediate removal, no repair attempt):** a fabricated or unresolvable ECLI, a fabricated norm designation (the article/section does not exist in the cited statute), a fabricated citation reference (volume, page, marginal number not verifiable), a fabricated citekey (not present in Zotero). These four cases are removed, not flagged, and logged as `Hard-Fail`. The rule "never invent an ECLI" used to be an instruction; here it becomes a check. Instructions enforce nothing, checks do.

If the page passes with no open finding, `verifiziert: YYYY-MM-DD` is set. If an `[!unbelegt]` callout remains, the field is not set.

```
- **Verification** [[Page name]] — 14 statements: 12 substantiated, 1 corrected, 1 not substantiated, 0 hard fail
```

## Supportedness ≠ correctness

> The verifier determines **only** whether the cited passage carries the claim. It does not decide whether the claim is correct, and it does not replace expert review.

Legal interpretation has no machine-checkable standard of truth; it is contested, and legitimately so. A verifier that ruled on correctness would elevate an opinion to a test result and thereby manufacture false confidence, complete with a seal of approval. Supportedness is the weaker property, but it is checkable, and therefore the only assurance the wiki makes.

## Findings need a counter-check

The verification pass produces findings that call for action, and a hard-fail finding calls for immediate removal. That is precisely why it needs a control step: **a finding is a claim about the text, not an established fact.**

The most expensive case in practice was not a missed error but an invented one. A verifier reported an author attribution in the wiki as wrong, basing this on the author field in the reference manager. The full text of the article carried the wiki's spelling throughout its running head. The reference-manager record was wrong, not the text. Applying the finding unchecked would have destroyed correct attributions in three files, and would have done so under the heading "hard fail", that is, with a claim to particular rigour.

Two rules follow:

**The counter-check follows the hierarchy of sources.** Reference-manager metadata is derived and error-prone; the publication itself governs. For norm designations the official text decides, not the secondary literature citing it. In the same run, checking against official sources confirmed two reported doubts about norms and refuted a third.

**What cannot be verified is removed, not replaced.** If a doubtful date could not be settled from the working environment, the statement is struck rather than swapped for a second unverified one. A docket number identifies a decision even without a date.

This is the same discipline that applies to the mechanical check scripts (see `tools/README.md`). For the verification pass it weighs more heavily, because its finding is phrased authoritatively and calls for deletion, whereas a script merely prints a list.

## Introducing it into an existing stock

If you do not introduce the verification pass on day one, you are left with a legacy stock that never went through it. Checking that stock retroactively is expensive: setting a locator presupposes having read the source, which makes it a re-ingest of every page. At a few hundred pages that is weeks of work.

The temptation is to plan it as a campaign anyway. The better rule has two halves, and it only holds as a pair:

**Grandfathering.** Pages last changed before the introduction date are not actively brought up to standard. This is not negligence but accurate labelling: if `verifiziert:` is absent, the page counts as unverified — which is exactly what it is. The error would not be leaving it unverified, but believing it verified.

**Lifting on touch.** When a legacy page is changed substantively for any other reason, it loses grandfathered status and is lifted within that same edit: locators, verification pass, `verifiziert:`. What governs is the size of the page, not the size of the change.

The stock then converges through ordinary work rather than a special effort — and in the right order, because what gets touched most often gets verified first. Pages nobody touches for years stay unverified; that is defensible as long as they are labelled unverified.

Two boundaries, without which the rule collapses: if lifting exceeds the scope of the edit, `verifiziert:` stays **open** and the log records what was checked and what was not — a partially checked state must never appear as checked. And purely mechanical runs do not lift: otherwise a search-and-replace across 40 files would force 40 verification passes.

## Ingest decomposition

A linear ingest loads full text, index, and writing context into a single context window. Splitting it into sub-agents that exchange data exclusively through standardized JSON reports, never through shared context, turns the context limit into a throughput question.

| Role | Input | Output | Holds in context |
|---|---|---|---|
| **Extractor** | Zotero item | `extraktion.json` | only that one source |
| **Collision checker** | `extraktion.json` + `index.md` | `kollision.json` | only index + JSON |
| **Writer** (parallel, one per page) | one entry from `kollision.json` | `schreibbericht.json` | only its own page |
| **Verifier** (fresh) | page + locators | `verifikat.json` | only the passages |

Activate only from a **bulk ingest of more than 3 sources** or a **single source with more than ~50 pages of full text** (monographs, commentaries, edited volumes) onward. Below that the linear flow remains correct; the overhead does not pay off.

The JSON files live in `/tmp/wiki-ingest/<citekey>/`, deliberately outside the vault, so that intermediate states do not contaminate the knowledge base. The orchestrator holds only the JSON reports, never the PDFs. On abort, that folder is the resume point.

## Benchmark

`lint wiki` measures structure, not answer quality. Without measurement there is no way to tell whether a schema change improved anything at all. File: `[BENCHMARK-LOCATION]/benchmark.md`, i.e. **outside** the wiki folder, so that answering agents cannot grep their way to the gold answers, trigger `bench wiki`, cadence after every 10 ingests together with `lint wiki`.

1. **Knowledge questions:** questions whose answer is demonstrably in the wiki. Per entry: `question` · `gold answer` · `source page` (wikilink). Gold answers are derived from the wiki pages, not formulated from model knowledge.
2. **Out-of-scope questions:** questions on topics the wiki demonstrably does not cover. Here the correct answer is **refusal** ("The wiki has nothing on that.").

**The second block is the more important one.** A knowledge base that fills its gaps with plausible model knowledge is more dangerous than one that stays silent, because the invented answer looks exactly like sourced wiki knowledge.

Every question is posed via `query wiki` without the gold answer in context. Scoring is two-tiered: **substantively correct** (yes/no) and **correctly sourced** (points to the source page). A substantively correct but unsourced answer counts as a partial hit and is reported separately.

```
- **Bench** — knowledge 13/15 correct (11 substantiated), out-of-scope 5/5 refused
```

## Where the procedure comes from

The verification pass, the decomposition, and the benchmark are modeled on the *test verifier–improver* from Paper2Agent: Miao et al., "Reimagining research papers as interactive and reliable AI agents", *Nature* 2026, DOI [`10.1038/s41586-026-11044-y`](https://doi.org/10.1038/s41586-026-11044-y), repo [`jmiao24/Paper2Agent`](https://github.com/jmiao24/Paper2Agent). There, no extracted function may enter the finished MCP server without having been tested against the source; whatever fails is excluded with an error comment rather than kept. The wiki transfers that principle to claims: what its source does not carry does not quietly remain.

## Next
→ `08-mcp-server.md` — the wiki MCP server, which exposes `list_unverified` and `list_stale` as tools.
