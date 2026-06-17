# Vault Context

Dieses Vault ist das Zweite Gehirn von **[DEIN NAME]** ([DEIN FACHGEBIET, z.B. „Jurist:in mit Schwerpunkt Medien- und Datenschutzrecht"]).

> **Hinweis für Nachbauer:** Diese Datei ist die agnostische Kontext-/Instruktionsdatei für deinen KI-Agenten. Codex und OpenCode lesen sie als `AGENTS.md` nativ; für Claude Code und Gemini CLI per Symlink `CLAUDE.md`/`GEMINI.md → AGENTS.md` einbinden (siehe `template/agent-config/symlinks.sh`). Ersetze alle `[…]`-Platzhalter durch deine Angaben.

## Über mich

[Kurzprofil: Wer du bist, Fachgebiet, Schwerpunkte, Arbeitsweise. Der Agent liest diesen Abschnitt für inhaltliche Aufgaben (Texte, Anträge, Lehre). Ausführliches Profil optional in `00 Kontext/Über mich`.]

## Vault-Struktur

Das Vault folgt der PARA-Methode:

- **00 Kontext/**: Persönliches Kontext-Profil (z.B. Über mich, Schreibstil, Vorannahmen). Zentrale Referenz für inhaltliche Aufgaben.
- **01 Inbox/**: Schnelle Gedanken, Brain Dumps, unverarbeitete Notizen. Alles ohne festen Platz landet hier.
- **02 Projekte/**: Aktive Projekte mit konkretem Ziel und Enddatum. Projekte starten als einzelne .md Datei; Unterordner nur bei mehreren Dateien.
- **03 Bereiche/**: Laufende Verantwortungsbereiche ohne Enddatum. Jeder Bereich ein eigener Ordner.
- **04 Ressourcen/**: Referenzmaterial/Wissen nach Fachgebiet — **hier lebt das LLMWiki** (s.u.).
- **05 Daily Notes/**: Tägliches Logbuch. Gibt dem Agenten Kontinuität zwischen Sessions.
- **06 Archiv/**: Abgeschlossene Projekte und inaktive Bereiche.
- **07 Anhänge/**: Bilder, PDFs, Medien.

## Regeln für dieses Vault

- Nutze [[Wikilinks]] für Verknüpfungen zwischen Notizen
- Neue Notizen ohne klaren Platz kommen in 01 Inbox/
- Halte Notizen atomar: eine Idee pro Notiz wo möglich. Ausnahme: Daily Notes fassen einen ganzen Tag zusammen.
- Daily Notes im Format `YYYY-MM-DD.md`
- Nutze YAML Frontmatter: tags, status (aktiv/abgeschlossen/pausiert), date
- Dateinamen in normaler Schreibweise mit Leerzeichen und Großbuchstaben: `Beschreibender Name.md`
- Neue Projekte als einzelne .md Datei direkt unter 02 Projekte/; Unterordner nur bei Bedarf
- Bereiche und Ressourcen sind immer Ordner
- Abgeschlossene Projekte nach 06 Archiv/ verschieben — nur auf Anweisung des Nutzers, nicht eigenständig
- Wenn du Dateien erstellst oder verschiebst, erkläre kurz warum
- Bevor du Dateien löschst oder überschreibst, frag nach
- Wenn der Nutzer sagt „merk dir das"/„speicher das", speichere es dort, wo es thematisch hingehört: Schreibregeln nach `00 Kontext/`, Projekt-Infos in die Projekt-Datei, fachliche Erkenntnisse in `04 Ressourcen/`, Vault-Regeln in diese `AGENTS.md`. Im Zweifel kurz fragen.

## Session-Routinen

### Bei Session-Start
1. Prüfe 01 Inbox/ auf neue Notizen, zeige was drin liegt, und biete an, die Einträge einzusortieren.

### Kontext bei Bedarf
Bei Fragen wie „Was ist gerade aktuell?" / „Wo war ich stehen geblieben?": Lies die letzten 2–3 Daily Notes und die aktiven Projekt-Dateien für ein Briefing.

### Bei Session-Ende
Biete an: (1) Daily-Note-Eintrag mit Tageszusammenfassung, (2) neue Erkenntnisse als Notizen sichern, (3) Inbox aufräumen.

## LLMWiki

Der Bereich `04 Ressourcen/` enthält ein LLM-gepflegtes Wiki nach dem Karpathy-LLMWiki-Muster. Zotero dient als unveränderlicher Rohdaten-Speicher. Der Agent schreibt und pflegt alle Wiki-Seiten autonom. Technische Details in `04 Ressourcen/wiki-schema.md` — diese Datei bei jedem Ingest lesen.

### Wiki-Themenordner
Lege deine eigenen Themenordner unter `04 Ressourcen/` an — je ein Ordner pro Fachgebiet — und trage sie hier ein:
`[Thema 1]` · `[Thema 2]` · `[Thema 3]` · …

Eigene Nicht-Wiki-Ordner (z.B. `Persönlich/`, `Werkzeuge/`) sind **nicht** Teil des Wikis.

### Ingest-Trigger

| Befehl | Verhalten |
|---|---|
| `ingest @citekey` | Holt genau diese Zotero-Quelle (Metadaten, Abstract, Annotationen) und verarbeitet sie |
| `Wiki aktualisieren` | Bulk-Ingest: liest letztes Datum aus `04 Ressourcen/log.md`, holt alle neueren Zotero-Einträge |
| `Aktualisiere Wiki: [Thema]` | Sucht Zotero nach diesem Thema/Tag, verarbeitet alle Treffer |
| `lint wiki` | Prüft Wiki-Integrität mit Schweregrad-Klassifikation — Details in `wiki-schema.md` |
| `query wiki: [Frage]` | Durchsucht `04 Ressourcen/` (Index + Grep), synthetisiert Antwort mit [[Wikilinks]], bietet Synthese-Seite an |

### Ingest-Ablauf (immer gleich, unabhängig vom Trigger)
1. `04 Ressourcen/wiki-schema.md` lesen
2. Zotero MCP-Server: Metadaten + Abstract per `get_item_by_key`; Volltext per `get_pdf_content`; Annotationen per `get_item_annotations`. Bei `ingest @citekey`: zuerst `search` mit q=citekey → Item-Key, dann `get_item_by_key`.
3. `04 Ressourcen/index.md` lesen — existierende Wiki-Seiten prüfen
4. Betroffene Konzepte/Entitäten identifizieren, Themenordner bestimmen
5. Wiki-Seiten schreiben/aktualisieren (max. ~15 pro Ingest), [[Wikilinks]] setzen
6. `04 Ressourcen/index.md` aktualisieren
7. `04 Ressourcen/log.md` Eintrag anhängen

### Neue Themenordner
Neuen Ordner anlegen, wenn eine Quelle keinem bestehenden Ordner sinnvoll zugeordnet werden kann (mind. 2–3 Konzepte). Dann: Hub-Datei `[Thema].md` erstellen, Ordner in `wiki-schema.md`-Themenliste, `index.md` und diese `AGENTS.md`-Liste ergänzen, in `log.md` dokumentieren. Bei Grenzfällen kurz beim Nutzer rückfragen.

### Token-Budget
Falls das Kontext-Limit absehbar erreicht wird: Stand in `log.md` mit `[unterbrochen nach N Quellen, N ausstehend]` dokumentieren, den Nutzer informieren. Nächste Session setzt nahtlos fort.

### Wiki-Seiten-Kennzeichen
Alle Wiki-Seiten haben `type: wiki-page` im Frontmatter. Quellenüberblick-Seiten aus dem Zotero-Import-Template (`tags: [literatur]`) sind **keine** Wiki-Seiten.

### Normknoten und Leitentscheidungen
Leitnormen (Artikel/Paragraphen) und Grundsatzentscheidungen erhalten eigene Anker-Seiten (`wiki-category: entitaet`, mit `rang:`; bei Urteilen zusätzlich `ecli:`). Konzeptseiten verlinken auf diese Knoten, statt Normen nur im Fließtext zu nennen — die Backlinks ersetzen die SPARQL-Abfrage eines klassischen Wissensgraphen. Beim Ingest juristischer Quellen: betroffene Normen/Urteile in den Frontmatter-Feldern `normen:`/`urteile:`/`rechtsgebiet:` führen und auf vorhandene Normknoten verlinken. Fehlt der Knoten und wird die Norm in ≥3 Seiten zitiert → Knoten anlegen. Beziehungen mit typisiertem Relationsvokabular (setzt um / verdrängt / konkretisiert / wendet an — Details in `wiki-schema.md`). **ECLI niemals erfinden.**

### Rechtshierarchie-Annotation
Rechtlich fundierte Aussagen werden mit einem `[!recht]`-Callout annotiert (steht *unter* der Aussage). Format: `⚖️ Rang [N] ([Normkategorie]) · [Gericht/Norm] → [Referenz]`. Rang folgt der Norm, nicht dem Gericht (6-stufige Hierarchietabelle in `wiki-schema.md`). Nur bei konkreten Normen/Entscheidungen setzen — nicht bei allgemeinen Literaturmeinungen.
