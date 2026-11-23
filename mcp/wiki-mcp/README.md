**🇬🇧 English** · [🇩🇪 Deutsch](README.de.md)

# wiki-mcp — read-only MCP server for the Obsidian wiki

## Purpose

`wiki-mcp` makes an Obsidian Markdown wiki accessible to an MCP client (Claude Code,
Claude Desktop) in a structured way — not as a file tree but as a knowledge graph:
full-text search, page retrieval, norm nodes with the pages citing them, backlinks, plus
two maintenance reports (unverified pages, outdated legal currency).

The server is deliberately small: a single file, Python standard library only, no MCP
SDK. The MCP protocol (JSON-RPC 2.0) is implemented directly. It runs on Python 3.9 —
that is, with the system Python shipped with macOS (`/usr/bin/python3`).

## Security model

**stdio instead of network.** The server communicates via newline-delimited JSON on
`stdin`/`stdout`. It opens no port, binds no address and imports no networking modules.
Third parties cannot reach it because there is nothing to connect to — the process
exists only as a child process of the MCP client on the same machine and dies with it.

**Read-only by design.** There is deliberately no write tool. The server writes, moves
and deletes no file. Its only filesystem operation is reading `.md` files. A misguided
model cannot damage a vault through this server.

**Path hardening.** Every path parameter is resolved against the wiki root with
`os.path.realpath`. Absolute paths, tilde paths, `..` segments and symlinks leading out
of the root are rejected with an error message before anything is read.

**No output to stdout except the protocol.** Diagnostic messages go exclusively to
`stderr`. An accidental `print` would destroy the JSON-RPC stream; the code avoids this
consistently.

## Installation

None. There are no dependencies, no `pip install`, no virtual environment. All that is
required is Python 3.9 or later — on macOS the bundled `/usr/bin/python3` is enough.

Manual trial run:

```bash
python3 server.py --wiki-root "/PATH/TO/YOUR/VAULT/[WIKI-FOLDER]" \
    --exclude "[NON-WIKI-FOLDER]"
```

The server then waits for JSON-RPC lines on stdin. In normal operation the MCP client
starts it.

## Configuration

In the vault's `.mcp.json` (or in the client configuration):

```json
{
  "mcpServers": {
    "wiki": {
      "command": "python3",
      "args": [
        "/PATH/TO/YOUR/VAULT/.wiki-mcp/server.py",
        "--wiki-root",
        "/PATH/TO/YOUR/VAULT/[WIKI-FOLDER]",
        "--exclude",
        "[NON-WIKI-FOLDER]"
      ]
    }
  }
}
```

`--exclude` may be given more than once and refers to folder names, not paths.
Directories beginning with `.` (such as `.obsidian`) are always skipped anyway.

## The 7 tools

| Tool | Parameters | Result |
|---|---|---|
| `wiki_info` | – | `version`, `wiki_root`, `pages_total`, `by_type`, `by_wiki_category`, `folders`, `indexed_at` |
| `search_wiki` | `query` (required), `limit` (default 20), `regex` (default `false`), `folder` (optional) | matching files with up to three matching lines each (`line_no`, `text`, truncated to 300 characters) |
| `get_page` | `path` (required) | `path`, `title`, `frontmatter`, `content` |
| `get_norm` | `norm` (required) | `node_page` (the norm-node page) and `citing_pages` (all pages carrying the norm in their `normen:` front matter) |
| `get_backlinks` | `page` (required) | all pages with a wikilink to the page, up to two context lines each |
| `list_unverified` | `limit` (default 50) | pages with sources but without `verifiziert:`, plus pages with an open `[!unbelegt]` finding, each with a `reason` |
| `list_stale` | `days` (default 365), `limit` (default 50) | pages whose `rechtsstand:` is older than `days`, descending by `age_days` |

Notes:

- **Search.** Without `regex`, `query` is searched as a literal; a `|` separates several
  literals as OR (`"Einwilligung|Consent"`). With `regex: true`, `query` is evaluated as
  a regular expression. Both are case-insensitive. `folder` restricts the search to a
  subfolder (relative to the wiki root).
- **Page retrieval.** `path` is relative to the wiki root; the `.md` extension is
  optional. If the path fails, resolution falls back to the file name as with an
  Obsidian wikilink; where this is ambiguous the tool returns the list of candidates
  rather than an arbitrary choice.
- **Norms.** Matching normalises whitespace and ignores case. `"DSGVO Art. 6"` also
  finds entries such as `"DSGVO Art. 6 Abs. 1 lit. f"`.
- **Backlinks.** Recognised are `[[Name]]`, `[[Name|Alias]]`, the `[[Name\|Alias]]`
  form required inside tables, `[[Name#Section]]` and `[[Folder/Name]]`.

All tools answer with a JSON document in the text field of the MCP response
(`ensure_ascii=False`, indented).

## Multi-device operation

Code and vault live in a synchronised folder (iCloud, Dropbox, Syncthing). What is
synchronised is only the file `server.py` together with the vault — not the running
service. On each device the local MCP client starts its own instance against the local
copy of the vault. There is no shared server, no session over the network and nothing
shared between devices. If one device fails, the others are unaffected.

The canonical version is the one in the repository (`mcp/wiki-mcp/server.py`). The vault
copy under `.wiki-mcp/server.py` is updated with `sync.sh`:

```bash
bash sync.sh "/path/to/vault"
```

The script creates the target directory, compares the `WIKI_MCP_VERSION` of both
versions beforehand and reports a discrepancy before copying.

## Limits

- **No write access.** Changes to the wiki still happen through the client's file
  access, not through this server. That is intentional.
- **In-memory index.** All pages are read in full at startup. With a few hundred files
  this is imperceptible; for very large vaults (tens of thousands of files) a persistent
  index would make more sense.
- **Refresh via mtime.** Before every tool call the tree is walked and changed, new or
  deleted files are picked up. This is necessary for iCloud vaults but costs a directory
  scan per call. Files whose modification time is not updated go unnoticed.
- **Simple YAML parser.** Supported are `key: value`, `key: [a, b]` and multi-line lists
  with `  - value`. Nested structures, anchors and block scalars are ignored — enough for
  this wiki's front-matter schema, but it is not a full YAML parser.
- **Folder exclusion by name.** `--exclude` compares folder names at every level, not
  paths.
