# 08 · Wiki MCP Server (optional)

The wiki MCP server (`mcp/wiki-mcp/`) makes the wiki addressable for agents through **tools** rather than through grep alone. That is not a cosmetic difference: `get_norm` and `get_backlinks` evaluate the **frontmatter**, i.e. structured fields such as `normen:` or `rechtsstand:`. Grep only sees lines. The two maintenance reports (`list_unverified`, `list_stale`) follow directly from the fields introduced in chapter 07.

The server is a single file, Python standard library only, with no MCP SDK; MCP (JSON-RPC 2.0) is implemented directly.

## Security model

**stdio instead of network.** The server communicates via newline-delimited JSON on `stdin`/`stdout`. It opens no port, calls no `bind()`, and imports no networking module. Third parties cannot reach it, because there is nothing to connect to: the process exists only as a child process of the MCP client on the same machine and dies with it.

**Read-only by design.** There is deliberately no write tool. The server never writes, moves, or deletes a file; its only filesystem operation is reading `.md` files. A misguided model cannot damage a vault through this server.

**Path hardening.** Every path parameter is resolved against the wiki root with `os.path.realpath`. Absolute paths, tilde paths, `..` segments, and symlinks that lead out of the root are rejected before anything is read.

## Prerequisites

System Python 3.9 or newer (on macOS the bundled `/usr/bin/python3` is enough). No pip dependencies, no venv, no Node.

## Installation

```bash
bash mcp/wiki-mcp/sync.sh /PATH/TO/YOUR/VAULT
# copies server.py to /PATH/TO/YOUR/VAULT/.wiki-mcp/server.py
```

The script creates the target directory, compares the `WIKI_MCP_VERSION` of the repo and vault copies beforehand, and reports any drift before copying. The repo version stays canonical.

## Configuration

`.mcp.json` in the **vault root** (Claude Code):

```json
{
  "mcpServers": {
    "wiki": {
      "command": "python3",
      "args": [
        "/PATH/TO/YOUR/VAULT/.wiki-mcp/server.py",
        "--wiki-root", "/PATH/TO/YOUR/VAULT/[WIKI-FOLDER]",
        "--exclude", "FolderName"
      ]
    }
  }
}
```

**Why project-scoped and not global?** An `.mcp.json` inside the vault travels with the vault and is therefore available on every device as soon as the vault arrives there. A global agent configuration (`~/.claude.json`, `~/.codex/config.toml`) is not synced and has to be replicated by hand on every machine.

`--exclude` may be given multiple times and refers to **folder names, not paths**; this is how you keep private areas inside the wiki folder out of the index. Directories starting with `.` (such as `.obsidian`) are always skipped.

Other agents, analogous to `04-agent-setup.md`:

| Agent | File | Form |
|---|---|---|
| Claude Code | `.mcp.json` (vault root) | `mcpServers.wiki` with `command` + `args` |
| OpenAI Codex | `~/.codex/config.toml` | `[mcp_servers.wiki]` with `command = "python3"`, `args = [...]` |
| OpenCode | `opencode.json` | `mcp.wiki` with `"type": "local"`, `command: [...]`, `enabled: true` |
| Gemini CLI | `~/.gemini/settings.json` | `mcpServers.wiki` with `command` + `args` |

## The seven tools

| Tool | Parameters | Returns |
|---|---|---|
| `wiki_info` | – | `version`, `wiki_root`, `pages_total`, `by_type`, `by_wiki_category`, `folders`, `indexed_at` |
| `search_wiki` | `query` (required), `limit` (default 20), `regex` (default `false`), `folder` (optional) | matching files with up to three hit lines each (`line_no`, `text`, truncated to 300 characters) |
| `get_page` | `path` (required) | `path`, `title`, `frontmatter`, `content` |
| `get_norm` | `norm` (required) | `node_page` (the norm node page) and `citing_pages` (all pages carrying the norm in their `normen:` frontmatter) |
| `get_backlinks` | `page` (required) | all pages with a wikilink to the page, up to two context lines each |
| `list_unverified` | `limit` (default 50) | pages that have sources but no `verifiziert:`, plus pages with an open `[!unbelegt]` finding, each with a `reason` |
| `list_stale` | `days` (default 365), `limit` (default 50) | pages whose `rechtsstand:` is older than `days`, sorted by `age_days` descending |

Notes: without `regex`, `query` is searched as a literal, and `|` separates several literals as OR (`"Einwilligung|Consent"`); both modes are case-insensitive. For `get_page`, `path` is relative to the wiki root and the `.md` extension is optional; if the path fails, resolution falls back to the filename as with an Obsidian wikilink, and on ambiguity the tool returns the candidate list instead of an arbitrary pick. `get_norm` normalizes whitespace and case, so `"DSGVO Art. 6"` also matches `"DSGVO Art. 6 Abs. 1 lit. f"`. All tools answer with a JSON document in the text field of the MCP response.

## Multi-device operation

Code and vault live in a synced folder (iCloud Drive, Dropbox, Syncthing). Only `server.py` and the vault are synced, never the running service. On each device the local MCP client starts its own instance against the local copy. There is no shared server, no session over the network, and nothing shared between devices; if one machine goes down, the others are unaffected.

The index is built in full at startup and refreshed before every tool call via mtime comparison. That costs one directory scan per call, but it is exactly the point for sync latecomers: files that the sync service delivers after startup become visible without a restart.

## Limits

- **No write access.** Changes to the wiki still go through the client's file access. That is by design, not a missing feature.
- **In-memory index.** All pages are read at startup. For a few hundred files this is imperceptible; for tens of thousands a persistent index would be the better choice.
- **No full-text indexing in the search-engine sense.** `search_wiki` is a line-wise literal/regex scan: no ranking, no stemming, no semantic similarity.
- **Simple YAML parser.** `key: value`, `key: [a, b]`, and multi-line lists are understood; nested structures, anchors, and block scalars are not.
- **mtime-based refresh.** Files whose modification time is not updated go unnoticed.

## Next
Full server documentation: `mcp/wiki-mcp/README.md`.
