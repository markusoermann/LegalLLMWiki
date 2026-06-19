# Skills

Vier Capabilities für das LegalWikiLLM. Ein „Skill" ist im Kern eine `SKILL.md`-Anleitung (+ optionale Skripte) — die Substanz ist agent-agnostisch, nur die Einbindung unterscheidet sich pro Agent.

> **Das LLMWiki als Single Point of Truth:** `wiki-query` ist die Schnittstelle zur verbindlichen Wissensschicht des Vaults. Inhaltsgenerierende Skills (Lehrmaterial, Prüfung/Bewertung, Recherche) sollten das Wiki **zuerst** abfragen, seine Inhalte vorrangig nutzen, mit [[Wikilinks]] belegen und Ergänzungen via `ingest` vorschlagen — so bleibt das Wiki die einzige Wahrheitsquelle.

| Skill | Zweck | Abhängigkeiten |
|---|---|---|
| `wiki-query` | Wiki durchsuchen + Antwort mit [[Wikilinks]] synthetisieren | — (Index + grep) |
| `zotero-skill` | Zotero-Bibliothek per MCP nutzen (Ingest, Metadaten, PDF, BibTeX) | Zotero-MCP-Server (s. `docs/03`) |
| `quellencheck` | Prüfen, ob zitierte Quellen real existieren (DOI/CrossRef/OpenAlex) | Python 3 (`scripts/verify_dois.py`); eigene E-Mail im Skript eintragen |
| `defuddle` | Web-Inhalte sauber als Markdown extrahieren | externes `defuddle` CLI (`npm install -g defuddle`) |

## Einbindung je Agent

### Claude Code (nativ)
Skill-Ordner nach `~/.claude/skills/` kopieren:
```bash
cp -R skills/wiki-query skills/zotero-skill skills/quellencheck skills/defuddle ~/.claude/skills/
```
Claude lädt die Skill-Metadaten automatisch und aktiviert sie bei passenden Triggern.

### Gemini CLI (nativ via Skill-Aktivierung)
Gemini CLI unterstützt Skills über die Skill-Aktivierung; lege die Ordner am von Gemini erwarteten Skill-Ort ab (siehe `docs/04-agenten-einrichtung.md`). Die `SKILL.md`-Beschreibung steuert die Aktivierung.

### Codex / OpenCode (als Prompt/Command bzw. Referenz)
Diese Agenten haben keine native Skill-Engine. Zwei Wege:
1. **Referenz aus `AGENTS.md`:** Die Trigger/Abläufe sind bereits im LLMWiki-Abschnitt der `AGENTS.md` beschrieben — der Agent folgt ihnen direkt.
2. **Custom-Command/-Prompt:** Den Inhalt der jeweiligen `SKILL.md` als wiederverwendbaren Prompt/Slash-Command des Agenten hinterlegen.

In beiden Fällen laufen die **Skripte** (`quellencheck/scripts/verify_dois.py`, das `defuddle` CLI) unverändert standalone in der Shell — unabhängig vom Agenten.

## Hinweis
Vor erster Nutzung von `quellencheck`: in `quellencheck/scripts/verify_dois.py` die Platzhalter-E-Mail (`your-email@example.com`) durch deine eigene ersetzen (höfliche Nutzung der CrossRef/OpenAlex-„polite pool").
