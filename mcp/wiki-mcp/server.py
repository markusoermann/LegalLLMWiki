#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only MCP-Server über einem Obsidian-Markdown-Wiki.

Der Server spricht MCP (JSON-RPC 2.0) über stdio — eine Zeile JSON je Nachricht.
Es wird ausschließlich die Python-Standardbibliothek verwendet, kein externes SDK.
Es gibt keinen Netzwerk-Transport und keine Schreiboperation: Der Server liest
Markdown-Dateien und gibt strukturierte Ergebnisse zurück.

Aufruf:
    python3 server.py --wiki-root /pfad/zum/wiki [--exclude Ordner ...]

Kompatibilität: Python 3.9 (keine neueren Sprachfeatures).
"""

import argparse
import datetime
import json
import os
import re
import sys

WIKI_MCP_VERSION = "1.0.0"

DEFAULT_PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "wiki"

MAX_MATCH_LINES = 3
MAX_LINE_LENGTH = 300
MAX_BACKLINK_CONTEXTS = 2


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------

def log(message):
    """Schreibt eine Diagnosemeldung nach stderr (niemals nach stdout)."""
    sys.stderr.write("[wiki-mcp] " + str(message) + "\n")
    sys.stderr.flush()


class WikiError(Exception):
    """Fachlicher Fehler, der dem Client als Tool-Fehlermeldung gezeigt wird."""


def truncate(text, limit=MAX_LINE_LENGTH):
    """Kürzt eine Zeile auf die Maximallänge und hängt eine Ellipse an."""
    text = text.rstrip("\n").rstrip("\r")
    if len(text) > limit:
        return text[:limit] + " …"
    return text


def normalize_ws(value):
    """Normalisiert Whitespace und liefert eine kleingeschriebene Fassung."""
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def strip_quotes(value):
    """Entfernt umschließende Anführungszeichen eines YAML-Skalars."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    return value


def parse_inline_list(raw):
    """Zerlegt eine einzeilige YAML-Liste `[a, b]` in ihre Elemente."""
    body = raw.strip()[1:-1].strip()
    if not body:
        return []
    items = []
    current = []
    quote = None
    for char in body:
        if quote is not None:
            if char == quote:
                quote = None
            else:
                current.append(char)
        elif char in "\"'":
            quote = char
        elif char == ",":
            items.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    items.append("".join(current).strip())
    return [item for item in items if item]


KEY_RE = re.compile(r"^([^\s:#][^:]*?)\s*:\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
WIKILINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")


def parse_frontmatter(text):
    """Zerlegt ein Dokument in YAML-Frontmatter (dict) und Rumpftext.

    Unterstützt werden `key: wert`, `key: [a, b]` sowie mehrzeilige Listen
    mit `  - wert`. Der Parser ist bewusst einfach gehalten und deckt das im
    Wiki verwendete Format ab; verschachtelte Strukturen werden ignoriert.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, text
    block = lines[1:end]
    body = "\n".join(lines[end + 1:])

    frontmatter = {}
    current_key = None
    for raw_line in block:
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        item_match = LIST_ITEM_RE.match(raw_line)
        if item_match is not None and current_key is not None:
            if not isinstance(frontmatter.get(current_key), list):
                frontmatter[current_key] = []
            frontmatter[current_key].append(strip_quotes(item_match.group(1)))
            continue
        key_match = KEY_RE.match(raw_line)
        if key_match is None:
            continue
        key = key_match.group(1).strip()
        value = key_match.group(2).strip()
        if value == "":
            frontmatter[key] = ""
            current_key = key
            continue
        current_key = key
        if value.startswith("[") and value.endswith("]"):
            frontmatter[key] = parse_inline_list(value)
        else:
            frontmatter[key] = strip_quotes(value)
    return frontmatter, body


def as_list(value):
    """Liefert einen Frontmatter-Wert stets als Liste von Strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(entry) for entry in value if str(entry).strip()]
    text = str(value).strip()
    if not text or text == "[]":
        return []
    return [text]


def parse_date(value):
    """Parst ein `YYYY-MM-DD`-Datum; liefert None bei unparsbaren Werten."""
    text = strip_quotes(str(value))[:10]
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if match is None:
        return None
    try:
        return datetime.date(int(match.group(1)), int(match.group(2)),
                             int(match.group(3)))
    except ValueError:
        return None


def split_wikilink(raw_link):
    """Reduziert einen Wikilink-Inhalt auf den reinen Seitennamen.

    Berücksichtigt Alias nach `|` und nach escaptem `\\|`, Anker nach `#`
    sowie Pfadangaben (nur das letzte Segment zählt).
    """
    inner = raw_link.replace("\\|", "|")
    inner = inner.split("|")[0]
    inner = inner.split("#")[0]
    inner = inner.strip()
    if "/" in inner:
        inner = inner.split("/")[-1]
    return inner.strip()


# --------------------------------------------------------------------------
# Index
# --------------------------------------------------------------------------

class Page(object):
    """Eine indexierte Markdown-Seite des Wikis."""

    __slots__ = ("path", "title", "frontmatter", "content", "body", "mtime")

    def __init__(self, path, title, frontmatter, content, body, mtime):
        self.path = path
        self.title = title
        self.frontmatter = frontmatter
        self.content = content
        self.body = body
        self.mtime = mtime


class WikiIndex(object):
    """Hält alle Seiten des Wikis im Speicher und frischt sie per mtime auf."""

    def __init__(self, wiki_root, excludes):
        self.root = os.path.realpath(wiki_root)
        if not os.path.isdir(self.root):
            raise WikiError("Wiki-Root existiert nicht: " + str(wiki_root))
        self.excludes = set(excludes or [])
        self.pages = {}
        self.indexed_at = None
        self.refresh(force=True)

    # -- Dateisystem ------------------------------------------------------

    def _walk(self):
        """Iteriert über alle relevanten `.md`-Pfade unterhalb des Roots."""
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [name for name in dirnames
                           if not name.startswith(".")
                           and name not in self.excludes]
            for filename in filenames:
                if not filename.endswith(".md"):
                    continue
                if filename.startswith("."):
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, self.root)
                yield rel, full

    def _read(self, rel, full):
        """Liest eine Datei ein und legt sie als Page im Index ab."""
        try:
            stat = os.stat(full)
            handle = open(full, "r", encoding="utf-8", errors="replace")
            try:
                text = handle.read()
            finally:
                handle.close()
        except (IOError, OSError) as error:
            log("Datei nicht lesbar: " + rel + " (" + str(error) + ")")
            return
        frontmatter, body = parse_frontmatter(text)
        title = os.path.basename(rel)[:-3]
        self.pages[rel] = Page(rel, title, frontmatter, text, body,
                               stat.st_mtime)

    def refresh(self, force=False):
        """Inkrementelle Auffrischung: neue, geänderte und gelöschte Dateien.

        Wichtig für iCloud-synchronisierte Vaults, in denen sich Dateien
        außerhalb dieses Prozesses ändern.
        """
        seen = set()
        for rel, full in self._walk():
            seen.add(rel)
            existing = self.pages.get(rel)
            try:
                mtime = os.stat(full).st_mtime
            except (IOError, OSError):
                continue
            if force or existing is None or existing.mtime != mtime:
                self._read(rel, full)
        for rel in list(self.pages.keys()):
            if rel not in seen:
                del self.pages[rel]
        self.indexed_at = datetime.datetime.now().replace(
            microsecond=0).isoformat()

    # -- Pfad-Härtung -----------------------------------------------------

    def safe_path(self, relative):
        """Löst einen Pfadparameter gegen den Wiki-Root auf.

        Absolute Pfade, `..`-Segmente und Symlinks, die aus dem Root
        herausführen, werden abgewiesen.
        """
        if relative is None or str(relative).strip() == "":
            raise WikiError("Leerer Pfad ist nicht zulässig.")
        candidate = str(relative).strip()
        if os.path.isabs(candidate):
            raise WikiError(
                "Absolute Pfade sind nicht zulässig: " + candidate)
        if candidate.startswith("~"):
            raise WikiError("Tilde-Pfade sind nicht zulässig: " + candidate)
        real = os.path.realpath(os.path.join(self.root, candidate))
        if real != self.root and not real.startswith(self.root + os.sep):
            raise WikiError(
                "Pfad liegt außerhalb des Wiki-Roots und wurde abgewiesen: "
                + candidate)
        return real

    # -- Zugriffe ---------------------------------------------------------

    def sorted_pages(self):
        """Alle Seiten, stabil nach relativem Pfad sortiert."""
        return [self.pages[key] for key in sorted(self.pages.keys())]

    def by_title(self, name):
        """Alle Seiten, deren Dateiname (ohne Endung) `name` entspricht."""
        target = normalize_ws(name)
        return [page for page in self.sorted_pages()
                if normalize_ws(page.title) == target]

    def folders(self):
        """Sortierte Liste aller Unterordner, die Seiten enthalten."""
        result = set()
        for rel in self.pages:
            folder = os.path.dirname(rel)
            result.add(folder if folder else ".")
        return sorted(result)


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------

def normalize_page_path(raw):
    """Normalisiert einen Seitenpfad: ohne führendes `./`, immer mit `.md`."""
    path = str(raw).strip()
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    if not path.endswith(".md"):
        path = path + ".md"
    return path


def tool_wiki_info(index, arguments):
    """Liefert Kennzahlen über den aktuellen Indexstand."""
    by_type = {}
    by_category = {}
    for page in index.pages.values():
        types = as_list(page.frontmatter.get("type")) or ["(ohne type)"]
        for entry in types:
            by_type[entry] = by_type.get(entry, 0) + 1
        categories = (as_list(page.frontmatter.get("wiki-category"))
                      or ["(ohne wiki-category)"])
        for entry in categories:
            by_category[entry] = by_category.get(entry, 0) + 1
    return {
        "version": WIKI_MCP_VERSION,
        "wiki_root": index.root,
        "pages_total": len(index.pages),
        "by_type": dict(sorted(by_type.items(),
                               key=lambda item: (-item[1], item[0]))),
        "by_wiki_category": dict(sorted(by_category.items(),
                                        key=lambda item: (-item[1], item[0]))),
        "folders": index.folders(),
        "indexed_at": index.indexed_at,
    }


def tool_search_wiki(index, arguments):
    """Volltextsuche über alle indexierten Seiten."""
    query = arguments.get("query")
    if not query or not str(query).strip():
        raise WikiError("Parameter 'query' ist erforderlich.")
    limit = int(arguments.get("limit", 20) or 20)
    use_regex = bool(arguments.get("regex", False))
    folder = arguments.get("folder")

    matcher = None
    literals = []
    if use_regex:
        try:
            matcher = re.compile(str(query), re.IGNORECASE)
        except re.error as error:
            raise WikiError("Ungültiger regulärer Ausdruck: " + str(error))
    else:
        literals = [part.strip().lower()
                    for part in str(query).split("|") if part.strip()]
        if not literals:
            raise WikiError("Parameter 'query' enthält keinen Suchbegriff.")

    folder_prefix = None
    if folder and str(folder).strip():
        folder_prefix = str(folder).strip().strip("/").lower()

    results = []
    for page in index.sorted_pages():
        if folder_prefix is not None:
            lowered = page.path.lower()
            if not (lowered == folder_prefix
                    or lowered.startswith(folder_prefix + "/")):
                continue
        matches = []
        for number, line in enumerate(page.content.split("\n"), start=1):
            if matcher is not None:
                hit = matcher.search(line) is not None
            else:
                lowered_line = line.lower()
                hit = any(literal in lowered_line for literal in literals)
            if hit:
                matches.append({"line_no": number, "text": truncate(line)})
                if len(matches) >= MAX_MATCH_LINES:
                    break
        if matches:
            results.append({
                "path": page.path,
                "title": page.title,
                "type": page.frontmatter.get("type"),
                "matches": matches,
            })
        if len(results) >= limit:
            break
    return {"query": query, "count": len(results), "results": results}


def tool_get_page(index, arguments):
    """Liefert eine einzelne Seite mit Frontmatter und Rumpftext."""
    raw = arguments.get("path")
    if raw is None or not str(raw).strip():
        raise WikiError("Parameter 'path' ist erforderlich.")
    normalized = normalize_page_path(raw)
    index.safe_path(normalized)

    page = index.pages.get(normalized)
    if page is None:
        for key in index.pages:
            if key.lower() == normalized.lower():
                page = index.pages[key]
                break
    if page is None:
        stem = os.path.basename(normalized)[:-3]
        candidates = index.by_title(stem)
        if len(candidates) == 1:
            page = candidates[0]
        elif len(candidates) > 1:
            return {
                "path": normalized,
                "ambiguous": True,
                "candidates": [{"path": item.path, "title": item.title}
                               for item in candidates],
            }
        else:
            raise WikiError("Seite nicht gefunden: " + str(raw))
    content = page.body if page.body.strip() else page.content
    return {
        "path": page.path,
        "title": page.title,
        "frontmatter": page.frontmatter,
        "content": content,
    }


def tool_get_norm(index, arguments):
    """Liefert Normknoten und alle Seiten, die die Norm im Frontmatter führen."""
    norm = arguments.get("norm")
    if not norm or not str(norm).strip():
        raise WikiError("Parameter 'norm' ist erforderlich.")
    needle = normalize_ws(norm)

    node_page = None
    for page in index.sorted_pages():
        if normalize_ws(page.title) == needle:
            node_page = {"path": page.path, "frontmatter": page.frontmatter}
            break

    citing = []
    for page in index.sorted_pages():
        entries = as_list(page.frontmatter.get("normen"))
        hits = []
        for entry in entries:
            value = normalize_ws(entry)
            if value.startswith(needle) or needle in value:
                hits.append(entry)
        if hits:
            citing.append({
                "path": page.path,
                "title": page.title,
                "norm_entries": hits,
            })
    return {
        "norm": norm,
        "node_page": node_page,
        "citing_pages": citing,
    }


def tool_get_backlinks(index, arguments):
    """Liefert alle Seiten, die auf die angegebene Seite verlinken."""
    raw = arguments.get("page")
    if raw is None or not str(raw).strip():
        raise WikiError("Parameter 'page' ist erforderlich.")
    name = str(raw).strip().replace("\\", "/")
    if name.endswith(".md"):
        name = name[:-3]
    if "/" in name:
        name = name.split("/")[-1]
    target = normalize_ws(name)

    backlinks = []
    for page in index.sorted_pages():
        if normalize_ws(page.title) == target:
            continue
        found = [split_wikilink(link)
                 for link in WIKILINK_RE.findall(page.content)]
        if not any(normalize_ws(item) == target for item in found):
            continue
        contexts = []
        for line in page.content.split("\n"):
            if "[[" not in line:
                continue
            names = [split_wikilink(link) for link in WIKILINK_RE.findall(line)]
            if any(normalize_ws(item) == target for item in names):
                contexts.append(truncate(line.strip()))
                if len(contexts) >= MAX_BACKLINK_CONTEXTS:
                    break
        backlinks.append({
            "path": page.path,
            "title": page.title,
            "contexts": contexts,
        })
    return {"page": name, "count": len(backlinks), "backlinks": backlinks}


def tool_list_unverified(index, arguments):
    """Listet Wiki-Seiten mit offenem Verifikationsbedarf."""
    limit = int(arguments.get("limit", 50) or 50)
    entries = []
    for page in index.sorted_pages():
        reasons = []
        types = as_list(page.frontmatter.get("type"))
        is_wiki_page = "wiki-page" in types
        has_sources = len(as_list(page.frontmatter.get("quellen"))) > 0
        has_verified = "verifiziert" in page.frontmatter and str(
            page.frontmatter.get("verifiziert")).strip() != ""
        if is_wiki_page and has_sources and not has_verified:
            reasons.append("kein verifiziert-Feld")
        if "[!unbelegt]" in page.content:
            reasons.append("offener [!unbelegt]-Befund")
        if not reasons:
            continue
        entries.append({
            "path": page.path,
            "title": page.title,
            "reason": "; ".join(reasons),
            "quellen": as_list(page.frontmatter.get("quellen")),
            "rechtsstand": page.frontmatter.get("rechtsstand"),
        })
    return {"count": len(entries), "pages": entries[:limit]}


def tool_list_stale(index, arguments):
    """Listet Seiten, deren `rechtsstand` älter als `days` Tage ist."""
    days = int(arguments.get("days", 365) or 365)
    limit = int(arguments.get("limit", 50) or 50)
    today = datetime.date.today()
    entries = []
    for page in index.sorted_pages():
        raw = page.frontmatter.get("rechtsstand")
        if raw is None:
            continue
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if raw is None:
            continue
        stand = parse_date(raw)
        if stand is None:
            continue
        age = (today - stand).days
        if age > days:
            entries.append({
                "path": page.path,
                "title": page.title,
                "rechtsstand": str(raw),
                "age_days": age,
            })
    entries.sort(key=lambda item: -item["age_days"])
    return {"count": len(entries), "days": days, "pages": entries[:limit]}


TOOLS = [
    {
        "name": "wiki_info",
        "description": (
            "Kennzahlen des Wikis: Anzahl Seiten, Verteilung nach type und "
            "wiki-category, Ordnerliste, Zeitpunkt der letzten Indexierung."),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "handler": tool_wiki_info,
    },
    {
        "name": "search_wiki",
        "description": (
            "Volltextsuche über alle Wiki-Seiten. Ohne 'regex' wird 'query' "
            "als Literal gesucht; '|' trennt mehrere Literale als ODER. "
            "Liefert je Datei bis zu drei Trefferzeilen."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Suchbegriff; '|' trennt ODER-Alternativen.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximale Zahl der Trefferdateien.",
                    "default": 20,
                },
                "regex": {
                    "type": "boolean",
                    "description": "Query als regulären Ausdruck auswerten.",
                    "default": False,
                },
                "folder": {
                    "type": "string",
                    "description": "Suche auf einen Unterordner begrenzen.",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "handler": tool_search_wiki,
    },
    {
        "name": "get_page",
        "description": (
            "Liefert eine Wiki-Seite mit Frontmatter und Text. 'path' ist "
            "relativ zum Wiki-Root, die Endung '.md' ist optional. Wird der "
            "Pfad nicht gefunden, erfolgt eine Auflösung über den Dateinamen "
            "wie bei einem Obsidian-Wikilink."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relativer Pfad oder Seitenname.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "handler": tool_get_page,
    },
    {
        "name": "get_norm",
        "description": (
            "Liefert zu einer Norm (z. B. 'DSGVO Art. 6') die Normknoten-Seite "
            "sowie alle Seiten, die die Norm im Frontmatter-Feld 'normen' "
            "führen."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "norm": {
                    "type": "string",
                    "description": "Normbezeichnung, z. B. 'DSGVO Art. 6'.",
                },
            },
            "required": ["norm"],
            "additionalProperties": False,
        },
        "handler": tool_get_norm,
    },
    {
        "name": "get_backlinks",
        "description": (
            "Liefert alle Seiten, die per Wikilink auf die angegebene Seite "
            "verweisen, inklusive Kontextzeilen. Alias-, Anker- und "
            "Pfadschreibweisen werden aufgelöst."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "string",
                    "description": "Seitenname oder relativer Pfad.",
                },
            },
            "required": ["page"],
            "additionalProperties": False,
        },
        "handler": tool_get_backlinks,
    },
    {
        "name": "list_unverified",
        "description": (
            "Listet Wiki-Seiten mit Quellenangaben, aber ohne 'verifiziert'-"
            "Feld, sowie Seiten mit offenem '[!unbelegt]'-Befund."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximale Zahl zurückgegebener Seiten.",
                    "default": 50,
                },
            },
            "additionalProperties": False,
        },
        "handler": tool_list_unverified,
    },
    {
        "name": "list_stale",
        "description": (
            "Listet Seiten, deren Frontmatter-Feld 'rechtsstand' älter als "
            "'days' Tage ist, absteigend nach Alter."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Schwelle in Tagen.",
                    "default": 365,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximale Zahl zurückgegebener Seiten.",
                    "default": 50,
                },
            },
            "additionalProperties": False,
        },
        "handler": tool_list_stale,
    },
]

TOOLS_BY_NAME = dict((entry["name"], entry) for entry in TOOLS)


def public_tool_list():
    """Liefert die Tool-Beschreibungen ohne interne Handler-Referenz."""
    result = []
    for entry in TOOLS:
        result.append({
            "name": entry["name"],
            "description": entry["description"],
            "inputSchema": entry["inputSchema"],
        })
    return result


# --------------------------------------------------------------------------
# MCP-Protokoll
# --------------------------------------------------------------------------

class WikiServer(object):
    """Minimale MCP-Implementierung über newline-getrenntes JSON auf stdio."""

    def __init__(self, index):
        self.index = index
        self.protocol_version = DEFAULT_PROTOCOL_VERSION

    # -- Transport --------------------------------------------------------

    def send(self, message):
        """Schreibt genau eine JSON-Zeile nach stdout und leert den Puffer."""
        sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def send_result(self, request_id, result):
        self.send({"jsonrpc": "2.0", "id": request_id, "result": result})

    def send_error(self, request_id, code, message):
        self.send({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        })

    # -- Methoden ---------------------------------------------------------

    def handle_initialize(self, params):
        requested = params.get("protocolVersion")
        if isinstance(requested, str) and requested.strip():
            self.protocol_version = requested
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": WIKI_MCP_VERSION},
        }

    def handle_tools_call(self, params):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            arguments = {}
        entry = TOOLS_BY_NAME.get(name)
        if entry is None:
            return {
                "content": [{"type": "text",
                             "text": "Unbekanntes Tool: " + str(name)}],
                "isError": True,
            }
        try:
            self.index.refresh()
        except Exception as error:  # Index-Fehler darf den Server nicht töten
            log("Index-Auffrischung fehlgeschlagen: " + str(error))
        try:
            payload = entry["handler"](self.index, arguments)
        except WikiError as error:
            return {
                "content": [{"type": "text", "text": str(error)}],
                "isError": True,
            }
        except Exception as error:
            log("Tool-Fehler in " + str(name) + ": " + repr(error))
            return {
                "content": [{"type": "text",
                             "text": ("Fehler bei der Ausführung von "
                                      + str(name) + ": " + str(error))}],
                "isError": True,
            }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        return {"content": [{"type": "text", "text": text}]}

    # -- Hauptschleife ----------------------------------------------------

    def handle_message(self, message):
        """Verarbeitet eine eingehende JSON-RPC-Nachricht."""
        if not isinstance(message, dict):
            return
        has_id = "id" in message and message.get("id") is not None
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params") or {}
        if not isinstance(params, dict):
            params = {}

        if method == "initialize":
            if has_id:
                self.send_result(request_id, self.handle_initialize(params))
            return
        if method == "notifications/initialized":
            return
        if method is not None and str(method).startswith("notifications/"):
            return
        if method == "ping":
            if has_id:
                self.send_result(request_id, {})
            return
        if method == "tools/list":
            if has_id:
                self.send_result(request_id, {"tools": public_tool_list()})
            return
        if method == "tools/call":
            if has_id:
                self.send_result(request_id, self.handle_tools_call(params))
            return
        if has_id:
            self.send_error(request_id, -32601,
                            "Methode nicht unterstützt: " + str(method))

    def serve_forever(self):
        """Liest Zeilen von stdin, bis der Client die Verbindung schließt."""
        while True:
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                break
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except ValueError as error:
                self.send_error(None, -32700,
                                "JSON konnte nicht gelesen werden: "
                                + str(error))
                continue
            try:
                self.handle_message(message)
            except Exception as error:
                log("Unerwarteter Fehler: " + repr(error))
                if isinstance(message, dict) and message.get("id") is not None:
                    self.send_error(message.get("id"), -32603,
                                    "Interner Fehler: " + str(error))


def build_parser():
    """Erzeugt den Kommandozeilen-Parser."""
    parser = argparse.ArgumentParser(
        description="Read-only MCP-Server für ein Obsidian-Markdown-Wiki.")
    parser.add_argument("--wiki-root", required=True,
                        help="Wurzelverzeichnis des Wikis.")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Ordnername, der nicht indexiert wird "
                             "(mehrfach angebbar).")
    parser.add_argument("--version", action="version",
                        version="wiki-mcp " + WIKI_MCP_VERSION)
    return parser


def main(argv=None):
    """Einstiegspunkt: Index aufbauen und die stdio-Schleife starten."""
    args = build_parser().parse_args(argv)
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    try:
        index = WikiIndex(args.wiki_root, args.exclude)
    except WikiError as error:
        log(str(error))
        return 2
    log("Index bereit: " + str(len(index.pages)) + " Seiten unter "
        + index.root)
    WikiServer(index).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
