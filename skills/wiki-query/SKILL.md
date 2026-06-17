---
name: wiki-query
description: |
  Use when user wants to query their knowledge base: "query wiki: [Frage]",
  "was weiß ich über X", "finde alles zu X im Wiki", "zeig mir was im Wiki steht zu X",
  "suche im Wiki nach X", "was sagt mein Wiki zu X", "search my wiki for X".
  Searches all of [WIKI-ORDNER]/ (the LLMWiki; any non-wiki folders are excluded) using
  index + grep, synthesizes an answer with [[wikilinks]], and optionally saves
  the result as a new synthesis wiki page.
---

# Wiki Query Skill

Beantwortet Fragen aus dem LLMWiki durch strukturierte Suche in `[WIKI-ORDNER]/` mit optionaler Speicherung als Synthese-Seite.

## Trigger

- `query wiki: [Frage]` — direkter Einstieg
- `query wiki` — Skill fragt nach der Frage
- Implizit bei: „was weiß ich über X", „finde alles zu X im Wiki", „suche im Wiki nach X"

---

## Workflow

### Schritt 1 — Index lesen

`[WIKI-ORDNER]/index.md` lesen. Thematisch relevante Wiki-Seiten identifizieren und vormerken.

### Schritt 2 — Grep-Suche

Schlüsselbegriffe aus der Frage extrahieren. Immer **deutsche + englische Varianten** suchen (Fachbegriffe kommen in beiden Sprachen vor):

```bash
# Mehrere Suchbegriffe kombinieren
grep -rl "Verantwortung\|accountability\|responsibility" \
  "/path/to/your/vault/[WIKI-ORDNER]/" \
  --include="*.md"
```

Synonyme und verwandte Konzepte aktiv einbeziehen (z.B. `Plattform|platform`, `Regulierung|regulation`).

### Schritt 3 — Quellen zusammenführen

- Index-Treffer + Grep-Treffer zusammenführen, Duplikate entfernen
- Seiten lesen, [[Wikilinks]] folgen wenn thematisch relevant
- **Priorisierung bei vielen Treffern:** Index-Treffer → exakte Grep-Treffer → verwandte Seiten
- Cap: max. ~10–12 Seiten lesen; bei mehr nach Relevanz filtern

### Schritt 4 — Antwort synthetisieren

Format je nach Fragetyp:

| Fragetyp | Format |
|---|---|
| Faktenfrage | Direkte Antwort + Belege |
| Vergleichsfrage | Strukturierter Vergleich |
| Erkundungsfrage | Thematischer Überblick mit Verweisen |
| Listenfrage | Kommentierte Liste |

Jede zentrale Aussage mit `[[Wikilink]]` belegen. Widersprüche zwischen Quellen explizit nennen.

### Schritt 5 — Rückfrage Synthese-Seite

Nach der Antwort fragen:

> „Soll ich diese Analyse als Synthese-Seite im Wiki speichern?"

**Bei Ja:**
1. Passendes Thema aus den Wiki-Themenordnern bestimmen (`Ethik`, `KI`, `Jura`, etc.)
2. Dateiname: `Synthese - [beschreibender Titel].md`
3. Frontmatter (Pflicht):
   ```yaml
   ---
   type: wiki-page
   wiki-category: synthese
   thema: [Thema]
   quellen: ["@citekey1", "@citekey2"]  # alle referenzierten Quellen
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---
   ```
4. Speichern: `[WIKI-ORDNER]/[Thema]/Synthese - [Titel].md`
5. `[WIKI-ORDNER]/index.md` aktualisieren
6. `[WIKI-ORDNER]/log.md` Eintrag anhängen:
   ```
   - **Query** „[Frage]" → erstellt [[Synthese - Titel]]
   ```

**Bei Nein:** fertig.

---

## Qualitätsstandards

- **Belegen:** Jede faktische Aussage mit `[[Wikilink]]` oder Quellenangabe
- **Transparent:** Wenn das Wiki zum Thema lückenhaft ist → klar sagen was fehlt + `ingest`-Vorschlag machen
- **Ehrlich:** Nicht aus Fachwissen ergänzen ohne Kennzeichnung — das ist eine Wiki-Abfrage, keine Expertise-Abfrage. Eigenes Wissen nur als explizit markierten Zusatz (`*Hinweis: nicht im Wiki belegt*`)
- **Widersprüche:** Zwischen Quellen explizit benennen, nicht glätten

## Grenzen

- Sucht nur in `[WIKI-ORDNER]/` — keine Projekte, Daily Notes, Inbox
- Synthetisiert nur was im Wiki steht; Lücken → `ingest`-Hinweis
- Synthese-Seiten folgen dem wiki-schema-Tiefenstandard (mindestens 3 Kernaspekte, Cross-Links)
