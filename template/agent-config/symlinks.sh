#!/usr/bin/env bash
# Verlinkt die kanonische AGENTS.md für Agenten, die andere Dateinamen erwarten.
# Im Vault-Root ausführen (dort, wo AGENTS.md liegt).
set -euo pipefail

if [ ! -f AGENTS.md ]; then
  echo "Fehler: AGENTS.md nicht im aktuellen Verzeichnis gefunden." >&2
  exit 1
fi

ln -sf AGENTS.md CLAUDE.md   # Claude Code
ln -sf AGENTS.md GEMINI.md   # Gemini CLI
echo "✓ CLAUDE.md & GEMINI.md → AGENTS.md verlinkt (Codex & OpenCode lesen AGENTS.md nativ)."
