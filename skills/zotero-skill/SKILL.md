---
name: zotero-skill
description: |
  Interact with a local Zotero 7+ library via the Zotero MCP server (port 23120, preferred)
  or the local HTTP API (localhost:23119, fallback) and the Zotero Web API (api.zotero.org).
  Use this skill whenever the user mentions Zotero, wants to search their research library,
  retrieve literature, find papers by topic/author/tag, fetch abstracts or metadata,
  list collections, export citations/BibTeX, read PDF content, or add items to Zotero.
  Trigger phrases include: "suche in Zotero", "welche Papers habe ich zu X",
  "hol mir die Quelle zu X aus Zotero", "exportiere als BibTeX", "Zotero-Bibliothek",
  "füge diesen Artikel zu Zotero hinzu", "meine Literatur zu X", "search my library",
  "find papers about X", "get citation for X", any mention of a DOI or paper title
  combined with reference management context.
  Always use this skill before asking the user to manually look up references.
---

# Zotero Skill

Access a running Zotero 7 installation via the **Zotero MCP Server** (preferred) or the local HTTP API (fallback).

> **MCP architecture (since Zotero plugin `zotero-mcp-plugin` v1.5.0):** The plugin now exposes a **native MCP server over Streamable HTTP** at `http://127.0.0.1:23120/mcp`. Claude Code connects to it directly (config `{"type":"http","url":"http://127.0.0.1:23120/mcp"}` in `~/.claude.json`) — the old separate npm bridge (`zotero-mcp` stdio) is obsolete. The tool names changed accordingly (see the migration table below). Collections are now writable via MCP; only new-item creation still needs the Connector API.

## Critical: API Key Security

**NEVER hardcode API keys or user IDs in code, files, or git repositories.**

- Store credentials exclusively as environment variables: `ZOTERO_API_KEY` and `ZOTERO_USER_ID`
- If the user provides credentials inline during a session, set them as shell variables only — do not write them to any file

---

## Architecture: MCP-First

| Operation | Primary | Fallback |
|---|---|---|
| Search, read items | **MCP** `search_library` | Local API `localhost:23119` |
| Full metadata + abstract | **MCP** `get_item_details` / `get_item_abstract` | Local API |
| PDF / full text | **MCP** `get_content` | Read-Tool on `~/Zotero/storage/` |
| Full-text search across docs | **MCP** `search_fulltext` / `fulltext_database` | — |
| Annotations & notes | **MCP** `get_annotations` / `search_annotations` | Local API `children`-endpoint |
| Collections (read) | **MCP** `get_collections` / `get_collection_items` / `get_subcollections` | Local API |
| Find by DOI/ISBN | **MCP** `search_library` (q=DOI) | BBT JSON-RPC |
| **Collection writes** | **MCP** `create_collection` / `update_collection` / `delete_collection` / `add_items_to_collection` / `remove_items_from_collection` | Web API `api.zotero.org` PATCH |
| **Create items** | — | Connector API `localhost:23119` |
| **Update item metadata** | — | Web API `api.zotero.org` PATCH |
| **Delete items** | — | Web API `api.zotero.org` DELETE |

**MCP not available?** Check: is port 23120 up? (`curl -s http://127.0.0.1:23120/ping` → `pong`). If `ping` works but data calls fail, the transport config is likely stale — see *Error Handling*. If nothing responds, fall back to the Local HTTP API section below.

### Tool-name migration (old npm bridge → native plugin v1.5.0)

| Old (obsolete) | New (native MCP) | Notes |
|---|---|---|
| `search` | `search_library` | params: `q`, `title`, `titleOperator`, `yearRange`, `fulltext`, `itemType`, `sort`, `mode`, `limit`, `offset` |
| `get_item_by_key` | `get_item_details` | `itemKey*`, `mode`; abstract-only: `get_item_abstract` |
| `get_pdf_content` | `get_content` | `itemKey` or `attachmentKey`, `format` (json/text), `mode`; **no `page` param** — use `mode` to size output |
| `get_item_annotations` | `get_annotations` | `itemKey` **or** `annotationId` **or** `annotationIds[]`; filters `colors`, `tags`, `types` |
| `get_item_notes` | `get_content` (`include` notes) / `get_item_details` | no dedicated notes tool |
| `get_annotation_by_id` | `get_annotations` (`annotationId`) | — |
| `get_annotations_batch` | `get_annotations` (`annotationIds[]`) | — |
| `find_item_by_identifier` | `search_library` (`q`=DOI/ISBN) | no dedicated identifier tool |
| `get_collections` / `search_collections` / `get_collection_details` / `get_collection_items` | *same names* | plus new `get_subcollections` |
| *(none)* | `get_libraries` / `search_libraries` | multi-library support (`libraryID` param on most tools) |

---

## Zotero MCP Server (Preferred)

All read operations use MCP tools directly — no HTTP calls, no local file path resolution needed. Tools are callable as `mcp__zotero__<tool>`. Most read tools accept an optional `libraryID` (defaults to the user library) and a `mode` (`minimal` | `preview` | `standard` | `complete`) that controls how much content/how many results are returned.

### Setup Check

```bash
curl -s http://127.0.0.1:23120/ping           # → pong (connectivity)
# Full check (the native MCP endpoint the client actually uses):
curl -s -X POST http://127.0.0.1:23120/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | head -c 200
# → JSON with a "tools" array. If /ping works but this 404s, see Error Handling.
```

If no response → Zotero or the MCP plugin is not running. Fall back to Local HTTP API.

---

### Search — `search_library`

Find items by keyword, title, year, item type, or full text.

Key parameters:
- `q` — General search query (all fields incl. abstract)
- `title` + `titleOperator` (`contains` | `exact` | `startsWith` | `endsWith` | `regex`)
- `yearRange` — `"2020-2023"`
- `fulltext` + `fulltextMode` (`attachment` | `note` | `both`) — search inside PDFs/notes
- `itemType` — e.g. `journalArticle`, `book`; use `itemType="attachment"` **with** `includeAttachments="true"` to find standalone PDFs imported without metadata
- `sort` — `relevance` | `date` | `title` | `year`; `relevanceScoring` (bool)
- `mode` / `limit` / `offset` — result sizing & pagination

**Find item by citekey / DOI / ISBN:** put the string in `q` → returns items incl. `itemKey`. There is **no** dedicated `find_item_by_identifier` tool anymore.

---

### Metadata & abstract — `get_item_details`, `get_item_abstract`

- `get_item_details(itemKey*, mode)` — full bibliographic metadata: `title`, `creators`, `date`, identifiers (DOI/ISBN/URL), `tags`, notes, and `attachments`. Primary tool for the Wiki ingest workflow after finding an item via `search_library`.
- `get_item_abstract(itemKey*, format)` — abstract/summary only (`format`: `json` | `text`).

---

### Full text / PDF content — `get_content`

`get_content(itemKey | attachmentKey, mode?, include?, format?)` — extract full text from PDFs, attachments, notes, and abstracts.

- `itemKey` — resolves the item's attachments automatically; **or** `attachmentKey` for a specific attachment
- `mode` — `minimal` (~500 chars) / `preview` (~1.5K) / `standard` (adaptive) / `complete` (full text). **Use `complete` for full-document ingest** — there is **no `page` parameter** anymore.
- `include` — content types to include (only with `itemKey`); `format` — `json` | `text`

No local file path needed — replaces Read-Tool on `~/Zotero/storage/[ATTKEY]/`.

**Full-text search across the whole library:** `search_fulltext(q*, itemKeys?, mode?, contextLength?, maxResults?)` returns matching passages with context. `fulltext_database(action*)` (`list`/`search`/`get`/`stats`) queries the cached full-text DB (faster, read-only).

---

### Annotations & Notes — `get_annotations`, `search_annotations`

- `get_annotations(...)` — REQUIRES one of `itemKey`, `annotationId`, or `annotationIds[]`. Filters: `colors` (hex `#ffd400` or names yellow/red/green/blue/purple/orange), `tags`, `types` (`note`/`highlight`/`annotation`/`ink`/`text`/`image`); `mode`, `limit`, `offset`. Replaces the old `get_item_annotations`, `get_annotation_by_id`, and `get_annotations_batch`.
- `search_annotations(...)` — search across the library; needs at least one of `q`, `colors`, or `tags`. Also: `itemKeys[]`, `types[]`, `minRelevance`, `mode`, `limit`, `offset`.
- **Notes:** no dedicated tool — retrieve via `get_content` (with `include` notes) or `get_item_details`.

---

### Collections

Read:

| Tool | Purpose |
|---|---|
| `get_collections(mode?, recursive?, parentCollection?)` | List collections (optionally recursive tree) |
| `search_collections(q?)` | Search collections by name |
| `get_collection_details(collectionKey*)` | Single collection info |
| `get_collection_items(collectionKey*, limit?, offset?)` | Items in a collection |
| `get_subcollections(collectionKey*, recursive?)` | Child collections (nested tree if `recursive`) |

Write (native MCP — no Web API credentials needed):

| Tool | Purpose |
|---|---|
| `create_collection(name*, parentCollection?)` | New collection (top-level if no parent) |
| `update_collection(collectionKey*, name?, parentCollection?)` | Rename / move (empty `parentCollection` = top level) |
| `delete_collection(collectionKey*, deleteItems?)` | Delete collection; `deleteItems=true` also trashes items (destructive) |
| `add_items_to_collection(collectionKey*, itemKeys*[])` | Add items |
| `remove_items_from_collection(collectionKey*, itemKeys*[])` | Remove items (not deleted from library) |

---

### Common MCP Patterns

**Full ingest of a citekey:**
1. `search_library(q: "mustermann2023")` → get `itemKey`
2. `get_item_details(itemKey)` → metadata + abstract + attachment list
3. `get_content(itemKey, mode: "complete")` → full text (check attachment presence first)
4. `get_annotations(itemKey)` → highlights

**Find by DOI:**
1. `search_library(q: "10.1234/...")` → get `itemKey`
2. `get_item_details(itemKey)` → full details

**Bulk ingest (all items since date):**
1. `get_collections()` → identify relevant collection keys
2. `get_collection_items(collectionKey)` per collection → item list
3. Filter by `dateAdded` / `dateModified` (use Local API `sort=dateAdded` if the MCP result lacks these fields)
4. Per item: `get_item_details` + `get_content`

---

## Fallback: Local HTTP API (Port 23119)

Use only when MCP is unavailable. All requests require header `Zotero-Allowed-Request: true` and `userID = 0`.

### Search

```bash
python3 -c "
import urllib.request, json
req = urllib.request.Request(
    'http://localhost:23119/api/users/0/items?q=SUCHBEGRIFF&limit=20&format=json',
    headers={'Zotero-Allowed-Request': 'true'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    items = json.load(r)
for it in items:
    d = it.get('data', {})
    if d.get('itemType') == 'attachment': continue
    creators = ', '.join(c.get('lastName', c.get('name','?')) for c in d.get('creators', [])[:2])
    year = (d.get('date') or '')[:4]
    print(f\"[{d.get('itemType','?')}] {d.get('title','(no title)')} — {creators} ({year})\")
    print(f\"  Key: {d.get('key')}  DOI: {d.get('DOI','-')}\")
"
```

### Single Item with Abstract

```bash
python3 -c "
import urllib.request, json
req = urllib.request.Request(
    'http://localhost:23119/api/users/0/items/ITEMKEY?format=json',
    headers={'Zotero-Allowed-Request': 'true'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    it = json.load(r)
d = it.get('data', it)
print('Title:   ', d.get('title'))
print('Abstract:', (d.get('abstractNote') or '(no abstract)')[:600])
"
```

### PDF via Local Storage (Fallback only)

```bash
# 1. Get attachment key
python3 -c "
import urllib.request, json
req = urllib.request.Request(
    'http://localhost:23119/api/users/0/items/ITEMKEY/children?format=json',
    headers={'Zotero-Allowed-Request': 'true'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    children = json.load(r)
for c in children:
    d = c.get('data',{})
    if d.get('itemType') == 'attachment' and d.get('contentType') == 'application/pdf':
        print(f\"Key: {d.get('key')}  Path: ~/Zotero/storage/{d.get('key')}/\")
"
# 2. Read-Tool on ~/Zotero/storage/[ATTKEY]/filename.pdf
```

### Collections (Fallback)

```bash
python3 -c "
import urllib.request, json
req = urllib.request.Request(
    'http://localhost:23119/api/users/0/collections?format=json',
    headers={'Zotero-Allowed-Request': 'true'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    colls = json.load(r)
for c in sorted(colls, key=lambda x: x['data'].get('name','')):
    d = c['data']
    print(f\"{d['name']} (key: {d['key']})\")
"
```

### BibTeX Export (Fallback)

```bash
curl -s -H "Zotero-Allowed-Request: true" \
  "http://localhost:23119/api/users/0/items/ITEMKEY?format=bibtex"
```

---

## Write Operations (Web API)

Use these for **item creation, metadata edits, and deletes**, which the MCP server does not offer. (**Collection** writes — create/update/delete, add/remove items — are available directly via MCP; see the Collections section.) Item-level writes here require `ZOTERO_API_KEY` and `ZOTERO_USER_ID`.

If credentials not set, ask user to:
1. Go to https://www.zotero.org/settings/keys
2. Note **User ID** (top right)
3. Create API key with library read/write access
4. Set: `export ZOTERO_API_KEY="..." ZOTERO_USER_ID="..."`

### Add Item to Collection

```bash
python3 -c "
import urllib.request, json, os
key = os.environ['ZOTERO_API_KEY']
uid = os.environ['ZOTERO_USER_ID']
collection_key = 'COLLECTIONKEY'
item_key = 'ITEMKEY'
req = urllib.request.Request(
    f'https://api.zotero.org/users/{uid}/items/{item_key}?format=json',
    headers={'Zotero-API-Key': key, 'Zotero-API-Version': '3'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    item = json.load(r)
version = item['version']
current_colls = item['data'].get('collections', [])
if collection_key not in current_colls:
    data = json.dumps({'collections': current_colls + [collection_key]}).encode('utf-8')
    req2 = urllib.request.Request(
        f'https://api.zotero.org/users/{uid}/items/{item_key}',
        data=data,
        headers={'Zotero-API-Key': key, 'Zotero-API-Version': '3',
                 'Content-Type': 'application/json', 'If-Unmodified-Since-Version': str(version)},
        method='PATCH'
    )
    with urllib.request.urlopen(req2, timeout=10) as r2:
        print(f'Added to collection: {r2.status}')
"
```

### Create Collection

```bash
python3 -c "
import urllib.request, json, os
key = os.environ['ZOTERO_API_KEY']
uid = os.environ['ZOTERO_USER_ID']
data = json.dumps([{'name': 'COLLECTION NAME'}]).encode('utf-8')
req = urllib.request.Request(
    f'https://api.zotero.org/users/{uid}/collections',
    data=data,
    headers={'Zotero-API-Key': key, 'Zotero-API-Version': '3', 'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=10) as r:
    result = json.load(r)
    for k, v in result.get('success', {}).items():
        print(f'Created: key={v}')
"
```

### Update Metadata / Delete

Same pattern as above: GET item → read `version` → PATCH or DELETE with `If-Unmodified-Since-Version` header.

### Create Items via Connector API (no Web API credentials needed)

Items land in the currently selected Zotero collection.

```bash
python3 -c "
import urllib.request, json
item = {
    'itemType': 'journalArticle', 'title': 'TITLE',
    'creators': [{'firstName': 'FIRST', 'lastName': 'LAST', 'creatorType': 'author'}],
    'date': 'YEAR', 'DOI': 'DOI', 'publicationTitle': 'JOURNAL', 'url': '', 'tags': []
}
payload = json.dumps({'items': [item], 'uri': 'http://zotero-import'}).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:23119/connector/saveItems', data=payload,
    headers={'Zotero-Allowed-Request': 'true', 'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=10) as r:
    print(f'Status: {r.status}')
"
```

---

## Better BibTeX JSON-RPC (Port 23119)

Useful for citekey-based export when MCP `search` doesn't resolve a citekey. Endpoint: `localhost:23119/better-bibtex/json-rpc`.

| Method | Params | Description |
|---|---|---|
| `item.search` | `terms` | Search by author/title |
| `item.export` | `citekeys`, `translator` | Export in various formats |
| `item.bibliography` | `citekeys` | Formatted bibliography |
| `item.citationkey` | `item_keys` | Get BBT citekeys for Zotero keys |
| `item.attachments` | `citekey` | Get attachments |

```bash
python3 -c "
import urllib.request, json
payload = json.dumps({'jsonrpc': '2.0', 'method': 'item.search', 'params': ['AUTHOR'], 'id': 1}).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:23119/better-bibtex/json-rpc',
    data=payload,
    headers={'Content-Type': 'application/json', 'Zotero-Allowed-Request': 'true'}
)
with urllib.request.urlopen(req, timeout=5) as r:
    result = json.load(r)
for item in result.get('result', []):
    print(f\"{item.get('citation-key','?')}: {item.get('title','?')}\")
"
```

---

## Quick Reference

```
# MCP (preferred — native plugin v1.5.0, transport http @ 127.0.0.1:23120/mcp)
search_library(q, title, yearRange, fulltext, itemType, sort, mode, limit)
get_item_details(itemKey, mode)              → metadata + abstract + attachments
get_item_abstract(itemKey, format)           → abstract only
get_content(itemKey|attachmentKey, mode)     → full text (mode:"complete" for whole doc)
search_fulltext(q, itemKeys?, mode)          → matching passages across docs
get_collections(mode?, recursive?)           → collections (tree if recursive)
search_collections(q) / get_collection_details(collectionKey)
get_collection_items(collectionKey)          → items
get_subcollections(collectionKey, recursive?)
get_annotations(itemKey | annotationId | annotationIds[])  → highlights/notes
search_annotations(q? | colors? | tags?)     → across library
get_libraries() / search_libraries(q)        → multi-library
# MCP writes (collections only; no creds needed):
create_collection / update_collection / delete_collection
add_items_to_collection / remove_items_from_collection (collectionKey, itemKeys[])

# Local API fallback (read-only, port 23119)
GET  /api/users/0/items?q=TEXT&limit=N
GET  /api/users/0/items/KEY
GET  /api/users/0/items/KEY/children    → attachments & annotations
GET  /api/users/0/collections
GET  /api/users/0/collections/KEY/items/top
Header: Zotero-Allowed-Request: true

# Connector API (item creation, port 23119)
POST /connector/saveItems               → into currently selected collection

# Web API (full CRUD, needs ZOTERO_API_KEY)
GET    https://api.zotero.org/users/UID/items/KEY
POST   https://api.zotero.org/users/UID/items
PATCH  https://api.zotero.org/users/UID/items/KEY  (needs If-Unmodified-Since-Version)
DELETE https://api.zotero.org/users/UID/items/KEY  (needs If-Unmodified-Since-Version)
POST   https://api.zotero.org/users/UID/collections
```

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `curl http://127.0.0.1:23120/ping` → refused | MCP plugin not running | Start Zotero; check plugin active |
| `/ping` → `pong` **but** MCP data calls → `404 Not Found` | Stale transport config: Claude still pointed at the obsolete npm stdio bridge, which calls removed REST routes | Set `~/.claude.json` → `"zotero": {"type":"http","url":"http://127.0.0.1:23120/mcp"}` and restart Claude Code |
| Connection refused port 23119 | Zotero not running | Start Zotero |
| "Request not allowed" | Missing header | Add `Zotero-Allowed-Request: true` |
| 404 / "No endpoint found" (Local API) | Wrong URL path | Check `users/0` prefix |
| Empty result from `search_library` | No match | Try broader `q`, check spelling |
| `get_content` returns empty | No PDF/text attachment | Check `attachments` in `get_item_details` |
| 403 | API key issue (Web API) | Check `ZOTERO_API_KEY` |
| 400 / 501 on local API write | Local API is read-only | Switch to Web API |

## Known Dead Ends

- **Local API writes**: POST/PATCH/DELETE to `localhost:23119/api/users/0/...` always fail. Don't retry.
- **MCP item creation / metadata edits**: the native MCP server has **no** create-item or edit-metadata tool. New items → Connector API; metadata edits/deletes → Web API. (Collections, however, **are** writable via MCP — see the Collections section.)
- **`get_content` has no `page` parameter**: size output with `mode` (`minimal`/`preview`/`standard`/`complete`), not per-page.
- **BBT collection management**: No methods for creating/managing collections via JSON-RPC (use the MCP collection-write tools instead).
- **connector/import for BibTeX**: Unreliable (returns 400). Use `connector/saveItems` instead.
