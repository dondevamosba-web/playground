"""
Tests for tools/windows_setup.py and tools/run_logged.py (run anywhere; nothing touches Windows).

Run: python3 -m unittest discover tests
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PureWindowsPath
from unittest import mock

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import windows_setup as ws

GO_SNIPPET = "func main() {\n\tconnect()\n\tstartRESTServer(client, messageStore, 8080)\n\twait()\n}\n"


class BridgePatchTest(unittest.TestCase):
    def test_disables_rest_server_once(self):
        out = ws.patch_bridge_source(GO_SNIPPET)
        self.assertNotIn("\tstartRESTServer(client", out)
        self.assertIn("startRESTServer disabled", out)
        self.assertEqual(ws.patch_bridge_source(out), out)                 # idempotent

    def test_handles_windows_line_endings(self):
        out = ws.patch_bridge_source(GO_SNIPPET.replace("\n", "\r\n"))
        self.assertIn("startRESTServer disabled", out)

    def test_refuses_unknown_code(self):
        with self.assertRaises(RuntimeError):
            ws.patch_bridge_source("func main() { startRESTServer(c, s, 9090) }")


class EnvTest(unittest.TestCase):
    def test_writes_without_bom_and_keeps_other_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_bytes("\ufeffANTHROPIC_API_KEY=x\nNOTION_TOKEN=old\n".encode("utf-8"))
            ws.write_env(env, {"NOTION_TOKEN": "ntn_new", "NOTION_PENDIENTES_DB": "db"})
            raw = env.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(raw.decode().splitlines(),
                             ["ANTHROPIC_API_KEY=x", "NOTION_TOKEN=ntn_new", "NOTION_PENDIENTES_DB=db"])


class ScheduleTest(unittest.TestCase):
    def test_task_commands_fit_the_261_char_limit(self):
        win_root = PureWindowsPath(r"C:\Users\Guido\playground")
        py = PureWindowsPath(r"C:\Users\Guido\AppData\Local\Programs\Python\Python312\pythonw.exe")
        with mock.patch.object(ws, "ROOT", win_root), mock.patch.object(ws, "pythonw", return_value=py):
            cmds = ws.task_commands()
        self.assertEqual([c[c.index("/SC") + 1] for c in cmds], ["WEEKLY", "HOURLY"])
        for c in cmds:
            tr = c[c.index("/TR") + 1]
            self.assertLessEqual(len(tr), 261, tr)
            self.assertIn("run_logged.py", tr)
        self.assertIn("SUN", cmds[0])

    def test_startup_launcher_is_hidden(self):
        vbs = ws.startup_vbs()
        self.assertTrue(vbs.startswith('CreateObject("WScript.Shell").Run "cmd /c'))
        self.assertTrue(vbs.rstrip().endswith(", 0, False"))                # 0 = hidden window

    def test_refuses_to_run_outside_windows_without_dry_run(self):
        if sys.platform == "win32":
            self.skipTest("only meaningful off Windows")
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "windows_setup.py"), "schedule"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "windows_setup.py"), "schedule", "--dry-run"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("schtasks /Create", r.stdout)


class RunLoggedTest(unittest.TestCase):
    def test_logs_output_and_errors(self):
        from tools import run_logged
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "boom.py"
            script.write_text("print('hola 🏠')\nraise ValueError('falló')\n", encoding="utf-8")
            argv, out, err = sys.argv, sys.stdout, sys.stderr
            try:
                with mock.patch.object(run_logged, "LOGS", Path(tmp) / "logs"), \
                     mock.patch.object(run_logged.os, "chdir"):
                    sys.argv = ["run_logged.py", str(script)]
                    run_logged.main()
            finally:
                sys.argv, sys.stdout, sys.stderr = argv, out, err
            log = (Path(tmp) / "logs" / "boom.log").read_text(encoding="utf-8")
            self.assertIn("hola 🏠", log)
            self.assertIn("ValueError: falló", log)


if __name__ == "__main__":
    unittest.main()
