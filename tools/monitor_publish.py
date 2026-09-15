#!/usr/bin/env python3
"""
Monitor the Fiestas publish log in real-time. Prints new lines as they appear.

Designed for Claude's Monitor tool: each stdout line becomes a notification.

Usage:
  python3 tools/monitor_publish.py
"""
import time
from pathlib import Path

LOG = Path(".tmp/fiestas_publish.log")

def main():
    seen = 0
    print("🔍 Monitoring Fiestas publish log...")
    time.sleep(0.5)

    while True:
        if not LOG.exists():
            time.sleep(5)
            continue

        content = LOG.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        # Print only new lines
        if len(lines) > seen:
            for line in lines[seen:]:
                if line.strip():
                    if "OK" in line:
                        print(f"✅ {line}")
                    elif "ERROR" in line:
                        print(f"❌ {line}")
                    else:
                        print(f"📝 {line}")
            seen = len(lines)

        time.sleep(30)


if __name__ == "__main__":
    main()
