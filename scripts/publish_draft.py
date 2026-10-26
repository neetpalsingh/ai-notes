#!/usr/bin/env python3
"""Publish the oldest note waiting in drafts/.

Moves drafts/<name>.md to notes/<category>/<today>-<slug>.md, stamps today's
date into its front matter, and rebuilds the README index. Used by the weekend
publishing workflow; also runnable by hand. Exits cleanly when the queue is empty,
so nothing is ever committed without a real note behind it.
"""
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "drafts"

sys.path.insert(0, str(ROOT / "scripts"))
from build_index import front_matter  # noqa: E402
from new_note import slugify  # noqa: E402


def main() -> int:
    queue = sorted(p for p in DRAFTS.glob("*.md") if not p.name.startswith("_"))
    if not queue:
        print("Draft queue is empty: nothing to publish.")
        return 0

    draft = queue[0]
    text = draft.read_text(encoding="utf-8")
    meta = front_matter(text)
    if not meta.get("title"):
        print(f"{draft.name} has no title in its front matter; skipping it.", file=sys.stderr)
        return 1

    today = dt.date.today().isoformat()
    if re.search(r"^date:.*$", text, re.M):
        text = re.sub(r"^date:.*$", f"date: {today}", text, count=1, flags=re.M)
    else:
        text = text.replace("---\n", f"---\ndate: {today}\n", 1)

    category = slugify(meta.get("category") or "llm")
    target = ROOT / "notes" / category / f"{today}-{slugify(meta['title'])}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    draft.unlink()

    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_index.py")], check=True)
    print(f"Published {target.relative_to(ROOT)} ({len(queue) - 1} draft(s) left)")
    # Expose the title to the workflow for the commit message
    (ROOT / ".published_title").write_text(meta["title"], encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
