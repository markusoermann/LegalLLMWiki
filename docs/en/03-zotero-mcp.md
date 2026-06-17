# 03 · Connecting Zotero ↔ Obsidian via MCP

The **Model Context Protocol (MCP)** is the backbone: it connects your AI agent to (a) your **Zotero library** and (b) your **vault filesystem**. Both servers run under all supported agents (Claude Code, Codex, OpenCode, Gemini CLI) — only the registration differs (→ `04-agent-setup.md`).

## 1. Prepare Zotero 7
- Install [Zotero 7](https://www.zotero.org) and set up your library.
- Enable the local API: **Settings → Advanced → "Allow other applications on this computer to communicate with Zotero"** (local HTTP API on `localhost:23119`).
- Zotero must be **running** while you work.

## 2. Install the Zotero MCP server
This uses [`zotero-mcp`](https://github.com/cookjohn/zotero-mcp) (an MCP server for Zotero):

```bash
npm install -g zotero-mcp
```

This places the **`zotero-mcp-server`** binary on your PATH. It talks to the local Zotero API and exposes tools: `search`, `get_item_by_key`, `get_pdf_content`, `get_item_annotations`, `get_collections`, and others.

> Alternative without a global install: use the full path to `build/index.js` as a `command`/`node` invocation.

## 3. Filesystem MCP server
For the agent's read/write access to the vault, use the official `@modelcontextprotocol/server-filesystem` server (via `npx`, no installation required):

```
npx -y @modelcontextprotocol/server-filesystem "/PATH/TO/YOUR/VAULT"
```

## 4. Register the servers with the agent
Ready-made config snippets live in `template/agent-config/<agent>/` and `mcp/mcp-config.example.json`. Exact registration per agent → **`04-agent-setup.md`**.

## 5. Connection test
1. Start the agent and open the vault folder.
2. Is Zotero running? → call a Zotero tool from within the agent (e.g. `ping` or `search`).
3. First ingest: `ingest @<citekey>` — the agent should pull metadata/abstract and create a wiki page.

## Troubleshooting
- **No Zotero tool visible:** Zotero isn't running / the local API isn't enabled / `zotero-mcp-server` isn't on your PATH.
- **Filesystem server can't find the vault:** Is the path in the config snippet (`/PATH/TO/YOUR/VAULT`) correct and wrapped in quotes (mind the spaces in the iCloud path!)?
- **Port in use:** Check whether `localhost:23119` (the Zotero API) is reachable.

## Next
→ `04-agent-setup.md` — config per agent.
