---
type: wiki-schema
updated: 2026-06-17
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
ecli:              # only on leading-decision pages: ECLI identifier
resource:          # optional: stable URI of the underlying legal asset (ELI/ECLI/DOI)
```

**Normalization:** Write norm strings uniformly as `<Law> Art./§ <N> Abs. <N> lit. <x>` (law first), so that backlinks and queries do not fragment. Never invent ECLI values — only verified identifiers; otherwise keep just the citation.

**`resource:` (stable asset URI, OKF recommended field).** Points to the page's machine-readable primary source. Conventions:
- **Norm nodes:** ELI URI — EU law via `http://data.europa.eu/eli/…` (e.g. DSGVO: `http://data.europa.eu/eli/reg/2016/679/oj`), German federal law via `https://recht.bund.de/eli/…`.
- **Leading-decision pages:** ECLI resolver — CJEU/EU via EUR-Lex (`https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=ecli:<ECLI>`), German courts via `https://www.rechtsprechung-im-internet.de` or the ECLI resolver.
- **Source/concept pages:** DOI (`https://doi.org/…`) or Zotero select link.
- Set URIs only when verified (no invention, by analogy to the ECLI rule).

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
- `wiki-category: entitaet`, plus `rang:` (1–6) set
- Structure: Definition · Paragraphs/elements of the offence (with wikilinks to concept pages) · Leading decisions · Relationship to other norms
- Purpose: anchor node — concept pages link here; backlinks replace the SPARQL query of the KG approach
- Distinction from the law entity: `DSGVO.md` describes the regulation as a whole; `DSGVO Art. 6.md` is the granular norm node and links to the law page

### Leading-Decision Page
- A special form of the entity page for a landmark decision
- Naming scheme: `[short label].md` (e.g. `BVerfGE 65,1 (Volkszählungsurteil).md`)
- `wiki-category: entitaet`, plus `rang:`, `ecli:` (where verified and available), `rechtsstand:`
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

## Typed Wikilinks (Relation Vocabulary)

Legal relationships between nodes are expressed in the running text with a controlled relation verb placed before the wikilink. Human-readable, grep-able for `query wiki`. Adopts the typed edges of the KG approach (setzt_um, ändert, konkretisiert) Obsidian-natively, without schema overhead.

Controlled vocabulary:

- **setzt um** — directive → transposition statute
- **ändert** / **hebt auf** — amendment/repeal
- **verdrängt** — application priority (lex superior/posterior)
- **konkretisiert** — case law refines an older decision/norm
- **definiert** — norm defines a term
- **wendet an** — decision applies a norm
- **zitiert** — general reference

Example:

> Der DSA **verdrängt** [[NetzDG]] §§ 2, 3 (seit 17.02.2024); das österr. KoPl-G-Analogon ist europarechtswidrig laut [[EuGH C-376-22 (KoPl-G)]].

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

### Ingest Obligation: Norm-Supersession Check

On every ingest of a legal source (statute, regulation, judgment, commentary) **before writing**:

1. **Identification** — Which older norms or decisions are replaced, amended, or superseded by the new source? Watch for signal phrasings in the source text: "ersetzt", "aufgehoben", "tritt an die Stelle von", "verdrängt", "Anwendungsvorrang", "gilt nicht mehr", "überholt durch".
2. **Wiki scan** — Check `index.md` and the affected wiki pages for callouts and running-text passages that cite the superseded norm/decision.
3. **Update** — Update the affected pages within the same ingest run (flag callouts, adjust running text for substantive changes, set `updated` and `rechtsstand` dates).

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
> Restanwendungsbereich: § 3a NetzDG (Meldepflicht staatsschützende Straftatbestände) bleibt eigenständig anwendbar.
```

Refined or revised court decision:

```
> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 149, 222 (Rundfunkbeitrag, 2018)
> Durch BVerfGE 158, 389 (Sachsen-Anhalt, 2021) in der Frage der Mitverantwortungspflicht der Länder konkretisiert.
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

## Zotero MCP Tools (Reference)

For ingest, only the Zotero MCP server is used (port 23120). The tools are callable directly as `mcp__zotero__*`.

| Tool | Use in ingest |
|---|---|
| `search` | Find item by @citekey or topic; returns item key |
| `find_item_by_identifier` | Find item by DOI or ISBN |
| `get_item_by_key` | Full metadata, abstract, attachment list, notes |
| `get_pdf_content` | Extract PDF full text (parameters: `itemKey`, optional `page`) |
| `get_item_annotations` | PDF highlights & annotations of an item |
| `get_item_notes` | Zotero notes of an item |
| `search_annotations` | Annotation search across the entire library |
| `get_collections` | List all collections (for bulk ingest) |
| `get_collection_items` | All items of a collection |
| `get_annotations_batch` | Retrieve several annotations at once |

**Fallback to the local API (port 23119):** Only when the MCP server does not respond (Zotero plugin not active). Then proceed as before via HTTP calls through Python/curl.

## Ingest Checklist

Before writing:
- [ ] `[WIKI-FOLDER]/index.md` read?
- [ ] Affected thematic folders identified?
- [ ] Check: is there already a page for this concept/entity?
- [ ] **Full-text check:** Retrieve attachments via Zotero MCP `get_item_by_key` (returns `attachments` field with `contentType`): `application/pdf` → PDF via `get_pdf_content`, `text/html` → HTML snapshot via the Read tool (`~/Zotero/storage/[ATTKEY]/`)
- [ ] **Norm-supersession check (legal sources):** Does the source contain norms or decisions that replace, amend, or supersede already documented wiki content? → Identify affected wiki pages via `index.md`; the update happens in the "write/update pages" step (see section *Legal Currency and Norm Supersession*)

Reading sources (standard — always before writing):
- [ ] Metadata + abstract read via Zotero MCP `get_item_by_key`?
- [ ] **PDF present?** (`contentType: application/pdf`) → Retrieve full text via `get_pdf_content` (MCP):
  - Articles/chapters: read in full (without `page` parameter = entire document)
  - Books: table of contents (pp. 1–5, `page: 1`) + relevant chapters (pages via `page` parameter, 1 page per call)
  - Evaluate annotations via `get_item_annotations` (MCP)
- [ ] **No PDF, but HTML snapshot present?** (`contentType: text/html`) → Read full text with the Read tool (`~/Zotero/storage/[ATTKEY]/`):
  - Read the HTML file in full; ignore HTML tags when evaluating
  - Treat like a PDF: fully for articles, selectively for longer documents
  - Evaluate annotations via `get_item_annotations` (MCP)
- [ ] Neither PDF nor HTML? → Work from metadata, abstract, and your own expertise; note in log.md: `[kein Volltext]`

While writing:
- [ ] Content based on the actual source text, not just on knowledge of the title
- [ ] Concrete page references or chapter references built in where possible
- [ ] Frontmatter complete (all required fields)?
- [ ] Cross-links set with [[Wikilinks]]?
- [ ] Existing atomic notes in the same folder checked for linkability?
- [ ] `updated` date updated?

After writing:
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
- [ ] **Broken wikilinks** — `[[Page]]` references to non-existent files. **When parsing, isolate the real link target** before checking against files: strip the alias after `|` *and* after escaped `\|` (mandatory escaping in Markdown tables!), strip `#` jump anchors, reduce the path to the last segment. Otherwise false positives arise for table links like `[[Antrag X\|Alias]]` and anchor links like `[[Seite#Abschnitt]]`.
- [ ] **Index consistency** — Entries in `index.md` without a corresponding file (and vice versa: files with `type: wiki-page` that are not listed in `index.md`)

**Warnings:**
- [ ] **Orphan pages** — Wiki pages with `type: wiki-page` that are not linked by any other page
- [ ] **Stale claims** — Pages with `[!recht]` callouts on norms that, according to newer sources (recognizable from `log.md`), have been superseded or changed, without the page having been updated
- [ ] **Missing pages** — Terms referenced in several pages via `[[Wikilink]]` but lacking their own file
- [ ] **Norm without node** — Norms in `normen:` frontmatter that occur in ≥3 pages but have no dedicated norm-node page
- [ ] **Judgment without node** — Judgments in `urteile:` frontmatter that occur in ≥3 pages but have no dedicated leading-decision page
- [ ] **Frontmatter drift** — Page with a `[!recht]` callout on a norm/decision that is not in the `normen:`/`urteile:` frontmatter

**Info:**
- [ ] **Data gaps** — Wiki pages with fewer than 2 sources in the `quellen:` frontmatter (topics with thin coverage)
- [ ] **Missing cross-links** — Pages on the same topic without mutual linking (recognizable by matching `thema:` fields)
- [ ] **Pages without frontmatter** — Files in wiki folders without `type: wiki-page`

### Output Format

```
## Lint-Ergebnis — YYYY-MM-DD

### Fehler (N)
- [[Seitenname]]: broken link zu [[NichtExistierendSeite]]

### Warnungen (N)
- [[Seitenname]]: Orphan-Seite (keine eingehenden Links)
- [[Seitenname]]: stale claim — NetzDG § 3 Abs. 2 (verdrängt durch DSA seit 17.02.2024, nicht markiert)

### Info (N)
- [[Seitenname]]: nur 1 Quelle, Thema unterrepräsentiert
```

Document findings in `log.md` with the syntax `- **Lint** — N Fehler, N Warnungen, N Info`.

### Recommended Cadence

After every 10 ingests, or monthly as minimum maintenance.

---

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

These types are **not** wiki pages within the meaning of the depth standard and are not captured by lint/ingest routines that filter on `type: wiki-page`. `Persönlich/` and `Werkzeuge/` remain entirely excluded.

## OKF Compatibility (Google Open Knowledge Format v0.1)

The wiki is deliberately kept largely OKF-compatible (knowledge exchange with third parties/agents).

- **Mandatory rule satisfied:** Every non-reserved `.md` in `[WIKI-FOLDER]/` carries a non-empty `type` field. All other fields (`wiki-category`, `normen`, `urteile`, `rang`, `ecli`, `thema`, `quellen`) are OKF-conformant extensions — consumers must tolerate unknown keys.
- **`resource:`** is the OKF recommended field for the asset URI (see Frontmatter Schema above; ELI/ECLI/DOI).
- **Reserved Files:** `index.md` + `log.md` present. Note: OKF provides *no* frontmatter for `index.md` — our `type: wiki-index` is a tolerated deviation. Optionally, `okf_version: 0.1` can be declared in the root `index.md`.
- **Deliberate divergence — links:** We use Obsidian `[[Wikilinks]]` instead of OKF-standard Markdown links (`[Text](/pfad.md)`). OKF tolerates this (links are tolerated as "broken", relation semantics reside in the running text anyway). For a true OKF export, a build pipeline (wikilinks → Markdown links) would be the right approach — not converting the vault.
