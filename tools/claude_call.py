"""
Base tool for calling Claude via the Anthropic SDK (with CLI fallback).
Usage: from tools.claude_call import call_claude
"""

import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Model aliases
# ---------------------------------------------------------------------------
_MODEL_MAP = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-8",
}


def _resolve_model(model: str) -> str:
    return _MODEL_MAP.get(model, model)


# ---------------------------------------------------------------------------
# Load .env so ANTHROPIC_API_KEY is available regardless of how the script
# was invoked (subprocess, direct, etc.)
# ---------------------------------------------------------------------------
def _load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


_load_env()


# ---------------------------------------------------------------------------
# SDK path (primary)
# ---------------------------------------------------------------------------
def _sdk_call(prompt: str, system_prompt: str | None, model: str, as_json: bool, schema: dict | None) -> str:
    import anthropic

    client = anthropic.Anthropic()
    resolved = _resolve_model(model)

    messages = [{"role": "user", "content": prompt}]

    kwargs: dict = {
        "model": resolved,
        "max_tokens": 4096,
        "messages": messages,
    }

    if system_prompt:
        # Cache the system prompt — saves tokens on repeated calls with the same system prompt
        kwargs["system"] = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    if schema:
        # Ask for JSON output matching the schema via a tool
        kwargs["tools"] = [
            {
                "name": "structured_output",
                "description": "Return structured output matching the provided schema.",
                "input_schema": schema,
            }
        ]
        kwargs["tool_choice"] = {"type": "tool", "name": "structured_output"}

    response = client.messages.create(**kwargs)

    if schema:
        for block in response.content:
            if block.type == "tool_use" and block.name == "structured_output":
                return json.dumps(block.input)
        raise RuntimeError("SDK call with schema returned no tool_use block")

    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    return text.strip()


# ---------------------------------------------------------------------------
# CLI fallback (used only if SDK call fails / SDK not available)
# ---------------------------------------------------------------------------
def _find_claude_binary() -> str:
    import shutil
    found = shutil.which("claude")
    if found:
        return found

    candidates = [
        Path.home() / ".vscode/extensions",
        Path.home() / "Library/Application Support/Claude/claude-code-vm",
        Path.home() / "Library/Application Support/Claude/claude-code",
    ]
    for base in candidates:
        if not base.exists():
            continue
        for p in sorted(base.rglob("claude"), reverse=True):
            if p.is_file() and p.stat().st_size > 1_000_000:
                return str(p)

    raise FileNotFoundError("Could not find the claude CLI.")


_CLAUDE_BIN = None


def _cli_call(prompt: str, system_prompt: str | None, model: str, as_json: bool, schema: dict | None) -> str:
    import subprocess
    global _CLAUDE_BIN
    if _CLAUDE_BIN is None:
        _CLAUDE_BIN = _find_claude_binary()

    cmd = [_CLAUDE_BIN, "-p", prompt, "--model", model]
    if system_prompt:
        cmd += ["--system-prompt", system_prompt]
    if schema:
        cmd += ["--json-schema", json.dumps(schema), "--output-format", "json"]
    elif as_json:
        cmd += ["--output-format", "json"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI call failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------
def call_claude(
    prompt: str,
    system_prompt: str = None,
    model: str = "haiku",
    as_json: bool = False,
    schema: dict = None,
) -> str | dict:
    """
    Call Claude and return the response.

    Args:
        prompt: The user prompt.
        system_prompt: Optional system prompt (cached automatically via SDK).
        model: 'haiku' (default), 'sonnet', 'opus', or a full model ID.
        as_json: If True, parse and return response as dict.
        schema: Optional JSON schema for structured output.

    Returns:
        String response, or dict if as_json=True or schema is provided.
    """
    try:
        output = _sdk_call(prompt, system_prompt, model, as_json, schema)
    except Exception:
        # Fall back to CLI if SDK fails (e.g. missing key, import error)
        output = _cli_call(prompt, system_prompt, model, as_json, schema)

    if schema or as_json:
        if isinstance(output, str):
            parsed = json.loads(output)
            # CLI wraps in {"result": ...}; SDK path returns raw JSON
            return parsed.get("result", parsed) if isinstance(parsed, dict) and "result" in parsed else parsed
        return output

    return output


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Say hello in one sentence."
    print(call_claude(prompt))
