"""Check generated metadata and links, or enumerate built briefing pages."""
import argparse
import json
from pathlib import Path

from core import HERE, download, validate_post

parser = argparse.ArgumentParser()
parser.add_argument("--posts", type=Path, default=Path("_posts"))
parser.add_argument("--links", action="store_true")
parser.add_argument("--pages", action="store_true")
args = parser.parse_args()
root = HERE.parents[1]
urls = set()
for path in sorted(args.posts.glob("*.md")):
    meta = validate_post(path, root)
    if meta.get("briefing_type"):
        urls.update(meta["briefing_sources"])
        if args.pages:
            print("/posts/" + path.stem[11:] + "/")
if args.links:
    for url in sorted(urls):
        download(url)
        print("Source link OK: " + url)
