# 03 · Zotero ↔ Obsidian über MCP verbinden

Das **Model Context Protocol (MCP)** ist das Rückgrat: Es verbindet deinen KI-Agenten mit (a) deiner **Zotero-Bibliothek** und (b) deinem **Vault-Dateisystem**. Beide Server laufen unter allen unterstützten Agenten (Claude Code, Codex, OpenCode, Gemini CLI) — nur die Eintragung unterscheidet sich (→ `04-agenten-einrichtung.md`).

## 1. Zotero 7 vorbereiten
- [Zotero 7](https://www.zotero.org) installieren, Bibliothek einrichten.
- Lokale API aktivieren: **Einstellungen → Erweitert → „Allow other applications on this computer to communicate with Zotero"** (lokale HTTP-API auf `localhost:23119`).
- Zotero muss beim Arbeiten **laufen**.

## 2. Zotero-MCP-Server installieren
Verwendet wird [`zotero-mcp`](https://github.com/cookjohn/zotero-mcp) (MCP-Server für Zotero):

```bash
npm install -g zotero-mcp
```

Das legt das Binary **`zotero-mcp-server`** auf den PATH. Es spricht die lokale Zotero-API an und stellt Tools bereit: `search`, `get_item_by_key`, `get_pdf_content`, `get_item_annotations`, `get_collections` u.a.

> Alternative ohne globalen Install: vollständigen Pfad zur `build/index.js` als `command`/`node`-Aufruf nutzen.

## 3. Filesystem-MCP-Server
Für Lese-/Schreibzugriff des Agenten auf den Vault dient der offizielle Server `@modelcontextprotocol/server-filesystem` (per `npx`, kein Install nötig):

```
npx -y @modelcontextprotocol/server-filesystem "/PFAD/ZU/DEINEM/VAULT"
```

## 4. Server beim Agenten eintragen
Die fertigen Config-Snippets liegen in `template/agent-config/<agent>/` und `mcp/mcp-config.example.json`. Genaue Eintragung pro Agent → **`04-agenten-einrichtung.md`**.

## 5. Verbindungstest
1. Agent starten, Vault-Ordner öffnen.
2. Zotero läuft? → im Agenten ein Zotero-Tool aufrufen (z.B. `ping` bzw. `search`).
3. Erster Ingest: `ingest @<citekey>` — der Agent sollte Metadaten/Abstract ziehen und eine Wiki-Seite anlegen.

## Troubleshooting
- **Kein Zotero-Tool sichtbar:** Zotero läuft nicht / lokale API nicht aktiviert / `zotero-mcp-server` nicht auf PATH.
- **Filesystem-Server findet Vault nicht:** Pfad im Config-Snippet (`/PFAD/ZU/DEINEM/VAULT`) korrekt und in Anführungszeichen (Leerzeichen im iCloud-Pfad!)?
- **Port belegt:** prüfen, ob `localhost:23119` (Zotero-API) erreichbar ist.

## Weiter
→ `04-agenten-einrichtung.md` — Config je Agent.
