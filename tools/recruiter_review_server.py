"""
Local server for the recruiter review UI.
Serves recruiter_review.html and provides API endpoints to read/write the log.

Usage:
  python3 tools/recruiter_review_server.py
  # Opens http://localhost:8742 in your browser
"""

import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, ".tmp")
LOG_FILE = os.path.join(TMP, "recruiter_outreach_log.json")
SEEN_FILE = os.path.join(TMP, "seen_recruiters.json")
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recruiter_review.html")

PORT = 8742


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence access logs

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, path):
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_html(HTML_FILE)
        elif self.path == "/api/log":
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE) as f:
                    data = json.load(f)
                self.send_json(data)
            else:
                self.send_json([])
        elif self.path == "/api/seen":
            if os.path.exists(SEEN_FILE):
                with open(SEEN_FILE) as f:
                    data = json.load(f)
                self.send_json(data)
            else:
                self.send_json([])
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        if self.path == "/api/save":
            try:
                payload = json.loads(body)
                updated_log = payload.get("log", [])
                rejected_emails = payload.get("rejected_emails", [])

                # Save updated log
                with open(LOG_FILE, "w") as f:
                    json.dump(updated_log, f, ensure_ascii=False, indent=2)

                # Add rejected emails to seen_recruiters so they're never contacted again
                if rejected_emails:
                    seen = set()
                    if os.path.exists(SEEN_FILE):
                        with open(SEEN_FILE) as f:
                            seen = set(json.load(f))
                    seen.update(rejected_emails)
                    with open(SEEN_FILE, "w") as f:
                        json.dump(sorted(seen), f, indent=2)

                print(f"  Saved: {len(updated_log)} records, {len(rejected_emails)} rejected added to seen_recruiters")
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"Recruiter Review UI → {url}")
    print("Press Ctrl+C to stop.\n")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
