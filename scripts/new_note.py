#!/usr/bin/env python3
"""Create a new note from a template.

Usage:
    python scripts/new_note.py til "Semantic chunking beats fixed-size" --category rag --tags chunking,embeddings
    python scripts/new_note.py paper "LoRA" --category fine-tuning
    python scripts/new_note.py snippet "Retry with backoff" --category backend --open
    python scripts/new_note.py til "MCP auth" --category mcp --draft   # queue for the weekend
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = ("til", "paper", "snippet")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60].rstrip("-") or "note"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new learning-log note.")
    parser.add_argument("type", choices=TYPES, help="kind of note")
    parser.add_argument("title", help="note title")
    parser.add_argument("--category", default="llm", help="folder under notes/ (e.g. rag, agents, mcp)")
    parser.add_argument("--tags", default="", help="comma-separated tags")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="YYYY-MM-DD (default: today)")
    parser.add_argument("--open", action="store_true", help="open the note in $EDITOR / default app")
    parser.add_argument("--draft", action="store_true", help="queue in drafts/; the weekend workflow publishes and dates it")
    args = parser.parse_args()

    category = slugify(args.category)
    tags = ", ".join(t.strip() for t in args.tags.split(",") if t.strip())
    template = (ROOT / "templates" / f"{args.type}.md").read_text(encoding="utf-8")
    body = (
        template.replace("{{title}}", args.title)
        .replace("{{date}}", args.date)
        .replace("{{category}}", category)
        .replace("{{tags}}", tags)
    )

    if args.draft:
        # Queue order is filename order, so prefix with the time it was written
        folder = ROOT / "drafts"
        path = folder / f"{dt.datetime.now():%Y%m%d-%H%M%S}-{slugify(args.title)}.md"
    else:
        folder = ROOT / "notes" / category
        path = folder / f"{args.date}-{slugify(args.title)}.md"
    folder.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"Already exists: {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    path.write_text(body, encoding="utf-8")
    print(f"Created {path.relative_to(ROOT)}")

    if args.open:
        editor = os.environ.get("EDITOR")
        if editor:
            subprocess.run([editor, str(path)])
        elif sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(path)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
