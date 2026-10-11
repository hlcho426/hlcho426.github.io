import copy
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import (HERE, categories, fetch_source, frontmatter, known_posts, normalize_url,
                  public_url, render, validate_article, validate_post)
from fixtures import fixture
from run import OpenAI, generate, preflight
from publish import publish

ROOT = HERE.parents[1]
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
TODAY = date(2026, 10, 11)


class BriefingTests(unittest.TestCase):
    def setUp(self):
        f = fixture("game", TODAY)
        self.article, self.source = copy.deepcopy(f["article"]), copy.deepcopy(f["source"])

    def validate(self, kind="game"):
        validate_article(self.article, self.source, kind, TODAY, CONFIG)

    def test_all_three_types_render_and_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind in ("game", "ai", "research"):
                f = fixture(kind, TODAY)
                validate_article(f["article"], f["source"], kind, TODAY, CONFIG)
                p = Path(tmp) / f"{TODAY}-{kind}-test.md"
                p.write_text(render(f["article"], f["source"], kind, TODAY, CONFIG), encoding="utf-8")
                meta = validate_post(p, ROOT)
                self.assertEqual(meta["categories"], [CONFIG["types"][kind]["category"]])
                self.assertEqual(meta["title"].split(" | ", 1)[0], meta["categories"][0])
                self.assertNotIn("image", meta)

    def test_missing_evidence_rejected(self):
        self.article["paragraphs"][0]["evidence"] = "This quote does not occur in the original source"
        with self.assertRaisesRegex(ValueError, "Evidence quote"):
            self.validate()

    def test_future_and_stale_sources_rejected(self):
        for stamp in ("2026-10-12", "2026-09-01"):
            self.article["source_date"] = self.source["document_date"] = stamp
            with self.assertRaisesRegex(ValueError, "publication window"):
                self.validate()

    def test_unsupported_date_rejected(self):
        self.source["document_date"] = ""
        self.article["date_evidence"] = "October 10 2026"
        with self.assertRaisesRegex(ValueError, "date lacks"):
            self.validate()

    def test_date_evidence_must_represent_claimed_date(self):
        self.source["document_date"] = ""
        self.source["text"] += " October 9, 2026"
        self.article["date_evidence"] = "October 9, 2026"
        with self.assertRaisesRegex(ValueError, "date lacks"):
            self.validate()

    def test_date_body_evidence_supported(self):
        self.source["document_date"] = ""
        self.validate()

    def test_research_abstract_and_truncation_rejected(self):
        for mutation in ("truncated", "research_full_text", "short"):
            f = fixture("research", TODAY)
            if mutation == "truncated": f["source"]["truncated"] = True
            if mutation == "research_full_text": f["article"]["research_full_text"] = False
            if mutation == "short": f["source"]["text"] = f["source"]["text"][:1500]
            with self.assertRaisesRegex(ValueError, "full text"):
                validate_article(f["article"], f["source"], "research", TODAY, CONFIG)

    def test_research_structure_required(self):
        self.article["paragraphs"][2]["heading"] = "일반 요약"
        with self.assertRaisesRegex(ValueError, "research question"):
            self.validate("research")

    def test_ai_conditions_required(self):
        self.article["ai_conditions"] = "알 수 없음"
        with self.assertRaisesRegex(ValueError, "AI access"):
            self.validate("ai")

    def test_path_traversal_slug_rejected(self):
        self.article["slug"] = "../../unsafe"
        with self.assertRaisesRegex(ValueError, "slug"):
            self.validate()

    def test_private_markers_and_template_injection_rejected(self):
        for text in ("C:/Users/admin/ProjectSecret", "{{ site.secret }}", "{% include x %}", "OPENAI_API_KEY"):
            self.article["lead"] = text + " " + self.article["lead"]
            with self.assertRaisesRegex(ValueError, "private information"):
                self.validate()

    def test_uncollected_model_link_rejected(self):
        self.article["importance"] += " https://example.org/unverified"
        with self.assertRaisesRegex(ValueError, "model-supplied"):
            self.validate()

    def test_url_tracking_and_fragment_dedup(self):
        self.assertEqual(normalize_url("http://www.example.org/news/?utm_source=x#here"),
                         normalize_url("https://example.org/news"))

    def test_render_preserves_working_source_host(self):
        self.source["url"] = "https://www.example.org/article"
        text = render(self.article, self.source, "game", TODAY, CONFIG)
        self.assertIn("](<https://www.example.org/article>)", text)

    def test_arxiv_version_dedup(self):
        self.assertEqual(normalize_url("https://arxiv.org/pdf/2601.12345v2.pdf"),
                         normalize_url("https://arxiv.org/abs/2601.12345"))

    def test_private_host_rejected(self):
        with patch("socket.getaddrinfo", return_value=[(0, 0, 0, "", ("127.0.0.1", 80))]):
            with self.assertRaisesRegex(ValueError, "Non-public"):
                public_url("https://localhost/article")

    def test_invalid_url_forms_rejected(self):
        for url in ("file:///tmp/private", "https://user:password@example.org/x", "https://example.org:8443/x"):
            with self.assertRaises(ValueError): normalize_url(url)

    def test_source_fetch_short_abstract_rejected(self):
        with patch("core.download", return_value=(b"<html><body>Abstract only</body></html>", "text/html", "https://example.org")):
            with self.assertRaisesRegex(ValueError, "too short"):
                fetch_source("https://example.org")

    def test_only_explicit_publication_metadata(self):
        prose = "This is an article about production techniques with careful analysis and detailed examples. " * 40
        html = '<html><head><title>Example</title><meta property="article:published_time" content="2026-10-10T12:00:00Z"></head><body><article><p>' + prose + '</p></article></body></html>'
        with patch("core.download", return_value=(html.encode(), "text/html", "https://example.org")):
            self.assertEqual(fetch_source("https://example.org")["document_date"], "2026-10-10")

    def test_existing_legacy_post_sources_are_indexed(self):
        urls, _ = known_posts(ROOT)
        self.assertIn(normalize_url("https://store.steampowered.com/app/1619280/Machinarium_2/"), urls)

    def test_paid_client_requires_explicit_gate(self):
        with patch.dict(os.environ, {"BRIEFING_PAID_ENABLED": "false"}):
            with self.assertRaisesRegex(ValueError, "disabled"): OpenAI(CONFIG)

    def test_paid_client_requires_key(self):
        with patch.dict(os.environ, {"BRIEFING_PAID_ENABLED": "true"}, clear=True):
            with self.assertRaisesRegex(ValueError, "missing"): OpenAI(CONFIG)

    def test_pending_type_pr_blocks_before_paid_api(self):
        with patch("run.gh", return_value=json.dumps([{"number": 42, "headRefName": "codex/briefing-ai-2026-10-10", "url": "https://example.org/pr/42"}])):
            pending, _, _ = preflight("owner/repo", "ai", TODAY)
            self.assertEqual(pending, "https://example.org/pr/42")

    def test_closed_same_day_pr_not_recreated(self):
        with patch("run.gh", side_effect=["[]", '[{"url":"https://example.org/closed"}]']):
            self.assertEqual(preflight("o/r", "game", TODAY)[0], "https://example.org/closed")

    def test_cross_type_pending_source_and_event_dedup(self):
        with patch("run.gh", side_effect=[
            '[{"number":1,"headRefName":"codex/briefing-ai-2026-10-10","url":"x"}]', "[]",
            '+briefing_event: product-v2-release\n+[Source](https://example.org/product?utm_source=test)']):
            _, urls, events = preflight("o/r", "game", TODAY)
            self.assertIn("https://example.org/product", urls)
            self.assertIn("productv2release", events)

    def test_github_error_fails_closed(self):
        with patch("run.gh", side_effect=RuntimeError("API unavailable")):
            with self.assertRaises(RuntimeError): preflight("o/r", "game", TODAY)

    def test_offline_generation_never_calls_api_or_github(self):
        with tempfile.TemporaryDirectory() as tmp, patch("run.OpenAI", side_effect=AssertionError("API called")), patch("run.gh", side_effect=AssertionError("GitHub called")):
            for kind in ("game", "ai", "research"):
                report = generate(kind, ROOT, Path(tmp) / kind, TODAY)
                self.assertEqual(len(report["posts"]), 1)
                self.assertEqual(report["usage"], [])

    def test_live_collector_writer_and_review_contract(self):
        client = MagicMock()
        client.usage = []
        client.call.side_effect = [
            {"candidates": [{"url": self.source["url"], "title": "Test", "event_key": "synthetic-game"}]},
            self.article, {"approved": True, "reason": "Supported"}]
        with tempfile.TemporaryDirectory() as tmp, patch("run.preflight", return_value=(None, set(), set())), patch("run.OpenAI", return_value=client), patch("run.fetch_source", return_value=self.source):
            report = generate("game", ROOT, Path(tmp), TODAY, "live", "o/r")
            self.assertEqual(len(report["posts"]), 1)
            self.assertEqual(client.call.call_count, 3)

    def test_source_collection_failure_records_error_and_no_post(self):
        client = MagicMock()
        client.usage = []
        client.call.return_value = {"candidates": [{"url": self.source["url"], "title": "Test", "event_key": "synthetic-game"}]}
        with tempfile.TemporaryDirectory() as tmp, patch("run.preflight", return_value=(None, set(), set())), patch("run.OpenAI", return_value=client), patch("run.fetch_source", side_effect=ValueError("Source unavailable")):
            with self.assertRaisesRegex(ValueError, "All candidates rejected"):
                generate("game", ROOT, Path(tmp), TODAY, "live", "o/r")
            report = json.loads((Path(tmp) / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["posts"], [])
            self.assertIn("Source unavailable", report["skipped"][0]["reason"])
            self.assertEqual(client.call.call_count, 1)

    def test_semantic_rejection_blocks_post(self):
        client = MagicMock()
        client.usage = []
        client.call.side_effect = [
            {"candidates": [{"url": self.source["url"], "title": "Test", "event_key": "synthetic-game"}]},
            self.article, {"approved": False, "reason": "Unsupported productivity claim"}]
        with tempfile.TemporaryDirectory() as tmp, patch("run.preflight", return_value=(None, set(), set())), patch("run.OpenAI", return_value=client), patch("run.fetch_source", return_value=self.source):
            with self.assertRaisesRegex(ValueError, "All candidates rejected"):
                generate("game", ROOT, Path(tmp), TODAY, "live", "o/r")
            self.assertFalse((Path(tmp) / "_posts").exists())

    def test_fixture_cannot_be_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            generate("game", ROOT, out, TODAY)
            with self.assertRaisesRegex(ValueError, "cannot be published"): publish(out, "o/r")

    def test_publisher_uses_only_review_branch_and_one_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "output"
            report = generate("game", ROOT, out, TODAY)
            report["mode"] = "live"  # Simulated writer output; every Git/GitHub mutation is mocked.
            (out / "report.json").write_text(json.dumps(report), encoding="utf-8")
            (root / "_posts").mkdir()
            name = report["posts"][0]["file"]
            shutil.copyfile(out / "_posts" / name, root / "_posts" / name)
            shutil.copyfile(ROOT / "README.md", root / "README.md")
            here = root / "tools" / "briefing"
            here.mkdir(parents=True)
            shutil.copyfile(HERE / "config.json", here / "config.json")
            with patch("publish.HERE", here), patch("publish.preflight", return_value=(None, set(), set())), patch("publish.command") as commands, patch("publish.subprocess.check_output", return_value=f"_posts/{name}\n"), patch("publish.gh", side_effect=["[]", "https://example.org/pr/test"]) as github:
                publish(out, "o/r")
                pushes = [c.args for c in commands.call_args_list if c.args[:2] == ("git", "push")]
                self.assertEqual(pushes, [("git", "push", "origin", "HEAD:refs/heads/codex/briefing-game-2026-10-11")])
                prs = [c.args for c in github.call_args_list if c.args[:2] == ("pr", "create")]
                self.assertEqual(len(prs), 1)
                self.assertNotIn("merge", " ".join(str(c.args) for c in github.call_args_list))

    def test_bad_category_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / f"{TODAY}-game-test.md"
            p.write_text(render(self.article, self.source, "game", TODAY, CONFIG).replace("게임 개발 브리핑\n", "새 카테고리\n"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Category"): validate_post(p, ROOT)

    def test_maximum_counts_match_user_request(self):
        self.assertEqual([CONFIG["types"][k]["max_posts"] for k in ("game", "ai", "research")], [5, 5, 3])


if __name__ == "__main__":
    unittest.main()
