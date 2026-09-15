#!/usr/bin/env python3
"""Temporary debug script — isolates exactly which path (SDK vs CLI) runs and what it returns."""
import sys
sys.path.insert(0, ".")

from tools.social_dashboard_server import _account_payload, IMPROVE_SYSTEM_PROMPT, IMPROVE_SCHEMA
from tools.claude_call import _sdk_call, _cli_call

data = _account_payload("fiestas")
posts_summary = "\n".join(
    f"- \"{p['caption']}\" ({p['media_type']}, {p['like_count']} likes, {p['comments_count']} comentarios, {p['timestamp']})"
    for p in data["posts"]
) or "(sin posts)"
prompt = (
    f"Cuenta: {data['name']} (@{data['username']})\n"
    f"Seguidores: {data['followers_count']} "
    f"(1d: {data['growth']['1d']}, 7d: {data['growth']['7d']}, 30d: {data['growth']['30d']})\n"
    f"Total de posts: {data['media_count']}\n\n"
    f"Últimos posteos:\n{posts_summary}"
)

print("=== trying _sdk_call directly ===")
try:
    r = _sdk_call(prompt, IMPROVE_SYSTEM_PROMPT, "sonnet", True, IMPROVE_SCHEMA)
    print("SDK SUCCESS, repr:", repr(r))
except Exception as e:
    print("SDK FAILED:", type(e).__name__, str(e)[:300])

print()
print("=== trying _cli_call directly ===")
try:
    r = _cli_call(prompt, IMPROVE_SYSTEM_PROMPT, "sonnet", True, IMPROVE_SCHEMA)
    print("CLI SUCCESS, repr:", repr(r))
except Exception as e:
    print("CLI FAILED:", type(e).__name__, str(e)[:500])
