#!/usr/bin/env python3
"""Temporary debug script — reproduces exactly what the Mejoras button does, step by step."""
import sys
sys.path.insert(0, ".")

from tools.social_dashboard_server import _account_payload, IMPROVE_SYSTEM_PROMPT, IMPROVE_SCHEMA
from tools.claude_call import call_claude

data = _account_payload("fiestas")
print("=== account payload ok, building prompt ===")

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

print("=== prompt built, length:", len(prompt), "===")
print(prompt[:200])
print("=== calling claude (model=sonnet, with system_prompt + schema) ===")

try:
    r = call_claude(prompt, system_prompt=IMPROVE_SYSTEM_PROMPT, model="sonnet",
                     as_json=True, schema=IMPROVE_SCHEMA)
    print("=== SUCCESS ===")
    print("type:", type(r))
    print("repr:", repr(r))
except Exception as e:
    print("=== FAILED ===")
    import traceback
    traceback.print_exc()
