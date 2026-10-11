"""Deterministic validation, safe source fetching and Jekyll rendering."""
from __future__ import annotations

import hashlib
import io
import ipaddress
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import jsonschema
import yaml

KST = timezone(timedelta(hours=9))
HERE = Path(__file__).resolve().parent
SECTIONS = ("무슨 일이 있었나", "왜 중요한가", "개발에 적용할 점", "원문과 확인 자료")


def object_schema(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


STRING = {"type": "string"}
PARAGRAPH = object_schema({"heading": STRING, "text": STRING, "evidence": STRING})
ARTICLE_SCHEMA = object_schema({
    "publishable": {"type": "boolean"}, "reason": STRING,
    "title": STRING, "slug": STRING, "event_key": STRING,
    "lead": STRING, "paragraphs": {"type": "array", "items": PARAGRAPH},
    "importance": STRING, "applications": {"type": "array", "items": STRING},
    "scope": STRING, "source_date": STRING, "date_evidence": STRING,
    "research_full_text": {"type": "boolean"},
    "ai_conditions": STRING, "ai_limits": STRING,
})
CANDIDATES_SCHEMA = object_schema({"candidates": {"type": "array", "items": object_schema({
    "url": STRING, "title": STRING, "event_key": STRING,
})}})


def normalize_url(url):
    if re.search(r'[\s<>"{}\\]', url):
        raise ValueError("Unsafe URL characters")
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
        raise ValueError("Invalid public URL")
    if p.port not in (None, 80, 443):
        raise ValueError("Nonstandard URL port")
    host = p.hostname.lower().removeprefix("www.")
    query = [(k, v) for k, v in urllib.parse.parse_qsl(p.query)
             if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid")]
    path = p.path.rstrip("/") or "/"
    # arXiv abstract/PDF/version URLs refer to the same research.
    if host == "arxiv.org":
        path = re.sub(r"^/(?:pdf|html)/", "/abs/", path)
        path = re.sub(r"v\d+(?:\.pdf)?$|\.pdf$", "", path)
    return urllib.parse.urlunsplit(("https", host, path, urllib.parse.urlencode(sorted(query)), ""))


def public_url(url):
    normalize_url(url)
    host = urllib.parse.urlsplit(url).hostname
    addresses = socket.getaddrinfo(host, None)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError("Non-public source host")


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url):
    public_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "BlogBriefing/1.0 (+https://hlcho426.github.io)"})
    with urllib.request.build_opener(SafeRedirect).open(request, timeout=30) as response:
        raw = response.read(3_000_001)
        if len(raw) > 3_000_000:
            raise ValueError("Source exceeds 3 MB limit")
        return raw, response.headers.get_content_type(), response.geturl()


def fetch_source(url, max_chars=30000):
    raw, content_type, final_url = download(url)
    if content_type == "application/pdf" or raw.startswith(b"%PDF"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages[:60])
        more_pages = len(reader.pages) > 60
        title = (reader.metadata or {}).get("/Title", "") or final_url
        document_date = ""
    elif content_type in ("text/html", "application/xhtml+xml"):
        import trafilatura
        html = raw.decode("utf-8", errors="replace")
        text = trafilatura.extract(html, include_comments=False, include_tables=True) or ""
        metadata = trafilatura.extract_metadata(html, default_url=final_url)
        title = metadata.title if metadata and metadata.title else final_url
        # Only explicit publication metadata; do not use a scraper's guessed/modified date.
        from html.parser import HTMLParser
        class PublicationMetadata(HTMLParser):
            value = ""
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                name = attrs.get("property", attrs.get("name", "")).lower()
                if tag == "meta" and name in ("article:published_time", "datepublished", "publication_date", "dcterms.issued"):
                    self.value = attrs.get("content", "")[:10]
        parser = PublicationMetadata()
        parser.feed(html)
        ld_date = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
        document_date = parser.value or (ld_date.group(1) if ld_date else "")
        more_pages = False
        if re.search(r"captcha|verify you are human|access denied", title, re.I):
            raise ValueError("Source blocked by access challenge")
    else:
        raise ValueError("Unsupported source content type")
    if len(text.strip()) < 1000:
        raise ValueError("Source is too short or only an abstract")
    return {"url": final_url, "title": title, "text": text[:max_chars],
            "document_date": document_date, "truncated": len(text) > max_chars or more_pages,
            "sha256": hashlib.sha256(text.encode()).hexdigest()}


def flat(text):
    return " ".join(text.split()).casefold()


def event_key(text):
    return re.sub(r"[^\w]+", "", text.casefold())


def known_posts(root):
    urls, events = set(), set()
    for path in (root / "_posts").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        meta, _ = frontmatter(text)
        if meta.get("briefing_event"):
            events.add(event_key(meta["briefing_event"]))
        for url in re.findall(r"https?://[^\s<>\)\]\"']+", text):
            try:
                urls.add(normalize_url(url))
            except ValueError:
                pass
    return urls, events


def frontmatter(text):
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("Missing YAML front matter")
    meta = yaml.safe_load(parts[1])
    if not isinstance(meta, dict):
        raise ValueError("Invalid front matter")
    return meta, parts[2]


def categories(root):
    readme = (root / "README.md").read_text(encoding="utf-8")
    table = readme.split("## 카테고리 규칙", 1)[1].split("헷갈릴 때", 1)[0]
    return {m.strip() for m in re.findall(r"^\| ([^|]+) \|", table, re.M) if m.strip() != "카테고리"}


def validate_article(article, source, kind, today, config):
    jsonschema.validate(article, ARTICLE_SCHEMA)
    if not article["publishable"]:
        raise ValueError("Editorial rejection: " + article["reason"][:200])
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", article["slug"]) or len(article["slug"]) > 90:
        raise ValueError("Invalid post slug")
    if not event_key(article["event_key"]) or len(article["title"]) < 10 or len(article["lead"]) < 80:
        raise ValueError("Incomplete title, lead or event identity")
    text = flat(source["text"])
    if len(article["paragraphs"]) < 2:
        raise ValueError("Insufficient factual summary")
    for paragraph in article["paragraphs"]:
        quote = flat(paragraph["evidence"])
        if len(quote) < 20 or quote not in text:
            raise ValueError("Evidence quote is not in collected source")
        if len(paragraph["text"]) < 100:
            raise ValueError("Summary paragraph is too short")
    published = date.fromisoformat(article["source_date"])
    date_quote = flat(article["date_evidence"])
    metadata_date = source.get("document_date", "")[:10]
    if metadata_date != published.isoformat():
        from dateparser import parse
        parsed = parse(article["date_evidence"], settings={"STRICT_PARSING": True, "DATE_ORDER": "YMD"})
        if len(date_quote) < 6 or date_quote not in text or parsed is None or parsed.date() != published:
            raise ValueError("Publication date lacks source evidence")
    days = config["research_lookback_days"] if kind == "research" else config["daily_lookback_days"]
    if not 0 <= (today - published).days <= days:
        raise ValueError("Source is outside the publication window")
    if len(article["importance"]) < 150 or len(article["scope"]) < 80:
        raise ValueError("Insufficient analysis or verification scope")
    if not 2 <= len(article["applications"]) <= 4 or any(len(p) < 40 for p in article["applications"]):
        raise ValueError("Insufficient actionable applications")
    if kind == "ai" and (len(article["ai_conditions"]) < 60 or len(article["ai_limits"]) < 60):
        raise ValueError("Missing AI access conditions or limitations")
    if kind == "research":
        if not article["research_full_text"] or source.get("truncated") or len(source["text"]) < 5000:
            raise ValueError("Research full text is not available in model input")
        headings = " ".join(p["heading"] for p in article["paragraphs"])
        if not all(word in headings for word in ("질문", "방법", "발견", "한계")):
            raise ValueError("Missing research question, method, findings or limitations")
    all_prose = json.dumps(article, ensure_ascii=False)
    if re.search(r"<\s*script|\{%|\{\{|C:[\\/]|OPENAI_API_KEY|ghp_|github_pat_", all_prose, re.I):
        raise ValueError("Unsafe markup or private information marker")
    # Model output cannot add links that bypass source collection/link validation.
    if re.search(r"https?://|!\[|<[^>]+>", all_prose):
        raise ValueError("Unexpected model-supplied URL, image or HTML")


def render(article, source, kind, today, config):
    spec = config["types"][kind]
    url = source["url"]
    normalize_url(url)  # Validate, but preserve the final working URL in public links.
    meta = {"title": spec["category"] + " | " + article["title"],
            "date": today.isoformat() + " 08:00:00 +0900", "categories": [spec["category"]],
            "tags": [spec["category"]], "briefing_type": kind,
            "briefing_event": article["event_key"], "briefing_sources": [url]}
    def heading(value):
        return f"\n\n## {value}\n{{:.briefing-heading}}\n\n"
    body = article["lead"] + heading(SECTIONS[0])
    body += "\n\n".join("### " + p["heading"] + "\n\n" + p["text"] for p in article["paragraphs"])
    if kind == "ai":
        body += "\n\n### 실제 사용 조건\n\n" + article["ai_conditions"]
        body += "\n\n### 확인된 범위와 한계\n\n" + article["ai_limits"]
    body += heading(SECTIONS[1]) + "**분석:** " + article["importance"]
    body += heading(SECTIONS[2]) + "\n\n".join("- " + p for p in article["applications"])
    source_title = re.sub(r"[\[\]\n\r{}<>`]", " ", source["title"])
    body += heading(SECTIONS[3]) + f"- [{source_title}](<{url}>) — **{article['source_date']}**, 원문 본문 확인.\n\n"
    body += f"**확인 범위:** {today.isoformat()} 원문을 수집했다. " + article["scope"] + "\n"
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + body


def validate_post(path, root):
    meta, body = frontmatter(path.read_text(encoding="utf-8"))
    if meta.get("categories") not in [[c] for c in categories(root)]:
        raise ValueError("Category does not match README")
    if meta.get("briefing_type"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md", path.name):
            raise ValueError("Post filename must be date + English slug")
        config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
        spec = config["types"][meta["briefing_type"]]
        if meta["categories"] != [spec["category"]] or not meta["title"].startswith(meta["categories"][0] + " | "):
            raise ValueError("Briefing type/category/title mismatch")
        if "image" in meta or any("## " + s not in body for s in SECTIONS):
            raise ValueError("Missing sections or unverified image")
        if body.count("{:.briefing-heading}") != 4 or "**확인 범위:**" not in body:
            raise ValueError("Missing section style or verification scope")
        stamp = str(meta["date"])
        if "+0900" not in stamp and "+09:00" not in stamp:
            raise ValueError("Missing KST timezone")
        if not meta.get("briefing_sources") or not meta.get("briefing_event"):
            raise ValueError("Missing duplicate prevention metadata")
    return meta
