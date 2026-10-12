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
RESEARCH_SECTIONS = ("연구 정보", "연구 목적과 질문", "연구 방법", "연구 결과",
                     "연구 발견과 한계", "게임 설계에 적용할 점", "원문과 확인 범위")
RESEARCH_GROUPS = {"purpose": RESEARCH_SECTIONS[1], "methods": RESEARCH_SECTIONS[2],
                   "results": RESEARCH_SECTIONS[3], "findings_limits": RESEARCH_SECTIONS[4]}


def object_schema(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


STRING = {"type": "string"}
PARAGRAPH = object_schema({"heading": STRING, "text": STRING, "evidence": STRING})
PARAGRAPH["properties"]["research_section"] = {"enum": list(RESEARCH_GROUPS)}
ARTICLE_SCHEMA = object_schema({
    "publishable": {"type": "boolean"}, "reason": STRING,
    "title": STRING, "slug": STRING, "event_key": STRING,
    "lead": STRING, "paragraphs": {"type": "array", "items": PARAGRAPH},
    "importance": STRING, "applications": {"type": "array", "items": STRING},
    "scope": STRING, "source_date": STRING, "date_evidence": STRING,
    "research_full_text": {"type": "boolean"},
    "ai_conditions": STRING, "ai_limits": STRING,
})
# Legacy kind/ai_* keys keep existing branches and duplicate checks compatible.
# These fields are required only for the game-development technology stream.
TECH_FIELDS = {"tech_workflow": 80, "tech_example": 100,
               "tech_audience": 40, "tech_verdict": 60}
ARTICLE_SCHEMA["properties"].update({field: STRING for field in TECH_FIELDS})
ARTICLE_SCHEMA["properties"]["research_info"] = object_schema({
    "title": STRING, "authors": {"type": "array", "items": STRING, "minItems": 1},
    "venue": STRING, "publication_type": STRING, "rights_note": STRING,
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
    """Allowed front matter category lists from the README table; a '-' sub-category means top level only."""
    readme = (root / "README.md").read_text(encoding="utf-8")
    table = readme.split("## 카테고리 규칙", 1)[1].split("헷갈릴 때", 1)[0]
    rows = re.findall(r"^\| ([^|]+) \| ([^|]+) \|", table, re.M)
    return [[top.strip()] + ([sub.strip()] if sub.strip() != "-" else [])
            for top, sub in rows if top.strip() != "큰 카테고리"]


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
    if kind == "ai":
        if len(article["ai_conditions"]) < 60 or len(article["ai_limits"]) < 60:
            raise ValueError("Missing technology access conditions or limitations")
        for field, minimum in TECH_FIELDS.items():
            if len(article.get(field, "")) < minimum:
                raise ValueError("Missing technology explanation: " + field)
    if kind == "research":
        if not article["research_full_text"] or source.get("truncated") or len(source["text"]) < 5000:
            raise ValueError("Research full text is not available in model input")
        info = article.get("research_info")
        if not info or any(not str(value).strip() for value in info.values()):
            raise ValueError("Missing research bibliography")
        if flat(info["title"]) not in text or any(not flat(author) or flat(author) not in text for author in info["authors"]):
            raise ValueError("Research title or author lacks collected source evidence")
        groups = {p.get("research_section") for p in article["paragraphs"]}
        if not set(RESEARCH_GROUPS).issubset(groups) or None in groups:
            raise ValueError("Missing research purpose, methods, results or findings_limits section")
        limits = [p for p in article["paragraphs"] if p["research_section"] == "findings_limits"]
        if len(limits) < 2 or not any("발견" in p["heading"] or "의미" in p["heading"] for p in limits):
            raise ValueError("Missing separate research findings and limitations paragraphs")
        if not any("한계" in p["heading"] for p in limits):
            raise ValueError("Missing explicit research limitations")
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
    meta = {"title": article["title"],
            "description": " ".join(article["lead"].split())[:160],
            "date": today.isoformat() + " 08:00:00 +0900",
            "categories": [spec["parent_category"], spec["category"]],
            "tags": [spec["category"]], "briefing_type": kind,
            "briefing_event": article["event_key"], "briefing_sources": [url]}
    def heading(value):
        return f"\n\n## {value}\n{{:.briefing-heading}}\n\n"
    body = "*이 글은 공개 원문을 바탕으로 Codex가 조사하고 정리했습니다.*\n\n" + article["lead"]
    source_title = re.sub(r"[\[\]\n\r{}<>`]", " ", source["title"])
    if kind == "research":
        meta["briefing_format"] = "research-v2"
        info = article["research_info"]
        def inline(value):
            # Bibliography is prose, not a route for additional links or headings.
            return re.sub(r'([\\`*_[\]{}()!|#])', r'\\\1', " ".join(value.split()))
        body += heading(RESEARCH_SECTIONS[0])
        body += (f"- **연구 제목:** {inline(info['title'])}\n"
                 f"- **연구 저자:** {', '.join(inline(a) for a in info['authors'])}\n"
                 f"- **발표 정보:** {inline(info['venue'])} · {article['source_date']}\n"
                 f"- **자료 유형:** {inline(info['publication_type'])}\n"
                 f"- **연구 원문:** [{source_title}](<{url}>)\n"
                 f"- **저작권·이용 조건:** {inline(info['rights_note'])}")
        for group, label in RESEARCH_GROUPS.items():
            body += heading(label)
            body += "\n\n".join("### " + p["heading"] + "\n\n" + p["text"]
                                  for p in article["paragraphs"] if p["research_section"] == group)
        body += heading(RESEARCH_SECTIONS[5]) + "**설계 적용에 관한 해석:** " + article["importance"]
        body += "\n\n" + "\n\n".join("- " + p for p in article["applications"])
        body += heading(RESEARCH_SECTIONS[6])
        body += f"- [{source_title}](<{url}>) — **{article['source_date']}**, 원문 전문 확인.\n\n"
        body += f"**확인 범위:** {today.isoformat()} 원문을 수집했다. " + article["scope"] + "\n"
        return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + body
    body += heading(SECTIONS[0])
    body += "\n\n".join("### " + p["heading"] + "\n\n" + p["text"] for p in article["paragraphs"])
    if kind == "ai":
        body += "\n\n### 제작 작업은 어떻게 달라지나\n\n" + article["tech_workflow"]
        body += "\n\n### 구체적인 작업 예시\n\n" + article["tech_example"]
        body += "\n\n### 실제 사용 조건\n\n" + article["ai_conditions"]
        body += "\n\n### 확인된 범위와 한계\n\n" + article["ai_limits"]
    body += heading(SECTIONS[1]) + "**분석:** " + article["importance"]
    if kind == "ai":
        body += "\n\n### 어떤 개발자에게 관련 있나\n\n" + article["tech_audience"]
        body += "\n\n### 지금 도입할 만한가\n\n" + article["tech_verdict"]
    body += heading(SECTIONS[2]) + "\n\n".join("- " + p for p in article["applications"])
    body += heading(SECTIONS[3]) + f"- [{source_title}](<{url}>) — **{article['source_date']}**, 원문 본문 확인.\n\n"
    body += f"**확인 범위:** {today.isoformat()} 원문을 수집했다. " + article["scope"] + "\n"
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + body


def validate_post(path, root):
    meta, body = frontmatter(path.read_text(encoding="utf-8"))
    if meta.get("categories") not in categories(root):
        raise ValueError("Category does not match README")
    if meta.get("briefing_type"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md", path.name):
            raise ValueError("Post filename must be date + English slug")
        config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
        spec = config["types"][meta["briefing_type"]]
        if meta["categories"] != [spec["parent_category"], spec["category"]]:
            raise ValueError("Briefing type/category/title mismatch")
        sections = RESEARCH_SECTIONS if meta.get("briefing_format") == "research-v2" else SECTIONS
        if meta.get("briefing_format") == "research-v2" and meta["briefing_type"] != "research":
            raise ValueError("Research format requires research type")
        if "image" in meta or any("## " + s not in body for s in sections):
            raise ValueError("Missing sections or unverified image")
        if body.count("{:.briefing-heading}") != len(sections) or "**확인 범위:**" not in body:
            raise ValueError("Missing section style or verification scope")
        stamp = str(meta["date"])
        if "+0900" not in stamp and "+09:00" not in stamp:
            raise ValueError("Missing KST timezone")
        if not meta.get("briefing_sources") or not meta.get("briefing_event"):
            raise ValueError("Missing duplicate prevention metadata")
    return meta
