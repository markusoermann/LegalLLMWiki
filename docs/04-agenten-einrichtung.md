# 04 · Agenten-Einrichtung (Claude Code · Codex · OpenCode · Gemini CLI)

Zwei Dinge pro Agent: **(A) Kontextdatei** (`AGENTS.md`) verdrahten und **(B) MCP-Server** eintragen. Optional **(C) Skills** (→ `skills/README.md`).

Fertige Snippets: `template/agent-config/<agent>/`. Vault-Pfad-Platzhalter `/PFAD/ZU/DEINEM/VAULT` überall ersetzen. Voraussetzung: `npm install -g zotero-mcp` (→ `03-zotero-mcp.md`).

## Kanonische Kontextdatei
`AGENTS.md` ist der Kanon. Für Agenten mit anderem Dateinamen Symlinks setzen — im Vault-Root:
```bash
bash /Pfad/zu/LegalWikiLLM/template/agent-config/symlinks.sh
# erzeugt CLAUDE.md → AGENTS.md und GEMINI.md → AGENTS.md
```

---

## Claude Code
- **(A)** Kontextdatei: `CLAUDE.md → AGENTS.md` (Symlink, s.o.).
- **(B)** MCP: `.mcp.json` im Vault-Root (oder global `~/.claude.json`). Vorlage: `template/agent-config/claude/.mcp.json`.
- **(C)** Skills: Ordner nach `~/.claude/skills/` kopieren (nativ).

## OpenAI Codex
- **(A)** Kontextdatei: liest `AGENTS.md` **nativ** — nichts zu tun.
- **(B)** MCP: `~/.codex/config.toml`. Vorlage: `template/agent-config/codex/config.toml`:
```toml
[mcp_servers.zotero]
command = "zotero-mcp-server"
args = []

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/PFAD/ZU/DEINEM/VAULT"]
```
- **(C)** Skills: keine native Engine → `SKILL.md`-Inhalte als Custom-Prompt nutzen bzw. Abläufe aus `AGENTS.md` befolgen; Skripte laufen standalone.

## OpenCode
- **(A)** Kontextdatei: liest `AGENTS.md` **nativ**.
- **(B)** MCP: `opencode.json`. Vorlage: `template/agent-config/opencode/opencode.json` (`type: "local"`, `command`-Array, `enabled: true`).
- **(C)** Skills: wie Codex (Prompt/Command + standalone-Skripte).

## Gemini CLI
- **(A)** Kontextdatei: `GEMINI.md → AGENTS.md` (Symlink, s.o.).
- **(B)** MCP: `~/.gemini/settings.json` (oder projektweit `.gemini/settings.json`). Vorlage: `template/agent-config/gemini/settings.json`.
- **(C)** Skills: Gemini CLI unterstützt Skill-Aktivierung — Skill-Ordner am erwarteten Ort ablegen.

---

## Verifikation
Nach der Einrichtung: Agent starten, `03-zotero-mcp.md` §5 (Verbindungstest) durchführen, dann `05-workflows.md`.
