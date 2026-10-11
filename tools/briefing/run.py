"""Stage Codex-authored drafts or fixtures. No model API client."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from core import HERE, KST, event_key, known_posts, normalize_url, render, validate_article, validate_post


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True, encoding="utf-8")


def preflight(repo, kind, today):
    """Optional read-only CLI check; Codex can use connected GitHub tools instead."""
    prs = json.loads(gh("pr", "list", "--repo", repo, "--state", "open", "--limit", "1000",
                        "--json", "number,headRefName,url"))
    prefix = "codex/briefing-" + kind + "-"
    pending = [p for p in prs if p["headRefName"].startswith(prefix)]
    if pending:
        return pending[0]["url"], set(), set()
    same_day = json.loads(gh("pr", "list", "--repo", repo, "--state", "all", "--head", prefix + today.isoformat(),
                             "--json", "url"))
    if same_day:
        return same_day[0]["url"], set(), set()
    urls, events = set(), set()
    for pr in prs:
        patch = gh("pr", "diff", str(pr["number"]), "--repo", repo)
        for url in re.findall(r"https?://[^\s<>\)\]\"']+", patch):
            try:
                urls.add(normalize_url(url))
            except ValueError:
                pass
        for key in re.findall(r"^\+briefing_event: (.+)$", patch, re.M):
            events.add(event_key(key.strip("'\"")))
    return None, urls, events


def generate(kind, root, output, today, mode="fixture", repo=None, input_file=None):
    config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    report = {"kind": kind, "date": today.isoformat(), "mode": mode, "posts": [], "skipped": [],
              "model_api_calls": 0, "api_cost_usd": 0}
    output.mkdir(parents=True, exist_ok=True)
    try:
        if mode not in ("fixture", "codex"):
            raise ValueError("Only fixture and codex modes are supported; model API execution was removed")
        known_urls, known_events = known_posts(root)
        if mode == "codex":
            if not input_file:
                raise ValueError("Codex mode requires --input; it never calls a model API")
            if repo:
                pending, pr_urls, pr_events = preflight(repo, kind, today)
                if pending:
                    report["pending_pr"] = pending
                    return report
                known_urls |= pr_urls
                known_events |= pr_events
            batch = json.loads(input_file.read_text(encoding="utf-8"))
            if not isinstance(batch, list) or len(batch) > config["max_candidates"]:
                raise ValueError("Draft input must be a list of at most 8 candidates")
        else:
            from fixtures import fixture
            batch = [fixture(kind, today)]
        for candidate in batch:
            if len(report["posts"]) >= config["types"][kind]["max_posts"]:
                break
            try:
                if mode == "codex":
                    source_path = (output / candidate["source_file"]).resolve()
                    if not source_path.is_relative_to(output.resolve()):
                        raise ValueError("Source cache must stay inside this run's output directory")
                    source = json.loads(source_path.read_text(encoding="utf-8"))
                    article = candidate["article"]
                else:
                    source, article = candidate["source"].copy(), candidate["article"].copy()
                url = normalize_url(source["url"])
                if url in known_urls or event_key(article["event_key"]) in known_events:
                    raise ValueError("Duplicate source or event")
                validate_article(article, source, kind, today, config)
                name = f"{today}-{kind}-{article['slug']}.md"
                path = output / "_posts" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists() or (root / "_posts" / name).exists():
                    raise ValueError("Post file already exists")
                path.write_text(render(article, source, kind, today, config), encoding="utf-8")
                validate_post(path, root)
                report["posts"].append({"file": name, "source": source["url"],
                                        "event_key": article["event_key"], "source_sha256": source.get("sha256"),
                                        "source_date": article["source_date"],
                                        "evidence_checked": len(article["paragraphs"])})
                known_urls.add(url)
                known_events.add(event_key(article["event_key"]))
            except Exception as error:
                report["skipped"].append({"reason": type(error).__name__ + ": " + str(error)[:200]})
        if mode == "codex" and batch and not report["posts"]:
            raise ValueError("All candidates rejected; inspect report.json, no PR was created")
        return report
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)[:200]
        raise
    finally:
        (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("game", "ai", "research"), required=True)
    parser.add_argument("--mode", choices=("fixture", "codex"), default="fixture")
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--output", type=Path, default=Path("output/briefing"))
    parser.add_argument("--date", type=date.fromisoformat, default=datetime.now(KST).date())
    parser.add_argument("--repo", help="Optional CLI PR check; connected GitHub preflight remains mandatory")
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    try:
        result = generate(args.kind, args.root, args.output, args.date, args.mode, args.repo, args.input)
        print(json.dumps(result, ensure_ascii=True))
    except Exception as error:
        print(str(error)[:200], file=sys.stderr)
        sys.exit(1)
