# 08 · Wiki-MCP-Server (optional)

Der Wiki-MCP-Server (`mcp/wiki-mcp/`) macht das Wiki für Agenten über **Tools** adressierbar statt nur über Grep. Das ist kein kosmetischer Unterschied: `get_norm` und `get_backlinks` werten das **Frontmatter** aus, also strukturierte Felder wie `normen:` oder `rechtsstand:`. Grep sieht nur Zeilen. Zwei Pflegeberichte (`list_unverified`, `list_stale`) folgen unmittelbar aus den Feldern, die Kapitel 07 eingeführt hat.

Der Server ist eine einzige Datei, ausschließlich Python-Standardbibliothek, ohne MCP-SDK; MCP (JSON-RPC 2.0) ist direkt implementiert.

## Sicherheitsmodell

**stdio statt Netzwerk.** Der Server kommuniziert über newline-getrenntes JSON auf `stdin`/`stdout`. Er öffnet keinen Port, ruft kein `bind()` auf und importiert kein Netzwerkmodul. Von Dritten ist er nicht erreichbar, weil es nichts gibt, womit man sich verbinden könnte: Der Prozess existiert nur als Kindprozess des MCP-Clients auf demselben Rechner und stirbt mit ihm.

**Read-only by design.** Es gibt bewusst kein Schreib-Tool. Der Server schreibt, verschiebt und löscht keine Datei; die einzige Dateisystemoperation ist das Lesen von `.md`-Dateien. Ein fehlgeleitetes Modell kann über diesen Server keinen Vault beschädigen.

**Pfad-Härtung.** Jeder Pfadparameter wird mit `os.path.realpath` gegen den Wiki-Root aufgelöst. Absolute Pfade, Tilde-Pfade, `..`-Segmente und Symlinks, die aus dem Root herausführen, werden abgewiesen, bevor irgendetwas gelesen wird.

## Voraussetzungen

System-Python ab 3.9 (unter macOS genügt `/usr/bin/python3`). Keine pip-Abhängigkeiten, kein venv, kein Node.

## Installation

```bash
bash mcp/wiki-mcp/sync.sh /PFAD/ZU/DEINEM/VAULT
# kopiert server.py nach /PFAD/ZU/DEINEM/VAULT/.wiki-mcp/server.py
```

Das Skript legt das Zielverzeichnis an, vergleicht vorher die `WIKI_MCP_VERSION` von Repo- und Vault-Stand und meldet eine Abweichung, bevor es kopiert. Kanonisch bleibt die Fassung im Repo.

## Konfiguration

`.mcp.json` im **Vault-Root** (Claude Code):

```json
{
  "mcpServers": {
    "wiki": {
      "command": "python3",
      "args": [
        "/PFAD/ZU/DEINEM/VAULT/.wiki-mcp/server.py",
        "--wiki-root", "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]",
        "--exclude", "Ordnername"
      ]
    }
  }
}
```

**Warum projektbezogen und nicht global?** Eine `.mcp.json` im Vault liegt im Vault und wird mit ihm synchronisiert, ist also auf jedem Gerät verfügbar, sobald der Vault dort ankommt. Eine globale Agentenkonfiguration (`~/.claude.json`, `~/.codex/config.toml`) wird nicht mitsynchronisiert und muss auf jedem Gerät von Hand nachgezogen werden.

`--exclude` ist mehrfach angebbar und meint **Ordnernamen, nicht Pfade**; damit lassen sich private Bereiche innerhalb des Wiki-Ordners ausnehmen. Verzeichnisse, die mit `.` beginnen (etwa `.obsidian`), werden immer übersprungen.

Andere Agenten analog zu `04-agenten-einrichtung.md`:

| Agent | Datei | Form |
|---|---|---|
| Claude Code | `.mcp.json` (Vault-Root) | `mcpServers.wiki` mit `command` + `args` |
| OpenAI Codex | `~/.codex/config.toml` | `[mcp_servers.wiki]` mit `command = "python3"`, `args = [...]` |
| OpenCode | `opencode.json` | `mcp.wiki` mit `"type": "local"`, `command: [...]`, `enabled: true` |
| Gemini CLI | `~/.gemini/settings.json` | `mcpServers.wiki` mit `command` + `args` |

## Die sieben Tools

| Tool | Parameter | Rückgabe |
|---|---|---|
| `wiki_info` | – | `version`, `wiki_root`, `pages_total`, `by_type`, `by_wiki_category`, `folders`, `indexed_at` |
| `search_wiki` | `query` (Pflicht), `limit` (Standard 20), `regex` (Standard `false`), `folder` (optional) | Trefferdateien mit je bis zu drei Fundzeilen (`line_no`, `text`, auf 300 Zeichen gekürzt) |
| `get_page` | `path` (Pflicht) | `path`, `title`, `frontmatter`, `content` |
| `get_norm` | `norm` (Pflicht) | `node_page` (Normknoten-Seite) und `citing_pages` (alle Seiten mit der Norm im `normen:`-Frontmatter) |
| `get_backlinks` | `page` (Pflicht) | alle Seiten mit einem Wikilink auf die Seite, je bis zu zwei Kontextzeilen |
| `list_unverified` | `limit` (Standard 50) | Seiten mit Quellen, aber ohne `verifiziert:`, sowie Seiten mit offenem `[!unbelegt]`-Befund, je mit `reason` |
| `list_stale` | `days` (Standard 365), `limit` (Standard 50) | Seiten mit `rechtsstand:` älter als `days`, absteigend nach `age_days` |

Hinweise: Ohne `regex` wird `query` als Literal gesucht, `|` trennt mehrere Literale als ODER (`"Einwilligung|Consent"`), in beiden Fällen case-insensitiv. Bei `get_page` ist `path` relativ zum Wiki-Root und die Endung `.md` optional; schlägt der Pfad fehl, wird wie bei einem Obsidian-Wikilink über den Dateinamen aufgelöst, bei Mehrdeutigkeit kommt die Kandidatenliste statt einer willkürlichen Auswahl. `get_norm` normalisiert Whitespace und Groß-/Kleinschreibung, `"DSGVO Art. 6"` findet also auch `"DSGVO Art. 6 Abs. 1 lit. f"`. Alle Tools antworten mit einem JSON-Dokument im Textfeld der MCP-Antwort.

## Mehrgeräte-Betrieb

Code und Vault liegen in einem synchronisierten Ordner (iCloud Drive, Dropbox, Syncthing). Synchronisiert werden nur `server.py` und der Vault, nicht der laufende Dienst. Auf jedem Gerät startet der lokale MCP-Client seine eigene Instanz gegen die lokale Kopie. Es gibt keinen gemeinsamen Server, keine Sitzung über Netz und nichts, was zwischen Geräten geteilt würde; fällt ein Gerät aus, betrifft das die anderen nicht.

Der Index wird beim Start vollständig aufgebaut und vor jedem Tool-Aufruf per mtime-Vergleich aufgefrischt. Das kostet pro Aufruf einen Verzeichnis-Scan, ist bei Sync-Nachzüglern aber genau der Punkt: Dateien, die der Sync-Dienst erst nach dem Start nachliefert, werden ohne Neustart sichtbar.

## Grenzen

- **Kein Schreibzugriff.** Änderungen am Wiki laufen weiterhin über den Dateizugriff des Clients. Das ist Absicht, nicht Rückstand.
- **Index im Speicher.** Alle Seiten werden beim Start eingelesen. Bei einigen hundert Dateien ist das unmerklich, bei zehntausenden wäre ein persistenter Index sinnvoller.
- **Keine Volltextindizierung im Sinne einer Suchmaschine.** `search_wiki` ist ein zeilenweiser Literal-/Regex-Scan, kein Ranking, kein Stemming, keine semantische Ähnlichkeit.
- **Einfacher YAML-Parser.** `key: wert`, `key: [a, b]` und mehrzeilige Listen werden verstanden; verschachtelte Strukturen, Anker und Blockskalare nicht.
- **Auffrischung über mtime.** Dateien, deren Änderungszeit nicht fortgeschrieben wird, bleiben unbemerkt.

## Weiter
Vollständige Server-Dokumentation: `mcp/wiki-mcp/README.md`.
