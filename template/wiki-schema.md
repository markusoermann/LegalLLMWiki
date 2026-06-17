---
type: wiki-schema
updated: 2026-06-17
---

# Wiki Schema

Technische Referenz für Claude. Wird bei jedem Ingest gelesen.

## Frontmatter-Schema

Pflichtfelder für alle Wiki-Seiten:

```yaml
---
type: wiki-page
wiki-category: konzept | entitaet | synthese
thema: [Thema1, Thema2]
quellen: ["@citekey1", "@citekey2"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
rechtsstand: YYYY-MM-DD   # optional; nur bei Seiten mit zeitkritischem juristischen Inhalt
---
```

### Optionale juristische Felder

Nur bei Seiten mit Rechtsbezug. Machen Normen und Entscheidungen maschinenlesbar abfragbar (ergänzen den `quellen:`-Mechanismus um die juristische Dimension).

```yaml
normen:            # maschinenlesbare Normreferenzen, je eine pro Zeile
  - "DSGVO Art. 6 Abs. 1 lit. f"
  - "EU AI Act Art. 10 Abs. 5"
urteile:           # Gerichtsentscheidungen, ECLI bevorzugt, sonst Fundstelle
  - "ECLI:DE:BVerfG:1983:rs19831215.1bvr020983"
  - "BVerfGE 65, 1"
rechtsgebiet:      # Rechtsgebiet-Klassifikation
  - Datenschutzrecht
  - KI-Recht
rang:              # nur bei Normknoten-/Leitentscheidungs-Seiten: 1–6 (s. Rechtshierarchie)
ecli:              # nur bei Leitentscheidungs-Seiten: ECLI-Identifikator
resource:          # optional: stabile URI des zugrunde liegenden Rechts-Assets (ELI/ECLI/DOI)
```

**Normalisierung:** Norm-Strings einheitlich als `<Gesetz> Art./§ <N> Abs. <N> lit. <x>` (Gesetz zuerst), damit Backlinks und Abfragen nicht zersplittern. ECLI-Werte niemals erfinden — nur verifizierte Identifikatoren; sonst nur Fundstelle führen.

**`resource:` (stabile Asset-URI, OKF-Empfehlungsfeld).** Verweist auf die maschinenlesbare Primärquelle der Seite. Konventionen:
- **Normknoten:** ELI-URI — EU-Recht über `http://data.europa.eu/eli/…` (z.B. DSGVO: `http://data.europa.eu/eli/reg/2016/679/oj`), Bundesrecht über `https://recht.bund.de/eli/…`.
- **Leitentscheidungs-Seiten:** ECLI-Resolver — EuGH/EU über EUR-Lex (`https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=ecli:<ECLI>`), deutsche Gerichte über `https://www.rechtsprechung-im-internet.de` bzw. den ECLI-Resolver.
- **Quellen-/Konzeptseiten:** DOI (`https://doi.org/…`) oder Zotero-Select-Link.
- URIs nur setzen, wenn verifiziert (kein Erfinden, analog ECLI-Regel).

## Seiten-Typen

### Konzept-Seite
- Namensschema: `[Begriff].md` (z.B. `Algorithmische Verantwortung.md`)
- Eine Seite pro Konzept/Fachbegriff
- `wiki-category: konzept`

### Entitäts-Seite
- Namensschema: `[Name].md` (z.B. `EU AI Act.md`, `Balkin Jack.md`)
- Für: Personen (Nachname Vorname), Gesetze/Verordnungen (offizielle Abkürzung), Institutionen
- `wiki-category: entitaet`

### Normknoten-Seite
- Spezialform der Entitäts-Seite für eine einzelne Leitnorm (Artikel/Paragraph)
- Namensschema: `[Gesetz] [Norm].md` (z.B. `DSGVO Art. 6.md`, `MStV § 93.md`)
- `wiki-category: entitaet`, zusätzlich `rang:` (1–6) gesetzt
- Struktur: Definition · Absätze/Tatbestandsmerkmale (mit Wikilinks zu Konzeptseiten) · Leitentscheidungen · Verhältnis zu anderen Normen
- Zweck: Anker-Knoten — Konzeptseiten verlinken hierauf; Backlinks ersetzen die SPARQL-Abfrage des KG-Konzepts
- Abgrenzung zur Gesetz-Entität: `DSGVO.md` beschreibt die Verordnung als Ganzes; `DSGVO Art. 6.md` ist der granulare Normknoten und verlinkt auf die Gesetz-Seite

### Leitentscheidungs-Seite
- Spezialform der Entitäts-Seite für eine Grundsatzentscheidung
- Namensschema: `[Kurzbezeichnung].md` (z.B. `BVerfGE 65,1 (Volkszählungsurteil).md`)
- `wiki-category: entitaet`, zusätzlich `rang:`, `ecli:` (wo verifiziert vorhanden), `rechtsstand:`
- Struktur: Leitsatz · Tragende Erwägungen · Bezug zu Normen (Wikilinks) · Nachfolge-/Vorgängerentscheidungen
- Zweck: Anker-Knoten für Rechtsprechung; verknüpft Normknoten mit Konzeptseiten

### Synthese-Seite
- Namensschema: `Synthese - [Thema].md` (z.B. `Synthese - Plattformregulierung.md`)
- Themenübergreifende Zusammenführung mehrerer Quellen
- `wiki-category: synthese`

## Seiten-Template

```markdown
---
type: wiki-page
wiki-category: [konzept|entitaet|synthese]
thema: [Thema]
quellen: ["@citekey"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# [Titel]

## Definition / Überblick

## Kernaspekte

## Bezüge & Kontroversen

## Verwandte Konzepte
[[Wikilink1]] · [[Wikilink2]]

## Quellen
[[@citekey1]], [[@citekey2]]
```

## Tiefenstandard

Wiki-Seiten sollen wissenschaftlich substanziell sein — nicht nur zusammenfassen, sondern einordnen, differenzieren und vernetzen.

**Definition / Überblick:** Mindestens ein vollständiger Absatz (4–6 Sätze). Systematische Einordnung (Rechtsgebiet, Normebene), Herkunft/Geschichte des Konzepts, Abgrenzung zu verwandten Begriffen.

**Kernaspekte:** Mindestens 3 benannte Unterabschnitte mit je 3–5 Sätzen. Konkrete Normbezüge (Artikel, Paragraphen), Tatbestandsmerkmale, Rechtsfolgen. Jede zentrale Aussage belegt — entweder mit `[!recht]`-Callout (bei Rechtsnormen/Urteilen) oder mit Quellenangabe.

**Bezüge & Kontroversen:** Mindestens 2 konkrete Diskussionspunkte oder Abgrenzungsfragen. Wo relevant: Gegenansichten, offene Rechtsfragen, Reformdiskussionen, Spannungsverhältnisse zu anderen Rechtsbereichen.

**Verwandte Konzepte:** Mindestens 3 Wikilinks, davon mindestens einer themenübergreifend (in andere Wiki-Ordner).

## Rechtshierarchie-Annotation

Aussagen in Wiki-Seiten, die sich direkt auf eine Rechtsnorm oder Gerichtsentscheidung stützen, werden mit einem Obsidian-Callout annotiert. Der Callout steht *unter* der jeweiligen Aussage im Fließtext.

### Format

```
> [!recht] ⚖️ Rang [N] ([Normkategorie]) · [Gericht/Norm] → [Referenz]
> [Optionaler Kurzkommentar zur Verbindlichkeit oder Einordnung]
```

Beispiele:

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSA Art. 33 Abs. 1
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 17.02.2023.

> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 65, 1 → Art. 2 Abs. 1 GG
> Volkszählungsurteil; Grundlage des Rechts auf informationelle Selbstbestimmung.

> [!recht] ⚖️ Rang 5 (Bundesgesetz) · BGH I ZR 69/08 → UrhG § 97
```

### Rechtshierarchie (6 Ränge, normzentriert)

| Rang | Normkategorie | Beispiel-Normen | Entscheidungen in diesem Rang |
|---|---|---|---|
| 1 | EU-Primärrecht | AEUV, EUV, GRC | EuGH zu Grundfreiheiten und GRC |
| 2 | EU-Sekundärrecht — Verordnung | DSGVO, DSA, DMA, AI Act | EuGH, BVerfG, BGH zu diesen VO |
| 3 | EU-Sekundärrecht — Richtlinie (umgesetzt) | AVMD-RL, NIS2-RL | EuGH, BGH zu umgesetzten RL |
| 4 | Deutsches Verfassungsrecht | GG, Landesverfassungen | BVerfG, VerfGH zu GG-Normen |
| 5 | Bundesgesetz / Staatsvertrag | TKG, TTDSG, UrhG, MStV | BGH, BVerwG, OLG zu Bundesgesetzen |
| 6 | Landesgesetz / Rechtsverordnung | LPG, LRfG, Landes-VO | OVG, VGH, LG zu Landesrecht |

Der Rang folgt der Norm, nicht dem Gericht. Ein BVerfG-Urteil zu Art. 5 GG ist Rang 4; ein EuGH-Urteil zur DSGVO ist Rang 2.

### Wann annotieren

- ✅ Bei Aussagen, die sich direkt auf eine konkrete Norm oder Entscheidung zurückführen lassen
- ✅ Bei Definitionen oder Tatbestandsmerkmalen aus Gesetzen
- ❌ Nicht bei allgemeinen Zusammenfassungen oder Literaturmeinungen
- ❌ Nicht bei jeder Aussage auf einer Seite — nur bei rechtlich fundierten Kernaussagen

## Typisierte Wikilinks (Relationsvokabular)

Rechtliche Beziehungen zwischen Knoten werden im Fließtext mit einem kontrollierten Relationsverb vor dem Wikilink ausgedrückt. Lesbar für Menschen, grep-bar für `query wiki`. Übernimmt die typisierten Kanten des KG-Konzepts (setzt_um, ändert, konkretisiert) Obsidian-nativ ohne Schema-Overhead.

Kontrolliertes Vokabular:

- **setzt um** — Richtlinie → Umsetzungsgesetz
- **ändert** / **hebt auf** — Novellierung/Aufhebung
- **verdrängt** — Anwendungsvorrang (lex superior/posterior)
- **konkretisiert** — Rechtsprechung präzisiert ältere Entscheidung/Norm
- **definiert** — Norm definiert einen Begriff
- **wendet an** — Entscheidung wendet eine Norm an
- **zitiert** — allgemeiner Verweis

Beispiel:

> Der DSA **verdrängt** [[NetzDG]] §§ 2, 3 (seit 17.02.2024); das österr. KoPl-G-Analogon ist europarechtswidrig laut [[EuGH C-376-22 (KoPl-G)]].

## Rechtliche Aktualität und Normersetzung

### Grundregel

Das Wiki spiegelt immer den **aktuellen Rechtsstand** wider — es ist kein historisches Archiv. Wenn eine neu ingested Quelle eine bereits dokumentierte Norm oder Entscheidung ablöst, modifiziert oder verdrängt, werden die betroffenen Wiki-Seiten im selben Ingest-Durchgang aktualisiert. Neuere Rechtslage überschreibt ältere Inhalte; veraltete Callouts werden entsprechend gekennzeichnet.

### Vier Supersessionstypen

| Typ | Auslöser | Beispiel | Konsequenz |
|---|---|---|---|
| **Vollständige Ablösung** | Neue Norm ersetzt alte vollständig (Aufhebungsklausel) | MStV (2020) ersetzt RStV | Callout um Hinweis ergänzen: `→ aufgehoben durch [X] seit [Datum]` |
| **Partielle Verdrängung** | EU-Verordnung mit Anwendungsvorrang (lex posterior/superior) | DSA Art. 15, 16 verdrängen NetzDG § 2, § 3 Abs. 2 | Verdrängten Teil im Callout markieren; verbliebenen Restanwendungsbereich dokumentieren |
| **Novellierung** | Geänderte Fassung einer bestehenden Norm | AVMD-RL 2018/1808 ändert AVMD-RL 2010/13/EU | Neue Fassung ist maßgeblich; Fassung/Datum im Callout führen (`i.d.F. [Jahr]`) |
| **Rechtsprechungsänderung** | Neueres Urteil klärt, präzisiert oder revidiert ältere Entscheidung | BVerfGE 158, 389 konkretisiert BVerfGE 149, 222 | Neueres Urteil primär zitieren; älteres Urteil mit Kontexthinweis auf Nachfolgeentscheidung versehen |

### Ingest-Pflicht: Normersetzungsprüfung

Bei jedem Ingest einer juristischen Quelle (Gesetz, Verordnung, Urteil, Kommentar) **vor dem Schreiben**:

1. **Identifikation** — Welche älteren Normen oder Entscheidungen werden durch die neue Quelle abgelöst, abgeändert oder verdrängt? Auf Signalformulierungen im Quelltext achten: „ersetzt", „aufgehoben", „tritt an die Stelle von", „verdrängt", „Anwendungsvorrang", „gilt nicht mehr", „überholt durch".
2. **Wiki-Scan** — `index.md` und betroffene Wiki-Seiten auf Callouts und Fließtextstellen prüfen, die die supersedierte Norm/Entscheidung zitieren.
3. **Update** — Betroffene Seiten im selben Ingest-Durchgang aktualisieren (Callouts kennzeichnen, Fließtext bei wesentlichen inhaltlichen Änderungen anpassen, `updated`- und `rechtsstand`-Datum setzen).

### Callout-Kennzeichnung abgelöster Normen

Vollständig aufgehobene oder ersetzte Norm:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · NetzDG § 2 i.d.F. 2021
> ⚠️ Verdrängt durch DSA Art. 15 Abs. 1 mit Wirkung ab 17.02.2024.
```

Teilweise verdrängte Norm mit verbleibendem Restanwendungsbereich:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · NetzDG § 3 Abs. 2 i.d.F. 2021
> Weitgehend verdrängt durch DSA Art. 16 Abs. 6 (seit 17.02.2024).
> Restanwendungsbereich: § 3a NetzDG (Meldepflicht staatsschützende Straftatbestände) bleibt eigenständig anwendbar.
```

Präzisierte oder revidierte Gerichtsentscheidung:

```
> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 149, 222 (Rundfunkbeitrag, 2018)
> Durch BVerfGE 158, 389 (Sachsen-Anhalt, 2021) in der Frage der Mitverantwortungspflicht der Länder konkretisiert.
```

### rechtsstand-Frontmatter-Feld

Das optionale Feld `rechtsstand: YYYY-MM-DD` markiert, bis zu welchem Datum die Rechtslage einer Seite vollständig geprüft wurde. Es wird gesetzt oder aktualisiert, wenn im Rahmen eines Ingest eine vollständige Normersetzungsprüfung für diese Seite durchgeführt wurde. Fehlt das Feld, gilt die Seite als bzgl. Aktualität ungeprüft.

Das Feld wird **nicht** bei jeder inhaltlichen Ergänzung gesetzt — nur nach expliziter Aktualitätsprüfung. Es hat keinen Einfluss auf `updated`, das bei jeder inhaltlichen Änderung fortgeschrieben wird.

## Thematische Ordner (Wiki-Bereich)

Anpassbarer juristischer Default — ersetze/ergänze durch deine eigenen Fachgebiete:

- `04 Ressourcen/Jura/` (z.B. inkl. `Jura/Kommunikationsrecht/` für medienrechtliche Seiten)
- `04 Ressourcen/KI/`
- `04 Ressourcen/Governance/`
- `04 Ressourcen/Digitalisierung/`
- `04 Ressourcen/Praktische Philosophie/` (inkl. `Ethik/`)
- `04 Ressourcen/Politikwissenschaft/`

Eigene Nicht-Wiki-Ordner (z.B. `Persönlich/`, `Werkzeuge/`) bleiben außen vor.

## Zotero MCP-Tools (Referenz)

Für den Ingest wird ausschließlich der Zotero MCP-Server genutzt (Port 23120). Die Tools sind direkt als `mcp__zotero__*` aufrufbar.

| Tool | Verwendung im Ingest |
|---|---|
| `search` | Item zu @citekey oder Thema finden; liefert Item-Key |
| `find_item_by_identifier` | Item per DOI oder ISBN finden |
| `get_item_by_key` | Vollständige Metadaten, Abstract, Attachment-Liste, Notizen |
| `get_pdf_content` | PDF-Volltext extrahieren (Parameter: `itemKey`, optional `page`) |
| `get_item_annotations` | PDF-Highlights & Annotationen eines Items |
| `get_item_notes` | Zotero-Notizen eines Items |
| `search_annotations` | Annotationssuche über die gesamte Bibliothek |
| `get_collections` | Alle Kollektionen auflisten (für Bulk-Ingest) |
| `get_collection_items` | Alle Items einer Kollektion |
| `get_annotations_batch` | Mehrere Annotationen auf einmal abrufen |

**Fallback auf lokale API (Port 23119):** Nur wenn der MCP-Server nicht antwortet (Zotero-Plugin nicht aktiv). Dann wie bisher per HTTP-Calls via Python/curl.

## Ingest-Checkliste

Vor dem Schreiben:
- [ ] `04 Ressourcen/index.md` gelesen?
- [ ] Betroffene Themenordner identifiziert?
- [ ] Prüfen: gibt es bereits eine Seite für dieses Konzept/diese Entität?
- [ ] **Volltext-Check:** Anhänge über Zotero MCP `get_item_by_key` abrufen (liefert `attachments`-Feld mit `contentType`): `application/pdf` → PDF per `get_pdf_content`, `text/html` → HTML-Snapshot via Read-Tool (`~/Zotero/storage/[ATTKEY]/`)
- [ ] **Normersetzungsprüfung (juristische Quellen):** Enthält die Quelle Normen oder Entscheidungen, die bereits dokumentierte Wiki-Inhalte ablösen, abändern oder verdrängen? → Betroffene Wiki-Seiten über `index.md` identifizieren; Update erfolgt im Schritt „Seiten schreiben/aktualisieren" (s. Abschnitt *Rechtliche Aktualität und Normersetzung*)

Quellenlesen (Standard — immer vor dem Schreiben):
- [ ] Metadaten + Abstract per Zotero MCP `get_item_by_key` gelesen?
- [ ] **PDF vorhanden?** (`contentType: application/pdf`) → Volltext per `get_pdf_content` (MCP) abrufen:
  - Artikel/Kapitel: vollständig lesen (ohne `page`-Parameter = gesamtes Dokument)
  - Bücher: Inhaltsverzeichnis (S. 1–5, `page: 1`) + relevante Kapitel (Seiten per `page`-Parameter, je Aufruf 1 Seite)
  - Annotations per `get_item_annotations` (MCP) auswerten
- [ ] **Kein PDF, aber HTML-Snapshot vorhanden?** (`contentType: text/html`) → Volltext lesen mit Read-Tool (`~/Zotero/storage/[ATTKEY]/`):
  - HTML-Datei vollständig lesen; HTML-Tags beim Auswerten ignorieren
  - Wie PDF behandeln: vollständig für Artikel, selektiv für längere Dokumente
  - Annotations per `get_item_annotations` (MCP) auswerten
- [ ] Weder PDF noch HTML? → Aus Metadaten, Abstract und eigenem Fachwissen arbeiten; im log.md vermerken: `[kein Volltext]`

Beim Schreiben:
- [ ] Inhalt basiert auf tatsächlichem Quelltext, nicht nur auf Titelkenntnis
- [ ] Konkrete Seitenangaben oder Kapitelreferenzen wo möglich eingebaut
- [ ] Frontmatter vollständig (alle Pflichtfelder)?
- [ ] Cross-Links mit [[Wikilinks]] gesetzt?
- [ ] Bestehende atomare Notizen im selben Ordner auf Verlinkbarkeit geprüft?
- [ ] `updated`-Datum aktualisiert?

Nach dem Schreiben:
- [ ] `04 Ressourcen/index.md` aktualisiert?
- [ ] `04 Ressourcen/log.md` Eintrag angehängt? (inkl. `[kein PDF]` falls zutreffend)
- [ ] Neuer Ordner angelegt? → Dann auch CLAUDE.md und wiki-schema.md Themenordner-Liste aktualisieren

## Lint-Spezifikation

`lint wiki` führt einen vollständigen Integritäts-Audit durch. Befunde werden nach Schweregrad klassifiziert.

### Schweregrade

| Schweregrad | Bedeutung | Beispiele |
|---|---|---|
| **Fehler** | Strukturell kaputt, muss behoben werden | Broken Wikilinks, Index-Einträge ohne Datei |
| **Warnung** | Qualitätsproblem, sollte behoben werden | Orphan-Seiten, stale claims, missing pages |
| **Info** | Verbesserungspotenzial | Fehlende Cross-Links, data gaps |

### Checks

**Fehler:**
- [ ] **Broken Wikilinks** — `[[Seite]]`-Verweise auf nicht existierende Dateien. **Beim Parsen das echte Linkziel isolieren**, bevor gegen Dateien geprüft wird: Alias nach `|` *und* nach escaptem `\|` (Pflicht-Escaping in Markdown-Tabellen!) abtrennen, `#`-Sprungmarken abtrennen, Pfad auf letztes Segment reduzieren. Sonst entstehen Fehlalarme bei Tabellen-Links wie `[[Antrag X\|Alias]]` und Anker-Links wie `[[Seite#Abschnitt]]`.
- [ ] **Index-Konsistenz** — Einträge in `index.md` ohne zugehörige Datei (und umgekehrt: Dateien mit `type: wiki-page` die nicht in `index.md` stehen)

**Warnungen:**
- [ ] **Orphan-Seiten** — Wiki-Seiten mit `type: wiki-page` die von keiner anderen Seite verlinkt werden
- [ ] **Stale claims** — Seiten mit `[!recht]`-Callouts zu Normen, die laut neueren Quellen (erkennbar aus `log.md`) abgelöst oder geändert wurden, ohne dass die Seite aktualisiert wurde
- [ ] **Missing pages** — Begriffe die in mehreren Seiten per `[[Wikilink]]` referenziert werden, aber keine eigene Datei haben
- [ ] **Norm ohne Knoten** — Normen in `normen:`-Frontmatter, die in ≥3 Seiten vorkommen, aber keine eigene Normknoten-Seite haben
- [ ] **Urteil ohne Knoten** — Urteile in `urteile:`-Frontmatter, die in ≥3 Seiten vorkommen, aber keine eigene Leitentscheidungs-Seite haben
- [ ] **Frontmatter-Drift** — Seite mit `[!recht]`-Callout zu einer Norm/Entscheidung, die nicht im `normen:`/`urteile:`-Frontmatter steht

**Info:**
- [ ] **Data gaps** — Wiki-Seiten mit weniger als 2 Quellen im `quellen:`-Frontmatter (Themen mit dünner Abdeckung)
- [ ] **Fehlende Cross-Links** — Seiten zum gleichen Thema ohne gegenseitige Verlinkung (erkennbar durch übereinstimmende `thema:`-Felder)
- [ ] **Seiten ohne Frontmatter** — Dateien in Wiki-Ordnern ohne `type: wiki-page`

### Ausgabeformat

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

Befunde in `log.md` mit Syntax `- **Lint** — N Fehler, N Warnungen, N Info` dokumentieren.

### Empfohlene Kadenz

Nach je 10 Ingests oder monatlich als Mindest-Wartung.

---

## Namenskonventionen

- Dateinamen: normale Schreibweise mit Leerzeichen und Großbuchstaben
- Personen: `Nachname Vorname.md` (z.B. `Balkin Jack.md`)
- Gesetze/Verordnungen: offizielle Kurzbezeichnung (z.B. `DSGVO.md`, `EU AI Act.md`, `MStV.md`)
- Institutionen: gebräuchlichste Kurzform (z.B. `Bundesnetzagentur.md`, `KEF.md`)
- Konzepte: Hauptbegriff, ggf. mit Klammer für Disambiguierung (z.B. `Verantwortung (KI).md`)

## log.md Syntax

Eintrag-Format:

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

Unterbrochene Sessions markieren mit:
`[unterbrochen nach N Quellen, N ausstehend]`

---

## Nicht-Wiki-Seitentypen

Neben den Wiki-Seiten (`type: wiki-page`) tragen alle übrigen `.md`-Dateien in `04 Ressourcen/` ebenfalls ein `type`-Feld (OKF-Anforderung, s.u.). Kontrolliertes Vokabular:

- `hub` — Themen-Hub-Seite (Dateiname == Ordnername, z.B. `KI/KI.md`)
- `quelle` — Zotero-/Literatur-Quellenüberblick (`tags: [literatur]`)
- `notiz` — sonstige Notizen (atomare Gedanken, Referenz-/Hilfsnotizen ohne Wiki-Seiten-Status)

Diese Typen sind **keine** Wiki-Seiten i.S.d. Tiefenstandards und werden von Lint-/Ingest-Routinen, die auf `type: wiki-page` filtern, nicht erfasst. `Persönlich/` und `Werkzeuge/` bleiben ganz außen vor.

## OKF-Kompatibilität (Google Open Knowledge Format v0.1)

Das Wiki ist bewusst weitgehend OKF-kompatibel gehalten (Knowledge-Austausch mit Dritten/Agenten).

- **Pflichtregel erfüllt:** Jede Nicht-Reserved-`.md` in `04 Ressourcen/` trägt ein nicht-leeres `type`-Feld. Alle übrigen Felder (`wiki-category`, `normen`, `urteile`, `rang`, `ecli`, `thema`, `quellen`) sind OKF-konforme Extensions — Consumer müssen unbekannte Keys tolerieren.
- **`resource:`** ist das OKF-Empfehlungsfeld für die Asset-URI (s. Frontmatter-Schema oben; ELI/ECLI/DOI).
- **Reserved Files:** `index.md` + `log.md` vorhanden. Hinweis: OKF sieht für `index.md` *kein* Frontmatter vor — unser `type: wiki-index` ist eine geduldete Abweichung. Optional kann im Root-`index.md` `okf_version: 0.1` deklariert werden.
- **Bewusste Divergenz — Links:** Wir nutzen Obsidian-`[[Wikilinks]]` statt OKF-Standard-Markdown-Links (`[Text](/pfad.md)`). OKF toleriert das (Links werden als „broken" geduldet, Relationssemantik liegt ohnehin im Fließtext). Für einen echten OKF-Export wäre eine Build-Pipeline (Wikilinks → Markdown-Links) der richtige Weg — nicht die Umstellung des Vaults.
