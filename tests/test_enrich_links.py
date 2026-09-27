"""
Tests for tools/enrich_links.py with fake HTTP responses (no network).

Run: python3 -m unittest discover tests
"""
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import enrich_links as el
from tools import notes_rag as rag


class Resp:
    def __init__(self, text="", data=None):
        self.text, self.data = text, data

    def json(self):
        return self.data


def fake_get(url, headers=None, timeout=None):
    if "youtube.com/oembed" in url:
        return Resp(data={"title": "Cómo usar Claude Code con MCP", "author_name": "Canal IA"})
    if "publish.twitter.com" in url:
        return Resp(data={"author_name": "alguien", "html": "<blockquote><p>Nuevo funnel de ads &amp; leads</p></blockquote>"})
    if "instagram.com" in url:
        raise ConnectionError("blocked")
    return Resp(text='<html><head><meta property="og:title" content="Ideas de cocina y deco"></head></html>')


class EnrichTest(unittest.TestCase):
    def test_fetch_title_per_source(self):
        self.assertEqual(el.fetch_title("https://youtu.be/abc", fake_get), "Canal IA: Cómo usar Claude Code con MCP")
        self.assertEqual(el.fetch_title("https://x.com/a/status/1", fake_get), "alguien: Nuevo funnel de ads & leads")
        self.assertEqual(el.fetch_title("https://blog.example.com/p", fake_get), "Ideas de cocina y deco")
        self.assertEqual(el.fetch_title("https://www.instagram.com/reel/X/", fake_get), "")

    def test_topics(self):
        self.assertEqual(el.topic_of("Cómo usar Claude Code con MCP", "https://youtu.be/abc"), "🤖 IA y código")
        self.assertEqual(el.topic_of("Ideas de cocina y deco", "https://blog.example.com"), "🏠 Casa y deco")
        self.assertEqual(el.topic_of("", "https://www.instagram.com/reel/X/"), "🔗 Otros (instagram.com)")
        self.assertEqual(el.topic_of("club: Techno rave all night DJ set", "https://www.instagram.com/reel/Y/"),
                         "🎉 Fiestas y eventos")

    def test_enrich_caches_and_makes_titles_searchable(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = rag.connect(Path(tmp) / "notes.db")
            rag.add_raw(db, "Ide", [{"ts": datetime(2026, 9, 1, 12), "text": "https://youtu.be/abc"},
                                    {"ts": datetime(2026, 9, 1, 13), "text": "https://www.instagram.com/reel/X/"}], "export")
            rag.rebuild(db)
            with mock.patch.object(el, "OUT", Path(tmp) / "links.md"):
                self.assertEqual(el.enrich(db, get=fake_get, pause=0), 2)
                self.assertEqual(el.enrich(db, get=fake_get, pause=0), 0)      # cached
                groups = el.report(db)
            self.assertEqual(groups, {"🤖 IA y código": 1, "🔗 Otros (instagram.com)": 1})
            self.assertTrue(rag.search(db, "claude mcp"))                        # found via the title
            db.close()


    def test_failed_links_are_retried_after_a_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = rag.connect(Path(tmp) / "notes.db")
            rag.add_raw(db, "Ide", [{"ts": datetime(2026, 9, 1, 12), "text": "https://www.instagram.com/reel/X/"}], "export")
            rag.rebuild(db)
            self.assertEqual(el.enrich(db, get=fake_get, pause=0), 1)   # fails → no title
            self.assertEqual(el.enrich(db, get=fake_get, pause=0), 0)   # not retried right away
            db.execute("UPDATE links SET fetched = '2026-01-01T00:00:00'")
            self.assertEqual(el.enrich(db, get=fake_get, pause=0), 1)   # retried after a week
            db.close()


if __name__ == "__main__":
    unittest.main()
