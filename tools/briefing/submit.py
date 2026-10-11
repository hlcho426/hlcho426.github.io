"""Fixed-repository briefing submission; no local Git writes or model API calls.

Approve only this script's command for unattended submission. Inputs are confined
to today's output/briefing/{kind}/{date}/drafts.json and source caches. It can
create a briefing branch, one commit of generated posts, and one draft PR.
It never merges, deletes refs, force-pushes, or writes to main.
"""
from __future__ import annotations
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / '.deps'))
from core import KST, frontmatter, normalize_url, event_key, render, validate_article, validate_post

REPO = 'hlcho426/hlcho426.github.io'
API = 'repos/' + REPO


def gh_json(*args, data=None):
    argv = ['gh', *args]
    if data is not None:
        argv += ['--input', '-']
    result = subprocess.run(argv, input=None if data is None else json.dumps(data),
                            capture_output=True, text=True, encoding='utf-8', check=True)
    return json.loads(result.stdout or '{}')


def api(path, data=None):
    # All endpoint suffixes are constructed here, never taken from input URLs.
    return gh_json('api', API + '/' + path, '--method', 'GET' if data is None else 'POST', data=data)


def content(path, sha):
    data = api('contents/' + path + '?ref=' + sha)
    return base64.b64decode(data['content']).decode('utf-8')


def sync_readme():
    """Refresh only clean README from reviewed main; no remote or Git writes."""
    main = api('git/ref/heads/main')['object']['sha']
    remote = content('README.md', main).replace('\r\n', '\n')
    path = ROOT / 'README.md'
    local = path.read_text(encoding='utf-8').replace('\r\n', '\n')
    if local == remote:
        return {'status': 'readme_current', 'main': main}
    tracked = subprocess.run(['git', 'show', 'HEAD:README.md'], cwd=ROOT,
                             capture_output=True, text=True, encoding='utf-8', check=True).stdout
    if local != tracked.replace('\r\n', '\n'):
        raise ValueError('README has local edits; preserve them and request synchronization')
    if api('git/ref/heads/main')['object']['sha'] != main:
        raise ValueError('main changed during README synchronization; retry')
    if path.read_text(encoding='utf-8').replace('\r\n', '\n') != local:
        raise ValueError('README changed locally during synchronization; preserve it')
    path.write_text(remote, encoding='utf-8')
    return {'status': 'readme_synchronized', 'main': main}


def load_candidates(kind, stamp, directory):
    config = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
    batch = json.loads((directory / 'drafts.json').read_text(encoding='utf-8'))
    if not isinstance(batch, list) or not 1 <= len(batch) <= config['types'][kind]['max_posts']:
        raise ValueError('Expected 1..configured maximum validated candidates')
    files, urls, events = {}, set(), set()
    for item in batch:
        source_path = (directory / item['source_file']).resolve()
        if not source_path.is_relative_to(directory.resolve()) or source_path.suffix != '.json':
            raise ValueError('Source cache must remain inside this run directory')
        source = json.loads(source_path.read_text(encoding='utf-8'))
        article = item['article']
        validate_article(article, source, kind, stamp.date(), config)
        url, event = normalize_url(source['url']), event_key(article['event_key'])
        if url in urls or event in events:
            raise ValueError('Duplicate candidate source/event')
        urls.add(url)
        events.add(event)
        name = f'{stamp.date()}-{kind}-{article["slug"]}.md'
        text = render(article, source, kind, stamp.date(), config)
        # A manual test before 08:00 must still produce pages in the real build.
        text = re.sub(r'^date: .+$', 'date: ' + stamp.strftime('%Y-%m-%d %H:%M:%S +0900'),
                      text, count=1, flags=re.M)
        if 'example.org' in text or 'synthetic-pipeline-test' in text:
            raise ValueError('Synthetic fixture must never be submitted')
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            check_path = Path(temp) / name
            check_path.write_text(text, encoding='utf-8')
            validate_post(check_path, ROOT)
        files['_posts/' + name] = text
    return files, urls, events


def check_remote(kind, day, files, candidate_urls, candidate_events):
    prefix = 'codex/briefing-' + kind + '-'
    branch = prefix + day
    opened = gh_json('pr', 'list', '--repo', REPO, '--state', 'open', '--limit', '1000',
                     '--json', 'number,headRefName,url')
    pending = [p for p in opened if p['headRefName'].startswith(prefix)]
    same = gh_json('pr', 'list', '--repo', REPO, '--state', 'all', '--head', branch,
                  '--json', 'number,url')
    if pending or same:
        return {'status': 'skipped_existing_pr', 'pr': (pending or same)[0]['url']}
    refs = api('git/matching-refs/heads/' + branch)
    if any(r['ref'] == 'refs/heads/' + branch for r in refs):
        raise ValueError('Branch already exists without PR; inspect it, never overwrite')
    main = api('git/ref/heads/main')['object']['sha']
    commit = api('git/commits/' + main)
    tree = api('git/trees/' + commit['tree']['sha'] + '?recursive=1')
    if tree.get('truncated'):
        raise ValueError('Remote tree truncated; cannot establish duplicate safety')
    paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob'
             and x['path'].startswith('_posts/') and x['path'].endswith('.md')]
    if set(files) & set(paths):
        raise ValueError('Post filename exists on main')
    # Refuse to operate with stale local editorial or validator rules.
    for path in ['README.md', 'tools/briefing/core.py', 'tools/briefing/config.json',
                 'tools/briefing/editorial.md']:
        remote = content(path, main).replace('\r\n', '\n')
        local = (ROOT / path).read_text(encoding='utf-8').replace('\r\n', '\n')
        if remote != local:
            raise ValueError('Local rules differ from main: ' + path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        texts = list(pool.map(lambda p: content(p, main), paths))
    for pr in opened:
        result = subprocess.run(['gh', 'pr', 'diff', str(pr['number']), '--repo', REPO],
                                capture_output=True, text=True, encoding='utf-8', check=True)
        texts.append(result.stdout)
    for text in texts:
        for raw_url in re.findall(r'https?://[^\s<>\)\]\"\x27]+', text):
            try:
                duplicate = normalize_url(raw_url) in candidate_urls
            except ValueError:
                continue
            if duplicate:
                raise ValueError('Source already covered on main or an open PR')
        for key in re.findall(r'^\+?briefing_event:\s*(.+)$', text, re.M):
            if event_key(key.strip('\x27\"')) in candidate_events:
                raise ValueError('Event already covered on main or an open PR')
    return {'status': 'validated', 'main': main, 'tree': commit['tree']['sha'], 'branch': branch}


def submit(kind, check_only=False):
    stamp = datetime.now(KST)
    directory = ROOT / 'output' / 'briefing' / kind / stamp.date().isoformat()
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / 'submit.lock'
    # Same-run parallel submissions are refused. A crash leaves a reviewable lock.
    with lock.open('x', encoding='utf-8') as handle:
        handle.write(stamp.isoformat())
    try:
        files, urls, events = load_candidates(kind, stamp, directory)
        state = check_remote(kind, stamp.date().isoformat(), files, urls, events)
        if state['status'] != 'validated' or check_only:
            return state
        config = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
        # Recheck the base immediately before mutations. No retries overwrite refs.
        if api('git/ref/heads/main')['object']['sha'] != state['main']:
            raise ValueError('main changed during validation; rerun preflight')
        tree = api('git/trees', {'base_tree': state['tree'], 'tree': [
            {'path': path, 'mode': '100644', 'type': 'blob', 'content': text}
            for path, text in files.items()]})
        commit = api('git/commits', {'message': f'Add {kind} briefing for {stamp.date()}',
                                    'tree': tree['sha'], 'parents': [state['main']]})
        api('git/refs', {'ref': 'refs/heads/' + state['branch'], 'sha': commit['sha']})
        body = ('공개 원문 기반 독립 게시물 ' + str(len(files)) + '편입니다.\n\n'
                '스키마·근거·날짜·메타데이터와 최신 main·열린 PR의 중복을 검사했습니다. '
                '원문 링크와 확인 범위는 각 글에 있습니다. '
                'Jekyll·내부 링크·미리보기 검사는 GitHub Actions 결과 확인 전입니다.\n\n'
                'main 직접 쓰기 및 자동 병합은 하지 않습니다.')
        pr = api('pulls', {'title': f'{config["types"][kind]["category"]} | {stamp.date()} ({len(files)}편)',
                           'body': body, 'head': state['branch'], 'base': 'main', 'draft': True})
        return {'status': 'draft_pr_created', 'pr': pr['html_url'], 'head': commit['sha'],
                'posts': list(files), 'ci': 'pending'}
    finally:
        lock.unlink()


def finish(kind):
    branch = f'codex/briefing-{kind}-{datetime.now(KST).date()}'
    prs = gh_json('pr', 'list', '--repo', REPO, '--state', 'open', '--head', branch,
                  '--json', 'number,url')
    if len(prs) != 1:
        raise ValueError('Expected exactly one open PR for today and this type')
    pr = gh_json('pr', 'view', str(prs[0]['number']), '--repo', REPO,
                 '--json', 'headRefName,headRefOid,isDraft,statusCheckRollup,url')
    if pr['headRefName'] != branch:
        raise ValueError('Unexpected PR branch')
    checks = {c.get('name'): c for c in pr.get('statusCheckRollup', [])}
    if any(checks.get(name, {}).get('conclusion') != 'SUCCESS' for name in ('build', 'tests')):
        return {'status': 'ci_pending_or_failed', 'pr': pr['url']}
    comments = api('issues/' + str(prs[0]['number']) + '/comments?per_page=100')
    if not any(c.get('user', {}).get('login') == 'github-actions[bot]'
               and '<!-- jekyll-pr-preview -->' in c.get('body', '')
               and pr['headRefOid'] in c['body'] for c in comments):
        return {'status': 'preview_pending', 'pr': pr['url']}
    if pr['isDraft']:
        subprocess.run(['gh', 'pr', 'ready', str(prs[0]['number']), '--repo', REPO], check=True,
                       capture_output=True, text=True, encoding='utf-8')
    return {'status': 'ready_for_review', 'pr': pr['url'], 'head': pr['headRefOid'], 'ci': 'passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=('game', 'ai', 'research'), required=True)
    parser.add_argument('--check-only', action='store_true', help='Read-only remote preflight; no GitHub writes')
    parser.add_argument('--finish', action='store_true', help='Mark only today\'s type PR ready after CI and preview verification')
    parser.add_argument('--sync-readme', action='store_true', help='Refresh only an unedited local README from main; no GitHub writes')
    args = parser.parse_args()
    try:
        if sum((args.finish, args.check_only, args.sync_readme)) > 1:
            raise ValueError('Choose only one operation')
        report = sync_readme() if args.sync_readme else (finish(args.kind) if args.finish else submit(args.kind, args.check_only))
    except Exception as error:
        report = {'status': 'failed', 'error': str(error)[:500], 'ci': 'not verified'}
    target = ROOT / 'output' / 'briefing' / args.kind / datetime.now(KST).date().isoformat() / 'submit-report.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    sys.exit(1 if report['status'] == 'failed' else 0)
