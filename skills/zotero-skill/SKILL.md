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

Access a running Zotero 7 installation via the **Zotero MCP Server** (preferred) or the local HTTP API (fallback). Write operations always use the Zotero Web API.

## Critical: API Key Security

**NEVER hardcode API keys or user IDs in code, files, or git repositories.**

- Store credentials exclusively as environment variables: `ZOTERO_API_KEY` and `ZOTERO_USER_ID`
- If the user provides credentials inline during a session, set them as shell variables only — do not write them to any file

---

## Architecture: MCP-First

| Operation | Primary | Fallback |
|---|---|---|
| Search, read items | **MCP** `search` | Local API `localhost:23119` |
| Full metadata + abstract | **MCP** `get_item_by_key` | Local API |
| PDF text extraction | **MCP** `get_pdf_content` | Read-Tool on `~/Zotero/storage/` |
| Annotations & notes | **MCP** `get_item_annotations` / `get_item_notes` | Local API `children`-endpoint |
| Collections | **MCP** `get_collections` / `get_collection_items` | Local API |
| Find by DOI/ISBN | **MCP** `find_item_by_identifier` | BBT JSON-RPC |
| **Create items** | — | Connector API `localhost:23119` |
| **Add to collection** | — | Web API `api.zotero.org` PATCH |
| **Update metadata** | — | Web API `api.zotero.org` PATCH |
| **Delete items** | — | Web API `api.zotero.org` DELETE |

**MCP not available?** Check: is port 23120 up? (`curl -s http://127.0.0.1:23120/ping` → `pong`). If not, fall back to Local HTTP API section below.

---

## Zotero MCP Server (Preferred)

All read operations use MCP tools directly — no HTTP calls, no local file path resolution needed.

### Setup Check

```bash
curl -s http://127.0.0.1:23120/ping
# Expected: pong
```

If no response → Zotero or the MCP plugin is not running. Fall back to Local HTTP API.

---

### Search

`search` — Find items by keyword, title, key, tags, year, date range.

Key parameters:
- `q` — General keyword (searches all fields incl. abstract)
- `title` — Title-only search
- `key` — Direct lookup by Zotero item key
- `tags` — Comma-separated tag filter; `tagMode`: `any` / `all` / `none`
- `yearRange` — `"2020-2023"`
- `sort` — `relevance` | `date` | `title` | `year`

**Find item by citekey** (BBT citekeys are stored in the Extra field):
Use `q` with the citekey string → returns `key` for follow-up with `get_item_by_key`.

---

### get_item_by_key

`get_item_by_key(key)` — Full metadata including `title`, `creators`, `date`, `abstract`, `DOI`, `URL`, `tags`, `notes`, `attachments` (with `contentType` per attachment).

This is the primary tool for the Wiki ingest workflow after finding an item via `search`.

---

### find_item_by_identifier

`find_item_by_identifier(doi?, isbn?)` — Find item by DOI or ISBN. Returns `key`, `title`, `itemType`, `date`, `creators`. Use returned `key` with `get_item_by_key` for full details.

---

### Collections

| Tool | Purpose |
|---|---|
| `get_collections()` | Hierarchical list of all collections |
| `search_collections(q)` | Search collections by name |
| `get_collection_details(collectionKey)` | Single collection info |
| `get_collection_items(collectionKey)` | All items in a collection |

---

### PDF Content

`get_pdf_content(itemKey, page?, format?)` — Extract text from PDF attachments.

- `itemKey` — Zotero item key (not attachment key; the tool resolves the PDF attachment automatically)
- `page` — Optional specific page number (1-based); omit for full document
- `format` — `"text"` (default) or `"json"`

No local file path needed — replaces Read-Tool on `~/Zotero/storage/[ATTKEY]/`.

---

### Annotations & Notes

| Tool | Purpose | Key params |
|---|---|---|
| `get_item_annotations(itemKey)` | PDF highlights & annotations for one item | `type`, `color`, `limit`, `offset` |
| `get_item_notes(itemKey)` | Zotero notes for one item | `limit`, `offset` |
| `search_annotations(q?)` | Search annotations across entire library | `q`, `type`, `itemKey`, `detailed` |
| `get_annotation_by_id(annotationId)` | Single annotation, full content | — |
| `get_annotations_batch(ids[])` | Multiple annotations at once | array of IDs |

For `search_annotations`: use `detailed: true` for full content, default is preview (truncated).

---

### Common MCP Patterns

**Full ingest of a citekey:**
1. `search(q: "mustermann2023")` → get `key`
2. `get_item_by_key(key)` → metadata + abstract + attachment list
3. If `contentType: application/pdf`: `get_pdf_content(itemKey)` → full text
4. `get_item_annotations(itemKey)` → highlights

**Find by DOI:**
1. `find_item_by_identifier(doi: "10.1234/...")` → get `key`
2. `get_item_by_key(key)` → full details

**Bulk ingest (all items since date):**
1. `get_collections()` → identify relevant collection keys
2. `get_collection_items(collectionKey)` per collection → item list
3. Filter by `dateAdded` / `dateModified`
4. Per item: `get_item_by_key` + `get_pdf_content`

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

Write operations always require `ZOTERO_API_KEY` and `ZOTERO_USER_ID`. No MCP alternative — the MCP server is read-only.

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
# MCP (preferred — no auth, no HTTP)
search(q, title, key, tags, yearRange, sort)
get_item_by_key(key)                    → metadata + abstract + attachments
find_item_by_identifier(doi?, isbn?)    → key
get_collections()                       → hierarchical list
get_collection_items(collectionKey)     → items
get_pdf_content(itemKey, page?)         → full text
get_item_annotations(itemKey)           → highlights
get_item_notes(itemKey)                 → notes
search_annotations(q?, itemKey?)        → across library
get_annotations_batch(ids[])            → multiple at once

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
| Connection refused port 23119 | Zotero not running | Start Zotero |
| "Request not allowed" | Missing header | Add `Zotero-Allowed-Request: true` |
| 404 / "No endpoint found" | Wrong URL path | Check `users/0` prefix |
| Empty result from `search` | No match | Try broader `q`, check spelling |
| `get_pdf_content` returns empty | No PDF attachment | Check `contentType` in `get_item_by_key` |
| 403 | API key issue (Web API) | Check `ZOTERO_API_KEY` |
| 400 / 501 on local API write | Local API is read-only | Switch to Web API |

## Known Dead Ends

- **Local API writes**: POST/PATCH/DELETE to `localhost:23119/api/users/0/...` always fail. Don't retry.
- **MCP write operations**: MCP server is read-only. All writes go through Web API or Connector API.
- **BBT collection management**: No methods for creating/managing collections via JSON-RPC.
- **connector/import for BibTeX**: Unreliable (returns 400). Use `connector/saveItems` instead.
