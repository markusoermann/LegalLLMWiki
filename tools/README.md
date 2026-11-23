**🇬🇧 English** · [🇩🇪 Deutsch](README.de.md)

# tools

Mechanical check scripts for the LLM wiki. No LLM, no dependencies beyond the Python
standard library, runtime in the order of seconds. They check things a language model
does not check reliably, and they are cheap enough to run continuously.

**Why they are separate from the verification pass:** the verification pass checks
*evidential support* against the reference manager. It only covers pages that cite
sources. Norm nodes carry `quellen: []` by definition and slip through its net. For
those, these tools take its place: comparison against the official version where a
machine-readable one exists, and comparison of the time axis where it does not.

| Tool | Checks | Network |
|---|---|---|
| `wiki_integrity_check.py` | citekeys against Zotero, **actually extractable** full text, ECLI syntax, norms without a node | local Zotero API |
| `knoten_check.py` | `resource:` URIs resolvable, age of `rechtsstand:`, missing anchor fields | yes |
| `normtext_check.py` | norm nodes against the official consolidated text: repeal, version marker | yes |
| `staffelung_check.py` | `in_kraft:` against `wirksam_ab:`: staggered applicability, stages passed | **no** |
| `rang_check.py` | `[!recht]` callouts: court used as norm category, rank against the governing norm, label variants, callouts without a norm reference, **date against ECLI** | **no** |

## Invocation

```bash
python3 tools/wiki_integrity_check.py /path/to/vault/WIKI-FOLDER
python3 tools/knoten_check.py         /path/to/vault/WIKI-FOLDER
python3 tools/normtext_check.py       /path/to/vault/WIKI-FOLDER
python3 tools/staffelung_check.py     /path/to/vault/WIKI-FOLDER
python3 tools/staffelung_check.py     /path/to/vault/WIKI-FOLDER --datum=2027-08-02
python3 tools/rang_check.py           /path/to/vault/WIKI-FOLDER
```

`wiki_integrity_check.py` requires a running Zotero with the local API on port 23119.
`knoten_check.py` and `normtext_check.py` need network access. `staffelung_check.py`
runs entirely offline; `--datum` shifts the reference date and thereby answers the
question of what changes on the day a future stage becomes applicable. `rang_check.py`
also runs offline and needs nothing but the Markdown files.

## Check E: date against ECLI — small, but exact

The German ECLI carries the decision date in its third segment:
`ECLI:DE:BGH:2020:`**`270720`**`UVIZR405.18.0` = 27 July 2020; for the Federal
Constitutional Court with a prefix and reversed order, `rs`**`20191106`** =
6 November 2019. If the same callout states a different date, one of the two is wrong —
**and that is detectable without retrieving anything.**

On its first run against a grown corpus the check found exactly one error, and a real
one: a Federal Court of Justice judgment appeared in three places on the same page with
a date shifted by one day.

**Reach, stated honestly.** The check only bites where a date **and** a German ECLI sit
in the same callout — in practice a small minority. Far more often a date appears
without an ECLI; there the check contributes nothing. That is also the most rewarding
place to add something: every ECLI supplied turns an unchecked assertion about a date
into a machine-checkable one.

**Why E is an error and not info.** Unlike check D there is no question of
interpretation: the two statements contradict each other, and both stand on the same
line. Which of them is right is not for the check to decide — it only reports that they
do not match.

**The check was tested against known cases before its null result was believed**
(5 date formats from BGH, BAG and BVerfG correctly recognised; a negative control with a
real discrepancy fires). A broken check reports the same thing as a clean corpus — that
confusion cost three attempts while building check D.

## Why there is no checksum

The obvious extension would be a hash over the norm text that turns `rechtsstand:` from
a promise into a check (as in RuML 1.0.0 ch. 4.12, SHA3-256 over the canonicalised
form). **Examined and rejected.**

The reason is `normtext_check.py` itself: it checks German norm nodes against the
official consolidated version and detects repeal **down to the individual section**. A
hash would add only the detection of *changes* rather than *repeal* — too little for the
price of a canonicalisation rule, a materiality definition and permanent noise. A hash
says *that* something changed, not *whether it matters*; an editorial correction and a
change to the elements of an offence produce the same result.

**Two justifications that came up along the way and neither of which holds** — recorded
here so they do not reappear as arguments next time:

- *"Only once LegalDocML.de makes GUID preservation binding."* This conflates two
  things. The GUID provides identity across versions; a hash provides change detection.
  If the anchor no longer resolves after a renumbering, **that is the signal** — "something
  structural changed about this norm" — not a failure of it.
- *"EU norm text is not machine-reachable."* True of EUR-Lex HTML (HTTP 202, JS
  challenge), not of Cellar: `<manifestation>/DOC_2` with
  `Accept: application/xhtml+xml` delivers the consolidated version with 198 `art_*`
  ids. Access was never the bottleneck.

**A documented remaining gap.** `normtext_check.py` **does not cover EU law** and never
could — it relies on the `(weggefallen)` marker, which EU law does not use. For EU norm
nodes, change detection therefore remains **source-driven**: it works when an amending
regulation lands in the reference manager and gets ingested. That has worked in practice
— an amending regulation with some 70 interventions in the AI Act was caught this way —
but it depends on the source arriving. If that path ever fails, this section is where to
look.

## Why validity and applicability need a tool of their own

`normtext_check.py` works because `gesetze-im-internet.de` marks repealed provisions
**section by section** as "(weggefallen)". For EU law no comparable signal exists. Three
routes were examined; all three are ruled out:

| Route | Result |
|---|---|
| EUR-Lex HTML (including via ELI and LexUriServ) | HTTP 202, JS challenge — the status line "No longer in force" is not machine-reachable |
| Cellar REST, `Accept: application/rdf+xml` | HTTP 200, but no validity predicate in the body delivered |
| Cellar SPARQL endpoint | reachable, but for **legal acts** it indexes only **consolidated** CELEX numbers (`02016R0679-20160504`); base acts return nothing, hence no `in-force` and no `end-of-validity`. **This does not hold for case law** — see the section below |

On top of that comes a granularity mismatch: anchor pages sit at article level, validity
status in EU law at act level. A dozen article nodes collapse into a single answer,
which almost always reads "still in force".

What matters more, though, is that EU law fails differently anyway. Regulations are
rarely repealed — they apply **in stages**. The EU AI Act becomes applicable in four
steps (2 Feb 2025 prohibitions, 2 Aug 2025 GPAI, 2 Aug 2026 high risk, 2 Aug 2027
Annex I). When a stage is passed, the meaning of a page changes without a single
character of the norm text changing: what was correctly phrased in the future tense
yesterday is wrong today. No network comparison in the world notices this, because
nothing changed that could be compared. It is checkable only against your own time
axis — and that sits in the front matter.

## Checking citations: existence and identity

The routes below do **not** check evidential support. They check whether the cited
decision exists and is the right one. The two must be kept strictly apart: that the
decision exists says nothing about whether it supports the statement.

### For case law Cellar does deliver

The negative finding above was stated too broadly. It holds for **legal acts**, where
Cellar indexes only consolidated versions. For **case law** the same endpoint provides
the predicate `cdm:case-law_ecli` and with it a dependable ECLI verification:

```bash
curl -s -G "https://publications.europa.eu/webapi/rdf/sparql" \
  --data-urlencode "query=PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    SELECT DISTINCT ?celex ?d WHERE {
      ?w cdm:case-law_ecli 'ECLI:EU:C:2023:957'^^<http://www.w3.org/2001/XMLSchema#string> .
      ?w cdm:resource_legal_id_celex ?celex .
      OPTIONAL { ?w cdm:work_date_document ?d }
    } LIMIT 1" \
  --data-urlencode "format=application/sparql-results+json"
# → 62021CJ0634, 2023-12-07  (C-634/21 SCHUFA)
```

Tried against an existing corpus: CELEX number and decision date could be held against
the node designation throughout. That closes the gap that had existed for Court of
Justice decisions ever since EUR-Lex became unreachable.

**Full text of a Court of Justice decision, in a particular language:**

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX cmr: <http://publications.europa.eu/ontology/cdm/cmr#>
SELECT ?m WHERE {
  ?w cdm:resource_legal_id_celex '62023CJ0416'^^xsd:string .
  ?e cdm:expression_belongs_to_work ?w ; cmr:lang ?l .
  FILTER(STR(?l) = 'deu')
  ?m cdm:manifestation_manifests_expression ?e ; cdm:manifestation_type ?t .
  FILTER(STR(?t) = 'xhtml')
}
```
Then fetch `<manifestation>/DOC_1` with `Accept: application/xhtml+xml`.

**Three stumbling blocks that defeated two earlier attempts:**
1. The language predicate lives in the namespace **`cdm/cmr#`**, not in `cdm#`, and is
   called `lang` there — so `cmr:lang`, not `cdm:lang` and not
   `cdm:expression_uses_language`. Its value is a **plain string literal** (`'deu'`,
   alongside `'de'`), **not a language URI** from the authority vocabulary. Both wrong
   forms return nothing **without failing** — the tempting conclusion is then that
   Cellar cannot select by language. (The first version documented here named
   `cdm:lang` with a URI filter and therefore did not work.)
2. `cdm:manifestation_type 'xhtml'` as a typed literal does not match reliably;
   `FILTER(STR(?t)='xhtml')` does.
3. The text sits under `<manifestation>/DOC_1` **or** `/DOC_2`. The manifestation URI
   itself returns only RDF metadata, not the text.

Without a language filter you get an arbitrary one of the roughly 25 versions — in a
test run it was Irish. For checking figures, the operative part and paragraph numbers
any version will do; for verbatim quotation it will not.

Two limitations: the query needs a **bound subject** (ECLI or CELEX) — unbounded
predicate searches run into the timeout. And it verifies an **existing** ECLI; it does
not find a missing one. The direction case number → ECLI remains fuzzy and must not be
automated.

### German decisions via the federal case-law API

The counterpart for German decisions is
`testphase.rechtsinformationen.bund.de/v1/rechtsprechung`. There **not only `ecli`**
works, but also the combination **`fileNumber` + `court`**:

```bash
curl -s -G "https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung" \
  --data-urlencode "fileNumber=VI ZR 277/22" --data-urlencode "size=5"
# → ECLI:DE:BGH:2023:121223BVIZR277.22.0
```

This corrects an earlier assessment: the direction case number → decision was thought
unusable because `searchTerm="1 BvR 209/83"` returned 468 hits. That is a finding about
`searchTerm`, not about the API — the dedicated `fileNumber` filter hits precisely.
Tried across several dozen citations without a false hit.

**The hit rate is itself a finding and must be read as one.** What was confirmed were
exclusively federal courts (BGH, BVerfG, BVerwG, BAG, BFH); what was missed were
exclusively lower courts (OLG, LG, AG, VG). The portal's holdings are centred on the
federal courts and begin around 2010. A null result is therefore `not checkable`,
**never** `fabricated` — confusing the two turns a limit of the holdings into a false
accusation against your own corpus. And it still holds: no ECLI may be inferred from a
null result.

Take care when evaluating: `fileNumber` also matches across jurisdictions. "6 S 21/21"
hit a Federal Social Court case, "15 W 13/26" a Federal Patent Court case. The court of
the hit must therefore be compared against the court cited, otherwise you count
coincidental matches as confirmations. The holdings begin around 2010: Lüth (1958),
Spiegel (1966) and the Census judgment (1983) return nothing. That is a finding about
the holdings, **not about the ECLI** — such cases belong in `not checkable`, not among
the errors.

### When the case number does not fit the subject matter

`searchTerm` is unusable for the direction case number → decision (see above, 468 hits),
but for the **reverse** direction it is the sharpest tool available. If a section carries
a case number under which an entirely different matter sits, the decision actually meant
can be found via its subject matter:

```bash
curl -s -G "https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung" \
  --data-urlencode "searchTerm=Auskunftsanspruch Disziplinarverfahren Verfassungsschutz Presse" \
  --data-urlencode "court=BVerwG" --data-urlencode "size=10"
# → 2 C 41/18, 2020-10-13, "Anspruch der Presse auf Auskunft aus den Akten eines
#   abgeschlossenen Disziplinarverfahrens", ECLI:DE:BVerwG:2020:131020U2C41.18.0
```

**The senate is a free extra test.** Hold `judicialBody` in the hit against the subject
matter: a press claim to information about a civil servant belongs to the civil-service
senate, not to the senate for freedom-of-information law. If the senate does not fit the
matter, the case number is wrong — and that shows up without costing a query.

**The notation of case numbers is not a stable feature.** The API takes Federal
Administrative Court case numbers sometimes with a dot, sometimes with a slash:
`6 C 10/21` hits, `6 C 10.21` returns nothing — for the same decision, whose ECLI is in
the holdings. In other cases it is the other way round. Every query must therefore be
made **in both forms** before a null result is counted. Otherwise you report your own
query error as a finding about the corpus.

### Joined cases sit in Cellar only under the lead case

The second, third, fourth case number of joined proceedings returns nothing even though
the judgment exists. This is demonstrable via the title of the lead case, which names
the joinder explicitly — `cdm:expression_title` then ends with "Verbundene Rechtssachen
C-339/20 und C-397/20." Skip that control and you report joined proceedings as
fabricated.

### DFR Bern for historical Federal Constitutional Court decisions

`https://www.servat.unibe.ch/dfr/bvVVVPPP.html` — volume and page each zero-padded to
three digits (BVerfGE 7, 377 → `bv007377.html`). Full text including headnotes and the
name of the decision. This makes BVerfGE volume citations checkable twice over: volume
and page via the HTTP status, the short name against the decision name in the title —
"BVerfGE 7, 29" is *Pressedelikte*, not Lüth (that is 7, 198). The federal case-law API
begins around 2010 and does not cover such decisions; DFR closes that gap.

### The commonest cause of "not checkable" is your own notation

Entries such as "LG Köln 4.000 EUR (KW47 2022)" or "BGH NJW 2018, 2324" name **no case
number** and are therefore unverifiable in principle — not because of the source but
because of how you wrote them down. They typically arise from newsletter ingests that
supply only a calendar week or a journal reference. If you want to raise the check rate,
start here and not with the tools: obtaining a case number during ingest is cheaper than
reconstructing one later.

## Adapting to your own situation

- **`EXCLUDE`** in all of them: folders inside the wiki folder that are not part of the wiki.
- **`GESETZE`** in `normtext_check.py`: mapping of statute abbreviations to portal slugs.
  The table shipped applies to German federal law on `gesetze-im-internet.de`. EU law,
  interstate treaties and convention law are not held there and are skipped. For other
  jurisdictions this table and the `BASIS` URL must be replaced.
- **`SAGT_KUENFTIG`** and **`IST_URTEIL`** in `staffelung_check.py`: both patterns are
  **language-bound**. `SAGT_KUENFTIG` detects from German phrasing whether a page
  presents itself as future law; `IST_URTEIL` recognises decision nodes by German and
  European court abbreviations and case-number formats. Anyone writing in another
  language or jurisdiction must replace both — otherwise S5 reports every decision as a
  missing field.

## Lessons from running them

Six points that save time when rebuilding this:

1. **Every finding needs a control before it leads to an action.** On first use every
   tool produced false alarms: an ECLI pattern that allowed only capitals for court
   abbreviations and therefore flagged every German ECLI; a citekey pattern that broke
   at the full stop; a URL check by HEAD that reported official servers as dead when
   they answer GET with 200. All three causes are commented in the code.
2. **Exempt the history.** `log.md` and `index.md` must not be touched by correction
   runs. A log records what happened at the time and is not smoothed over afterwards.
3. **Resolve HTML entities before comparing.** `gesetze-im-internet.de` delivers `§` as
   `&#167;`; a pattern matching `§` finds nothing there.
4. **Do not identify decision nodes by the `ecli:` field.** Tempting, but wrong: a large
   share of decision nodes carry no ECLI — older BVerfGE citations, BGH case numbers,
   lower courts. On the first run `staffelung_check.py` therefore reported eleven
   judgments as missing norm fields. Detection additionally needs a pattern for court
   abbreviations and case numbers.
5. **A PDF attachment is not yet full text.** The obvious check for whether a source can
   be verified asks for a PDF or HTML attachment. It fails as soon as the PDF is a scan
   without an OCR layer: the file is there but yields zero characters. In practice this
   affected five cited sources, among them the only supporting source of an entire core
   section, and the verifier correctly reported "not checkable" there while the integrity
   check listed the same source as supplied. The check must therefore run `pdftotext`
   against the file. Conversely: an empty full-text cache in the reference manager does
   **not** prove that the text layer is missing — it may simply never have been built.
   Here too, only looking into the file separates the two cases.

   The scan case is mechanically fixable: `ocrmypdf --language deu --skip-text <pdf>
   <pdf-new>`. The tool therefore reports the affected sources as a class of their own
   instead of mixing them with sources that have no attachment, because the one kind can
   be opened up in minutes and the other not at all.
6. **A guard with a frozen reference date is no guard.** The other tools may carry a
   fixed date because they check against an external source. This one checks against the
   calendar: it takes `date.today()`, otherwise it would never notice a stage being
   passed. Before adopting it, run it with `--datum` set beyond the next stage — a check
   that never fires looks exactly like one that works.

## What they cannot do

`wiki_integrity_check.py` requires `pdftotext` (Poppler) for the full-text check and
expects the attachment store under `~/Zotero/storage`. If either is missing, the check
falls back to the old attachment heuristic instead of producing false findings.

None of the tools checks whether a statement is substantively correct.
`normtext_check.py` detects that a norm has been repealed, not whether the
interpretation on the page is right. `staffelung_check.py` checks the time axis against
your own front-matter entries — if a `wirksam_ab:` was wrong to begin with, it will
confirm that error without contradiction. It reports inconsistency, not incorrectness.

`rang_check.py` can only check a callout that **names a norm**. Where only a decision
stands there (`· EuGH C-131/12 (Google Spain)`), it has nothing to anchor on and stays
silent. In the reference corpus exactly that spot carried rank 2 for years, although the
judgment was handed down on Directive 95/46/EC and is therefore rank 3. Callouts without
a norm reference remain manual work — the tool narrows the surface to be checked, it
does not replace it.

The limit is the same as for the verification pass: what gets checked is evidential
support and currency, not correctness.
