"""
Tests for tools/notion_sync.py with a fake Notion API (no network, no token).

Run: python3 -m unittest discover tests
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import notes_rag as rag
from tools import notion_sync as ns


def fake_page(pid, title, clave="", done=False):
    return {"id": pid, "properties": {
        "Tarea": {"title": [{"plain_text": title}]},
        "Clave": {"rich_text": [{"plain_text": clave}] if clave else []},
        "Hecho": {"checkbox": done}}}


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class FakeNotion:
    """Two pages of query results + records every created page."""
    def __init__(self, pages):
        self.pages, self.created = pages, []

    def post(self, url, headers, json, timeout):
        if url.endswith("/query"):
            start = int(json.get("start_cursor", 0))
            chunk = self.pages[start:start + 1]
            more = start + 1 < len(self.pages)
            return FakeResponse({"results": chunk, "has_more": more, "next_cursor": str(start + 1) if more else None})
        self.created.append(json)
        return FakeResponse({"id": "new"})


def msg(ts, text):
    from datetime import datetime
    return {"ts": datetime.fromisoformat(ts), "text": text}


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = rag.connect(Path(self.tmp.name) / "notes.db")
        self._state = mock.patch.object(rag, "NOTION_STATE", Path(self.tmp.name) / "state.json")
        self._state.start()
        rag.add_raw(self.db, "Vida", [
            msg("2026-09-20 10:00:00", "Comprar balanza"),          # before BASELINE → never auto-created
            msg("2026-09-29 10:00:00", "Comprar bicarbonato"),       # already in Notion (manual title match)
            msg("2026-09-29 11:00:00", "Comprar pilas"),             # already in Notion, done, by Clave
            msg("2026-09-30 09:00:00", "Comprar lamparita"),         # new → created
        ], "export")
        rag.add_raw(self.db, "Ide", [msg("2026-09-30 10:00:00", "Hacer landing nueva")], "export")
        rag.rebuild(self.db)
        self.notion = FakeNotion([
            fake_page("p1", "Comprar Bicarbonato!"),
            fake_page("p2", "pilas AA", clave=rag.wd.task_key("Comprar pilas"), done=True),
        ])

    def tearDown(self):
        self._state.stop()
        self.db.close()
        self.tmp.cleanup()

    def test_creates_only_new_tasks_after_baseline(self):
        res = ns.sync(self.db, self.notion, "tok", "dbid")
        titles = [c["properties"]["Tarea"]["title"][0]["text"]["content"] for c in self.notion.created]
        self.assertEqual(sorted(titles), ["Comprar lamparita", "Hacer landing nueva"])
        self.assertEqual(res, {"notion_rows": 2, "done": 1, "created": 2})

    def test_created_rows_carry_key_origin_and_tags(self):
        ns.sync(self.db, self.notion, "tok", "dbid")
        props = [c for c in self.notion.created
                 if c["properties"]["Tarea"]["title"][0]["text"]["content"] == "Comprar lamparita"][0]["properties"]
        self.assertEqual(props["Clave"]["rich_text"][0]["text"]["content"], rag.wd.task_key("Comprar lamparita"))
        self.assertEqual(props["Origen"]["select"]["name"], "auto")
        self.assertEqual(props["Tag"]["select"]["name"], "#compra")
        self.assertEqual(props["Chat"]["select"]["name"], "Vida 🏠💪")

    def test_second_run_creates_nothing_and_done_is_hidden_locally(self):
        ns.sync(self.db, self.notion, "tok", "dbid")
        # simulate Notion now holding the created rows
        for i, c in enumerate(self.notion.created):
            p = c["properties"]
            self.notion.pages.append(fake_page(f"n{i}", p["Tarea"]["title"][0]["text"]["content"],
                                               p["Clave"]["rich_text"][0]["text"]["content"]))
        self.notion.created = []
        self.assertEqual(ns.sync(self.db, self.notion, "tok", "dbid")["created"], 0)
        self.assertNotIn("Comprar pilas", [p["title"] for p in rag.pending(self.db)])

    def test_dry_run_writes_nothing(self):
        res = ns.sync(self.db, self.notion, "tok", "dbid", dry_run=True)
        self.assertEqual(self.notion.created, [])
        self.assertEqual(res["created"], 2)


if __name__ == "__main__":
    unittest.main()
