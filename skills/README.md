**🇬🇧 English** · [🇩🇪 Deutsch](README.de.md)

# Skills

Four capabilities for the LegalWikiLLM. At its core, a "skill" is a `SKILL.md` instruction file (+ optional scripts) — the substance is agent-agnostic, only the integration differs per agent.

Each skill ships bilingually: `SKILL.md` (German) and `SKILL.en.md` (English). To install, use the desired language variant as `SKILL.md`.

| Skill | Purpose | Dependencies |
|---|---|---|
| `wiki-query` | Search the wiki + synthesize an answer with [[Wikilinks]] | — (index + grep) |
| `zotero-skill` | Use the Zotero library via MCP (ingest, metadata, PDF, BibTeX) | Zotero MCP server (see `docs/03`) |
| `quellencheck` | Check whether cited sources actually exist (DOI/CrossRef/OpenAlex) | Python 3 (`scripts/verify_dois.py`); enter your own email in the script |
| `defuddle` | Extract web content cleanly as Markdown | external `defuddle` CLI (`npm install -g defuddle`) |

## Integration per agent

### Claude Code (native)
Copy the skill folders into `~/.claude/skills/`:
```bash
cp -R skills/wiki-query skills/zotero-skill skills/quellencheck skills/defuddle ~/.claude/skills/
```
Claude loads the skill metadata automatically and activates them on matching triggers.

### Gemini CLI (native via skill activation)
Gemini CLI supports skills through skill activation; place the folders at the skill location Gemini expects (see `docs/04-agenten-einrichtung.md`). The `SKILL.md` description controls activation.

### Codex / OpenCode (as prompt/command or reference)
These agents have no native skill engine. Two ways:
1. **Reference from `AGENTS.md`:** The triggers/workflows are already described in the LLMWiki section of `AGENTS.md` — the agent follows them directly.
2. **Custom command/prompt:** Store the content of the respective `SKILL.md` as a reusable prompt/slash command of the agent.

In both cases, the **scripts** (`quellencheck/scripts/verify_dois.py`, the `defuddle` CLI) run unchanged standalone in the shell — independent of the agent.

## Note
Before first use of `quellencheck`: in `quellencheck/scripts/verify_dois.py`, replace the placeholder email (`your-email@example.com`) with your own (polite use of the CrossRef/OpenAlex "polite pool").
