# 06 · Juristische Features

Was LegalWikiLLM von einem generischen LLMWiki unterscheidet. Technische Details in `template/wiki-schema.md`.

## Normknoten & Leitentscheidungen
Leitnormen (Artikel/Paragraphen) und Grundsatzentscheidungen bekommen **eigene Anker-Seiten** (`wiki-category: entitaet`). Konzeptseiten verlinken darauf — die **Backlinks** dieser Knoten sind der Abfragepfad (ersetzen SPARQL). Beispiele: `template/examples/DSGVO Art. 6.md`, `template/examples/EuGH C-300-21 (Österreichische Post).md`.

## Maschinenlesbare Frontmatter-Felder
```yaml
normen:        # ["DSGVO Art. 6", "EU AI Act Art. 9", …]  — Norm zuerst, einheitlich
urteile:       # ["ECLI:…", "BVerfGE 65, 1", …]
rechtsgebiet:  # ["Datenschutzrecht", …]
rang:          # 1–6 (nur Norm-/Urteilsknoten)
ecli:          # nur Leitentscheidungen (verifiziert)
resource:      # stabile Asset-URI: ELI (Normen) / ECLI-Resolver (Urteile) / DOI
```
Norm-Strings einheitlich normalisieren (`<Gesetz> Art./§ <N>`), sonst zersplittern Backlinks/Abfragen.

## Rechtshierarchie (6 Ränge)
Rang folgt der **Norm**, nicht dem Gericht:

| Rang | Kategorie |
|---|---|
| 1 | EU-Primärrecht (AEUV/EUV/GRC) |
| 2 | EU-Verordnung (DSGVO/DSA/AI Act) |
| 3 | EU-Richtlinie (umgesetzt) |
| 4 | Deutsches Verfassungsrecht (GG) |
| 5 | Bundesgesetz / Staatsvertrag |
| 6 | Landesgesetz / Rechtsverordnung |

## `[!recht]`-Callouts
Rechtlich fundierte Aussagen werden annotiert (steht *unter* der Aussage):
```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

## ECLI / ELI als `resource`
- **Normen → ELI:** EU `http://data.europa.eu/eli/…`, Bundesrecht `https://recht.bund.de/eli/…` bzw. `gesetze-im-internet.de` (paragraphengenau).
- **Urteile → ECLI-Resolver:** EU über EUR-Lex (CELEX/ECLI), deutsche Gerichte über die jeweilige amtliche Quelle.
- **Goldene Regel: ECLI/URIs niemals erfinden** — nur verifizierte Identifikatoren; sonst nur Fundstelle.

## Normersetzung
Das Wiki spiegelt den **aktuellen Rechtsstand**. Löst eine neue Quelle eine Norm/Entscheidung ab, werden betroffene Seiten im selben Ingest aktualisiert und veraltete Callouts gekennzeichnet (Details: `wiki-schema.md`, Abschnitt „Rechtliche Aktualität und Normersetzung").
