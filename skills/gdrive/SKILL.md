---
name: gdrive
description: Browse and read files from Maarten's Google Drive — My Drive and files shared with him. Use when asked to find dashboards, plans, specs, or any Drive document.
allowed-tools:
  - Bash
  - Read
---

# Google Drive Tool

CLI tool for browsing and reading Maarten's Google Drive (My Drive + shared files).

## Tool Path

```bash
~/Documents/Claude/picnic-analyst-assistant/skills/gdrive/gdrive.sh <command>
```

## Commands

| Command | Description |
|---------|-------------|
| `list [--folder <id>] [--type doc\|sheet\|slide\|folder]` | List files in a folder (default: root) |
| `shared [--type doc\|sheet\|slide]` | List files shared with me (sorted by recent) |
| `search <query> [--type doc\|sheet\|slide]` | Full-text search across Drive |
| `read <file_id>` | Export Google Doc/Sheet/Slide as plain text |
| `tree [--folder <id>] [--depth N] [--ids]` | Show folder tree |

## Workflow

1. **Find a file**: use `search` or `list` to locate it, note the file ID
2. **Read it**: use `read <file_id>` to get the content as text
3. **Browse structure**: use `tree` to understand how Drive is organised

## Examples

```bash
# List root of My Drive
~/Documents/Claude/picnic-analyst-assistant/skills/gdrive/gdrive.sh list

# Find all documents with "usuals" in the name or content
~/Documents/Claude/picnic-analyst-assistant/skills/gdrive/gdrive.sh search "usuals"

# List recently shared files
~/Documents/Claude/picnic-analyst-assistant/skills/gdrive/gdrive.sh shared

# Read a specific document
~/Documents/Claude/picnic-analyst-assistant/skills/gdrive/gdrive.sh read 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms

# Show folder tree 2 levels deep
~/Documents/Claude/picnic-analyst-assistant/skills/gdrive/gdrive.sh tree --depth 2 --ids
```

## Notes

- Covers My Drive + files shared with Maarten — does NOT browse Shared Drives
- Google Sheets are exported as CSV; Docs and Slides as plain text
- File IDs appear in the URL: `docs.google.com/document/d/<FILE_ID>/`
- Credentials cached at `~/.cache/picnic-google-sheets/authorized_user.json` (shared with gsheet)
