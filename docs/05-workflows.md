# 05 · Workflows & Trigger

Alle Trigger sind in `AGENTS.md` definiert; der Agent erkennt sie im Chat. Vor jedem Ingest liest der Agent `04 Ressourcen/wiki-schema.md`.

| Trigger | Was passiert |
|---|---|
| `ingest @citekey` | Holt genau diese Zotero-Quelle (Metadaten, Abstract, Annotationen, PDF-Volltext) und schreibt/aktualisiert Wiki-Seiten. |
| `Wiki aktualisieren` | Bulk-Ingest: liest letztes Datum aus `log.md`, holt alle neueren Zotero-Einträge. |
| `Aktualisiere Wiki: [Thema]` | Sucht Zotero nach Thema/Tag, verarbeitet alle Treffer. |
| `query wiki: [Frage]` | Durchsucht `04 Ressourcen/` (Index + Grep), synthetisiert eine Antwort mit `[[Wikilinks]]`, bietet optional eine Synthese-Seite an. |
| `lint wiki` | Integritäts-Audit (Broken Links, Orphans, fehlende Knoten, Frontmatter-Drift) mit Schweregraden. |

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
1. `wiki-schema.md` lesen → 2. Zotero-Tools (`search` → `get_item_by_key` → `get_pdf_content` → `get_item_annotations`) → 3. `index.md` prüfen → 4. Themenordner bestimmen → 5. Seiten schreiben (max. ~15/Ingest) → 6. `index.md` aktualisieren → 7. `log.md`-Eintrag.

## Pflege
- `lint wiki` regelmäßig (z.B. nach 10 Ingests) ausführen.
- Bei Norm-/Urteilsänderungen: Normersetzungsregeln in `wiki-schema.md` beachten (`[!recht]`-Callouts kennzeichnen).

## Weiter
→ `06-recht-features.md` — die juristischen Besonderheiten.
