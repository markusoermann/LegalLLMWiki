# 04 · Agent Setup (Claude Code · Codex · OpenCode · Gemini CLI)

Two things per agent: **(A)** wire up the **context file** (`AGENTS.md`) and **(B)** register the **MCP servers**. Optionally **(C)** Skills (→ `skills/README.md`).

Ready-made snippets: `template/agent-config/<agent>/`. Replace the vault path placeholder `/PATH/TO/YOUR/VAULT` everywhere. Prerequisite: `npm install -g zotero-mcp` (→ `03-zotero-mcp.md`).

## Canonical context file
`AGENTS.md` is the canon. For agents that use a different filename, set up symlinks — in the vault root:
```bash
bash /Path/to/LegalWikiLLM/template/agent-config/symlinks.sh
# creates CLAUDE.md → AGENTS.md and GEMINI.md → AGENTS.md
```

---

## Claude Code
- **(A)** Context file: `CLAUDE.md → AGENTS.md` (symlink, see above).
- **(B)** MCP: `.mcp.json` in the vault root (or global `~/.claude.json`). Template: `template/agent-config/claude/.mcp.json`.
- **(C)** Skills: copy the folder to `~/.claude/skills/` (native).

## OpenAI Codex
- **(A)** Context file: reads `AGENTS.md` **natively** — nothing to do.
- **(B)** MCP: `~/.codex/config.toml`. Template: `template/agent-config/codex/config.toml`:
```toml
[mcp_servers.zotero]
command = "zotero-mcp-server"
args = []

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/PATH/TO/YOUR/VAULT"]
```
- **(C)** Skills: no native engine → use the `SKILL.md` contents as a custom prompt or follow the workflows in `AGENTS.md`; the scripts run standalone.

## OpenCode
- **(A)** Context file: reads `AGENTS.md` **natively**.
- **(B)** MCP: `opencode.json`. Template: `template/agent-config/opencode/opencode.json` (`type: "local"`, `command` array, `enabled: true`).
- **(C)** Skills: same as Codex (prompt/command + standalone scripts).

## Gemini CLI
- **(A)** Context file: `GEMINI.md → AGENTS.md` (symlink, see above).
- **(B)** MCP: `~/.gemini/settings.json` (or project-wide `.gemini/settings.json`). Template: `template/agent-config/gemini/settings.json`.
- **(C)** Skills: Gemini CLI supports skill activation — place the skill folder in the expected location.

---

## Verification
After setup: start the agent, run `03-zotero-mcp.md` §5 (connection test), then `05-workflows.md`.
