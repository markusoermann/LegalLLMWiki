# wiki-mcp — Read-only MCP-Server für das Obsidian-Wiki

## Zweck

`wiki-mcp` macht ein Obsidian-Markdown-Wiki für einen MCP-Client (Claude Code,
Claude Desktop) strukturiert zugänglich — nicht als Dateibaum, sondern als
Wissensgraph: Volltextsuche, Seitenabruf, Normknoten mit ihren Fundstellen,
Backlinks sowie zwei Pflege-Berichte (unverifizierte Seiten, veralteter
Rechtsstand).

Der Server ist bewusst klein: eine einzige Datei, ausschließlich
Python-Standardbibliothek, kein MCP-SDK. Das MCP-Protokoll (JSON-RPC 2.0) ist
direkt implementiert. Lauffähig unter Python 3.9 — also mit dem
System-Python von macOS (`/usr/bin/python3`).

## Sicherheitsmodell

**stdio statt Netzwerk.** Der Server kommuniziert über newline-getrenntes JSON
auf `stdin`/`stdout`. Er öffnet keinen Port, bindet keine Adresse und
importiert keine Netzwerkmodule. Von Dritten ist er nicht erreichbar, weil es
nichts gibt, womit man sich verbinden könnte — der Prozess existiert nur als
Kindprozess des MCP-Clients auf demselben Rechner und stirbt mit ihm.

**Read-only by design.** Es gibt bewusst kein Schreib-Tool. Der Server
schreibt, verschiebt und löscht keine Datei. Die einzige Dateisystemoperation
ist das Lesen von `.md`-Dateien. Ein fehlgeleitetes Modell kann über diesen
Server keinen Vault beschädigen.

**Pfad-Härtung.** Jeder Pfadparameter wird mit `os.path.realpath` gegen den
Wiki-Root aufgelöst. Absolute Pfade, Tilde-Pfade, `..`-Segmente und Symlinks,
die aus dem Root herausführen, werden mit einer Fehlermeldung abgewiesen,
bevor irgendetwas gelesen wird.

**Keine Ausgabe nach stdout außer Protokoll.** Diagnosemeldungen gehen
ausschließlich nach `stderr`. Ein versehentliches `print` würde den
JSON-RPC-Strom zerstören; der Code vermeidet das konsequent.

## Installation

Keine. Es gibt keine Abhängigkeiten, kein `pip install`, keine virtuelle
Umgebung. Vorausgesetzt wird lediglich ein Python ab Version 3.9 — auf macOS
genügt das mitgelieferte `/usr/bin/python3`.

Manueller Probelauf:

```bash
python3 server.py --wiki-root "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]" \
    --exclude "[NICHT-WIKI-ORDNER]"
```

Der Server wartet dann auf JSON-RPC-Zeilen auf stdin. Im Normalbetrieb startet
ihn der MCP-Client.

## Konfiguration

In der `.mcp.json` des Vaults (oder in der Client-Konfiguration):

```json
{
  "mcpServers": {
    "wiki": {
      "command": "python3",
      "args": [
        "/PFAD/ZU/DEINEM/VAULT/.wiki-mcp/server.py",
        "--wiki-root",
        "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]",
        "--exclude",
        "[NICHT-WIKI-ORDNER]"
      ]
    }
  }
}
```

`--exclude` ist mehrfach angebbar und meint Ordnernamen, nicht Pfade.
Verzeichnisse, die mit `.` beginnen (etwa `.obsidian`), werden ohnehin immer
übersprungen.

## Die 7 Tools

| Tool | Parameter | Ergebnis |
|---|---|---|
| `wiki_info` | – | `version`, `wiki_root`, `pages_total`, `by_type`, `by_wiki_category`, `folders`, `indexed_at` |
| `search_wiki` | `query` (Pflicht), `limit` (Standard 20), `regex` (Standard `false`), `folder` (optional) | Trefferdateien mit je bis zu drei Fundzeilen (`line_no`, `text`, auf 300 Zeichen gekürzt) |
| `get_page` | `path` (Pflicht) | `path`, `title`, `frontmatter`, `content` |
| `get_norm` | `norm` (Pflicht) | `node_page` (Normknoten-Seite) und `citing_pages` (alle Seiten mit der Norm im `normen:`-Frontmatter) |
| `get_backlinks` | `page` (Pflicht) | alle Seiten mit einem Wikilink auf die Seite, je bis zu zwei Kontextzeilen |
| `list_unverified` | `limit` (Standard 50) | Seiten mit Quellen, aber ohne `verifiziert:`, sowie Seiten mit offenem `[!unbelegt]`-Befund, je mit `reason` |
| `list_stale` | `days` (Standard 365), `limit` (Standard 50) | Seiten mit `rechtsstand:` älter als `days`, absteigend nach `age_days` |

Erläuterungen:

- **Suche.** Ohne `regex` wird `query` als Literal gesucht; ein `|` trennt
  mehrere Literale als ODER (`"Einwilligung|Consent"`). Mit `regex: true`
  wird `query` als regulärer Ausdruck ausgewertet. In beiden Fällen
  case-insensitiv. `folder` begrenzt die Suche auf einen Unterordner
  (relativ zum Wiki-Root).
- **Seitenabruf.** `path` ist relativ zum Wiki-Root, die Endung `.md` ist
  optional. Schlägt der Pfad fehl, wird wie bei einem Obsidian-Wikilink über
  den Dateinamen aufgelöst; bei Mehrdeutigkeit liefert das Tool die
  Kandidatenliste statt einer willkürlichen Auswahl.
- **Normen.** Der Abgleich normalisiert Whitespace und ignoriert
  Groß-/Kleinschreibung. `"DSGVO Art. 6"` findet auch Einträge wie
  `"DSGVO Art. 6 Abs. 1 lit. f"`.
- **Backlinks.** Erkannt werden `[[Name]]`, `[[Name|Alias]]`, das in
  Tabellen nötige `[[Name\|Alias]]`, `[[Name#Abschnitt]]` und
  `[[Ordner/Name]]`.

Alle Tools antworten mit einem JSON-Dokument im Textfeld der MCP-Antwort
(`ensure_ascii=False`, eingerückt).

## Mehrgeräte-Betrieb

Code und Vault liegen in einem synchronisierten Ordner (iCloud, Dropbox,
Syncthing). Synchronisiert wird nur die Datei `server.py` samt Vault — nicht
der laufende Dienst. Auf jedem Gerät startet der lokale MCP-Client seine
eigene Instanz gegen die lokale Kopie des Vaults. Es gibt keinen gemeinsamen
Server, keine Sitzung über Netz und nichts, was zwischen Geräten geteilt
würde. Fällt ein Gerät aus, betrifft das die anderen nicht.

Kanonisch ist die Fassung im Repository (`mcp/wiki-mcp/server.py`). Die
Vault-Kopie unter `.wiki-mcp/server.py` wird mit `sync.sh` aktualisiert:

```bash
bash sync.sh "/Pfad/zum/Vault"
```

Das Skript legt das Zielverzeichnis an, vergleicht vorher die
`WIKI_MCP_VERSION` beider Stände und meldet eine Abweichung, bevor es kopiert.

## Grenzen

- **Kein Schreibzugriff.** Änderungen am Wiki erfolgen weiterhin über den
  Dateizugriff des Clients, nicht über diesen Server. Das ist Absicht.
- **Index im Speicher.** Alle Seiten werden beim Start vollständig eingelesen.
  Bei einigen hundert Dateien ist das unmerklich; bei sehr großen Vaults
  (zehntausende Dateien) wäre ein persistenter Index sinnvoller.
- **Auffrischung über mtime.** Vor jedem Tool-Aufruf wird der Baum
  durchlaufen und geänderte, neue oder gelöschte Dateien werden nachgeführt.
  Das ist für iCloud-Vaults nötig, kostet aber pro Aufruf einen Verzeichnis-
  Scan. Dateien, deren Änderungszeit nicht fortgeschrieben wird, bleiben
  unbemerkt.
- **Einfacher YAML-Parser.** Unterstützt werden `key: wert`, `key: [a, b]`
  und mehrzeilige Listen mit `  - wert`. Verschachtelte Strukturen, Anker
  und Blockskalare werden ignoriert — für das Frontmatter-Schema dieses Wikis
  genügt das, ein vollständiger YAML-Parser ist es nicht.
- **Ordnerausschluss nach Namen.** `--exclude` vergleicht Ordnernamen auf
  jeder Ebene, nicht Pfade.
