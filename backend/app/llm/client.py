"""Single LLM client for all agents — Anthropic Claude."""
import json
import re
from typing import Any

from anthropic import Anthropic

from app.config import get_settings


def _client() -> Anthropic:
    settings = get_settings()
    api_key = (settings.cursor_composer_api_key or "").strip()
    if not api_key:
        raise ValueError("No LLM API key set. Set CURSOR_COMPOSER_1_5_API_KEY in backend/.env")
    return Anthropic(api_key=api_key)


def llm_invoke(
    system: str,
    user_message: str,
    max_tokens: int = 8192,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Returns assistant text. Raises on API error."""
    client = _client()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    if not resp.content or not resp.content[0].text:
        return ""
    return resp.content[0].text


def extract_json_block(text: str) -> dict[str, Any] | None:
    """Extract first JSON object from markdown code block or raw text."""
    # Try ```json ... ``` first
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        raw = m.group(1).strip()
    else:
        raw = text.strip()
    # Find first { ... }
    start = raw.find("{")
    if start == -1:
        return None
    depth = 0
    end = -1
    for i in range(start, len(raw)):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end == -1:
        return None
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError:
        return None
