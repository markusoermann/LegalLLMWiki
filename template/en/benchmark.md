---
type: wiki-benchmark
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Wiki Benchmark

Scaffold for the gold benchmark. Trigger: `bench wiki`. Cadence: after every 10 ingests, together with `lint wiki`. Specification in `wiki-schema.md`, section *Benchmark Specification*.

This file ships deliberately empty. The questions must come from your own wiki, otherwise the benchmark measures nothing. The two entries per block are pure format samples and are replaced on the first real run.

**Target size:** 30 knowledge questions, 10 out-of-scope questions. Fewer is possible but makes the rates coarse.

## Block 1: Knowledge questions

Questions whose answer demonstrably exists in the wiki. The gold answer is **derived from the evidence page**, not formulated from model knowledge. If the evidence page changes substantively, the gold answer is updated with it.

### W01

- **Question:** [question that one wiki page answers unambiguously]
- **Gold:** [short answer in one or two sentences, derived from the evidence page]
- **Evidence:** [[Page name]]

### W02

- **Question:** [question that requires combining two pages]
- **Gold:** [short answer; names both partial aspects]
- **Evidence:** [[Page name 1]], [[Page name 2]]

## Block 2: Out-of-scope questions

Questions on topics the wiki demonstrably does *not* cover. The correct answer is the **refusal**, not a plausible answer from model knowledge. This block is the more important one: a knowledge base that fills gaps with model knowledge is more dangerous than one that stays silent, because the answer looks like substantiated wiki knowledge.

**Check before adding:** test every question by grep across the wiki folder for zero hits. If relevant material turns up, the question does not belong in this block but in block 1.

### O01

- **Question:** [question on a topic that does not appear in the wiki]
- **Expected:** refusal ("There is nothing on this in the wiki.")
- **Grep check:** `[search term]` → 0 hits, checked on YYYY-MM-DD

### O02

- **Question:** [question that superficially resembles a covered topic but sits just outside it]
- **Expected:** refusal, optionally with a pointer to the adjacent topic that *is* covered
- **Grep check:** `[search term]` → 0 hits, checked on YYYY-MM-DD

## Scoring rules

- Every question is asked via `query wiki`, without the gold answer being in context.
- Scoring is two-tiered: **substantively correct** (yes/no) and **correctly substantiated** (points to the evidence page).
- A substantively correct but unsubstantiated answer counts as a **partial hit** and is reported separately.
- An answer to an out-of-scope question counts as correct only if it refuses. A factually accurate answer drawn from model knowledge is an **error** here, not a partial hit.
- If an answer diverges from the gold answer, first check whether the evidence page has changed in the meantime. In that case correct the gold answer, not the score.

## Evaluation

```
## Bench YYYY-MM-DD

Knowledge questions:  N/30 substantively correct, of which N substantiated (N partial hits)
Out-of-scope:         N/10 correctly refused
Notable failures:     [questions that failed, with a short diagnosis]
```

Entry in `log.md`:

```
- **Bench** — knowledge N/30 correct (N substantiated), out-of-scope N/10 refused
```
