#!/usr/bin/env bash
#
# sync.sh — kopiert die kanonische server.py des Repositories in einen Vault.
#
# Aufruf: bash sync.sh /pfad/zum/vault
#
# Ziel ist "<vault>/.wiki-mcp/server.py". Vor dem Kopieren werden die
# WIKI_MCP_VERSION beider Stände verglichen und eine Abweichung gemeldet.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${SCRIPT_DIR}/server.py"

if [[ $# -ne 1 ]]; then
    echo "Aufruf: bash sync.sh /pfad/zum/vault" >&2
    exit 64
fi

VAULT="${1%/}"

if [[ ! -f "${SOURCE}" ]]; then
    echo "Fehler: Quelldatei nicht gefunden: ${SOURCE}" >&2
    exit 66
fi

if [[ ! -d "${VAULT}" ]]; then
    echo "Fehler: Vault-Verzeichnis nicht gefunden: ${VAULT}" >&2
    exit 66
fi

TARGET_DIR="${VAULT}/.wiki-mcp"
TARGET="${TARGET_DIR}/server.py"

# Liest die Konstante WIKI_MCP_VERSION aus einer server.py.
read_version() {
    local file="$1"
    if [[ ! -f "${file}" ]]; then
        echo "-"
        return 0
    fi
    local version
    version="$(sed -n 's/^WIKI_MCP_VERSION[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "${file}" | head -n 1)"
    if [[ -z "${version}" ]]; then
        echo "?"
    else
        echo "${version}"
    fi
}

SOURCE_VERSION="$(read_version "${SOURCE}")"
TARGET_VERSION="$(read_version "${TARGET}")"

echo "Repo-Version:  ${SOURCE_VERSION}  (${SOURCE})"
echo "Vault-Version: ${TARGET_VERSION}  (${TARGET})"

if [[ "${TARGET_VERSION}" == "-" ]]; then
    echo "Hinweis: Im Vault liegt noch keine Kopie — sie wird neu angelegt."
elif [[ "${TARGET_VERSION}" != "${SOURCE_VERSION}" ]]; then
    echo "Drift erkannt: Vault-Stand ${TARGET_VERSION} weicht von Repo-Stand ${SOURCE_VERSION} ab."
elif cmp -s "${SOURCE}" "${TARGET}"; then
    echo "Gleiche Version und identischer Inhalt — Kopie wird trotzdem erneuert."
else
    echo "Gleiche Version, aber abweichender Inhalt: Der Vault-Stand wurde verändert oder das Repo hat nachgebessert, ohne die Version zu erhöhen."
fi

mkdir -p "${TARGET_DIR}"
cp "${SOURCE}" "${TARGET}"

echo "Fertig: server.py ${SOURCE_VERSION} nach ${TARGET} kopiert."
