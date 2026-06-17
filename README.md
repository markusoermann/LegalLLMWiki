# LegalWikiLLM

**Ein KI-gepflegtes, juristisch optimiertes Fach-Wiki für Obsidian — mit Zotero-Anbindung und Multi-Agent-Unterstützung.**

Ein KI-Agent baut in deinem Obsidian-Vault ein strukturiertes Wiki auf und hält es aktuell: Quellen liegen in **Zotero**, der Agent zieht sie per **MCP** heran und schreibt kuratierte Wiki-Seiten. Optimiert für Recht — mit Normknoten, Leitentscheidungen, Rechtshierarchie und ECLI/ELI-Identifikatoren.

Das Projekt beruht auf dem **LLM-Wiki-Muster von Andrej Karpathy** (2026) und ist an den **Open Knowledge Format (OKF)**-Standard von Google angepasst — siehe [Grundlagen & Standards](#grundlagen--standards).

## Für wen?

Jurist:innen, Forschende und alle, die ein befragbares Fach-Wiki mit sauberer Quellenanbindung wollen — **unabhängig vom KI-Agenten**.

## Features

- 📚 **Zotero ↔ Obsidian** über MCP (Ingest von Metadaten, Abstract, PDF-Volltext, Annotationen)
- ⚖️ **Juristisch optimiert:** Normknoten, Leitentscheidungen, 6-stufige Rechtshierarchie, `[!recht]`-Callouts, `ecli`/`resource` (ELI/ECLI)
- 🤖 **Multi-Agent:** funktioniert mit **Claude Code, OpenAI Codex, OpenCode und Gemini CLI** (kanonische `AGENTS.md`)
- 🔗 **Graph ohne Triplestore:** Backlinks der Norm-/Urteilsknoten als Abfragepfad
- 🧩 **4 Skills:** `wiki-query`, `zotero-skill`, `quellencheck`, `defuddle`
- 📐 **An den OKF-Standard angepasstes Schema** ([Google Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md))

## Quickstart

1. **Obsidian-Vault** + PARA-Struktur anlegen → [`docs/02-obsidian.md`](docs/02-obsidian.md)
2. **Framework-Dateien** aus `template/` einsetzen (`AGENTS.md`, `wiki-schema.md`, `index.md`, `log.md`)
3. **Zotero + MCP** verbinden → [`docs/03-zotero-mcp.md`](docs/03-zotero-mcp.md)
4. **Deinen Agenten** einrichten (Kontextdatei + MCP-Config + Skills) → [`docs/04-agenten-einrichtung.md`](docs/04-agenten-einrichtung.md)
5. **Loslegen:** `ingest @citekey`, `query wiki: …`, `lint wiki` → [`docs/05-workflows.md`](docs/05-workflows.md)

Juristische Besonderheiten: [`docs/06-recht-features.md`](docs/06-recht-features.md) · Konzept/Architektur: [`docs/01-konzept.md`](docs/01-konzept.md)

## Repo-Aufbau

```
docs/        Setup-Guide (01–06)
template/    AGENTS.md, wiki-schema.md, index/log, examples/, agent-config/
skills/      4 Skills + Einbindungs-Guide (skills/README.md)
mcp/         Beispiel-MCP-Konfiguration
```

## Hinweise

- **Keine personenbezogenen Daten:** Das Repo enthält nur das generalisierte Framework + gemeinfreie Beispielinhalte. Eigene Inhalte/Zotero-Bibliothek bleiben lokal.
- **Abhängigkeiten:** Zotero 7, [`zotero-mcp`](https://github.com/cookjohn/zotero-mcp) (`npm i -g zotero-mcp`), Node.js (für `npx`-Filesystem-Server); für `defuddle`: `npm i -g defuddle`.

## Grundlagen & Standards

- **LLM-Wiki-Muster** — Das zugrunde liegende Konzept (ein KI-gepflegtes, „kompoundierendes" Markdown-Wissens-Wiki als Schicht zwischen Nutzer und Rohquellen) stammt von **Andrej Karpathy** ([@karpathy](https://x.com/karpathy)), vorgestellt im April 2026. LegalWikiLLM ist eine für juristische Inhalte spezialisierte, agent-agnostische Umsetzung dieses Musters.
- **Open Knowledge Format (OKF)** — Das Schema ist an Googles offenen Wissens-Format-Standard angepasst: jede Nicht-Reserved-Seite trägt ein `type`-Feld, `resource` ist das OKF-Asset-URI-Feld (ELI/ECLI/DOI). Spezifikation: [GoogleCloudPlatform/knowledge-catalog · okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). Details + bewusste Abweichungen im Schema (`template/wiki-schema.md`, Abschnitt „OKF-Kompatibilität").

## Lizenz

[MIT](LICENSE) © 2026 Markus Oermann
