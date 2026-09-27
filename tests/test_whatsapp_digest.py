"""
Tests for tools/whatsapp_digest.py with synthetic chats (tests/fixtures/*_test.txt).

Run: python3 -m unittest discover tests
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import whatsapp_digest as wd

FIX = Path(__file__).parent / "fixtures"


def load_all():
    items = []
    for title, text in wd._load_sources([str(FIX / f) for f in ("Psi_test.txt", "Ide_test.txt", "Vida_test.txt")]):
        key = wd._chat_key(title)
        items += [wd.classify(m, key) for m in wd.parse_chat(text)]
    items.sort(key=lambda x: x["date"])
    wd.mark_duplicates(items)
    return items


class ParseTest(unittest.TestCase):
    def test_chat_key_from_title(self):
        self.assertEqual(wd._chat_key("Psi 💭 #terapia #aprender"), "Psi")
        self.assertEqual(wd._chat_key("Fit 🎾"), "Vida")          # old name
        self.assertEqual(wd._chat_key("Psi_test"), "Psi")
        self.assertIsNone(wd._chat_key("Familia"))

    def test_skips_deleted_media_and_system_lines(self):
        msgs = wd.parse_chat((FIX / "Psi_test.txt").read_text(encoding="utf-8"))
        texts = [m["text"] for m in msgs]
        self.assertEqual(len(msgs), 4)
        self.assertFalse(any("Eliminaste" in t or "omitida" in t for t in texts))
        ide = wd.parse_chat((FIX / "Ide_test.txt").read_text(encoding="utf-8"))
        self.assertFalse(any("cambió el nombre" in m["text"] for m in ide))

    def test_multiline_messages_are_merged(self):
        msgs = wd.parse_chat((FIX / "Psi_test.txt").read_text(encoding="utf-8"))
        self.assertIn("segunda línea", msgs[2]["text"])

    def test_format_change_fails_loudly(self):
        # If WhatsApp changes the export format, nothing parses → the caller must notice.
        self.assertEqual(wd.parse_chat("2026-09-01 10:00 - Tú: hola\n"), [])


class ClassifyTest(unittest.TestCase):
    def setUp(self):
        self.items = load_all()
        self.by_note = {i["note"].splitlines()[0]: i for i in self.items if i["note"]}

    def test_explicit_tag_wins(self):
        it = self.by_note["#cliente mandar propuesta a la panadería"]
        self.assertEqual(it["tags"], ["#cliente"])
        self.assertEqual(it["tag_source"], "explicit")

    def test_bare_link_flagged_but_link_with_verb_not(self):
        bare = [i for i in self.items if "instagram.com" in "".join(i["urls"])][0]
        noted = [i for i in self.items if "x.com" in "".join(i["urls"])][0]
        self.assertIn("link_sin_nota", bare["flags"])
        self.assertNotIn("link_sin_nota", noted["flags"])

    def test_purchase_in_psi_is_misplaced(self):
        it = [i for i in self.items if i["chat"] == "Psi 💭" and "bicarbonato" in i["note"]][0]
        self.assertEqual(it["tags"], ["#compra"])
        self.assertIn("fuera_de_lugar", it["flags"])

    def test_late_night_and_task(self):
        it = [i for i in self.items if i["note"].startswith("Soñé")][0]
        self.assertIn("madrugada", it["flags"])
        self.assertEqual(self.by_note["Hacer landing para el cliente nuevo"]["kind"], "task")

    def test_duplicates_across_days(self):
        drafts = [i for i in self.items if i["note"].startswith("Borrador")]
        self.assertEqual([("duplicado" in d["flags"]) for d in drafts], [False, True])


class PendingTest(unittest.TestCase):
    def test_uses_latest_checklist_and_dedupes_tasks(self):
        pend = wd.pending_items(load_all())
        titles = [p["title"] for p in pend]
        self.assertIn("Pintar pieza", titles)
        self.assertNotIn("Techo", titles)                          # checked in the newer copy
        self.assertEqual(titles.count("Comprar bicarbonato"), 1)   # noted in Psi and Vida
        self.assertEqual(len({p["key"] for p in pend}), len(pend))

    def test_task_key_ignores_case_and_punctuation(self):
        self.assertEqual(wd.task_key("Comprar  bicarbonato!"), wd.task_key("comprar bicarbonato"))


if __name__ == "__main__":
    unittest.main()
