---
name: quellencheck
description: >
  Verify that all references cited in an academic thesis, paper, or bibliography actually exist.
  Use this skill whenever the user asks to: check, verify, validate, or prüfen references/sources/Quellen/Literatur
  in a thesis, Masterarbeit, Bachelorarbeit, Dissertation, research paper, or any document with a bibliography.
  Also trigger when the user says things like "gibt es alle Quellen wirklich?", "stimmen die Quellen?",
  "Literaturverzeichnis prüfen", "check if sources are real", "verify my references".
  The skill systematically checks DOIs via CrossRef, resolves URLs via HTTP, searches for incomplete
  references in OpenAlex and CrossRef, detects duplicates, year mismatches, fake authors, missing fields,
  and filenames used as titles. Delivers a structured report categorized by severity.
---

# Quellencheck — Academic Source Verification

Systematically verify that every reference in an academic bibliography actually exists,
is correctly described, and is reachable. Surface errors by severity so the author
can fix them before submission.

## What this skill checks

- **DOI existence**: resolved via CrossRef API (primary) and arXiv for arXiv DOIs
- **URL reachability**: HTTP status codes for every linked web resource
- **Year accuracy**: CrossRef publication year vs. the year in the citation
- **Duplicate DOIs**: same DOI appearing under two different reference entries
- **Incomplete references**: missing publisher, journal, URL, or DOI for non-book sources
- **Filename-as-title**: references where the title field contains a file name (e.g., `2018_report_en_fn`)
- **Author name errors**: academic degrees or titles used as author names (e.g., "Econ, M." instead of a person)
- **Unreliable sources**: academia.edu links or similar platforms cited as if they were the canonical publication
- **Unverifiable grey literature**: reports, studies, or internal documents with no institutional link, DOI, or URL

---

## Step 1 — Locate and read the document

Ask the user for the file path if not already provided. Accept PDF, DOCX, or plain text.

**For PDF** — extract text with pdftotext (install poppler if needed):
```bash
brew install poppler 2>/dev/null || apt-get install -y poppler-utils 2>/dev/null
pdftotext "<path>" /tmp/thesis_text.txt
```

Then read the file and locate the bibliography section. Common German/English headers to search for:
`Literatur`, `Literaturverzeichnis`, `Quellenverzeichnis`, `Bibliographie`, `References`, `Bibliography`

Use `grep -n` to find the line number, then read from there to the end of the document.

**For DOCX** — extract with python-docx or pandoc:
```bash
pandoc "<path>" -t plain -o /tmp/thesis_text.txt
```

---

## Step 2 — Parse and classify all references

Read through the bibliography and build a list of all entries. For each entry, extract:
- Short label (Author + Year)
- Title
- DOI (if present — starts with `10.`)
- URL (if present — starts with `http`)
- Publication year
- Journal / publisher / institution (if present)

Classify each reference into one of these types:
- **DOI reference** — has a DOI string
- **URL-only reference** — no DOI, but has a URL
- **Book/monograph** — no DOI, no URL, publisher present
- **Grey literature** — no DOI, no URL, no publisher (reports, studies, institutional documents)

Count totals per type and announce them to the user before starting verification.

---

## Step 3 — Batch-verify DOIs via CrossRef

Use the script `scripts/verify_dois.py` for efficient batch checking with rate limiting.
Run it with a JSON list of `{label, doi}` pairs and capture the output.

The script:
- Queries `https://api.crossref.org/works/{doi}` for each DOI
- Sets `User-Agent: QuellenCheck/1.0 mailto:<user-email>` (use the user's email from context)
- Sleeps 100 ms between requests to respect CrossRef's polite pool
- Returns: status (OK / FEHLER), CrossRef title, CrossRef year, HTTP code

For arXiv DOIs (prefix `10.48550/`):
- CrossRef will return 404 (arXiv is not indexed there) — this is expected
- Verify instead via `https://arxiv.org/abs/{arxiv_id}` (strip the `arXiv.` prefix from the DOI)
- If the page loads and contains the expected title keywords, mark as OK
- Additionally try resolving the DOI via `https://doi.org/{doi}` — a 200 redirect to arxiv.org confirms existence

Note year mismatches: if CrossRef reports year Y but the citation says year Z, flag it.
The most common cause is the gap between online-first publication and the print issue date —
a one-year difference (e.g., CrossRef: 2021, citation: 2022) is usually not an error.
A two-year or more gap, or a year earlier than CrossRef, is suspicious and worth flagging.

---

## Step 4 — Verify all URLs

Use the script `scripts/verify_urls.py` for batch HTTP checking.

For each URL:
- Send a GET request with a realistic browser User-Agent
- Follow redirects (up to 5 hops)
- Timeout: 15 seconds per URL
- Record: HTTP status, final URL after redirect (to catch moved resources)

Interpret status codes:
- 200–299: OK
- 301/302 redirect to different domain: note the new URL
- 403: Access denied (page exists but requires login — mark as UNKLAR, not FEHLER)
- 404: Not found — FEHLER
- 5xx / timeout / connection error: FEHLER
- 523 (Cloudflare): Server unreachable — FEHLER

Special handling for academia.edu URLs: even if they return 200, flag them with a note
that academia.edu is not a stable publication venue and lacks a DOI — the canonical
source (journal or book) should be cited instead.

---

## Step 5 — Search for incomplete and grey-literature references

For entries without DOI or URL (books, grey literature), use the search APIs to attempt verification:

**CrossRef full-text search:**
```
https://api.crossref.org/works?query.author=<lastname>&query.title=<keywords>&rows=3
```

**OpenAlex search:**
```
https://api.openalex.org/works?search=<title+author>&per_page=5&mailto=<email>
```

**Google Books API** (for books and monographs, 1-second delay between requests):
```
https://www.googleapis.com/books/v1/volumes?q=<title+author>&maxResults=3
```

If a match is found:
- Compare title similarity (fuzzy match — key words must align)
- Compare year
- Note the canonical DOI or ISBN if found

If no match is found in any database: mark as "nicht verifizierbar" (unverifiable).

---

## Step 6 — Detect structural and formatting errors

Beyond existence checks, look for these specific issues in the raw reference data:

**Duplicate DOIs:**
Build a `{doi: [labels]}` dictionary. Any DOI with 2+ entries is a duplicate —
the same source is cited twice as if it were two different publications.

**Filename as title:**
A title is likely a filename if it: contains underscores or hyphens separating words,
matches a pattern like `YYYY_report_lang`, or has no spaces. Flag these.

**Degree as author name:**
"Econ, M.", "Dipl., A.", "Prof., B." follow the pattern `<Degree/Abbrev>, <Initial>`.
A real author name has a surname of ≥3 letters. Flag entries where the "author" looks like an academic title.

**Wrong `(a)` / `(b)` disambiguation:**
When two entries share the same DOI but are labeled (2024a) and (2024b), they are not
two different sources — they are the same source cited twice. This is different from
legitimate (a)/(b) disambiguation where the author genuinely published two things that year.

---

## Step 7 — Compile and present the report

Structure the report in four tiers. Use markdown with clear headers.

```
## Quellenprüfung: [Document title] (N Einträge)

### KRITISCHE FEHLER
[Sources that are definitely wrong or non-existent]
- Numbered list with: source label → problem → evidence / corrected info

### DEUTLICHE MÄNGEL
[Sources with significant issues that need fixing before submission]

### FEHLENDE ANGABEN (nicht verifizierbar)
[Sources that could not be verified due to missing metadata — may be real but cannot be confirmed]

### GERINGFÜGIGE ABWEICHUNGEN
[Minor year mismatches likely explained by online-first vs. print date — informational only]

### ALLE ÜBRIGEN QUELLEN (ca. N)
OK — DOIs aufgelöst ✓ · URLs erreichbar ✓ · Angaben plausibel ✓
```

After the report, offer a brief summary sentence: how many sources were checked,
how many have problems, and whether the overall quality is high/medium/low.

---

## API rate limits and fallbacks

| API | Rate limit | Fallback if unavailable |
|-----|-----------|------------------------|
| CrossRef | ~50 req/s (polite pool with email) | Try doi.org resolver |
| OpenAlex | 10 req/s with email, 1 without | Use CrossRef search |
| Google Books | ~1 req/s, 429 if exceeded | Skip; note not verified |
| arXiv | ~3 req/s | Try doi.org |

If any API returns 429 (rate limit), add a 2-second sleep and retry once.
If it fails again, mark the entry as "nicht geprüft (API-Limit)" and continue.

---

## Common patterns and what they mean

| Pattern | Typical cause | How to handle |
|---------|---------------|---------------|
| CrossRef year = N, citation year = N+1 | Online-first vs. print issue | Usually OK, note it |
| CrossRef year = N, citation year = N-1 | Preprint cited with later journal year | Flag — inconsistent |
| DOI resolves to different title | Wrong DOI copy-pasted | Critical error |
| academia.edu as primary source | Preprint uploaded by author, no stable DOI | Flag — find canonical publication |
| No DOI for journal article | Not all journals use DOIs | Attempt OpenAlex lookup |
| Two (a)/(b) entries, same DOI | Duplicate citation | Critical error |
| Title is all lowercase filename format | Copy-paste from file system | Flag — add real title |
