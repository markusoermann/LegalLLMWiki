# 06 · Juristische Features

Was LegalLLMWiki von einem generischen LLMWiki unterscheidet. Technische Details in `template/de/wiki-schema.md`.

## Normknoten & Leitentscheidungen
Leitnormen (Artikel/Paragraphen) und Grundsatzentscheidungen bekommen **eigene Anker-Seiten** (`wiki-category: entitaet`). Konzeptseiten verlinken darauf — die **Backlinks** dieser Knoten sind der Abfragepfad (ersetzen SPARQL). Beispiele: `template/de/examples/DSGVO Art. 6.md`, `template/de/examples/EuGH C-300-21 (Österreichische Post).md`.

## Maschinenlesbare Frontmatter-Felder
```yaml
normen:        # ["DSGVO Art. 6", "EU AI Act Art. 9", …]  — Norm zuerst, einheitlich
urteile:       # ["ECLI:…", "BVerfGE 65, 1", …]
rechtsgebiet:  # ["Datenschutzrecht", …]
rang:          # 1–6 (nur Norm-/Urteilsknoten)
ecli:          # nur Leitentscheidungen (verifiziert)
resource:      # stabile Asset-URI: ELI (Normen) / ECLI-Resolver (Urteile) / DOI
resource_element: # Elementanker im Rechtsakt: art_9 (EU) / art-z22 (Bund)
behandelt:     # nur Ankerseiten: wovon die Seite HANDELT (genau ein Wert)
relationen:    # nur Ankerseiten: typisierte Kanten als Projektion des Fließtexts
ausser_kraft:  # nur Normknoten: Außerkrafttreten
```

**`behandelt:` trennt Knoten von Zitat.** `normen:` sagt, welche Normen eine Seite *erwähnt* — „DSGVO Art. 22" steht so auf 13 Seiten. `behandelt:` sagt, welche Seite der *Knoten* dazu ist: genau eine.

**`relationen:` macht die Kante abfragbar.** Das Relationsvokabular stand bisher nur als fettes Verb im Fließtext — lesbar, aber nicht abfragbar. `relationen:` spiegelt es ins Frontmatter:
```yaml
relationen:
  - typ: verdrängt
    ziel: "NetzDG § 3"
    seit: 2024-02-17
```
Maßgeblich bleibt der Fließtext; das Feld fügt **nichts** hinzu. Verneinungen („überlagert, aber *nicht* verdrängt") erzeugen keine Kante, und nichts wird erschlossen. Weil nichts hinzukommt, ist das Anlegen ein **mechanischer Lauf ohne Hebepflicht**.

**`resource_element:` macht elementgenau — nicht novellenfest.** `resource:` bezeichnet den Rechtsakt, `resource_element:` das Element darin. Ohne den Anker tragen `DSGVO Art. 9` und `DSGVO Art. 22` denselben URI. Die Zusage endet aber dort: LegalDocML.de 1.9 nennt die `eId` ausdrücklich „kein über verschiedene Expressions hinweg stabiler Identifikator", und wann GUIDs erhalten bleiben, ist „noch nicht abschließend definiert". Der Anker ist ein **datierter Zeiger**, keine dauerhafte Identität.
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

In die Klammer gehört die **Normkategorie**, nie ein Gericht. Das gilt auch, wenn ein nationales Gericht Unionsrecht anwendet — ein BGH-Urteil zu Art. 82 DSGVO ist Rang 2, nicht Rang 5. Das ist die häufigste Fehlerquelle überhaupt; die Regel früh durchsetzen spart einen Großlauf.

**Völkerrecht** bekommt keinen eigenen Rang, sondern wird über seinen innerstaatlichen geführt: Vertrag mit Zustimmungsgesetz → Rang 5; allgemeine Regeln (Art. 25 GG) → Rang 5 mit Vermerk des Zwischenrangs; nicht-bindende Instrumente (UN-GA-Resolutionen, OECD-Empfehlungen) → kein Rang und kein `[!recht]`-Callout. Bei der EMRK ist der Görgülü-Vermerk Pflicht. Details in `wiki-schema.md`.

> **Hinweis:** Diese 6-stufige Hierarchie bildet das EU- und deutsche Recht ab. Für andere Jurisdiktionen muss sie angepasst werden — eigene Normkategorien und Ränge definieren.

## `[!recht]`-Callouts
Rechtlich fundierte Aussagen werden annotiert (steht *unter* der Aussage):
```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

## ECLI / ELI als `resource`

> **Hinweis:** ECLI, ELI und CELEX sind **EU-Standards**; die hier verwendeten Identifikatoren und Datenquellen sind auf EU- und deutsches Recht abgestimmt. Für andere Jurisdiktionen entsprechend anpassen.

- **Normen → ELI:** EU `http://data.europa.eu/eli/…`, Bundesrecht `https://recht.bund.de/eli/…` bzw. `gesetze-im-internet.de` (paragraphengenau).
- **Urteile → ECLI-Resolver:** EU über EUR-Lex (CELEX/ECLI), deutsche Gerichte über die jeweilige amtliche Quelle.
- **Goldene Regel: ECLI/URIs niemals erfinden** — nur verifizierte Identifikatoren; sonst nur Fundstelle.

## Normersetzung
Das Wiki spiegelt den **aktuellen Rechtsstand**. Löst eine neue Quelle eine Norm/Entscheidung ab, werden betroffene Seiten im selben Ingest aktualisiert und veraltete Callouts gekennzeichnet (Details: `wiki-schema.md`, Abschnitt „Rechtliche Aktualität und Normersetzung").
