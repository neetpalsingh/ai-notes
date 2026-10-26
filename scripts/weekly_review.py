#!/usr/bin/env python3
"""Weekly review: document the week's commits with GitHub Models, or plan improvements.

Runs in GitHub Actions every Sunday night (see .github/workflows/weekly-review.yml).

* Collects the commits you authored this week (Monday to today, IST) across your
  repositories, excluding this notes repo, with their changed files and diffs.
* If there were commits: writes notes/weekly/<year>-W<week>.md, an AI-written digest
  that documents the changes, plus exact stats computed here (never by the AI).
* If there were no commits on Saturday or Sunday: writes plans/<year>-W<week>-plan.md,
  an AI improvement plan for next week, and opens it as a GitHub Issue.
  The workflow commits both files as Neetpal Singh.

Writes the paths it created to .weekly_outputs (digest=..., plan=...) for the workflow.

Environment:
  GITHUB_TOKEN      Actions token: calls GitHub Models and opens the issue.
  SEARCH_TOKEN      Optional PAT so private/org repos are included (defaults to GITHUB_TOKEN).
  GITHUB_USER       Your GitHub username.
  GITHUB_REPOSITORY owner/repo of this notes repo (set by Actions).
  MODEL             GitHub Models model id (default openai/gpt-4.1-mini).
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
API = "https://api.github.com"
MODELS_URL = "https://models.github.ai/inference/chat/completions"
MAX_COMMITS = 40
MAX_PATCH_CHARS = 600
MAX_CONTEXT_CHARS = 24000


def http_json(method: str, url: str, token: str, body: dict | None = None) -> dict:
    """Minimal JSON HTTP helper (stdlib only, easy to stub in tests).

    Raises RuntimeError with the status and the start of the body when the reply
    is an HTTP error or isn't JSON, so the log shows what the server actually said.
    """
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    is_models = url.startswith(MODELS_URL.rsplit("/inference", 1)[0])
    req.add_header("Accept", "application/json" if is_models else "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "ai-notes-weekly-review")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=90) as res:
            status, raw = res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"{method} {url} -> HTTP {err.code}: {err.read().decode('utf-8', 'replace')[:400]}") from err
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"{method} {url} -> HTTP {status}, not JSON: {raw[:400]!r}") from err


def week_window(today: dt.date) -> tuple[dt.date, dt.date]:
    monday = today - dt.timedelta(days=today.weekday())
    return monday, today


def fetch_commits(user: str, start: dt.date, end: dt.date, token: str, skip_repo: str) -> list[dict]:
    q = f"author:{user} author-date:{start.isoformat()}..{end.isoformat()}"
    url = f"{API}/search/commits?q={urllib.parse.quote(q)}&sort=author-date&order=asc&per_page=100"
    items = http_json("GET", url, token).get("items", [])
    commits = []
    for item in items:
        repo = item["repository"]["full_name"]
        if repo.lower() == skip_repo.lower():
            continue
        detail = http_json("GET", f"{API}/repos/{repo}/commits/{item['sha']}", token)
        authored = dt.datetime.fromisoformat(item["commit"]["author"]["date"].replace("Z", "+00:00")).astimezone(IST)
        commits.append({
            "repo": repo,
            "sha": item["sha"][:7],
            "url": item.get("html_url", ""),
            "date": authored,
            "message": item["commit"]["message"].strip(),
            "additions": detail.get("stats", {}).get("additions", 0),
            "deletions": detail.get("stats", {}).get("deletions", 0),
            "files": [
                {
                    "name": f["filename"],
                    "status": f.get("status", ""),
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "patch": (f.get("patch") or "")[:MAX_PATCH_CHARS],
                }
                for f in detail.get("files", [])[:15]
            ],
        })
        if len(commits) >= MAX_COMMITS:
            break
    return commits


def stats_table(commits: list[dict]) -> str:
    by_repo = defaultdict(lambda: {"commits": 0, "add": 0, "del": 0, "files": set()})
    for c in commits:
        r = by_repo[c["repo"]]
        r["commits"] += 1
        r["add"] += c["additions"]
        r["del"] += c["deletions"]
        r["files"].update(f["name"] for f in c["files"])
    rows = ["| Repository | Commits | Files | Lines |", "|---|---:|---:|---|"]
    for repo, r in sorted(by_repo.items(), key=lambda kv: -kv[1]["commits"]):
        rows.append(f"| [{repo}](https://github.com/{repo}) | {r['commits']} | {len(r['files'])} | +{r['add']} / −{r['del']} |")
    days = sorted({c["date"].strftime("%a") for c in commits}, key=lambda d: "MonTueWedThuFriSatSun".index(d))
    total_add = sum(c["additions"] for c in commits)
    total_del = sum(c["deletions"] for c in commits)
    head = f"**{len(commits)} commits** across **{len(by_repo)} repositories** · +{total_add} / −{total_del} lines · active on {', '.join(days)}"
    return head + "\n\n" + "\n".join(rows)


def commit_context(commits: list[dict]) -> str:
    parts = []
    for c in commits:
        files = "\n".join(
            f"    {f['status']} {f['name']} (+{f['additions']}/-{f['deletions']})\n" + "\n".join(f"      {l}" for l in f["patch"].splitlines()[:12])
            for f in c["files"]
        )
        parts.append(f"## {c['repo']} @ {c['sha']} · {c['date']:%a %d %b %H:%M}\n{c['message']}\n  files:\n{files}")
    text = "\n\n".join(parts)
    return text[:MAX_CONTEXT_CHARS]


def ask_model(system: str, user: str, token: str, model: str) -> str | None:
    try:
        res = http_json("POST", MODELS_URL, token, {
            "model": model,
            "temperature": 0.3,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        })
        content = ((res.get("choices") or [{}])[0].get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        raise RuntimeError("empty or invalid GitHub Models response payload")
    except Exception as err:  # never let the AI step break the weekly log
        print(f"::warning::GitHub Models call failed, writing the log without AI text: {err}", file=sys.stderr)
        return None


DIGEST_SYSTEM = (
    "You are a senior engineer writing a concise weekly engineering log for an AI engineer's public notes repo. "
    "Use ONLY the commits provided. Never invent features, numbers or repositories. "
    "Write GitHub-flavoured Markdown with these sections: '## Summary' (3-4 sentences), "
    "'## What changed' (one ### subsection per repository, bullet points that document each notable change and why it matters), "
    "'## Concepts & learnings' (technical ideas the changes involve, 3-6 bullets), "
    "'## Next steps' (3-5 concrete follow-ups suggested by the work). Do not add a title."
)

PLAN_SYSTEM = (
    "You are a pragmatic career coach for an AI Engineer (Python, FastAPI, LangGraph, RAG, MCP servers, multi-agent systems, "
    "LLM fine-tuning). He made no commits this weekend. Write an encouraging, specific improvement plan for next week in "
    "GitHub-flavoured Markdown with: '## Where things stand' (2-3 sentences based only on the activity given), "
    "'## Goals for next week' (3 measurable goals), '## Weekend plan' (a Saturday and a Sunday block of 2-3 hours each, "
    "as '- [ ]' checklist items), '## Small project ideas' (3 ideas that build on his recent work and could become public repos), "
    "'## Notes to write' (3 TIL or paper-summary topics). Keep it under 450 words. Do not add a title."
)


def write_digest(commits, start, end, year, week, token, model) -> Path:
    body = ask_model(DIGEST_SYSTEM, f"Week {start} to {end}.\n\n{commit_context(commits)}", token, model)
    if not body:
        body = "## What changed\n\n" + "\n".join(f"- **{c['repo']}**: {c['message'].splitlines()[0]}" for c in commits)
    repos = sorted({c["repo"].split("/")[-1] for c in commits})
    commit_list = "\n".join(
        f"- `{c['date']:%a %d %b}` [{c['repo']}@{c['sha']}]({c['url']}) {c['message'].splitlines()[0]}" for c in commits
    )
    text = (
        f"---\ntitle: Weekly log {year}-W{week:02d} ({start:%d %b} – {end:%d %b})\ndate: {end.isoformat()}\n"
        f"type: weekly\ncategory: weekly\ntags: [{', '.join(repos[:6])}]\n---\n\n"
        f"# Weekly log · {start:%d %b} – {end:%d %b %Y}\n\n{stats_table(commits)}\n\n{body}\n\n"
        f"## Commits\n\n{commit_list}\n\n"
        f"<sub>Generated from the week's commits with GitHub Models ({model}). Stats are computed directly from the GitHub API.</sub>\n"
    )
    path = ROOT / "notes" / "weekly" / f"{year}-W{week:02d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_plan(commits, start, end, year, week, token, model, repo) -> Path:
    activity = commit_context(commits) if commits else "No commits this week."
    notes = sorted((ROOT / "notes").rglob("*.md"))[-8:]
    recent_topics = ", ".join(p.stem[11:].replace("-", " ") for p in notes) or "none yet"
    body = ask_model(PLAN_SYSTEM, f"Week {start} to {end}. Activity:\n{activity}\n\nRecent note topics: {recent_topics}", token, model)
    if not body:
        body = (
            "## Weekend plan\n\n- [ ] Saturday: pick one open idea and ship a first commit\n"
            "- [ ] Sunday: write one TIL about what you built or read\n"
        )
    title = f"Improvement plan · week of {end + dt.timedelta(days=1):%d %b %Y}"
    path = ROOT / "plans" / f"{year}-W{week:02d}-plan.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n\n<sub>Generated with GitHub Models ({model}) because there were no weekend commits.</sub>\n", encoding="utf-8")
    try:
        http_json("POST", f"{API}/repos/{repo}/issues", token, {"title": title, "body": body, "labels": ["improvement-plan"]})
    except Exception as err:
        print(f"::warning::Could not open the issue: {err}", file=sys.stderr)
    return path


def main() -> int:
    token = os.environ["GITHUB_TOKEN"]
    search_token = os.environ.get("SEARCH_TOKEN") or token
    user = os.environ.get("GITHUB_USER", "neetpalsingh")
    repo = os.environ.get("GITHUB_REPOSITORY", f"{user}/ai-notes")
    model = os.environ.get("MODEL", "openai/gpt-4.1-mini")

    today = dt.datetime.now(IST).date()
    start, end = week_window(today)
    year, week, _ = end.isocalendar()
    commits = fetch_commits(user, start, end, search_token, skip_repo=repo)
    weekend = [c for c in commits if c["date"].weekday() >= 5]
    print(f"{len(commits)} commits from {start} to {end}; {len(weekend)} on the weekend")

    outputs = []
    if commits:
        outputs.append(f"digest={write_digest(commits, start, end, year, week, token, model).relative_to(ROOT)}")
    if not weekend:
        outputs.append(f"plan={write_plan(commits, start, end, year, week, token, model, repo).relative_to(ROOT)}")
    (ROOT / ".weekly_outputs").write_text("\n".join(outputs) + "\n", encoding="utf-8")
    print("\n".join(outputs) or "Nothing to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
