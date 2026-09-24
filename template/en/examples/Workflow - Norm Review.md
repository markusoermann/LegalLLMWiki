---
type: wiki-workflow
thema: [Methodik]
created: 2026-09-23
updated: 2026-09-23
---

# Workflow: Norm Review

> **Example page (workflow).** Shows the structure of a callable procedure page (`type: wiki-workflow`). In a live vault it lives in `[WIKI-FOLDER]/Workflows/`. Replace or extend it with your own procedures.

## Purpose

Work through a single norm systematically before using it in a wiki page, an expert opinion, or teaching material. The workflow answers one question: what exactly does this norm require, of whom, from when, and with what consequence? It replaces neither the subsumption of an individual case nor substantive review by a human being.

**Invocation:** `workflow: Norm Review`

## Steps

Work through the steps in this order. Each step ends with a checking question; if it cannot be answered, do not proceed but go back to the source.

1. **Determine the scope of application.** Keep four dimensions apart:
   - material: which facts and objects the norm covers
   - personal: who is the addressee, who is the beneficiary
   - territorial: which territory, does a marketplace or effects principle apply
   - temporal: `in_kraft:`, `wirksam_ab:`, transitional law

   *Checking question:* Can one sentence with a norm reference be formulated for each of the four dimensions?

2. **Classify the norm function.** Assign the norm to one or more values of the `normtyp:` vocabulary (Gebot, Verbot, Erlaubnis, Anspruchsnorm, Freiheitsrecht, Kompetenznorm, Gestaltungsrecht, Immunität, Definitionsnorm, Qualifikationsnorm). Combinations are the normal case, not the exception.

   *Checking question:* Which legal position does the norm establish, and for whom is it the correlative burden?

3. **Break down the elements of the offence.** Name each element separately, map the legal definitions from the definitions article of the statute, mark indeterminate legal concepts, and flag open questions of interpretation as such.

   *Checking question:* Is every element either legally defined or specified by a landmark decision, and is there a locator for it?

4. **Determine the legal consequence.** Distinguish a bound decision from discretion. Keep claims, sanctions, invalidity consequences, and procedural duties apart, because they follow different enforcement paths.

   *Checking question:* Who can demand what from whom, and who enforces it?

5. **Clarify the relationship to other norms.** Express priority, supersession, speciality, and complementarity with the typed relation vocabulary (setzt um, verdrängt, konkretisiert, wendet an, wirkt nach). Note transposition and opening clauses separately.

   *Checking question:* Is there a higher-ranking or later norm that supersedes this one wholly or in part?

6. **Document.** Write the result into the norm node:
   - frontmatter: `rang:`, `normtyp:`, `in_kraft:`, `wirksam_ab:`, `normen:`, `rechtsstand:`
   - a `[!recht]` callout with a `Beleg:` line for every interpretive statement
   - wikilinks to the affected concept pages and landmark decisions

   *Checking question:* Does every interpretive statement carry a locator, and has the verification pass run?

## Abort criteria

- The norm is neither in force nor applicable at the time of review: suspend the review, record the status in the norm node, and note the expected date of entry into force.
- The official norm text is unavailable: do not reconstruct it from memory; abort with the note `[kein Volltext]` in the log.
- The norm has been fully repealed or declared void: abort the review, flag the callout following the pattern for superseded norms, and check for ultra-activity in old cases.
- The interpretation of an element is openly contested: present the state of the controversy instead of deciding it, and give opposing views their own locator.
- The request is evidently about a concrete individual case: abort and refer it to substantive legal work. This workflow opens up norms; it does not give advice.

## Related nodes

[[DSGVO Art. 6]] · [[EuGH C-300-21 (Österreichische Post)]] · [[Beispielkonzept (Datenminimierung)]]
