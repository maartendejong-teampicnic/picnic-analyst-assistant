#!/usr/bin/env python3
"""
Google Drive CLI tool for Claude Code.

Reuses Picnic's shared Google OAuth credentials (same token as gsheet tool).
Covers: My Drive + files/folders shared with me.

Usage:
  gdrive_tool.py list [--folder <id>] [--type doc|sheet|slide|folder] [--limit N]
  gdrive_tool.py search <query> [--type doc|sheet|slide] [--limit N]
  gdrive_tool.py read <file_id>
  gdrive_tool.py tree [--folder <id>] [--depth N]
  gdrive_tool.py shared [--type doc|sheet|slide] [--limit N]
"""

import argparse
import json
import sys
from pathlib import Path

# Reuse existing Picnic Google OAuth token (already has drive scope)
AUTHORIZED_USER_PATH = Path.home() / ".cache" / "picnic-google-sheets" / "authorized_user.json"
CREDENTIALS_PATH = Path.home() / ".cache" / "picnic-google-sheets" / "credentials.json"

# Picnic's shared OAuth client (same as gsheet tool)
GOOGLE_OAUTH_CLIENT = {
    "installed": {
        "client_id": "874265227487-cllfu4fjm5omd6d04d55gn52l8ird1ie.apps.googleusercontent.com",
        "project_id": "python-platform",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}

# Use the same scopes as the gsheet tool so the shared token stays compatible
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MIME_FILTERS = {
    "doc": "mimeType = 'application/vnd.google-apps.document'",
    "sheet": "mimeType = 'application/vnd.google-apps.spreadsheet'",
    "slide": "mimeType = 'application/vnd.google-apps.presentation'",
    "folder": "mimeType = 'application/vnd.google-apps.folder'",
}

MIME_LABELS = {
    "application/vnd.google-apps.document": "Doc",
    "application/vnd.google-apps.spreadsheet": "Sheet",
    "application/vnd.google-apps.presentation": "Slide",
    "application/vnd.google-apps.folder": "Folder",
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PPT",
}

EXPORT_MIME = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


def get_credentials():
    """Load Google credentials from the shared Picnic OAuth token cache."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None

    if AUTHORIZED_USER_PATH.exists():
        try:
            data = json.loads(AUTHORIZED_USER_PATH.read_text())
            # Handle both gspread format and standard google-auth format
            creds = Credentials(
                token=data.get("token"),
                refresh_token=data.get("refresh_token"),
                token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=data.get("client_id"),
                client_secret=data.get("client_secret"),
                scopes=data.get("scopes"),
            )
        except Exception as e:
            print(f"Warning: could not load existing credentials: {e}", file=sys.stderr)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            # Always try refresh before full OAuth (token may be None but refresh_token valid)
            try:
                creds.refresh(Request())
                AUTHORIZED_USER_PATH.write_text(creds.to_json())
            except Exception:
                creds = None

        if not creds or not creds.valid:
            # Full OAuth flow (will open browser)
            CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
            CREDENTIALS_PATH.write_text(json.dumps(GOOGLE_OAUTH_CLIENT))
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
            AUTHORIZED_USER_PATH.write_text(creds.to_json())

    return creds


def get_service():
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=get_credentials())


def fmt_size(size_bytes):
    if size_bytes is None:
        return ""
    n = int(size_bytes)
    if n < 1024:
        return f"{n}B"
    elif n < 1024 * 1024:
        return f"{n // 1024}KB"
    else:
        return f"{n // (1024 * 1024)}MB"


def fmt_label(mime):
    return MIME_LABELS.get(mime, mime.split(".")[-1][:6])


def print_file_row(f):
    label = fmt_label(f["mimeType"])
    size = fmt_size(f.get("size"))
    modified = f.get("modifiedTime", "")[:10]
    name = f["name"][:60]
    print(f"[{label:6}] {name:<62} {size:>6}  {modified}  {f['id']}")


def cmd_list(args):
    """List files in a folder (default: My Drive root)."""
    service = get_service()

    folder_id = args.folder or "root"
    query = f"'{folder_id}' in parents and trashed = false"
    if args.type:
        query += f" and {MIME_FILTERS[args.type]}"

    results = service.files().list(
        q=query,
        pageSize=args.limit,
        fields="files(id, name, mimeType, modifiedTime, size)",
        orderBy="folder,name",
    ).execute()

    files = results.get("files", [])
    if not files:
        print("No files found.")
        return

    print(f"Listing folder: {folder_id}  ({len(files)} items)\n")
    for f in files:
        print_file_row(f)


def cmd_shared(args):
    """List files shared with me."""
    service = get_service()

    query = "sharedWithMe = true and trashed = false"
    if args.type:
        query += f" and {MIME_FILTERS[args.type]}"

    results = service.files().list(
        q=query,
        pageSize=args.limit,
        fields="files(id, name, mimeType, modifiedTime, size, sharingUser)",
        orderBy="modifiedTime desc",
    ).execute()

    files = results.get("files", [])
    if not files:
        print("No shared files found.")
        return

    print(f"Files shared with me ({len(files)} items)\n")
    for f in files:
        sharer = f.get("sharingUser", {}).get("displayName", "")
        label = fmt_label(f["mimeType"])
        modified = f.get("modifiedTime", "")[:10]
        name = f["name"][:55]
        print(f"[{label:6}] {name:<57} {modified}  {sharer:<25}  {f['id']}")


def cmd_search(args):
    """Full-text search across My Drive and files shared with me."""
    service = get_service()

    # Escape single quotes in query
    q = args.query.replace("'", "\\'")
    query = f"fullText contains '{q}' and trashed = false"
    if args.type:
        query += f" and {MIME_FILTERS[args.type]}"

    results = service.files().list(
        q=query,
        pageSize=args.limit,
        fields="files(id, name, mimeType, modifiedTime, parents)",
        orderBy="modifiedTime desc",
    ).execute()

    files = results.get("files", [])
    if not files:
        print(f"No results for: {args.query}")
        return

    print(f"Search results for '{args.query}'  ({len(files)} hits)\n")
    for f in files:
        label = fmt_label(f["mimeType"])
        modified = f.get("modifiedTime", "")[:10]
        name = f["name"][:60]
        print(f"[{label:6}] {name:<62} {modified}  {f['id']}")


def cmd_read(args):
    """Export a Google Doc/Sheet/Slide as plain text."""
    service = get_service()

    meta = service.files().get(
        fileId=args.file_id,
        fields="id, name, mimeType, modifiedTime, webViewLink",
    ).execute()

    mime = meta["mimeType"]
    print(f"# {meta['name']}")
    print(f"# Type: {fmt_label(mime)}  |  Modified: {meta.get('modifiedTime', '')[:10]}")
    if meta.get("webViewLink"):
        print(f"# URL: {meta['webViewLink']}")
    print()

    if mime in EXPORT_MIME:
        content = service.files().export(
            fileId=args.file_id,
            mimeType=EXPORT_MIME[mime],
        ).execute()
        if isinstance(content, bytes):
            print(content.decode("utf-8", errors="replace"))
        else:
            print(content)
    else:
        print(f"Cannot export file type: {mime}")
        print("Supported: Google Docs (text), Google Sheets (CSV), Google Slides (text)")


def cmd_tree(args):
    """Show a folder tree (My Drive root by default)."""
    service = get_service()

    def walk(folder_id, indent, remaining_depth):
        if remaining_depth <= 0:
            return
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, mimeType)",
            orderBy="folder,name",
        ).execute()
        for f in results.get("files", []):
            is_folder = f["mimeType"] == "application/vnd.google-apps.folder"
            icon = "D" if is_folder else fmt_label(f["mimeType"])[0]
            prefix = "  " * indent
            suffix = f"  [{f['id']}]" if args.ids else ""
            print(f"{prefix}{'[' + icon + '] '}{f['name']}{suffix}")
            if is_folder:
                walk(f["id"], indent + 1, remaining_depth - 1)

    folder_id = args.folder or "root"
    depth = args.depth or 3
    print(f"Drive tree  (root: {folder_id}, depth: {depth})\n")
    walk(folder_id, indent=0, remaining_depth=depth)


def main():
    parser = argparse.ArgumentParser(description="Google Drive CLI tool for Claude Code")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List files in a folder")
    p.add_argument("--folder", help="Folder ID (default: My Drive root)")
    p.add_argument("--type", choices=["doc", "sheet", "slide", "folder"])
    p.add_argument("--limit", type=int, default=50)

    # shared
    p = sub.add_parser("shared", help="List files shared with me")
    p.add_argument("--type", choices=["doc", "sheet", "slide", "folder"])
    p.add_argument("--limit", type=int, default=30)

    # search
    p = sub.add_parser("search", help="Search Drive by text content or name")
    p.add_argument("query")
    p.add_argument("--type", choices=["doc", "sheet", "slide", "folder"])
    p.add_argument("--limit", type=int, default=20)

    # read
    p = sub.add_parser("read", help="Export a Google Doc/Sheet/Slide as text")
    p.add_argument("file_id")

    # tree
    p = sub.add_parser("tree", help="Show a folder tree")
    p.add_argument("--folder", help="Folder ID (default: My Drive root)")
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--ids", action="store_true", help="Show file IDs")

    args = parser.parse_args()
    dispatch = {
        "list": cmd_list,
        "shared": cmd_shared,
        "search": cmd_search,
        "read": cmd_read,
        "tree": cmd_tree,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
