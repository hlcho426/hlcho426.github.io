"""Publish only validated, live-generated files to a review branch and PR."""
import argparse
import json
import os
import subprocess
from datetime import date
from pathlib import Path

from core import HERE, normalize_url, validate_post
from run import gh, preflight


def command(*args):
    subprocess.run(args, check=True)


def publish(output, repo):
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    if report["mode"] != "live":
        raise ValueError("Fixture data cannot be published")
    if not report["posts"]:
        print("No eligible articles; no PR")
        return
    root = HERE.parents[1]
    pending, urls, events = preflight(repo, report["kind"], date.fromisoformat(report["date"]))
    if pending:
        print("Existing PR; publication skipped: " + pending)
        return
    files = []
    for post in report["posts"]:
        path = root / "_posts" / post["file"]
        if path.parent != root / "_posts":
            raise ValueError("Invalid publish path")
        meta = validate_post(path, root)
        from core import event_key
        if normalize_url(post["source"]) in urls or event_key(meta["briefing_event"]) in events:
            raise ValueError("Source/event appeared in another PR since generation; rerun")
        files.append(str(path.relative_to(root)))
    branch = f"codex/briefing-{report['kind']}-{report['date']}"
    # Never overwrite a leftover branch after a partially failed run.
    existing = gh("api", f"repos/{repo}/git/matching-refs/heads/{branch}")
    if json.loads(existing):
        raise ValueError("Remote branch exists without PR; inspect and recover manually")
    command("git", "switch", "-c", branch)
    command("git", "config", "user.name", "github-actions[bot]")
    command("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    command("git", "add", "--", *files)
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
    if set(staged) != set(files):
        raise ValueError("Unexpected staged files; refusing publication")
    command("git", "commit", "-m", f"Add {report['kind']} briefing for {report['date']}")
    command("git", "push", "origin", f"HEAD:refs/heads/{branch}")
    config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    title = f"{config['types'][report['kind']]['prefix']} | {report['date']} ({len(files)}편)"
    body = "공개 원문을 수집해 작성한 독립 게시물입니다. 사용자 검토·병합 후 공개됩니다.\n\n"
    body += "\n".join(f"- `{p['file']}` — [원문](<{p['source']}>) ({p['source_date']})" for p in report["posts"])
    run_url = f"https://github.com/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    body += f"\n\n검증: 원문 근거 구절·날짜·중복·메타데이터·Jekyll 빌드·내부 및 출처 링크 검사.\n[생성 실행 및 사용량 기록]({run_url})\n\n"
    body += "대표 이미지는 사용 권한 검증 전이므로 생략했습니다. 필자의 분석과 적용 제안은 직접 실험한 결과가 아닙니다. "
    body += "근거 구절 포함 검사는 사실 전체의 진실성을 보장하지 않습니다. PR 본문과 출처를 검토해 주세요. "
    body += "기존 Jekyll PR Preview가 미리보기 댓글을 제공합니다. GITHUB_TOKEN으로 생성했다면 Approve workflows to run이 필요할 수 있습니다."
    body_file = output / "pr-body.md"
    body_file.write_text(body, encoding="utf-8")
    url = gh("pr", "create", "--repo", repo, "--base", "main", "--head", branch,
             "--title", title, "--body-file", str(body_file)).strip()
    (output / "pr-url.txt").write_text(url + "\n", encoding="utf-8")
    print(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    publish(args.output, args.repo)
