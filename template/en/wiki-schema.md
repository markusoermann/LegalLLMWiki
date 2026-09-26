---
type: wiki-schema
updated: 2026-09-23
---

# Wiki Schema

Technical reference for Claude. Read on every ingest.

## Frontmatter Schema

Required fields for all wiki pages:

```yaml
---
type: wiki-page
wiki-category: konzept | entitaet | synthese
thema: [Topic1, Topic2]
quellen: ["@citekey1", "@citekey2"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
rechtsstand: YYYY-MM-DD   # optional; only on pages with time-sensitive legal content
verifiziert: YYYY-MM-DD   # optional; date of the last passed verification pass (see section Verification Pass)
---
```

### Optional Legal Fields

Only on pages with a legal dimension. They make norms and decisions machine-queryable (extending the `quellen:` mechanism with the legal dimension).

```yaml
normen:            # machine-readable norm references, one per line
  - "DSGVO Art. 6 Abs. 1 lit. f"
  - "EU AI Act Art. 10 Abs. 5"
urteile:           # court decisions, ECLI preferred, otherwise citation
  - "ECLI:DE:BVerfG:1983:rs19831215.1bvr020983"
  - "BVerfGE 65, 1"
rechtsgebiet:      # legal-area classification
  - Datenschutzrecht
  - KI-Recht
rang:              # only on norm-node / leading-decision pages: 1–6 (see legal hierarchy)
normtyp:           # norm nodes only: norm function (Hohfeld-granular) — see below (10 values, combinable)
in_kraft:          # norm nodes only: date of entry into force (formal start of validity), YYYY-MM-DD
wirksam_ab:        # norm nodes only: date of applicability/efficacy (start of legal effects), YYYY-MM-DD
ecli:              # only on leading-decision pages: ECLI identifier
bindungswirkung:   # leading decisions only: Gesetzeskraft | faktisch (see below)
resource:          # optional: stable URI of the underlying legal asset (ELI/ECLI/DOI)
```

**Normalization:** Write norm strings uniformly as `<Law> Art./§ <N> Abs. <N> lit. <x>` (law first), so that backlinks and queries do not fragment. Never invent ECLI values — only verified identifiers; otherwise keep just the citation.

**`resource:` (stable asset URI, OKF recommended field).** Points to the page's machine-readable primary source. Conventions:
- **Norm nodes:** ELI URI — EU law via `http://data.europa.eu/eli/…` (e.g. DSGVO: `http://data.europa.eu/eli/reg/2016/679/oj`), German federal law via `https://recht.bund.de/eli/…`.
- **Leading-decision pages:** ECLI resolver — CJEU/EU via EUR-Lex (`https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=ecli:<ECLI>`), German courts via `https://www.rechtsprechung-im-internet.de` or the ECLI resolver.
- **Source/concept pages:** DOI (`https://doi.org/…`) or Zotero select link.
- Set URIs only when verified (no invention, by analogy to the ECLI rule).

**`normtyp:` (norm function, Hohfeld-granular).** Classifies *which legal position* a norm establishes — fully aligned with the LKIF-Core ontology (`norm` module: deontics + Hohfeld + expression). Controlled vocabulary (values kept in German for consistency with the other schema fields):

*Deontic modality:*
- **Gebot** — commands an action (LKIF `Obligation`/`Obliged`), e.g. DSGVO Art. 5.
- **Verbot** — prohibits a behaviour (LKIF `Prohibition`/`Disallowed`), e.g. EU AI Act Art. 5.
- **Erlaubnis** — permits/justifies a behaviour (LKIF `Permission`/`Allowed`), e.g. DSGVO Art. 6.

*Hohfeldian legal positions:*
- **Anspruchsnorm** — subjective right with a correlative duty (claim; LKIF `Right`/`Obligative_Right`/`Liability_Right`), e.g. DSGVO Art. 15, 17, 82.
- **Freiheitsrecht** — liberty/defensive position (privilege/liberty; LKIF `Liberty_Right`/`Permissive_Right`), e.g. GG Art. 5, GRCh Art. 11.
- **Kompetenznorm** — public-law empowerment/competence (power; LKIF `Hohfeldian_Power`/`Enabling_`/`Declarative_`/`Action_Power`), e.g. GG Art. 70, DSGVO Art. 83.
- **Gestaltungsrecht** — unilateral private-law power to alter legal relations (potestative; LKIF `Potestative_Right`), e.g. termination, revocation, avoidance.
- **Immunität** — protection against another's legal power / sectoral exemption (LKIF `Immunity`/`Exclusionary_Right`), e.g. parliamentary indemnity (Art. 46 GG), media privilege.

*Function norms:*
- **Definitionsnorm** — legal definition (LKIF `Definitional_Expression`), e.g. DSGVO Art. 4.
- **Qualifikationsnorm** — legal classification/status assignment (LKIF `Qualificatory_Expression`), e.g. high-risk classification EU AI Act Art. 6.

Norm-node pages only. **Combinable as a list** (e.g. `[Verbot, Erlaubnis]`; a fundamental right `[Freiheitsrecht, Gebot]` = defensive right + protective duty). Sanction/fine norms are recorded as `Kompetenznorm` (empowerment to sanction). Grep-able for `query wiki`.

**`in_kraft:` / `wirksam_ab:` (entry into force vs. applicability).** The LKIF `time-modification` module separates `In_Force_Interval` (formal start of validity) from `Efficacy_Interval` (actual start of legal effects). The two often diverge: the DSGVO was *in force* from 24.05.2016 but only *applicable* from 25.05.2018. `in_kraft:` = entry into force, `wirksam_ab:` = applicability/efficacy. Set only when the dates diverge or are legally relevant; when they coincide, `in_kraft:` suffices (see section "Validity: Entry into Force vs. Efficacy").

**`bindungswirkung:` (binding force of leading decisions).** LKIF distinguishes `Mandatory_Precedent` from `Persuasive_Precedent`. For the German context: **Gesetzeskraft** = formal binding force (BVerfG decisions under § 31 Abs. 1 BVerfGG, partly with statutory force under § 31 Abs. 2 BVerfGG); **faktisch** = no formal binding force but de facto guiding effect (other high-court decisions, CJEU interpretation in the national context). Leading-decision pages only. The value is independent of `rang:` — which follows the norm, not the binding force of the judgment.

## Page Types

### Concept Page
- Naming scheme: `[term].md` (e.g. `Algorithmische Verantwortung.md`)
- One page per concept/technical term
- `wiki-category: konzept`

### Entity Page
- Naming scheme: `[name].md` (e.g. `EU AI Act.md`, `Balkin Jack.md`)
- For: persons (last name first name), laws/regulations (official abbreviation), institutions
- `wiki-category: entitaet`

### Norm-Node Page
- A special form of the entity page for a single key norm (article/section)
- Naming scheme: `[Law] [Norm].md` (e.g. `DSGVO Art. 6.md`, `MStV § 93.md`)
- `wiki-category: entitaet`, plus `rang:` (1–6) set; optionally `normtyp:`, `in_kraft:`/`wirksam_ab:`
- Structure: Definition · Paragraphs/elements of the offence (with wikilinks to concept pages) · Leading decisions · Relationship to other norms
- Purpose: anchor node — concept pages link here; backlinks replace the SPARQL query of the KG approach
- Distinction from the law entity: `DSGVO.md` describes the regulation as a whole; `DSGVO Art. 6.md` is the granular norm node and links to the law page

### Leading-Decision Page
- A special form of the entity page for a landmark decision
- Naming scheme: `[short label].md` (e.g. `BVerfGE 65,1 (Volkszählungsurteil).md`)
- `wiki-category: entitaet`, plus `rang:`, `ecli:` (where verified and available), `rechtsstand:`; optionally `bindungswirkung:`
- Structure: Holding · Supporting reasons · Reference to norms (wikilinks) · Successor/predecessor decisions
- Purpose: anchor node for case law; links norm nodes with concept pages

### Synthesis Page
- Naming scheme: `Synthese - [topic].md` (e.g. `Synthese - Plattformregulierung.md`)
- Cross-topic consolidation of several sources
- `wiki-category: synthese`

## Page Template

```markdown
---
type: wiki-page
wiki-category: [konzept|entitaet|synthese]
thema: [Topic]
quellen: ["@citekey"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# [Title]

## Definition / Overview

## Core Aspects

## References & Controversies

## Related Concepts
[[Wikilink1]] · [[Wikilink2]]

## Sources
[[@citekey1]], [[@citekey2]]
```

## Depth Standard

Wiki pages should be academically substantial — not merely summarizing, but classifying, differentiating, and interconnecting.

**Definition / Overview:** At least one complete paragraph (4–6 sentences). Systematic classification (legal area, norm level), origin/history of the concept, distinction from related terms.

**Core Aspects:** At least 3 named subsections of 3–5 sentences each. Concrete norm references (articles, sections), elements of the offence, legal consequences. Every central statement substantiated — either with a `[!recht]` callout (for legal norms/judgments) or with a source reference.

**References & Controversies:** At least 2 concrete points of discussion or questions of distinction. Where relevant: opposing views, open legal questions, reform debates, tensions with other legal areas.

**Related Concepts:** At least 3 wikilinks, at least one of them cross-topic (into other wiki folders).

## Legal-Hierarchy Annotation

Statements on wiki pages that rest directly on a legal norm or court decision are annotated with an Obsidian callout. The callout sits *below* the respective statement in the running text.

### Format

```
> [!recht] ⚖️ Rang [N] ([Normkategorie]) · [Gericht/Norm] → [Referenz]
> [Optional short comment on bindingness or classification]
```

Examples:

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSA Art. 33 Abs. 1
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 17.02.2023.

> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 65, 1 → Art. 2 Abs. 1 GG
> Volkszählungsurteil; Grundlage des Rechts auf informationelle Selbstbestimmung.

> [!recht] ⚖️ Rang 5 (Bundesgesetz) · BGH I ZR 69/08 → UrhG § 97
```

### Legal Hierarchy (6 ranks, norm-centered)

| Rank | Norm category | Example norms | Decisions at this rank |
|---|---|---|---|
| 1 | EU primary law | AEUV, EUV, GRC | CJEU on fundamental freedoms and GRC |
| 2 | EU secondary law — regulation | DSGVO, DSA, DMA, AI Act | CJEU, BVerfG, BGH on these regulations |
| 3 | EU secondary law — directive (transposed) | AVMD-RL, NIS2-RL | CJEU, BGH on transposed directives |
| 4 | German constitutional law | GG, state constitutions | BVerfG, VerfGH on GG norms |
| 5 | Federal statute / state treaty | TKG, TTDSG, UrhG, MStV | BGH, BVerwG, OLG on federal statutes |
| 6 | State statute / ordinance | LPG, LRfG, state ordinance | OVG, VGH, LG on state law |

The rank follows the norm, not the court. A BVerfG judgment on Art. 5 GG is rank 4; a CJEU judgment on the DSGVO is rank 2.

> **Note:** This hierarchy is EU/German-specific. For other jurisdictions, the norm categories and ranks must be adapted accordingly.

### When to Annotate

- ✅ For statements that can be traced directly to a concrete norm or decision
- ✅ For definitions or elements of the offence taken from statutes
- ❌ Not for general summaries or scholarly opinions
- ❌ Not for every statement on a page — only for legally grounded core statements

## Evidence and Locator Granularity

The `quellen:` field substantiates a page as a whole. That is not enough to check an individual statement. Every core statement therefore additionally carries its own **evidence locator**: citekey plus pinpoint reference. This is also what keeps the verification pass cheap, because what gets checked is a passage, not an entire PDF. The model for this is agentic code extraction, where every generated tool carries a reference to the specific line of code it was derived from.

### Legal statements: `Beleg:` line inside the `[!recht]` callout

The `[!recht]` callout gains an optional but desirable `Beleg:` line ("Beleg" = evidence). It sits directly below the title line, before the short comment:

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6 Abs. 1 lit. f
> Beleg: @citekey S. 142 Rn. 18
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

If the statement rests directly on the norm text itself rather than on scholarly literature, the `Beleg:` line is omitted: the norm reference in the title line *is* the locator. It is mandatory wherever an **interpretation, an account of a controversy, or a figure** comes from a secondary source.

### Non-legal core statements: inline locator

Statements without a norm or decision reference that nevertheless go back to a source carry the locator in parentheses at the end of the sentence:

```markdown
The effect is measurable in the data from 2023 onwards and mainly affects labour-market entrants (@citekey, S. 14).
```

Format: `(@citekey, S. N)` or `(@citekey, Abschn. N)`, or `(@citekey)` when the source has no pagination (website, preprint without page numbers). The form is grep-able via `\(@[a-z]`.

### Failed statements: the `[!unbelegt]` callout

Statements that do not pass the verification pass and could not be corrected are **flagged rather than silently kept**. The callout keeps its German name `[!unbelegt]` ("unsubstantiated") so that both language versions produce identical markup:

```
> [!unbelegt] ⚠️ Not substantiated — checked YYYY-MM-DD
> The cited source @citekey does not carry this statement at the passage given.
> Either correct the locator, supply a source, or remove the statement.
```

(Title line: "not substantiated — checked YYYY-MM-DD"; body: the cited source does not carry this statement at the given place; either correct the locator, supply a source, or remove the statement.)

The callout is an open finding, not a permanent state: lint reports `[!unbelegt]` findings older than 30 days as a warning.

## Verification Pass (Ingest Step 6)

Lint checks **structure**: dead links, index consistency, frontmatter drift. It does not check whether a sentence is actually carried by its source. The verification pass closes exactly this gap. The pattern comes from agentic code extraction: whatever cannot be checked against the source is not silently adopted, but flagged with a finding or removed.

Two design decisions carry the procedure and should survive any adaptation. **First, a fresh sub-agent without the writing context performs the check.** Whoever wrote a text reads it against the source as confirmation rather than as verification; that separation is the core of the method, not a formality. **Second, what fails is excluded rather than kept.** A statement its source does not carry is either removed or visibly flagged, and it is never left standing without comment.

Provenance and evidence for both: Miao et al., *Reimagining research papers as interactive and reliable AI agents*, Nature 2026, DOI [10.1038/s41586-026-11044-y](https://doi.org/10.1038/s41586-026-11044-y); reference implementation [jmiao24/Paper2Agent](https://github.com/jmiao24/Paper2Agent). In detail in `docs/en/07-verification.md`.

### Principle: supportedness, not correctness

Legal statements have no executable test standard, because interpretation is contestable. The verifier therefore establishes **only** whether the cited source passage carries the statement. It does not decide whether the statement is correct, and it does not replace substantive review. Confusing the two produces false confidence.

### Procedure

The pass runs **automatically as step 6 of every ingest** and additionally on the trigger `verify wiki [page|topic|last ingest]`.

1. **A fresh subagent.** The check is performed by a subagent *without* the writing context. Whoever wrote the text cannot review it impartially. That is the core of the procedure, not a formality.
2. **Input:** page path, all locators on the page (`Beleg:` lines, inline locators, `quellen:`) plus `normen:`/`urteile:`/`ecli:`.
3. **Source retrieval:** look up passages via Zotero MCP (`get_content` targeted, `search_fulltext` for the locator position, `get_annotations`).
4. **Classification per statement:**

| Finding | Meaning | Consequence |
|---|---|---|
| `belegt` (substantiated) | the source passage carries the statement | nothing |
| `nicht belegt` (not substantiated) | the passage exists but does not carry the statement | max. 2 repair attempts (correct the locator, look for a better passage), then `[!unbelegt]` |
| `widersprochen` (contradicted) | the source says something different | correct the statement in the same run, note the correction in `log.md` |
| `nicht prüfbar` (not checkable) | no full text available | the page keeps the statement, `verifiziert:` is **not** set, `log.md` note `[kein Volltext]` |

5. **Hard-fail class, immediate removal without repair attempts:**
   - invented or untraceable **ECLI**
   - invented **norm designation** (the article or section does not exist in the cited law)
   - invented **citation** (volume, page, or marginal number not verifiable)
   - invented **citekey** (not present in Zotero)

   These four cases are removed, not flagged, and recorded as `Hard-Fail` in the `log.md` entry.

   **When removing a source, check the running text as well, not just `quellen:`.** Striking a source that turned out not to exist from the frontmatter and the source list is not enough: the attributions live in the prose as author-year mentions and survive the cleanup. In practice this produced four hard fails across two pages that stated a few lines further down that the source does not exist. The search therefore has to match the **surname**, not the citekey.

   **Before removing anything, counter-check the finding against the higher-ranking source:** the publication itself takes precedence over reference-manager metadata, and the official norm text over the secondary literature citing it. A reported hard fail resting on derived data can hit correct information. If a doubtful statement cannot be settled, remove it rather than swapping it for a second unverified one. The schema rule "never invent an ECLI" thereby stops being a mere instruction and becomes a check. Instructions enforce nothing; checks do.

6. **Completion:** if the page passes without an open finding, `verifiziert: YYYY-MM-DD` is set. If an `[!unbelegt]` callout remains, the field is **not** set.

### Grandfathering and lifting on touch

Introducing the verification pass into a wiki that already exists leaves you with a legacy stock that never went through it. Checking that stock retroactively is expensive: setting a locator presupposes having read the source, which makes it a re-ingest of every page.

The workable rule has two halves, and it only works as a pair:

**Grandfathering.** Pages whose `updated:` predates `[INTRODUCTION-DATE]` are not actively brought up to standard. No campaign. This is not negligence but accurate labelling: if `verifiziert:` is absent the page counts as unverified — which is exactly what it is.

**Lifting on touch.** As soon as a legacy page is changed substantively for any other reason — ingest, correction, norm supersession, addition — it loses grandfathered status and must be lifted within that same edit: set locators, run the verification pass, set `verifiziert:`. **What governs is the size of the page, not the size of the change.** Correct one sentence and you lift the page; if you are not prepared to lift it, do not change it.

The stock then converges through ordinary work rather than through a special effort, and in the right order: what gets touched most often gets verified first.

Two boundaries, without which the rule collapses:

- **If lifting exceeds the scope of the edit** — very large legacy pages with many sources — set `updated:` (it is a fact), leave `verifiziert:` **open**, and record in `log.md` which part was checked and which was not. A partially checked state must never be presented as checked: `verifiziert:` refers to the whole page, not to the latest change.
- **Purely mechanical runs do not trigger lifting.** Fixing a citekey, adding a `resource:` URI or renaming a link touches no statement and does not trigger the duty. Otherwise a single search-and-replace across 40 files would force 40 verification passes.

### Entry in `log.md`

```
- **Verification** [[Page name]] — 14 statements: 12 substantiated, 1 corrected, 1 not substantiated, 0 hard fail
```

## Typed Wikilinks (Relation Vocabulary)

Legal relationships between nodes are expressed in the running text with a controlled relation verb placed before the wikilink. Human-readable, grep-able for `query wiki`. Adopts the typed edges of the KG approach (setzt_um, ändert, konkretisiert) Obsidian-natively, without schema overhead.

Controlled vocabulary:

- **setzt um** — directive → transposition statute
- **ändert** / **hebt auf** — amendment/repeal
- **verdrängt** — application priority (lex superior/posterior)
- **konkretisiert** — case law refines an older decision/norm
- **definiert** — norm defines a term
- **wendet an** — decision applies a norm
- **setzt aus** — temporary suspension of efficacy (LKIF `Suspension`)
- **erklärt für nichtig** — judicial annulment, ex tunc (LKIF `Annulment`; ≠ legislative repeal "hebt auf")
- **wirkt nach** — superseded norm remains applicable to old cases (ultra-activity, LKIF `Ultractivity`)
- **wirkt zurück** — norm retroactively covers already-concluded facts (LKIF `Retroactivity`)
- **zitiert** — general reference

Example:

> Der DSA **verdrängt** [[NetzDG]] §§ 2, 3 (seit 17.02.2024); der Gesetzgeber **hebt** die §§ 2 bis 3f mit Wirkung zum 14.05.2024 **auf**; das österr. KoPl-G-Analogon ist europarechtswidrig laut [[EuGH C-376-22 (KoPl-G)]].

## Legal Currency and Norm Supersession

### Basic Rule

The wiki always reflects the **current legal status** — it is not a historical archive. When a newly ingested source replaces, modifies, or supersedes a norm or decision that is already documented, the affected wiki pages are updated within the same ingest run. Newer legal status overwrites older content; outdated callouts are flagged accordingly.

### Four Supersession Types

| Type | Trigger | Example | Consequence |
|---|---|---|---|
| **Full replacement** | New norm replaces the old one entirely (repeal clause) | MStV (2020) replaces RStV | Extend callout with note: `→ aufgehoben durch [X] seit [Datum]` |
| **Partial supersession** | EU regulation with application priority (lex posterior/superior) | DSA Art. 15, 16 supersede NetzDG § 2, § 3 Abs. 2 | Mark superseded part in callout; document the remaining scope of application |
| **Amendment** | Amended version of an existing norm | AVMD-RL 2018/1808 amends AVMD-RL 2010/13/EU | New version is authoritative; carry version/date in callout (`i.d.F. [Jahr]`) |
| **Change in case law** | Newer judgment clarifies, refines, or revises an older decision | BVerfGE 158, 389 refines BVerfGE 149, 222 | Cite the newer judgment primarily; annotate the older judgment with a context note pointing to the successor decision |

### Validity: Entry into Force vs. Efficacy

The LKIF `time-modification` module separates two timelines that pages on time-sensitive norms should keep clean:

- **Entry into force** (`In_Force`, field `in_kraft:`) — from when the norm formally belongs to the legal order.
- **Efficacy/applicability** (`Efficacy`, field `wirksam_ab:`) — from when it actually produces legal effects.

If the two diverge, carry both dates in the `[!recht]` callout (example below). For superseded norms it matters that entry into force can end while efficacy persists for old cases → **ultra-activity** (see below).

### Further Modification Types

Beyond the four supersession types, the LKIF `time-modification` module recognizes temporal modifications that are not a replacement but change the validity status. Express them with the relation vocabulary and flag them in the callout:

| Type | LKIF class | Trigger | Consequence |
|---|---|---|---|
| **Suspension** | `Suspension` | Efficacy temporarily suspended (court order, moratorium) | Relation `setzt aus`; callout `⏸️ ausgesetzt [period/reason]`; page stays valid, status flagged |
| **Annulment** | `Annulment` | Court declares a norm void (ex tunc) — ≠ legislative repeal | Relation `erklärt für nichtig`; callout with court/ECLI; distinguish from "aufgehoben" (by the legislator) |
| **Ultra-activity** | `Ultractivity` | Superseded norm remains applicable to old cases (transitional law) | Relation `wirkt nach`; callout: superseded from [date], **but** applicable to facts before [date] |
| **Retroactivity** | `Retroactivity` | Norm retroactively covers already-concluded facts | Relation `wirkt zurück`; callout `wirkt zurück auf [date]`; note constitutional ban on retroactivity where relevant |

### Warning: supersession is often mistaken for the final state

The most common failure when maintaining this section is not missing a supersession, but **stopping at the first event**. A norm can be affected several times in sequence, and recording only the first stage eventually produces a false statement.

The teaching case is the German NetzDG:

1. From 2024-02-17 the directly applicable DSA superseded §§ 2, 3 NetzDG by virtue of application priority. The provisions remained in existence and merely stepped back. § 3a (reporting duty to the Federal Criminal Police Office) had no DSA equivalent and therefore counted as a **remaining scope of application**.
2. Only months later the legislator **formally repealed** §§ 2 to 3f, including § 3a (Art. 29 no. 2 of the Act implementing Regulation (EU) 2022/2065 of 2024-05-06, Federal Law Gazette 2024 I no. 149; in force 2024-05-14).

A wiki that captured only step 1 will then assert that § 3a remains independently applicable. That is wrong, yet it sounds plausible and is well sourced, because the literature up to 2024 said exactly that.

Two practical consequences:

- **Supersession is a state, not a conclusion.** Wherever `verdrängt` is set, put the topic on a review list; in such constellations the legislator often follows up.
- **A remaining scope of application is the most fragile statement in the whole vocabulary.** It asserts that something survived, and that is precisely what changes fastest. Such statements need a `rechtsstand:` date and a cross-check against the official consolidated text, not only against secondary literature.

### Ingest Obligation: Norm-Supersession Check

On every ingest of a legal source (statute, regulation, judgment, commentary) **before writing**:

1. **Identification** — Which older norms or decisions are replaced, amended, or superseded by the new source? Watch for signal phrasings in the source text: "ersetzt", "aufgehoben", "tritt an die Stelle von", "verdrängt", "Anwendungsvorrang", "gilt nicht mehr", "überholt durch".
2. **Wiki scan** — Check `index.md` and the affected wiki pages for callouts and running-text passages that cite the superseded norm/decision.
3. **Update** — Update the affected pages within the same ingest run (flag callouts, adjust running text for substantive changes, set `updated` and `rechtsstand` dates).
4. **Closing check** — The review is complete only once a search across the **entire** corpus for the superseded statement returns zero hits, not once the obviously affected pages have been edited. In practice a repealed provision survived a correction that had been reported as finished in six further places, one of them inside a `[!recht]` callout, that is, in the very element that asserts a norm is in force. Build the search terms from the **old** statement, not from the new one. Exclude the log (`log.md`) from such a run: it records what was true at the time.

### Callout Flagging of Superseded Norms

Fully repealed or replaced norm:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · NetzDG § 2 i.d.F. 2021
> ⚠️ Verdrängt durch DSA Art. 15 Abs. 1 mit Wirkung ab 17.02.2024.
```

Partially superseded norm with a remaining scope of application:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · NetzDG § 3 Abs. 2 i.d.F. 2021
> Weitgehend verdrängt durch DSA Art. 16 Abs. 6 (seit 17.02.2024).
> Restanwendungsbereich: § 5 NetzDG (inländischer Zustellungsbevollmächtigter) bleibt eigenständig anwendbar.
```

Refined or revised court decision:

```
> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 149, 222 (Rundfunkbeitrag, 2018)
> Durch BVerfGE 158, 389 (Sachsen-Anhalt, 2021) in der Frage der Mitverantwortungspflicht der Länder konkretisiert.
```

In force but not yet applicable (validity ≠ efficacy):

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · EU AI Act Art. 5
> In Kraft seit 01.08.2024; Verbote anwendbar ab 02.02.2025.
```

Norm declared void (≠ legislative repeal):

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · [Norm] i.d.F. [Jahr]
> ⚠️ Vom BVerfG für nichtig erklärt (ex tunc) durch [ECLI/Fundstelle].
```

Superseded norm with ultra-activity for old cases:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · [Norm] i.d.F. [Jahr]
> Verdrängt durch [X] ab [Datum]; wirkt nach auf vor [Datum] abgeschlossene Sachverhalte.
```

### rechtsstand Frontmatter Field

The optional field `rechtsstand: YYYY-MM-DD` marks the date up to which the legal status of a page has been fully checked. It is set or updated when a full norm-supersession check has been carried out for this page during an ingest. If the field is absent, the page is considered unchecked with respect to currency.

The field is **not** set on every content addition — only after an explicit currency check. It has no effect on `updated`, which is advanced on every content change.

## Thematic Folders (Wiki Area)

To be defined by the user — one folder per subject area under `[WIKI-FOLDER]/`. Example notation (replace with your own topics):

- `[WIKI-FOLDER]/[Topic 1]/`
- `[WIKI-FOLDER]/[Topic 2]/`
- `[WIKI-FOLDER]/[Topic 3]/` …

Your own non-wiki folders (e.g. `Persönlich/`, `Werkzeuge/`) remain excluded.

## Workflow Pages (`type: wiki-workflow`)

Wiki pages record knowledge, not procedures. Procedural steps (how a norm review proceeds, in which order things are checked) otherwise lie scattered as prose across this schema, remain implicit, and only take effect during ingest. Workflow pages make them explicit and callable.

- **Location:** `[WIKI-FOLDER]/Workflows/`, an **infrastructure folder**, not a topic folder. It is not covered by thematic evaluations or by the depth standard.
- **Naming scheme:** `Workflow - [procedure].md`
- **Frontmatter:** `type: wiki-workflow`, plus `thema:`, `created:`, `updated:`. No `wiki-category:` (that is reserved for wiki pages), no mandatory `quellen:`.
- **Trigger:** `workflow: [name]`. The agent reads the page and works through it step by step.
- **Structure:** `Purpose` · `Steps` (numbered, each with a checking question) · `Abort criteria` · `Related nodes` (wikilinks to norm nodes and concept pages).

Workflow pages are **not** wiki pages within the meaning of the depth standard and are not captured by any lint check that filters on `type: wiki-page`. They are also the place where other skills (teaching material, expert opinions, case studies) pick up procedural knowledge instead of reconstructing it each time.

A complete example is in `examples/Workflow - Norm Review.md`.

### Which procedures deserve their own page

Not every legal test belongs here. The workable criterion is: **does the procedure produce an artefact that this schema defines?**

- **Yes** for wiki operating procedures (verification pass, supersession check) and for build instructions for a page type. Norm review, for instance, fills exactly the four sections prescribed for norm-node pages.
- **No** for general legal methodology without a counterpart in the corpus. A fundamental-rights test (scope, interference, justification) is doctrinally sound but produces no page type. Its consumers are assessment, teaching and case-study skills. As long as those do not consult the page, it is dead weight, and the *workflow drift* lint check flags it rightly.

### Relation to this schema

In a live installation it is advisable to make the **workflow page the authoritative version of the procedure** and have this schema merely point to it at the relevant place. The schema then retains what frontmatter and lint refer to (finding classes, typologies, callout formats), the workflow retains the steps. Otherwise the same procedure lives in two places and drifts apart.

This template deliberately keeps both procedures in full here, because `examples/` is not necessarily installed when the framework is adopted and the schema must remain readable on its own.

## Zotero MCP Tools (Reference)

For ingest, only the Zotero MCP server is used (native MCP-over-HTTP endpoint `http://127.0.0.1:23120/mcp`, Zotero plugin `zotero-mcp-plugin` v1.5.0). The tools are callable directly as `mcp__zotero__*`. Most read tools optionally accept `libraryID` (default: user library) and `mode` (`minimal`|`preview`|`standard`|`complete`) to control results/content.

| Tool | Use in ingest |
|---|---|
| `search_library` | Find item by @citekey, DOI/ISBN, or topic; returns `itemKey` (params: `q`, `title`, `yearRange`, `fulltext`, `itemType`, `sort`, `mode`) |
| `get_item_details` | Full metadata, attachment list, tags, notes (params: `itemKey`, `mode`) |
| `get_item_abstract` | Abstract/summary only (params: `itemKey`, `format`) |
| `get_content` | Full text from PDF/attachment/notes (params: `itemKey` **or** `attachmentKey`, `mode`; entire document = `mode: "complete"`; **no `page` parameter**) |
| `search_fulltext` | Full-text search across all documents; returns passages with context |
| `get_annotations` | Annotations/notes of an item (param: `itemKey` **or** `annotationId` **or** `annotationIds[]`; filters `colors`, `tags`, `types`) |
| `search_annotations` | Annotation search across the entire library (at least one of `q`, `colors`, `tags`) |
| `get_collections` | List all collections (params: `mode`, `recursive`, `parentCollection`) |
| `get_collection_items` | All items of a collection (param: `collectionKey`) |
| `get_subcollections` | Subcollections of a collection (params: `collectionKey`, `recursive`) |

**Fallback to the local API (port 23119):** Only when the MCP server does not respond (Zotero plugin not active). Then proceed as before via HTTP calls through Python/curl.

## Ingest Decomposition (Sub-agents with JSON Handoff)

A linear ingest loads full text, index, and writing context into a single context window. That is exactly where the token-budget abort protocol comes from. The alternative is decomposition: an orchestrator dispatches specialized sub-agents that exchange data **exclusively via standardized JSON reports**, never via shared context. The monolithic variant performs measurably worse even in a large context window (ablation in Miao et al., *Reimagining research papers as interactive and reliable AI agents*, Nature 2026, DOI [10.1038/s41586-026-11044-y](https://doi.org/10.1038/s41586-026-11044-y)).

### When to apply it

Not on every ingest, because the overhead only pays off from:

- a bulk ingest with **more than 3 sources**, or
- a single source with **more than ~50 pages** of full text (monographs, commentaries, edited volumes).

Below that, the classic linear workflow remains correct.

### Four roles

| Role | Input | Output | Holds in context |
|---|---|---|---|
| **Extractor** | Zotero item | `extraktion.json` | only the single source |
| **Collision checker** | `extraktion.json` + `index.md` | `kollision.json` | only index and JSON |
| **Writer** (parallel, one per page) | one entry from `kollision.json` | `schreibbericht.json` | only its own page |
| **Verifier** (fresh) | page and locators | `verifikat.json` | only passages |

The orchestrator holds **only the JSONs**, never the PDFs. This turns the limit of roughly 15 pages per ingest from a context question into a throughput question.

### Storage

`/tmp/wiki-ingest/<citekey>/`, deliberately outside the vault so that intermediate states do not contaminate the knowledge base. After a successful run the folder can be discarded; on an abort it is the resumption point (referenced in the `log.md` entry `[unterbrochen …]`).

### Schemas

```jsonc
// extraktion.json
{
  "citekey": "citekey2024",
  "titel": "...",
  "volltext_status": "complete | partial | kein_volltext",
  "konzepte":   [{"name": "...", "kurz": "...", "belege": [{"locator": "S. 142", "zitat": "..."}]}],
  "entitaeten": [{"name": "...", "art": "person | gesetz | institution"}],
  "normen":     ["DSGVO Art. 6 Abs. 1 lit. f"],
  "urteile":    ["EuGH C-300-21 (Österreichische Post)"],
  "themen":     ["[Topic 1]"]
}

// kollision.json
{
  "neu":               [{"titel": "...", "pfad": "[Topic 1]/....md", "kategorie": "konzept"}],
  "update":            [{"pfad": "[Topic 2]/....md", "aenderung": "Abschnitt Kernaspekte ergaenzen"}],
  "normknoten_faellig":[{"norm": "MStV § 93", "zitiert_in": 3}]
}

// schreibbericht.json
{"pfad": "...", "status": "erstellt | aktualisiert | uebersprungen",
 "wikilinks": 7, "callouts": 2, "locatoren": 5}

// verifikat.json
{"pfad": "...", "geprueft": 14, "belegt": 12,
 "nicht_belegt": [{"aussage": "...", "locator": "S. 88"}],
 "widersprochen": [], "hard_fail": []}
```

The JSON keys stay in German, mirroring the frontmatter field names.

## Ingest Checklist

Before writing:
- [ ] `[WIKI-FOLDER]/index.md` read?
- [ ] Affected thematic folders identified?
- [ ] Check: is there already a page for this concept/entity?
- [ ] **Full-text check:** Retrieve attachments via Zotero MCP `get_item_details` (returns `attachments` field with `contentType`): `application/pdf` → PDF via `get_content`, `text/html` → HTML snapshot via the Read tool (`~/Zotero/storage/[ATTKEY]/`)
- [ ] **Norm-supersession check (legal sources):** Does the source contain norms or decisions that replace, amend, or supersede already documented wiki content? → Identify affected wiki pages via `index.md`; the update happens in the "write/update pages" step (see section *Legal Currency and Norm Supersession*)

Reading sources (standard — always before writing):
- [ ] Metadata + abstract read via Zotero MCP `get_item_details` (or `get_item_abstract`)?
- [ ] **PDF present?** (`contentType: application/pdf`) → Retrieve full text via `get_content` (MCP):
  - Articles/chapters: `get_content(itemKey, mode: "complete")` = entire document
  - Books/long documents: probe with `mode: "standard"`/`"preview"`, then `mode: "complete"` if needed (no per-page `page` parameter anymore); alternatively `search_fulltext` for targeted passages
  - Evaluate annotations via `get_annotations` (MCP)
- [ ] **No PDF, but HTML snapshot present?** (`contentType: text/html`) → Read full text with the Read tool (`~/Zotero/storage/[ATTKEY]/`):
  - Read the HTML file in full; ignore HTML tags when evaluating
  - Treat like a PDF: fully for articles, selectively for longer documents
  - Evaluate annotations via `get_annotations` (MCP)
- [ ] Neither PDF nor HTML? → Work from metadata, abstract, and your own expertise; note in log.md: `[kein Volltext]`

While writing:
- [ ] Content based on the actual source text, not just on knowledge of the title
- [ ] Concrete page references or chapter references built in where possible
- [ ] Frontmatter complete (all required fields)?
- [ ] Cross-links set with [[Wikilinks]]?
- [ ] Existing atomic notes in the same folder checked for linkability?
- [ ] `updated` date updated?
- [ ] **Locator set?** Every statement taken from a secondary source carries a `Beleg:` line (legal) or an inline locator `(@citekey, S. N)` (all others), see section *Evidence and Locator Granularity*

After writing:
- [ ] **Verification pass (step 6) carried out?** Fresh subagent, finding classes, hard-fail check, see section *Verification Pass*
- [ ] `verifiziert:` date set (only if no open `[!unbelegt]` finding remains)?
- [ ] `[WIKI-FOLDER]/index.md` updated?
- [ ] `[WIKI-FOLDER]/log.md` entry appended? (incl. `[kein PDF]` if applicable)
- [ ] New folder created? → Then also update CLAUDE.md and the wiki-schema.md thematic-folder list

## Lint Specification

`lint wiki` performs a full integrity audit. Findings are classified by severity.

### Severities

| Severity | Meaning | Examples |
|---|---|---|
| **Error** | Structurally broken, must be fixed | Broken wikilinks, index entries without a file |
| **Warning** | Quality issue, should be fixed | Orphan pages, stale claims, missing pages |
| **Info** | Room for improvement | Missing cross-links, data gaps |

### Checks

**Errors:**
- [ ] **Broken wikilinks** — `[[Page]]` references to non-existent files. **When parsing, isolate the real link target** before checking against files: strip the alias after `|` *and* after escaped `\|` (mandatory escaping in Markdown tables!), strip `#` jump anchors, reduce the path to the last segment. Otherwise false positives arise for table links like `[[Antrag X\|Alias]]` and anchor links like `[[Seite#Abschnitt]]`. **Mind Unicode normalisation:** macOS stores filenames on APFS/iCloud in **NFD** (`ü` = `u` + combining mark), while Markdown files contain **NFC**. A naive string comparison therefore reports *every* page with an umlaut in its filename as broken. Normalise both sides with `unicodedata.normalize("NFC", …)` before comparing. Likewise strip a trailing `.md` from the link target (`[[folder/Page.md]]`), which otherwise produces the same false positive. **Exempt source wikilinks:** links of the form `[[@citekey]]` in the *Sources* section point to the Zotero entry and **not** to a vault file. There are deliberately no `@citekey.md` files. Since virtually every wiki page carries such a link, a check without this exemption produces more false positives than the corpus has pages. Skip link targets starting with `@`.
- [ ] **Index consistency** — Entries in `index.md` without a corresponding file (and vice versa: files with `type: wiki-page` that are not listed in `index.md`)

**Warnings:**
- [ ] **Orphan pages** — Wiki pages with `type: wiki-page` that are not linked by any other page
- [ ] **Stale claims** — Pages with `[!recht]` callouts on norms that, according to newer sources (recognizable from `log.md`), have been superseded or changed, without the page having been updated
- [ ] **Missing pages** — Terms referenced in several pages via `[[Wikilink]]` but lacking their own file
- [ ] **Norm without node** — Norms in `normen:` frontmatter that occur in ≥3 pages but have no dedicated norm-node page
- [ ] **Judgment without node** — Judgments in `urteile:` frontmatter that occur in ≥3 pages but have no dedicated leading-decision page
- [ ] **Frontmatter drift** — Page with a `[!recht]` callout on a norm/decision that is not in the `normen:`/`urteile:` frontmatter
- [ ] **Unverified** — Pages with `type: wiki-page` and a non-empty `quellen:` that carry no `verifiziert:` field and whose `updated:` is later than `[INTRODUCTION-DATE]`. Enter there the date on which you introduced the verification pass; older pages are grandfathered in and are not reported.
- [ ] **Open evidence finding** — Pages with an `[!unbelegt]` callout whose check date is more than 30 days old. An `[!unbelegt]` is an open item, not a permanent state.

**Info:**
- [ ] **Evidence without locator** — Page carries `quellen:` and contains `[!recht]` callouts, none of which has a `Beleg:` line. Not an error (statements resting on the norm text need none), but an indication of unchecked secondary citations.
- [ ] **Workflow drift** — `type: wiki-workflow` pages that are referenced by no wiki page, no skill, and no `AGENTS.md`/`CLAUDE.md`.
- [ ] **Data gaps** — Wiki pages with fewer than 2 sources in the `quellen:` frontmatter (topics with thin coverage)
- [ ] **Missing cross-links** — Pages on the same topic without mutual linking (recognizable by matching `thema:` fields)
- [ ] **Pages without frontmatter** — Files in wiki folders without `type: wiki-page`

### Output Format

```
## Lint result — YYYY-MM-DD

### Errors (N)
- [[Page name]]: broken link to [[NonExistentPage]]

### Warnings (N)
- [[Page name]]: orphan page (no incoming links)
- [[Page name]]: stale claim — NetzDG § 3(2) (superseded by the DSA since 2024-02-17, not flagged)

### Info (N)
- [[Page name]]: only 1 source, topic underrepresented
```

Document findings in `log.md` with the syntax `- **Lint** — N errors, N warnings, N info`.

### Recommended Cadence

After every 10 ingests, or monthly as minimum maintenance.

---

## Benchmark Specification

Lint measures structure. It does not measure **answer quality**, that is, whether the wiki answers a question correctly and whether it properly refuses a question it cannot answer. Without this measurement there is no way to tell whether a schema change (the introduction of `normtyp:`, say) improved anything at all.

- **File:** `[BENCHMARK-LOCATION]/benchmark.md`. `[BENCHMARK-LOCATION]` is a folder **outside** `[WIKI-FOLDER]/`, for example a context or configuration folder of the vault.
- **Trigger:** `bench wiki`
- **Cadence:** after every 10 ingests, together with `lint wiki`

**Store it outside the wiki folder.** The file deliberately does **not** live in `[WIKI-FOLDER]/` but next to it. Reason: `query wiki` searches the entire wiki folder. If the question set were inside it, answering agents would hit the gold answers via grep, and for out-of-scope questions the expected verdict "refusal". The measurement would then no longer capture whether the wiki recognises its own boundary, but whether the agent finds the answer key. This actually happened on the first live run: all four answering agents encountered the file, three disclosed it unprompted, and that run's result is therefore not usable.

### Structure

Two blocks:

1. **Knowledge questions** are questions whose answer demonstrably exists in the wiki. Per entry: `Question` · `Gold answer` · `Evidence page` (wikilink). The gold answers are **derived from the wiki pages**, not formulated from model knowledge.
2. **Out-of-scope questions** are questions on topics the wiki demonstrably does *not* cover. The correct answer is the **refusal** ("There is nothing on this in the wiki."). Check such questions by grep for zero hits before adding them.

The second block is the more important one. A knowledge base that answers gaps with plausible model knowledge is more dangerous than one that stays silent, because the answer looks like substantiated wiki knowledge.

### Execution

Every question is asked via `query wiki`, without the gold answer being in context. Scoring is two-tiered: **substantively correct** (yes/no) and **correctly substantiated** (points to the evidence page). A substantively correct but unsubstantiated answer counts as a partial hit and is reported separately.

### Entry in `log.md`

```
- **Bench** — knowledge 13/15 correct (11 substantiated), out-of-scope 5/5 refused
```

## Naming Conventions

- File names: normal spelling with spaces and capitalization
- Persons: `Nachname Vorname.md` (e.g. `Balkin Jack.md`)
- Laws/regulations: official short label (e.g. `DSGVO.md`, `EU AI Act.md`, `MStV.md`)
- Institutions: most common short form (e.g. `Bundesnetzagentur.md`, `KEF.md`)
- Concepts: main term, with parentheses for disambiguation if needed (e.g. `Verantwortung (KI).md`)

## log.md Syntax

Entry format:

```
## YYYY-MM-DD

- **Ingest** `@citekey` ([Kurztitel])
  → erstellt: [[Seitenname1]], [[Seitenname2]]
  → aktualisiert: [[Seitenname3]]
  → Thema: Thema1, Thema2

- **Bulk-Ingest** ([N] Quellen, Thema: [Thema])
  → [N] neue Seiten, [N] aktualisiert

- **Lint** — [N] Probleme gefunden, [N] behoben

- **Neuer Ordner** `[Thema]/` angelegt
```

Mark interrupted sessions with:
`[unterbrochen nach N Quellen, N ausstehend]`

---

## Non-Wiki Page Types

Besides the wiki pages (`type: wiki-page`), all other `.md` files in `[WIKI-FOLDER]/` also carry a `type` field (OKF requirement, see below). Controlled vocabulary:

- `hub` — topic hub page (file name == folder name, e.g. `KI/KI.md`)
- `quelle` — Zotero/literature source overview (`tags: [literatur]`)
- `notiz` — other notes (atomic thoughts, reference/helper notes without wiki-page status)
- `wiki-workflow` — callable procedure page in `Workflows/` (see section *Workflow Pages*)

These types are **not** wiki pages within the meaning of the depth standard and are not captured by lint/ingest routines that filter on `type: wiki-page`. `Persönlich/` and `Werkzeuge/` remain entirely excluded.

## OKF Compatibility (Google Open Knowledge Format v0.1)

The wiki is deliberately kept largely OKF-compatible (knowledge exchange with third parties/agents).

- **Mandatory rule satisfied:** Every non-reserved `.md` in `[WIKI-FOLDER]/` carries a non-empty `type` field. All other fields (`wiki-category`, `normen`, `urteile`, `rang`, `normtyp`, `in_kraft`, `wirksam_ab`, `bindungswirkung`, `ecli`, `thema`, `quellen`) are OKF-conformant extensions — consumers must tolerate unknown keys.
- **`resource:`** is the OKF recommended field for the asset URI (see Frontmatter Schema above; ELI/ECLI/DOI).
- **Reserved Files:** `index.md` + `log.md` present. Note: OKF provides *no* frontmatter for `index.md` — our `type: wiki-index` is a tolerated deviation. Optionally, `okf_version: 0.1` can be declared in the root `index.md`.
- **Deliberate divergence — links:** We use Obsidian `[[Wikilinks]]` instead of OKF-standard Markdown links (`[Text](/pfad.md)`). OKF tolerates this (links are tolerated as "broken", relation semantics reside in the running text anyway). For a true OKF export, a build pipeline (wikilinks → Markdown links) would be the right approach — not converting the vault.
