#!/usr/bin/env python3
"""
File-based logging for the Fiestas batch scripts (auto_fiestas_queue.py,
publish_fiestas_next.py), replacing bare print() calls.

These run headless via cron; print() output was going nowhere once the
terminal that launched them closed. get_logger() writes to both stdout
(so interactive runs still show output) and a per-day log file under
.tmp/logs/, per CLAUDE.md's convention that .tmp/ holds regenerable
intermediates.

Usage:
    from tools.batch_logger import get_logger
    log = get_logger("auto_fiestas_queue")
    log.info("Sheet has %d existing entries.", len(known))
"""

import logging
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOG_DIR = ROOT / ".tmp" / "logs"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"fiestas.{name}")
    if logger.handlers:
        return logger  # already configured — avoid duplicate handlers on re-import

    logger.setLevel(logging.INFO)
    logger.propagate = False

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stream_handler)

    return logger


if __name__ == "__main__":
    # Self-contained smoke test (no network/credentials needed).
    log = get_logger("smoke_test")
    log.info("smoke test info line")
    log.warning("smoke test warning line")

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"smoke_test_{today}.log"
    ok = log_file.exists() and "smoke test info line" in log_file.read_text()
    print(f"\n[{'OK' if ok else 'FAIL'}] log file written to {log_file}")
    raise SystemExit(0 if ok else 1)
