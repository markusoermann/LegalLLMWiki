# Vault Context

Dieses Vault ist das Zweite Gehirn von **[DEIN NAME]** ([DEIN FACHGEBIET, z.B. „Jurist:in mit Schwerpunkt Medien- und Datenschutzrecht"]).

> **Hinweis für Nachbauer:** Diese Datei ist die agnostische Kontext-/Instruktionsdatei für deinen KI-Agenten. Codex und OpenCode lesen sie als `AGENTS.md` nativ; für Claude Code und Gemini CLI per Symlink `CLAUDE.md`/`GEMINI.md → AGENTS.md` einbinden (siehe `template/agent-config/symlinks.sh`). Ersetze alle `[…]`-Platzhalter durch deine Angaben — insbesondere `[WIKI-ORDNER]` (s.u.).

## Über mich

[Kurzprofil: Wer du bist, Fachgebiet, Schwerpunkte, Arbeitsweise. Der Agent liest diesen Abschnitt für inhaltliche Aufgaben (Texte, Anträge, Lehre). Ausführliches Profil optional in einer eigenen Notiz.]

## Ordnerstruktur

Du legst deine Ordnerstruktur **selbst** fest — es wird keine bestimmte Methode vorgeschrieben. Das LLMWiki benötigt nur **einen Wiki-Ordner**, dessen Ort du frei wählst. Trage ihn hier ein und ersetze im Folgenden überall `[WIKI-ORDNER]` durch diesen Pfad:

- **`[WIKI-ORDNER]/`** — enthält `wiki-schema.md`, `index.md`, `log.md` sowie alle Wiki-Seiten (s. „LLMWiki" unten). Frei wählbar, z.B. `Wiki/`, `Ressourcen/` oder `.` (Vault-Root).

Alle weiteren Ordner sind optional und ganz dir überlassen (z.B. für Inbox, Projekte, tägliche Notizen, Archiv, Anhänge). Die Routinen und Regeln unten greifen jeweils nur, soweit du solche Ordner führst. Eine verbreitete (nicht erforderliche) Konvention ist [PARA](https://fortelabs.com/blog/para/).

## Regeln für dieses Vault

- Nutze [[Wikilinks]] für Verknüpfungen zwischen Notizen
- Halte Notizen atomar: eine Idee pro Notiz wo möglich (Ausnahme: Tageszusammenfassungen)
- Nutze YAML Frontmatter: tags, status (aktiv/abgeschlossen/pausiert), date
- Dateinamen in normaler Schreibweise mit Leerzeichen und Großbuchstaben: `Beschreibender Name.md`
- Tägliche Notizen (falls genutzt) im Format `YYYY-MM-DD.md`
- Wenn du Dateien erstellst oder verschiebst, erkläre kurz warum
- Bevor du Dateien löschst oder überschreibst, frag nach
- Dateien verschieben/archivieren nur auf Anweisung des Nutzers, nicht eigenständig
- Wenn der Nutzer sagt „merk dir das"/„speicher das": fachliche Erkenntnisse ins Wiki (`[WIKI-ORDNER]/`), Vault-Regeln in diese `AGENTS.md`, alles andere dort, wo es thematisch passt. Im Zweifel kurz fragen.

## Session-Routinen

### Bei Session-Start
Falls du einen Ordner für unsortierte Notizen (Inbox o.Ä.) führst: prüfe ihn auf neue Einträge, zeige was drin liegt, und biete an, sie einzusortieren.

### Kontext bei Bedarf
Bei Fragen wie „Was ist gerade aktuell?" / „Wo war ich stehen geblieben?": Lies — soweit vorhanden — die letzten Tagesnotizen und die aktiven Projekt-Dateien für ein Briefing.

### Bei Session-Ende
Biete an: (1) eine Tageszusammenfassung zu notieren (falls du Daily Notes führst), (2) neue Erkenntnisse als Wiki-/Notiz-Seiten zu sichern, (3) Unsortiertes aufzuräumen.

## LLMWiki

Der Ordner `[WIKI-ORDNER]/` enthält ein LLM-gepflegtes Wiki nach dem Karpathy-LLMWiki-Muster. Zotero dient als unveränderlicher Rohdaten-Speicher. Der Agent schreibt und pflegt alle Wiki-Seiten autonom. Technische Details in `[WIKI-ORDNER]/wiki-schema.md` — diese Datei bei jedem Ingest lesen.

**Single Point of Truth:** Das LLMWiki ist die verbindliche Wissensreferenz dieses Vaults. Andere (inhaltsgenerierende) Skills konsultieren es vor dem Arbeiten, nutzen seine Inhalte vorrangig, belegen mit [[Wikilinks]] und schlagen Ergänzungen via `ingest` vor.

### Wiki-Themenordner
Lege deine eigenen Themenordner unter `[WIKI-ORDNER]/` an — je ein Ordner pro Fachgebiet — und trage sie hier ein:
`[Thema 1]` · `[Thema 2]` · `[Thema 3]` · …

Eigene Nicht-Wiki-Ordner sind **nicht** Teil des Wikis. `Workflows/` ist ein **Infrastruktur-Ordner** und kein Themenordner: Dort liegen aufrufbare Verfahrensseiten (`type: wiki-workflow`), die von thematischen Auswertungen und vom Tiefenstandard nicht erfasst werden.

### Ingest-Trigger

| Befehl | Verhalten |
|---|---|
| `ingest @citekey` | Holt genau diese Zotero-Quelle (Metadaten, Abstract, Annotationen) und verarbeitet sie |
| `Wiki aktualisieren` | Bulk-Ingest: liest letztes Datum aus `[WIKI-ORDNER]/log.md`, holt alle neueren Zotero-Einträge |
| `Aktualisiere Wiki: [Thema]` | Sucht Zotero nach diesem Thema/Tag, verarbeitet alle Treffer |
| `lint wiki` | Prüft Wiki-Integrität mit Schweregrad-Klassifikation — Details in `wiki-schema.md` |
| `query wiki: [Frage]` | Durchsucht `[WIKI-ORDNER]/` (Index + Grep), synthetisiert Antwort mit [[Wikilinks]], bietet Synthese-Seite an |
| `verify wiki [Seite\|Thema\|letzter Ingest]` | Verifikations-Pass: frischer Subagent prüft jede Aussage gegen ihre Quellenstelle, markiert Unbelegtes, entfernt Hard-Fails |
| `bench wiki` | Führt den Gold-Benchmark aus `[BENCHMARK-ORT]/benchmark.md` aus (Wissensfragen und Out-of-Scope-Fragen) |
| `workflow: [Name]` | Liest die Workflow-Seite `[WIKI-ORDNER]/Workflows/Workflow - [Name].md` und arbeitet sie Schritt für Schritt ab |

### Ingest-Ablauf (immer gleich, unabhängig vom Trigger)
1. `[WIKI-ORDNER]/wiki-schema.md` lesen
2. Zotero MCP-Server (nativer Endpoint `http://127.0.0.1:23120/mcp`): Metadaten + Abstract per `get_item_details` (bzw. `get_item_abstract`); Volltext per `get_content` (`mode: "complete"` = ganzes Dokument, kein `page`-Parameter); Annotationen per `get_annotations`. Bei `ingest @citekey`: zuerst `search_library` mit q=citekey → `itemKey`, dann `get_item_details`.
3. `[WIKI-ORDNER]/index.md` lesen — existierende Wiki-Seiten prüfen
4. Betroffene Konzepte/Entitäten identifizieren, Themenordner bestimmen
5. Wiki-Seiten schreiben/aktualisieren (max. ~15 pro Ingest), [[Wikilinks]] setzen und **Locator setzen**: `Beleg:`-Zeile im `[!recht]`-Callout bei juristischen Aussagen, sonst Inline-Locator `(@citekey, S. N)`
6. **Verifikations-Pass:** frischer Subagent prüft jede Aussage gegen ihre Quellenstelle, markiert Unbelegtes mit `[!unbelegt]`, entfernt Hard-Fails, setzt bei sauberem Befund `verifiziert:` (Details in `wiki-schema.md`)
7. `[WIKI-ORDNER]/index.md` aktualisieren
8. `[WIKI-ORDNER]/log.md` Eintrag anhängen

Bei großen Ingests (mehr als 3 Quellen oder Einzelquellen mit mehr als ~50 Seiten Volltext) den Ablauf in Sub-Agenten mit JSON-Handoff zerlegen, statt alles in ein Kontextfenster zu laden (Abschnitt *Ingest-Dekomposition* in `wiki-schema.md`).

### Belegdisziplin
Jede Kernaussage trägt ihren eigenen Locator: bei juristischen Aussagen eine `Beleg:`-Zeile im `[!recht]`-Callout (`Beleg: @citekey S. 142 Rn. 18`), sonst einen Inline-Locator am Satzende (`(@citekey, S. 14)`). Stützt sich eine Aussage unmittelbar auf den Normtext, genügt der Normverweis im Callout. Der Verifikations-Pass prüft anschließend jede Aussage gegen ihre Quellenstelle. **Geprüft wird Belegtheit, nicht Richtigkeit.** Aussagen, die die Prüfung nicht bestehen und nicht korrigiert werden können, werden mit `[!unbelegt]` markiert statt stillschweigend behalten; erfundene ECLI, Normbezeichnungen, Fundstellen oder citekeys werden entfernt. Details in `wiki-schema.md`.

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

### Wiki-MCP-Server
Das Wiki lässt sich zusätzlich als lokaler MCP-Server einbinden: read-only, Kommunikation über stdio, kein Netzwerk-Port und kein Zugriff von außen. Sieben Tools:

| Tool | Zweck |
|---|---|
| `wiki_info` | Kennzahlen und Konfiguration des Wikis |
| `search_wiki` | Volltextsuche über alle Wiki-Seiten |
| `get_page` | Eine Seite mit Frontmatter und Inhalt |
| `get_norm` | Normknoten zu einer Normreferenz |
| `get_backlinks` | Eingehende Wikilinks einer Seite |
| `list_unverified` | Seiten ohne `verifiziert:`-Feld |
| `list_stale` | Seiten mit veraltetem `rechtsstand:` |

Einrichtung und Details in `docs/de/08-mcp-server.md`.
