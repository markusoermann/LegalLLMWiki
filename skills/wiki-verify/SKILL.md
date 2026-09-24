---
name: wiki-verify
description: |
  Use when the user wants to verify that wiki claims are actually supported by their sources,
  or wants to measure wiki answer quality: "verify wiki", "verify wiki [page]",
  "check the citations in my wiki", "are these claims supported", "bench wiki",
  "run the benchmark", "how well does my wiki answer questions",
  "prüf die Belege", "Belegprüfung", "stimmen die Belege im Wiki",
  "sind die Aussagen belegt", "Benchmark laufen lassen", "Verifikations-Pass".
  Runs a fresh-subagent verification pass that checks whether each claim on a wiki page is
  carried by its cited source passage (supportedness, not correctness), marks unsupported
  claims, removes fabricated identifiers, and logs the result. Also runs the gold benchmark.
---

# Wiki Verify Skill

Zwei Funktionen: **Belegprüfung** einzelner Seiten (`verify wiki`) und **Benchmark** der Antwortqualität (`bench wiki`). Beide schreiben ihr Ergebnis nach `[WIKI-ORDNER]/log.md`.

Vollständige Spezifikation: `[WIKI-ORDNER]/wiki-schema.md`, Abschnitte *Verifikations-Pass* und *Benchmark-Spezifikation*. Der Ablauf lässt sich zusätzlich als Verfahrensseite im Wiki führen (etwa [[Workflow - Belegprüfung]]).

## Trigger

| Trigger | Funktion |
|---|---|
| `verify wiki` | fragt nach dem Prüfgegenstand |
| `verify wiki [Seitenname]` | prüft eine Seite |
| `verify wiki [Thema]` | prüft alle Seiten eines Themenordners |
| `verify wiki letzter Ingest` | prüft die Seiten des letzten `log.md`-Eintrags |
| `bench wiki` | führt `[WIKI-ORDNER]/benchmark.md` aus |

Unabhängig davon läuft die Belegprüfung automatisch als abschließender Schritt jedes Ingests.

---

## Teil 1 — Belegprüfung

### Grundsatz

**Geprüft wird Belegtheit, nicht Richtigkeit.** Festgestellt wird ausschließlich, ob die angegebene Quellenstelle die Aussage trägt. Ob die Aussage zutrifft, wird nicht beurteilt, weil juristische Auslegung keinen maschinell prüfbaren Wahrheitsmaßstab hat. Ein Verifier, der über Richtigkeit befände, würde eine Anmaßung in eine Prüfroutine gießen und falsche Sicherheit erzeugen, die genau deshalb schwer zu bemerken wäre, weil sie ein Prüfsiegel trägt.

### Schritt 1: Frischer Subagent

Die eigentliche Prüfung läuft in einem **Subagent ohne den Schreibkontext**. Das ist der Kern des Verfahrens, keine Formalie: Wer den Text geschrieben hat, liest ihn gegen die Quelle als Bestätigung, nicht als Prüfung.

Der Subagent bekommt: Seitenpfad, Seiteninhalt, Frontmatter. Er bekommt **nicht**: die Begründung, warum die Seite so geschrieben wurde, oder den Ingest-Verlauf.

### Schritt 2: Prüfgegenstand sammeln

Aus der Seite extrahieren:

- `Beleg:`-Zeilen aus `[!recht]`-Callouts
- Inline-Locator der Form `(@citekey, S. N)`
- `quellen:`, `normen:`, `urteile:`, `ecli:` aus dem Frontmatter
- **Aussagen, die einen Beleg bräuchten, aber keinen tragen** — oft der ergiebigste Posten

### Schritt 3: Quellenrückgriff

Zotero MCP (Standard-Endpunkt `http://127.0.0.1:23120/mcp`, siehe `docs/de/03-zotero-mcp.md`):

- `search_fulltext` mit einer charakteristischen Wendung der Aussage, um die Stelle zu finden
- `get_content` gezielt für den Abschnitt (`mode: "standard"` genügt meist)
- `get_annotations` für eigene Hervorhebungen

Normen und Entscheidungen gegen die amtliche Quelle prüfen: EUR-Lex/ELI für EU-Recht, gesetze-im-internet.de für deutsches Bundesrecht, ECLI-Resolver für Entscheidungen. Für andere Jurisdiktionen die jeweils amtliche Fundstelle verwenden.

### Schritt 4: Klassifizieren

| Befund | Bedeutung | Konsequenz |
|---|---|---|
| `belegt` | Stelle trägt die Aussage | nichts |
| `nicht belegt` | Stelle existiert, trägt die Aussage nicht | max. 2 Nachbesserungsversuche (Locator korrigieren, bessere Stelle suchen), danach `[!unbelegt]` |
| `widersprochen` | Quelle sagt etwas anderes | im selben Durchgang korrigieren, Korrektur protokollieren |
| `nicht prüfbar` | kein Volltext vorhanden | Aussage bleibt, `verifiziert:` **nicht** setzen |

### Schritt 5: Hard-Fail

Vier Befunde führen zur **sofortigen Entfernung ohne Nachbesserung**:

1. erfundene oder nicht auffindbare **ECLI**
2. erfundene **Normbezeichnung** (Artikel/Paragraph existiert im zitierten Gesetz nicht)
3. erfundene **Fundstelle** (Band, Seite, Randnummer nicht verifizierbar)
4. erfundener **citekey** (nicht in Zotero vorhanden)

Diese werden entfernt, nicht markiert. Die Schema-Regel „ECLI niemals erfinden" war eine Anweisung an den schreibenden Agenten; hier wird sie zur Prüfung durch einen anderen. Anweisungen erzwingen nichts, Prüfungen schon.

### Schritt 6: Markieren

Nicht bestandene Aussagen bekommen einen Callout. Sie verschwinden nicht kommentarlos und bleiben nicht unkommentiert stehen:

```markdown
> [!unbelegt] ⚠️ Nicht belegt — geprüft YYYY-MM-DD
> Die angegebene Quelle @citekey trägt diese Aussage an der genannten Stelle nicht.
> Entweder Locator korrigieren, Quelle nachliefern oder Aussage entfernen.
```

### Schritt 7: Abschließen

- keine offenen Befunde → `verifiziert: YYYY-MM-DD` im Frontmatter setzen
- offener `[!unbelegt]`-Befund → Feld **nicht** setzen
- `updated:` fortschreiben, wenn der Text geändert wurde

`log.md`-Eintrag:

```
- **Verifikation** [[Seitenname]] — 14 Aussagen: 12 belegt, 1 korrigiert, 1 unbelegt, 0 Hard-Fail
```

### Ausgabeformat

```markdown
## Belegprüfung — [Seite] — YYYY-MM-DD

**Ergebnis:** 12/14 belegt · 1 korrigiert · 1 unbelegt · 0 Hard-Fail
**Status:** `verifiziert:` nicht gesetzt (offener Befund)

### Korrigiert (1)
- „[Aussage]" — Locator war @citekey S. 88, richtig ist S. 91

### Unbelegt (1)
- „[Aussage]" — @citekey trägt die Aussage an keiner auffindbaren Stelle

### Hard-Fail (0)
```

---

## Teil 2 — Benchmark

### Ablauf

1. `[WIKI-ORDNER]/benchmark.md` lesen
2. Jede Frage aus **Block A** über den `wiki-query`-Workflow beantworten, **ohne dass die Goldantwort im Kontext liegt**. In der Praxis heißt das: je Frage ein Subagent, der nur die Frage bekommt.
3. Jede Frage aus **Block B** ebenso. Erwartet wird die Zurückweisung.
4. Antworten gegen die Goldantworten prüfen

### Bewertung

| Kriterium | Bedeutung |
|---|---|
| **inhaltlich korrekt** | trifft den Kern der Goldantwort |
| **korrekt belegt** | verweist auf die angegebene Belegseite |
| **Teiltreffer** | inhaltlich korrekt, aber ohne Beleg |
| **kein Treffer** | inhaltlich korrekt, aber aus Modellwissen statt aus dem Wiki |

Der letzte Fall ist wichtig: Eine Antwort, die stimmt, aber nicht aus dem Wiki stammt, misst das Modell und nicht das Wiki. Sie zählt nicht.

Bei **Block B** gilt eine korrekte Zurückweisung als bestanden, auch wenn ausdrücklich markiertes Modellwissen ergänzt wurde. Nicht bestanden ist die Frage, wenn Modellwissen als Wiki-Inhalt präsentiert wird.

### Ausgabe

```markdown
## Benchmark — YYYY-MM-DD

**Block A (Wissen):** 13/15 korrekt, davon 11 korrekt belegt
**Block B (Out-of-Scope):** 5/5 korrekt zurückgewiesen

### Fehlschläge
- A7 — Antwort nannte das Datum nicht, Belegseite korrekt
- A12 — Antwort aus Modellwissen, kein Wiki-Beleg

### Vergleich zum Vorlauf
Block A: 13/15 (zuvor 12/15) · Block B: 5/5 (unverändert)
```

`log.md`-Eintrag:

```
- **Bench** — Wissen 13/15 korrekt (11 belegt), Out-of-Scope 5/5 zurückgewiesen
```

Ein Rückgang nach einer Schema-Änderung ist ein Befund über die Schema-Änderung, nicht über das Frageset.

---

## Grenzen

- Der Skill prüft **Belegtheit**, nicht fachliche Richtigkeit. Er ersetzt keine juristische Prüfung.
- Ohne Volltext in Zotero ist keine Prüfung möglich. Eine Seite als geprüft zu markieren, die nicht geprüft werden konnte, wäre schlimmer als gar keine Prüfung.
- Seiten mit `updated:` vor dem Einführungsdatum der Belegschicht (`[EINFÜHRUNGSDATUM]`, eigenes Datum eintragen) stehen unter Bestandsschutz und werden nur auf ausdrücklichen Trigger geprüft.
- Der Benchmark misst das Wiki, nicht das Modell. Er ist nur aussagekräftig, solange die Goldantworten dem Wiki-Stand folgen.
