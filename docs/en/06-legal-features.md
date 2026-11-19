# 06 · Legal Features

What sets LegalLLMWiki apart from a generic LLMWiki. Technical details in `template/en/wiki-schema.md`.

## Norm Nodes & Landmark Decisions
Leading norms (articles/sections) and landmark decisions get **dedicated anchor pages** (`wiki-category: entitaet`). Concept pages link to them — the **backlinks** of these nodes are the query path (replacing SPARQL). Examples: `template/en/examples/DSGVO Art. 6.md`, `template/en/examples/EuGH C-300-21 (Österreichische Post).md`.

## Machine-Readable Frontmatter Fields
```yaml
normen:        # ["DSGVO Art. 6", "EU AI Act Art. 9", …]  — Norm zuerst, einheitlich
urteile:       # ["ECLI:…", "BVerfGE 65, 1", …]
rechtsgebiet:  # ["Datenschutzrecht", …]
rang:          # 1–6 (nur Norm-/Urteilsknoten)
ecli:          # nur Leitentscheidungen (verifiziert)
resource:      # stabile Asset-URI: ELI (Normen) / ECLI-Resolver (Urteile) / DOI
resource_element: # element anchor inside the act: art_9 (EU) / art-z22 (DE federal)
behandelt:     # anchor pages only: what the page IS ABOUT (exactly one value)
relationen:    # anchor pages only: typed edges as a projection of the prose
ausser_kraft:  # norm nodes only: date of repeal
```

**`behandelt:` separates node from citation.** `normen:` records which norms a page *mentions* — "DSGVO Art. 22" appears on 13 pages that way. `behandelt:` records which page *is the node*: exactly one.

**`relationen:` makes the edge queryable.** The relation vocabulary previously existed only as a bold verb in the prose — readable, but not queryable. `relationen:` mirrors it into the frontmatter:
```yaml
relationen:
  - typ: verdrängt
    ziel: "NetzDG § 3"
    seit: 2024-02-17
```
The prose stays authoritative; the field adds **nothing**. Negations ("overlaid, but *not* superseded") produce no edge, and nothing is inferred. Because nothing is added, creating it is a **mechanical pass without the lifting duty**.

**`resource_element:` delivers element precision — not amendment-proofing.** `resource:` names the act, `resource_element:` the element within it. Without the anchor, `DSGVO Art. 9` and `DSGVO Art. 22` carry the same URI. But the promise stops there: LegalDocML.de 1.9 expressly calls the `eId` "not an identifier stable across expressions", and when GUIDs are preserved is "not yet conclusively defined". The anchor is a **dated pointer**, not a durable identity.
Normalize norm strings consistently (`<Statute> Art./§ <N>`), otherwise backlinks/queries fragment.

## Legal Hierarchy (6 ranks)
The rank follows the **norm**, not the court:

| Rank | Category |
|---|---|
| 1 | EU primary law (AEUV/EUV/GRC) |
| 2 | EU regulation (DSGVO/DSA/AI Act) |
| 3 | EU directive (transposed) |
| 4 | German constitutional law (GG) |
| 5 | Federal statute / interstate treaty |
| 6 | State statute / ordinance |

The parentheses hold the **norm category**, never a court. This holds even where a national court applies Union law — a Federal Court of Justice judgment on Art. 82 GDPR is rank 2, not rank 5. It is the single most common source of error; enforcing the rule early saves a large retrofit.

**International law** gets no rank of its own but is ranked by its domestic rank: treaty with an act of approval → rank 5; general rules (Art. 25 Basic Law) → rank 5 with a note on the intermediate rank; non-binding instruments (UN General Assembly resolutions, OECD recommendations) → no rank and no `[!recht]` callout. For the ECHR the Görgülü note is mandatory. Details in `wiki-schema.md`.

> **Note:** This six-level hierarchy reflects EU and German law. It must be adapted for other jurisdictions — define your own norm categories and ranks.

## `[!recht]` Callouts
Legally grounded statements are annotated (placed *below* the statement):
```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

## ECLI / ELI as `resource`

> **Note:** ECLI, ELI and CELEX are **EU standards**; the identifiers and data sources used here are geared toward EU and German law. Adapt accordingly for other jurisdictions.

- **Norms → ELI:** EU `http://data.europa.eu/eli/…`, German federal law `https://recht.bund.de/eli/…` or `gesetze-im-internet.de` (section-precise).
- **Decisions → ECLI resolver:** EU via EUR-Lex (CELEX/ECLI), German courts via the respective official source.
- **Golden rule: never invent an ECLI/URI** — only verified identifiers; otherwise just the citation reference.

## Norm Supersession
The wiki reflects the **current state of the law**. If a new source supersedes a norm/decision, the affected pages are updated in the same ingest and outdated callouts are flagged (details: `wiki-schema.md`, section „Rechtliche Aktualität und Normersetzung").
