# 03 · Connecting Zotero ↔ Obsidian via MCP

The **Model Context Protocol (MCP)** is the backbone: it connects your AI agent to (a) your **Zotero library** and (b) your **vault filesystem**. Both servers run under all supported agents (Claude Code, Codex, OpenCode, Gemini CLI) — only the registration differs (→ `04-agent-setup.md`).

## 1. Prepare Zotero 7
- Install [Zotero 7](https://www.zotero.org) and set up your library.
- Enable the local API: **Settings → Advanced → "Allow other applications on this computer to communicate with Zotero"** (local HTTP API on `localhost:23119`; used as a fallback).
- Zotero must be **running** while you work.

## 2. Install the Zotero MCP plugin
The Zotero MCP server runs as a **native Zotero plugin**: it exposes an MCP server over **Streamable HTTP** at `http://127.0.0.1:23120/mcp`. A separate npm package / bridge process (`zotero-mcp-server`) is **no longer** required.

1. Download the `zotero-mcp-plugin` `.xpi` from the releases of [`cookjohn/zotero-mcp`](https://github.com/cookjohn/zotero-mcp/releases/latest).
2. In Zotero: **Tools → Plugins** → gear menu → **"Install Plugin From File…"** → select the `.xpi`.
3. Restart Zotero. The endpoint is then reachable at `http://127.0.0.1:23120/mcp`.

Tools exposed (selection): `search_library`, `get_item_details`, `get_item_abstract`, `get_content`, `search_fulltext`, `get_annotations`, `search_annotations`, `get_collections`, and more — details and parameters in the Zotero skill (`skills/zotero-skill/`).

> **Quick check:** `curl -s http://127.0.0.1:23120/ping` → `pong`. The actual MCP endpoint is `…/mcp` (Streamable HTTP), **not** the root.

## 3. Filesystem MCP server
For the agent's read/write access to the vault, use the official `@modelcontextprotocol/server-filesystem` server (via `npx`, no installation required):

```
npx -y @modelcontextprotocol/server-filesystem "/PATH/TO/YOUR/VAULT"
```

## 4. Register the servers with the agent
Ready-made config snippets live in `template/agent-config/<agent>/` and `mcp/mcp-config.example.json`. The Zotero entry is an **HTTP transport** at `http://127.0.0.1:23120/mcp`; the exact field differs per agent (Claude `type: "http"`, Gemini `httpUrl`, OpenCode `type: "remote"`, Codex `url`). Exact registration per agent → **`04-agent-setup.md`**.

## 5. Connection test
1. Start the agent and open the vault folder.
2. Is Zotero running? → call a Zotero tool from within the agent (e.g. `search_library`).
3. First ingest: `ingest @<citekey>` — the agent should pull metadata/abstract and create a wiki page.

## Troubleshooting
- **No Zotero tool visible:** Zotero isn't running / the plugin isn't installed or is disabled / wrong MCP entry in the agent config.
- **`curl …/ping` returns `pong`, but tool calls fail with `404`:** the agent still uses the old npm bridge (stdio, `zotero-mcp-server`), whose REST routes were removed from the plugin. Switch the entry to the HTTP endpoint `http://127.0.0.1:23120/mcp` and restart the agent.
- **Filesystem server can't find the vault:** Is the path in the config snippet (`/PATH/TO/YOUR/VAULT`) correct and wrapped in quotes (mind the spaces in the iCloud path!)?
- **Port in use / unreachable:** Check whether `127.0.0.1:23120` (the plugin) or `localhost:23119` (the Zotero API fallback) is reachable.

## Next
→ `04-agent-setup.md` — config per agent.
