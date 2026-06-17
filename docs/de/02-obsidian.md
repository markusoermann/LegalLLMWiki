# 02 · Obsidian-Vault einrichten

## 1. Obsidian installieren
[obsidian.md](https://obsidian.md) herunterladen und einen neuen Vault anlegen (Speicherort frei wählbar).

## 2. Ordnerstruktur — deine Entscheidung
**Es wird keine bestimmte Ordnerstruktur vorgeschrieben.** Lege die Ordner an, die zu deiner Arbeitsweise passen. Wer mag, kann eine etablierte Methode wie [PARA](https://fortelabs.com/blog/para/) nutzen — nötig ist das **nicht**.

Das LLMWiki braucht nur **einen Ort, an dem es lebt**. Entscheide:

- **Wo soll das Wiki liegen?** Ein eigener Unterordner (z.B. `Wiki/`, `Ressourcen/`, `Wissen/`) — oder direkt der **Vault-Root** (`.`). Diesen Ort nennen wir im Folgenden `[WIKI-ORDNER]`.

## 3. Framework-Dateien einsetzen
Aus diesem Repo kopieren:

| Repo-Datei | Ziel im Vault |
|---|---|
| `template/de/AGENTS.md` | **Vault-Root** `AGENTS.md` |
| `template/de/wiki-schema.md` | `[WIKI-ORDNER]/wiki-schema.md` |
| `template/de/index.md` | `[WIKI-ORDNER]/index.md` |
| `template/de/log.md` | `[WIKI-ORDNER]/log.md` |
| `template/de/examples/*` | optional als Muster nach `[WIKI-ORDNER]/<Thema>/` |

## 4. Platzhalter ausfüllen
In `AGENTS.md`:
- `[DEIN NAME]` / `[DEIN FACHGEBIET]` setzen.
- **Überall `[WIKI-ORDNER]` durch den in Schritt 2 gewählten Pfad ersetzen** (z.B. `Wiki` — oder leeren Pfad bzw. `.`, falls das Wiki im Vault-Root liegt).
- Unter „Wiki-Themenordner" deine Fachgebiete eintragen.

## 5. Themenordner anlegen
Unter `[WIKI-ORDNER]/` je einen Ordner pro Fachgebiet anlegen (selbst gewählt) und in `AGENTS.md` eintragen. Du kannst auch klein anfangen und Ordner später ergänzen (s. „Neue Themenordner" in `AGENTS.md`).

## 6. Empfohlene Obsidian-Einstellungen
- **Backlinks**-Panel aktivieren (Kern des Abfrage-Konzepts: Norm-/Urteilsknoten werden über ihre Backlinks gefunden).
- Optional: Graph-Ansicht, Outgoing Links, Tag-Pane.

## Weiter
→ `03-zotero-mcp.md` — Zotero anbinden.
