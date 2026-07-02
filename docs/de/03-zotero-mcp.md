# 03 · Zotero ↔ Obsidian über MCP verbinden

Das **Model Context Protocol (MCP)** ist das Rückgrat: Es verbindet deinen KI-Agenten mit (a) deiner **Zotero-Bibliothek** und (b) deinem **Vault-Dateisystem**. Beide Server laufen unter allen unterstützten Agenten (Claude Code, Codex, OpenCode, Gemini CLI) — nur die Eintragung unterscheidet sich (→ `04-agenten-einrichtung.md`).

## 1. Zotero 7 vorbereiten
- [Zotero 7](https://www.zotero.org) installieren, Bibliothek einrichten.
- Lokale API aktivieren: **Einstellungen → Erweitert → „Allow other applications on this computer to communicate with Zotero"** (lokale HTTP-API auf `localhost:23119`; dient als Fallback).
- Zotero muss beim Arbeiten **laufen**.

## 2. Zotero-MCP-Plugin installieren
Der Zotero-MCP-Server läuft als **natives Zotero-Plugin**: Es stellt einen MCP-Server über **Streamable HTTP** unter `http://127.0.0.1:23120/mcp` bereit. Ein separates npm-Paket bzw. ein Bridge-Prozess (`zotero-mcp-server`) ist **nicht mehr** nötig.

1. Das Plugin `zotero-mcp-plugin` als `.xpi` aus den Releases von [`cookjohn/zotero-mcp`](https://github.com/cookjohn/zotero-mcp/releases/latest) herunterladen.
2. In Zotero: **Werkzeuge → Plugins** → Zahnrad-Menü → **„Install Plugin From File…"** → die `.xpi` auswählen.
3. Zotero neu starten. Der Endpoint ist danach unter `http://127.0.0.1:23120/mcp` erreichbar.

Bereitgestellte Tools (Auswahl): `search_library`, `get_item_details`, `get_item_abstract`, `get_content`, `search_fulltext`, `get_annotations`, `search_annotations`, `get_collections` u.a. — Details und Parameter im Zotero-Skill (`skills/zotero-skill/`).

> **Schnelltest:** `curl -s http://127.0.0.1:23120/ping` → `pong`. Der eigentliche MCP-Endpoint ist `…/mcp` (Streamable HTTP), **nicht** die Wurzel.

## 3. Filesystem-MCP-Server
Für Lese-/Schreibzugriff des Agenten auf den Vault dient der offizielle Server `@modelcontextprotocol/server-filesystem` (per `npx`, kein Install nötig):

```
npx -y @modelcontextprotocol/server-filesystem "/PFAD/ZU/DEINEM/VAULT"
```

## 4. Server beim Agenten eintragen
Die fertigen Config-Snippets liegen in `template/agent-config/<agent>/` und `mcp/mcp-config.example.json`. Der Zotero-Eintrag ist ein **HTTP-Transport** auf `http://127.0.0.1:23120/mcp`; das genaue Feld unterscheidet sich je Agent (Claude `type: "http"`, Gemini `httpUrl`, OpenCode `type: "remote"`, Codex `url`). Genaue Eintragung pro Agent → **`04-agenten-einrichtung.md`**.

## 5. Verbindungstest
1. Agent starten, Vault-Ordner öffnen.
2. Zotero läuft? → im Agenten ein Zotero-Tool aufrufen (z.B. `search_library`).
3. Erster Ingest: `ingest @<citekey>` — der Agent sollte Metadaten/Abstract ziehen und eine Wiki-Seite anlegen.

## Troubleshooting
- **Kein Zotero-Tool sichtbar:** Zotero läuft nicht / Plugin nicht installiert oder deaktiviert / falscher MCP-Eintrag beim Agenten.
- **`curl …/ping` liefert `pong`, aber Tool-Aufrufe schlagen mit `404` fehl:** Der Agent nutzt noch die alte npm-Bridge (stdio, `zotero-mcp-server`), deren REST-Routen im Plugin entfernt wurden. Eintrag auf den HTTP-Endpoint `http://127.0.0.1:23120/mcp` umstellen und Agent neu starten.
- **Filesystem-Server findet Vault nicht:** Pfad im Config-Snippet (`/PFAD/ZU/DEINEM/VAULT`) korrekt und in Anführungszeichen (Leerzeichen im iCloud-Pfad!)?
- **Port belegt/nicht erreichbar:** prüfen, ob `127.0.0.1:23120` (Plugin) bzw. `localhost:23119` (Zotero-API-Fallback) erreichbar ist.

## Weiter
→ `04-agenten-einrichtung.md` — Config je Agent.
