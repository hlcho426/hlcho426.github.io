"""Collect public source text or export the Codex draft schema; no paid API."""
import argparse
import json
from pathlib import Path
from core import ARTICLE_SCHEMA, HERE, fetch_source

parser = argparse.ArgumentParser()
parser.add_argument("--url")
parser.add_argument("--kind", choices=("game", "ai", "research"), default="game")
parser.add_argument("--output", type=Path)
parser.add_argument("--schema", action="store_true")
args = parser.parse_args()
if args.schema:
    print(json.dumps(ARTICLE_SCHEMA, ensure_ascii=False, indent=2))
else:
    if not args.url or not args.output:
        parser.error("--url and --output are required for collection")
    config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    limit = config["max_research_chars"] if args.kind == "research" else config["max_source_chars"]
    source = fetch_source(args.url, limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"title": source["title"], "chars": len(source["text"]),
                      "truncated": source["truncated"]}, ensure_ascii=True))
