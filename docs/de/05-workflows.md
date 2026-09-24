# 05 · Workflows & Trigger

Alle Trigger sind in `AGENTS.md` definiert; der Agent erkennt sie im Chat. Vor jedem Ingest liest der Agent `[WIKI-ORDNER]/wiki-schema.md`.

| Trigger | Was passiert |
|---|---|
| `ingest @citekey` | Holt genau diese Zotero-Quelle (Metadaten, Abstract, Annotationen, PDF-Volltext) und schreibt/aktualisiert Wiki-Seiten. |
| `Wiki aktualisieren` | Bulk-Ingest: liest letztes Datum aus `log.md`, holt alle neueren Zotero-Einträge. |
| `Aktualisiere Wiki: [Thema]` | Sucht Zotero nach Thema/Tag, verarbeitet alle Treffer. |
| `query wiki: [Frage]` | Durchsucht `[WIKI-ORDNER]/` (Index + Grep), synthetisiert eine Antwort mit `[[Wikilinks]]`, bietet optional eine Synthese-Seite an. |
| `lint wiki` | Integritäts-Audit (Broken Links, Orphans, fehlende Knoten, Frontmatter-Drift) mit Schweregraden. |
| `verify wiki [Seite]` | Belegprüfung durch einen frischen Subagenten: Trägt die zitierte Quellenstelle die Aussage? Argument optional (Seite, Thema oder letzter Ingest), läuft ohnehin als Schritt 6 jedes Ingests. (→ `07-verifikation.md`) |
| `bench wiki` | Misst die Antwortqualität gegen `[BENCHMARK-ORT]/benchmark.md` (Wissensfragen + Out-of-Scope-Fragen). |
| `workflow: [Name]` | Der Agent liest die Workflow-Seite in `[WIKI-ORDNER]/Workflows/` und arbeitet sie Schritt für Schritt ab. |

## Typischer Ablauf

```
1. Quelle in Zotero ablegen (citekey notieren)
2. Im Agenten:  ingest @mustermann2024
   → Agent liest Zotero-Eintrag, identifiziert Konzepte/Normen/Urteile,
     schreibt Wiki-Seiten in passende Themenordner, setzt [[Wikilinks]],
     aktualisiert index.md + log.md
3. Später:  query wiki: Was sagt mein Wiki zu Datenminimierung?
   → Antwort aus Frontmatter (normen/urteile) + Backlinks
```

## Ingest-Ablauf (intern, immer gleich)
1. `wiki-schema.md` lesen → 2. Zotero-Tools (`search_library` → `get_item_details` → `get_content` → `get_annotations`) → 3. `index.md` prüfen → 4. Themenordner bestimmen → 5. Seiten schreiben (max. ~15/Ingest), jede Kernaussage mit Locator (`Beleg:`-Zeile bzw. `(@citekey, S. N)`) → 6. **Verifikations-Pass** durch einen frischen Subagenten, danach `verifiziert:` setzen → 7. `index.md` aktualisieren → 8. `log.md`-Eintrag.

## Pflege
- `lint wiki` und `bench wiki` regelmäßig (z.B. nach je 10 Ingests) gemeinsam ausführen: das eine misst Struktur, das andere Antwortqualität.
- Bei Norm-/Urteilsänderungen: Normersetzungsregeln in `wiki-schema.md` beachten (`[!recht]`-Callouts kennzeichnen).

## Weiter
→ `06-recht-features.md` — die juristischen Besonderheiten · `07-verifikation.md` — Belege, Verifikations-Pass und Benchmark · `08-mcp-server.md` — der optionale Wiki-MCP-Server.
