"""Single LLM client — Google Gemini API only."""
import json
import re
from typing import Any

from google import genai
from google.genai import types

from app.config import get_settings

_client_instance = None


def _client() -> genai.Client:
    global _client_instance
    if _client_instance is None:
        settings = get_settings()
        api_key = (settings.gemini_api_key or "").strip()
        if not api_key:
            raise ValueError(
                "No Gemini API key set. Set GEMINI_API_KEY in backend/.env "
                "(get from https://aistudio.google.com/apikey)"
            )
        _client_instance = genai.Client(api_key=api_key)
    return _client_instance


def llm_invoke(
    system: str,
    user_message: str,
    max_tokens: int = 8192,
    model: str | None = None,
) -> str:
    """Returns assistant text via Gemini. Raises on API error."""
    settings = get_settings()
    model = model or settings.gemini_model
    client = _client()
    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        ),
    )
    return (response.text or "").strip()


def extract_json_block(text: str) -> dict[str, Any] | None:
    """Extract first JSON object from markdown code block or raw text."""
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        raw = m.group(1).strip()
    else:
        raw = text.strip()
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
