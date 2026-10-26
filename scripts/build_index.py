#!/usr/bin/env python3
"""Rebuild the index section of README.md from the notes' front matter.

Everything between the INDEX markers in README.md is regenerated; the rest of
the README is left untouched. Run it locally or let the GitHub Action do it.
"""
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START, END = "<!-- INDEX:START -->", "<!-- INDEX:END -->"
TYPE_LABEL = {"til": "💡 TIL", "paper": "📄 Paper", "snippet": "🧩 Snippet"}


def front_matter(text: str) -> dict:
    """Parse the simple `key: value` front matter used by the templates."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    meta = {}
    if not match:
        return meta
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        meta[key.strip()] = value
    return meta


def load_notes() -> list[dict]:
    notes = []
    for path in sorted((ROOT / "notes").rglob("*.md")):
        meta = front_matter(path.read_text(encoding="utf-8"))
        if not meta.get("title"):
            continue
        meta["path"] = path.relative_to(ROOT).as_posix()
        meta.setdefault("category", path.parent.name)
        meta.setdefault("type", "til")
        meta.setdefault("tags", [])
        notes.append(meta)
    return sorted(notes, key=lambda n: (n.get("date", ""), n["title"]), reverse=True)


def render(notes: list[dict]) -> str:
    if not notes:
        return "_No notes yet. Create one with `python scripts/new_note.py til \"My first note\"`._"

    by_cat = defaultdict(list)
    for n in notes:
        by_cat[n["category"]].append(n)
    types = Counter(n["type"] for n in notes)
    weeks = {n.get("date", "")[:7] for n in notes if n.get("date")}

    def n_of(count: int, word: str) -> str:
        return f"{count} {word}{'' if count == 1 else 's'}"

    out = [
        f"**{n_of(len(notes), 'note')}** · {n_of(types.get('til', 0), 'TIL')} · {n_of(types.get('paper', 0), 'paper')} · "
        f"{n_of(types.get('snippet', 0), 'snippet')} · {n_of(len(by_cat), 'topic')} · active in {n_of(len(weeks), 'month')}",
        "",
        "### 🆕 Latest",
        "",
        "| Date | Note | Type | Topic |",
        "|---|---|---|---|",
    ]
    for n in notes[:10]:
        out.append(f"| {n.get('date', '')} | [{n['title']}]({n['path']}) | {TYPE_LABEL.get(n['type'], n['type'])} | `{n['category']}` |")

    out += ["", "### 🗂️ By topic", ""]
    for cat in sorted(by_cat):
        items = by_cat[cat]
        out.append(f"<details><summary><b>{cat}</b> ({len(items)})</summary>\n")
        for n in items:
            tags = " ".join(f"`{t}`" for t in n["tags"])
            out.append(f"- {n.get('date', '')} · [{n['title']}]({n['path']}) {tags}".rstrip())
        out.append("\n</details>")

    tag_counts = Counter(t for n in notes for t in n["tags"])
    if tag_counts:
        out += ["", "### 🏷️ Tags", "", " ".join(f"`{t}`×{c}" for t, c in tag_counts.most_common(30))]
    return "\n".join(out)


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise SystemExit(f"README.md must contain {START} and {END}")
    head, rest = readme.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{render(load_notes())}\n{END}{tail}"
    if new != readme:
        README.write_text(new, encoding="utf-8")
        print("README index updated")
    else:
        print("README index already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
