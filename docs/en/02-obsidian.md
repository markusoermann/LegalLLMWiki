# 02 · Setting Up the Obsidian Vault

## 1. Install Obsidian
Download [obsidian.md](https://obsidian.md) and create a new vault (choose any storage location you like).

## 2. Folder Structure — Your Decision
**No particular folder structure is prescribed.** Create the folders that fit the way you work. If you like, you can use an established method such as [PARA](https://fortelabs.com/blog/para/) — but it is **not** required.

The LLMWiki only needs **one place where it lives**. Decide:

- **Where should the wiki live?** A dedicated subfolder (e.g. `Wiki/`, `Resources/`, `Knowledge/`) — or directly the **vault root** (`.`). In the following, we call this location `[WIKI-FOLDER]`.

## 3. Putting the Framework Files in Place
Copy from this repo:

| Repo file | Destination in the vault |
|---|---|
| `template/en/AGENTS.md` | **vault root** `AGENTS.md` |
| `template/en/wiki-schema.md` | `[WIKI-FOLDER]/wiki-schema.md` |
| `template/en/index.md` | `[WIKI-FOLDER]/index.md` |
| `template/en/log.md` | `[WIKI-FOLDER]/log.md` |
| `template/en/examples/*` | optional as templates in `[WIKI-FOLDER]/<topic>/` |

## 4. Fill In the Placeholders
In `AGENTS.md`:
- Set `[YOUR NAME]` / `[YOUR FIELD]`.
- **Replace `[WIKI-FOLDER]` everywhere with the path chosen in step 2** (e.g. `Wiki` — or an empty path or `.` if the wiki lives in the vault root).
- Under "Wiki topic folders", enter your fields.

## 5. Create the Topic Folders
Under `[WIKI-FOLDER]/`, create one folder per field (your own choice) and enter it in `AGENTS.md`. You can also start small and add folders later (see "New topic folders" in `AGENTS.md`).

## 6. Recommended Obsidian Settings
- Enable the **Backlinks** panel (core of the query concept: norm and ruling nodes are found via their backlinks).
- Optional: Graph view, Outgoing Links, Tag pane.

## Next
→ `03-zotero-mcp.md` — connect Zotero.
