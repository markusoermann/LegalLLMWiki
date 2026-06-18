# 06 · Legal Features

What sets LegalWikiLLM apart from a generic LLMWiki. Technical details in `template/en/wiki-schema.md`.

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
```
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
