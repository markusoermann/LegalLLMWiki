# 02 · Obsidian-Vault einrichten

## 1. Obsidian installieren
[obsidian.md](https://obsidian.md) herunterladen und einen neuen Vault anlegen (Speicherort frei wählbar).

## 2. PARA-Ordnerstruktur anlegen
Im Vault-Root diese Ordner erstellen:

```
00 Kontext/
01 Inbox/
02 Projekte/
03 Bereiche/
04 Ressourcen/      ← hier lebt das LLMWiki
05 Daily Notes/
06 Archiv/
07 Anhänge/
```

## 3. Framework-Dateien einsetzen
Aus diesem Repo kopieren:

| Repo-Datei | Ziel im Vault |
|---|---|
| `template/AGENTS.md` | Vault-Root `AGENTS.md` |
| `template/wiki-schema.md` | `04 Ressourcen/wiki-schema.md` |
| `template/index.md` | `04 Ressourcen/index.md` |
| `template/log.md` | `04 Ressourcen/log.md` |
| `template/examples/*` | nach Belieben in `04 Ressourcen/<Thema>/` (optional, als Muster) |

Danach in `AGENTS.md` alle `[…]`-Platzhalter ausfüllen (Name, Fachgebiet, Themenordner).

## 4. Themenordner festlegen
Unter `04 Ressourcen/` je einen Ordner pro Fachgebiet anlegen (selbst gewählt) und in `AGENTS.md` unter „Wiki-Themenordner" eintragen.

## 5. Empfohlene Obsidian-Einstellungen
- **Backlinks**-Panel aktivieren (Kern des Abfrage-Konzepts).
- Optional: Graph-Ansicht, Outgoing Links, Tag-Pane.
- Neue Notizen: Standardordner `01 Inbox/`.

## Weiter
→ `03-zotero-mcp.md` — Zotero anbinden.
