# 01 · Konzept

## Was ist LegalWikiLLM?

Ein Setup, mit dem ein KI-Agent in deinem **Obsidian-Vault** ein gepflegtes Fach-Wiki aufbaut und befragbar hält — optimiert für **juristische Inhalte**. Quellen liegen in **Zotero**; der Agent zieht sie per MCP heran, schreibt strukturierte Wiki-Seiten und hält sie aktuell.

Es folgt dem **LLM-Wiki-Muster** von [Andrej Karpathy](https://x.com/karpathy) (2026): nicht der Mensch pflegt das Wiki manuell, sondern ein LLM kuratiert es nach festen Regeln (`AGENTS.md` + `wiki-schema.md`). Zotero ist der unveränderliche Rohdaten-Speicher; das Wiki die kuratierte Wissensschicht.

## Warum „juristisch optimiert"?

- **Normknoten** (z.B. `DSGVO Art. 6`) und **Leitentscheidungen** (z.B. `EuGH C-300-21`) als eigene Anker-Seiten.
- Maschinenlesbare Frontmatter-Felder: `normen`, `urteile`, `rechtsgebiet`, `rang`, `ecli`, `resource`.
- **Rechtshierarchie** (6 Ränge) und `[!recht]`-Callouts unter rechtlich fundierten Aussagen.
- **ECLI/ELI** als stabile Identifikatoren (Feld `resource`).

## Architektur in einem Satz

Konzeptseiten verlinken per `[[Wikilink]]` auf Normknoten/Leitentscheidungen — die **Backlinks** dieser Knoten ersetzen die SPARQL-Abfrage eines klassischen Wissensgraphen. Kein Triplestore, rein Obsidian-nativ.

```
Zotero (Rohdaten)  --MCP-->  Agent  -->  Obsidian-Vault ([WIKI-ORDNER]/ = Wiki)
                                          ├─ Konzeptseiten ──┐
                                          ├─ Normknoten  <───┤ Backlinks = Abfragepfad
                                          └─ Leitentscheidungen <─┘
```

## Verhältnis zu OKF

Das Schema ist an Googles **[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)** angepasst: jede Nicht-Reserved-Seite trägt ein `type`-Feld; `resource` ist das OKF-Empfehlungsfeld für die Asset-URI. Details + bewusste Abweichungen im Schema (`template/wiki-schema.md`, Abschnitt „OKF-Kompatibilität").

## Nächste Schritte

→ `02-obsidian.md` (Vault anlegen) · `03-zotero-mcp.md` (Zotero anbinden) · `04-agenten-einrichtung.md` (deinen Agenten einrichten).
