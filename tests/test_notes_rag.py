"""
Tests for tools/notes_rag.py: exports + a fake bridge DB, search, pending, proposals.

Run: python3 -m unittest discover tests
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import notes_rag as rag

FIX = Path(__file__).parent / "fixtures"
EXPORTS = [str(FIX / f) for f in ("Psi_test.txt", "Ide_test.txt", "Vida_test.txt")]


def fake_bridge(path):
    """Same schema as lharries/whatsapp-mcp whatsapp-bridge/store/messages.db (only the columns we read)."""
    db = sqlite3.connect(path)
    db.executescript("""
        CREATE TABLE chats (jid TEXT PRIMARY KEY, name TEXT, last_message_time TIMESTAMP);
        CREATE TABLE messages (id TEXT, chat_jid TEXT, sender TEXT, content TEXT, timestamp TIMESTAMP,
                               is_from_me BOOLEAN, media_type TEXT);
        INSERT INTO chats VALUES ('1@g.us', 'Vida 🏠💪 #casa #compra #cuerpo', NULL),
                                 ('2@g.us', 'Familia', NULL),
                                 ('3@s.whatsapp.net', 'Juan', NULL);
        INSERT INTO messages VALUES
          ('a', '1@g.us', 'me', 'Comprar cable HDMI', '2026-09-20 10:00:00-03:00', 1, ''),
          ('b', '1@g.us', 'me', '', '2026-09-20 10:01:00-03:00', 1, 'image'),
          ('c', '2@g.us', 'x',  'secreto familiar', '2026-09-20 10:02:00-03:00', 0, ''),
          ('d', '3@s.whatsapp.net', 'me', 'hola Juan', '2026-09-20 10:03:00-03:00', 1, '');
    """)
    db.commit()
    db.close()


class RagTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.db = rag.connect(self.dir / "notes.db")
        self._state = mock.patch.object(rag, "NOTION_STATE", self.dir / "notion_state.json")
        self._state.start()

    def tearDown(self):
        self._state.stop()
        self.db.close()
        self.tmp.cleanup()

    def test_ingest_is_idempotent(self):
        first = rag.ingest_exports(self.db, EXPORTS)
        second = rag.ingest_exports(self.db, EXPORTS)
        self.assertGreater(first, 0)
        self.assertEqual(second, 0)
        self.assertEqual(len(rag.rebuild(self.db)), first)

    def test_bridge_reads_only_my_messages_in_note_chats(self):
        bridge = self.dir / "messages.db"
        fake_bridge(bridge)
        self.assertEqual(rag.ingest_bridge(self.db, bridge), 1)
        items = rag.rebuild(self.db)
        notes = [i["note"] for i in items]
        self.assertEqual(notes, ["Comprar cable HDMI"])
        self.assertEqual(items[0]["chat"], "Vida 🏠💪")
        self.assertEqual(items[0]["date"], "2026-09-20 10:00")   # local wall time kept

    def test_refresh_only_when_bridge_changes(self):
        bridge = self.dir / "messages.db"
        fake_bridge(bridge)
        with mock.patch.dict("os.environ", {"WHATSAPP_BRIDGE_DB": str(bridge)}):
            self.assertTrue(rag.refresh_from_bridge(self.db))
            self.assertFalse(rag.refresh_from_bridge(self.db))

    def test_search_ignores_accents(self):
        rag.ingest_exports(self.db, EXPORTS)
        rag.rebuild(self.db)
        hits = rag.search(self.db, "panaderia")
        self.assertTrue(hits and "panadería" in hits[0]["note"])

    def test_pending_skips_tasks_done_in_notion(self):
        rag.ingest_exports(self.db, EXPORTS)
        rag.rebuild(self.db)
        before = [p["title"] for p in rag.pending(self.db)]
        self.assertIn("Comprar bicarbonato", before)
        key = rag.wd.task_key("Comprar bicarbonato")
        rag.NOTION_STATE.write_text(json.dumps({"tasks": {key: {"done": True}}}))
        after = [p["title"] for p in rag.pending(self.db)]
        self.assertNotIn("Comprar bicarbonato", after)

    def test_proposals(self):
        rag.ingest_exports(self.db, EXPORTS)
        rag.rebuild(self.db)
        props = "\n".join(rag.propose(self.db, days=7, today=datetime(2026, 9, 7)))
        self.assertIn("links sin nota", props)
        self.assertIn("chat equivocado", props)                  # bicarbonato in Psi
        self.assertIn("lo anotaste 2 veces", props)              # bicarbonato in Psi + Vida
        old = "\n".join(rag.propose(self.db, days=7, today=datetime(2026, 10, 30)))
        self.assertIn("tareas con más de", old)
        self.assertIn("No hay notas", old)


class McpTest(unittest.TestCase):
    def setUp(self):
        from tools import notes_mcp
        self.mcp = notes_mcp
        self.tmp = tempfile.TemporaryDirectory()
        self.db = rag.connect(Path(self.tmp.name) / "notes.db")
        rag.ingest_exports(self.db, EXPORTS)
        rag.rebuild(self.db)
        self._env = mock.patch.dict("os.environ", {"WHATSAPP_BRIDGE_DB": str(Path(self.tmp.name) / "none.db")})
        self._env.start()

    def tearDown(self):
        self._env.stop()
        self.db.close()
        self.tmp.cleanup()

    def call(self, method, params=None, rid=1):
        return self.mcp.handle(self.db, {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}})

    def test_handshake_and_tool_list(self):
        self.assertEqual(self.call("initialize")["result"]["serverInfo"]["name"], "notas")
        self.assertIsNone(self.mcp.handle(self.db, {"jsonrpc": "2.0", "method": "notifications/initialized"}))
        names = {t["name"] for t in self.call("tools/list")["result"]["tools"]}
        self.assertEqual(names, {"buscar_notas", "pendientes", "propuestas", "notas_recientes"})

    def test_tools_are_read_only_and_errors_do_not_crash(self):
        res = self.call("tools/call", {"name": "buscar_notas", "arguments": {"consulta": "landing"}})["result"]
        self.assertIn("landing", res["content"][0]["text"])
        res = self.call("tools/call", {"name": "enviar_mensaje", "arguments": {}})["result"]
        self.assertTrue(res["isError"])
        self.assertEqual(self.call("borrar_todo")["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
