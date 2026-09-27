#!/usr/bin/env python3
"""
Run a tool with its output appended (UTF-8) to a log file. Used by scheduled tasks on Windows,
which start pythonw.exe (no console window, no stdout) — without this, errors would vanish.

Usage: pythonw tools/run_logged.py tools/weekly_review.py [args...]
       → appends to .tmp/notes_rag/logs/weekly_review.log
"""
import os
import runpy
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOGS = ROOT / ".tmp" / "notes_rag" / "logs"


def main():
    script, *args = sys.argv[1:]
    os.chdir(ROOT)                       # scheduled tasks start in C:\Windows\System32
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{Path(script).stem}.log"
    with open(log_path, "a", encoding="utf-8") as log:
        sys.stdout = sys.stderr = log
        print(f"\n=== {datetime.now():%Y-%m-%d %H:%M} {script} {' '.join(args)}")
        sys.argv = [script, *args]
        try:
            runpy.run_path(script, run_name="__main__")
        except SystemExit as e:
            if e.code not in (None, 0):
                print(f"exit: {e.code}")
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    main()
