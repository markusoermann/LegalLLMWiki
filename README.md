**🇬🇧 English** · [🇩🇪 Deutsch](README.de.md)

# LegalWikiLLM

**An AI-maintained, law-optimized subject wiki for Obsidian — with Zotero integration and multi-agent support.**

An AI agent builds a structured wiki inside your Obsidian vault and keeps it up to date: sources live in **Zotero**, the agent pulls them in via **MCP** and writes curated wiki pages. Optimized for law — with norm nodes, landmark decisions, a legal hierarchy and ECLI/ELI identifiers.

The project is based on **Andrej Karpathy's LLM wiki pattern** (2026) and is aligned with Google's **Open Knowledge Format (OKF)** standard — see [Foundations & Standards](#foundations--standards).

## Who is it for?

Lawyers, researchers and anyone who wants a queryable subject wiki with clean source integration — **independent of the AI agent**.

## Features

- 📚 **Zotero ↔ Obsidian** via MCP (ingest of metadata, abstract, PDF full text, annotations)
- ⚖️ **Law-optimized:** norm nodes, landmark decisions, 6-level legal hierarchy, `[!recht]` callouts, `ecli`/`resource` (ELI/ECLI)
- 🤖 **Multi-agent:** works with **Claude Code, OpenAI Codex, OpenCode and Gemini CLI** (canonical `AGENTS.md`)
- 🔗 **Graph without a triplestore:** backlinks of the norm/decision nodes as the query path
- 🧩 **4 skills:** `wiki-query`, `zotero-skill`, `quellencheck`, `defuddle`
- 📐 **Schema aligned with the OKF standard** ([Google Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md))

## Quickstart

1. **Create an Obsidian vault**, choose your own folder structure + wiki location → [`docs/en/02-obsidian.md`](docs/en/02-obsidian.md)
2. **Drop in the framework files** from `template/` (`AGENTS.md`, `wiki-schema.md`, `index.md`, `log.md`)
3. **Connect Zotero + MCP** → [`docs/en/03-zotero-mcp.md`](docs/en/03-zotero-mcp.md)
4. **Set up your agent** (context file + MCP config + skills) → [`docs/en/04-agent-setup.md`](docs/en/04-agent-setup.md)
5. **Get going:** `ingest @citekey`, `query wiki: …`, `lint wiki` → [`docs/en/05-workflows.md`](docs/en/05-workflows.md)

Legal specifics: [`docs/en/06-legal-features.md`](docs/en/06-legal-features.md) · Concept/architecture: [`docs/en/01-concept.md`](docs/en/01-concept.md)

## Repository layout

```
docs/        Setup guide (01–06), per language: docs/en/ + docs/de/
template/    AGENTS.md, wiki-schema.md, index/log, examples/, agent-config/
             localized text in template/en/ + template/de/; language-neutral agent-config/, mcp/
skills/      4 skills + integration guide (skills/README.md)
mcp/         Example MCP configuration
```

## Notes

- **No personal data:** the repo contains only the generalized framework + public-domain example content. Your own content/Zotero library stays local.
- **Dependencies:** Zotero 7, [`zotero-mcp`](https://github.com/cookjohn/zotero-mcp) (`npm i -g zotero-mcp`), Node.js (for the `npx` filesystem server); for `defuddle`: `npm i -g defuddle`.

## Foundations & Standards

- **LLM wiki pattern** — The underlying concept (an AI-maintained, "compounding" Markdown knowledge wiki as a layer between the user and the raw sources) comes from **Andrej Karpathy** ([gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)), introduced in April 2026. LegalWikiLLM is an agent-agnostic implementation of this pattern specialized for legal content.
- **Second-brain implementation** — The concrete wiki architecture (the concepts/entities/synthesis taxonomy, `index.md`/`log.md`, the ingest/query/lint skills, the Obsidian and multi-agent integration) builds on Nicholas Spisak's [second-brain](https://github.com/NicholasSpisak/second-brain) project, adapted and extended for legal content.
- **Open Knowledge Format (OKF)** — The schema is aligned with Google's open knowledge format standard: every non-reserved page carries a `type` field, `resource` is the OKF asset URI field (ELI/ECLI/DOI). Specification: [GoogleCloudPlatform/knowledge-catalog · okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). Details + deliberate deviations in the schema (`template/wiki-schema.md`, section "OKF compatibility").

### Legal standards & identifiers

For stable, dereferenceable source citations (`ecli` and `resource` fields), the schema uses established legal identifiers:

- **ECLI** — European Case Law Identifier; uniform citation of court decisions (`ECLI:Country:Court:Year:Number`). Coordinator at EU level: CJEU. Reference: [e-Justice Portal](https://e-justice.europa.eu/topics/legislation-and-case-law/european-case-law-identifier-ecli_en) · [EUR-Lex](https://eur-lex.europa.eu/EN/legal-content/summary/european-case-law-identifier.html)
- **ELI** — European Legislation Identifier; standardized URIs/metadata for legislation. Reference: [EUR-Lex ELI register](https://eur-lex.europa.eu/eli-register/index.html) · [ELI help](https://eur-lex.europa.eu/content/help/eurlex-content/eli.html)
- **CELEX** — EUR-Lex's document numbering system; used in `resource` URLs for EU case law. Reference: [EUR-Lex](https://eur-lex.europa.eu/)

Official data sources used for `resource` URIs:

- **EUR-Lex / data.europa.eu** — EU law & case law (ELI: `http://data.europa.eu/eli/…`, CELEX)
- **gesetze-im-internet.de** — German federal law, down to the individual section (e.g. `…/uwg_2004/__5a.html`)
- **recht.bund.de** — German ELI (Federal Law Gazette)

## License

[MIT](LICENSE) © 2026 Markus Oermann
