---
name: zotero-skill
description: |
  Interact with a local Zotero 7+ library via the Zotero MCP server (port 23120, preferred)
  or the local HTTP API (localhost:23119, fallback) and the Zotero Web API (api.zotero.org).
  Use this skill whenever the user mentions Zotero, wants to search their research library,
  retrieve literature, find papers by topic/author/tag, fetch abstracts or metadata,
  list collections, export citations/BibTeX, read PDF content, or add items to Zotero.
  Trigger phrases include: "search Zotero", "which papers do I have on X",
  "get me the source for X from Zotero", "export as BibTeX", "Zotero library",
  "add this article to Zotero", "my literature on X", "search my library",
  "find papers about X", "get citation for X", any mention of a DOI or paper title
  combined with reference management context.
  Always use this skill before asking the user to manually look up references.
---

# Zotero Skill

Access a running Zotero 7 installation via the **Zotero MCP Server** (preferred) or the local HTTP API (fallback).

> **MCP architecture (since Zotero plugin `zotero-mcp-plugin` v1.5.0):** The plugin now exposes a **native MCP server over Streamable HTTP** at `http://127.0.0.1:23120/mcp`. Claude Code connects to it directly (config `{"type":"http","url":"http://127.0.0.1:23120/mcp"}` in `~/.claude.json`) — the old separate npm bridge (`zotero-mcp` stdio) is obsolete. The tool names changed accordingly (see the migration table below). Collections are writable via MCP; and since v1.6+ so are items themselves — `write_item` / `write_metadata` / `write_note` / `write_tag` create items, attach full-text PDFs, and edit metadata once *Write Operations* is enabled in the plugin preferences (see **MCP Write Tools**). The Connector API remains a creds-free fallback for creating items into the currently-selected collection.

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
| PDF / full text | **MCP** `get_content` | Read tool on `~/Zotero/storage/` |
| Full-text search across docs | **MCP** `search_fulltext` / `fulltext_database` | — |
| Annotations & notes | **MCP** `get_annotations` / `search_annotations` | Local API `children` endpoint |
| Collections (read) | **MCP** `get_collections` / `get_collection_items` / `get_subcollections` | Local API |
| Find by DOI/ISBN | **MCP** `search_library` (q=DOI) | BBT JSON-RPC |
| **Collection writes** | **MCP** `create_collection` / `update_collection` / `delete_collection` / `add_items_to_collection` / `remove_items_from_collection` | Web API `api.zotero.org` PATCH |
| **Create items** | **MCP** `write_item` (`create`)* / Connector API `saveItems` (creds-free, honours selected collection) | Connector API `localhost:23119` |
| **Attach full-text PDF** | **MCP** `write_item` (`import`)* | Web API attachment upload |
| **Update item metadata** | **MCP** `write_metadata`* | Web API `api.zotero.org` PATCH |
| **Delete items** | — | Web API `api.zotero.org` DELETE |

\* MCP `write_*` tools require *Write Operations* enabled in the plugin preferences — see **MCP Write Tools**.

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

If no response → Zotero or the MCP plugin is not running. Fall back to the Local HTTP API.

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

No local file path needed — replaces the Read tool on `~/Zotero/storage/[ATTKEY]/`.

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

## MCP Write Tools (`write_*`) — requires "Write Operations" enabled

Since plugin v1.6+, the native MCP server can **create and modify items and attach files directly** — no Web API credentials needed. These tools are **off by default**: enable them once in *Zotero → Tools → Add-ons → Zotero MCP Plugin → Preferences → "Write Operations"*. If disabled, calls fail with `-32603 ... Write operations are currently disabled` — in that case ask the user to flip the toggle, then retry.

| Tool | Purpose |
|---|---|
| `write_item(action, ...)` | `create` (itemType, fields, creators, tags, attachmentKeys) · **`import`** (filePath, parentItemKey, title → attach a local file as full text) · `reparent` (attachmentKeys, parentKey) |
| `write_metadata(itemKey, fields?, creators?)` | Edit fields/creators on an existing regular item (not notes/attachments) — e.g. fill an empty `abstractNote` |
| `write_note(...)` | Add/edit item notes |
| `write_tag(...)` | Add/edit tags |

**Registry caveat:** the `write_*` tools may not be surfaced by the client's ToolSearch registry even when the plugin exposes them. If `ToolSearch select:mcp__zotero__write_item` returns nothing, confirm the tool exists (`tools/list`, see Setup Check) and call it by **direct JSON-RPC** to the endpoint:

```bash
curl -s -X POST http://127.0.0.1:23120/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{
       "name":"write_item",
       "arguments":{"action":"import","filePath":"/abs/path.pdf","parentItemKey":"ABCD1234","title":"Volltext"}}}'
# Response is SSE-framed: parse the `data:` line as JSON, read result.content[].text → {"success": true, "data": {"attachmentKey": ...}}
```

`write_item action="create"` can create items too, but the Connector API (`saveItems`) stays useful: it needs no write-enable toggle and drops items into the currently-selected collection.

---

### Common MCP Patterns

**Full ingest of a citekey:**
1. `search_library(q: "oermann2023")` → get `itemKey`
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

## Full-Text Enrichment — immer bei neuen Quellen versuchen

Whenever you add items to Zotero — a single source **or** a bulk import — **always try to attach the full-text PDF right after creating each item.** Treat "create record" and "attach full text" as *one* workflow, not two optional steps. Rationale: a bare bibliographic record sends the user back to the browser every time they want to read the paper, whereas a record *with* the PDF is instantly readable via `get_content` and searchable via `search_fulltext`. The cost of trying is low; the payoff compounds across the whole library. Do this by default — you don't need to ask first (the user can always remove a PDF). Only skip it if the user explicitly says "metadata only".

**Per-item workflow:**

1. **Get the `itemKey`.** After creating via Connector `saveItems` (empty 201 body — no key returned) look the item up with `search_library(q: title/DOI)`. `write_item action="create"` returns the key directly.
2. **Find an openly downloadable PDF.** Start from the item's DOI/arXiv-ID. For any DOI, query **Unpaywall** to discover a legal OA copy:
   ```bash
   curl -sL "https://api.unpaywall.org/v2/<DOI>?email=<user-email>" \
     | python3 -c "import sys,json;d=json.load(sys.stdin);l=d.get('best_oa_location') or {};print(d.get('is_oa'),l.get('url_for_pdf') or l.get('url'))"
   ```
3. **Download to a temp file and VERIFY it is a real PDF** before attaching — bot-protection walls happily return an HTML "Access Denied" page under a `.pdf` filename:
   ```bash
   UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
   curl -sL -A "$UA" -o /tmp/zot_dl.pdf "<PDF_URL>"
   file -b --mime-type /tmp/zot_dl.pdf   # must be application/pdf …
   head -c 5 /tmp/zot_dl.pdf             # … and start with %PDF-
   ```
4. **Attach** with `write_item action="import"` (`filePath` = absolute path, `parentItemKey` = the item's key, optional `title`). Needs *Write Operations* enabled — see MCP Write Tools.
5. **Clean up** temp files and **report** which items got a full text and which didn't, each with a one-line reason.

**Source map — what actually downloads via `curl` (verified):**

| Source | Full text via `curl`? | How |
|---|---|---|
| arXiv | ✅ reliable | `https://arxiv.org/pdf/<id>` |
| PubMed Central (PMC) | ✅ | `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC<id>/pdf/` |
| Nature (OA articles) | ✅ | `https://www.nature.com/articles/<doi-suffix>.pdf` |
| Frontiers | ✅ | `https://www.frontiersin.org/articles/<DOI>/pdf` |
| PLOS & other true-OA journals | ✅ usually | publisher PDF link / Unpaywall |
| **MDPI** (Societies, Sensors, …) | ⚠️ often blocked | Incapsula bot-wall → "Access Denied" HTML, even though the article *is* OA |
| **Zenodo** | ⚠️ often blocked | 403 to `curl`; downloads fine in a real browser |
| Elsevier · IEEE · SAGE · Springer · Wiley (paywalled) | ❌ no legal direct download | leave the record without a PDF |

**When automated download fails** (bot-wall or paywall): do **not** fabricate a file or hammer the server. Record the item as "no full text (reason)" and offer the realistic alternatives:
- **Zotero's own "Find Available PDF"** (right-click the item) — it uses a genuine browser session and frequently succeeds where `curl` hits a bot-wall (MDPI, Zenodo);
- the user's **institutional / library access** for paywalled articles;
- the user drops the PDF into a folder and you attach it via `write_item action="import"`.

**Bulk imports:** run steps 2–4 per item, but attach OA-friendly sources (arXiv/PMC/Nature/Frontiers) first — they nearly always succeed — and batch the "no full text" cases into a single summary at the end so the report stays readable.

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
# MCP writes — collections (no creds needed):
create_collection / update_collection / delete_collection
add_items_to_collection / remove_items_from_collection (collectionKey, itemKeys[])
# MCP writes — items (needs "Write Operations" enabled in plugin prefs):
write_item(action:create|import|reparent)   # import = attach local PDF: filePath + parentItemKey
write_metadata(itemKey, fields?, creators?) # e.g. fill empty abstractNote
write_note(...) / write_tag(...)
# Full-text enrichment on every new item: create → find OA PDF (Unpaywall) → verify %PDF- → write_item import

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
- **MCP writes disabled by default**: `write_item` / `write_metadata` / `write_note` / `write_tag` exist (v1.6+) but return `-32603 ... Write operations are currently disabled` until the user enables *Write Operations* in the plugin preferences. Item **deletes** still have no MCP tool → Web API `DELETE`. (Older skill note said MCP has *no* create/edit tools — that is outdated.)
- **Attaching a bot-walled/paywalled PDF**: MDPI, Zenodo (bot-wall) and Elsevier/IEEE/SAGE/Springer (paywall) won't yield a valid PDF to `curl`. Don't loop on it — fall back to Zotero's "Find Available PDF" or ask the user (see Full-Text Enrichment).
- **`get_content` has no `page` parameter**: size output with `mode` (`minimal`/`preview`/`standard`/`complete`), not per-page.
- **BBT collection management**: No methods for creating/managing collections via JSON-RPC (use the MCP collection-write tools instead).
- **connector/import for BibTeX**: Unreliable (returns 400). Use `connector/saveItems` instead.
