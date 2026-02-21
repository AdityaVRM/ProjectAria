"""Single LLM client — Cursor Cloud Agents API only."""
import base64
import json
import re
import time
from typing import Any

import httpx

from app.config import get_settings

_POLL_INTERVAL = 2.0
_MAX_POLL_SECONDS = 120


def _auth_header() -> str:
    settings = get_settings()
    api_key = (settings.cursor_api_key or "").strip()
    if not api_key:
        raise ValueError(
            "No Cursor API key set. Set CURSOR_COMPOSER_1_5_API_KEY in backend/.env "
            "(Cursor Dashboard → Integrations)"
        )
    return "Basic " + base64.b64encode(f"{api_key}:".encode()).decode()


def _api(method: str, path: str, body: dict | None = None, timeout: float = 30.0) -> dict:
    headers = {"Authorization": _auth_header(), "Content-Type": "application/json"}
    url = f"https://api.cursor.com{path}"
    with httpx.Client(timeout=timeout) as client:
        if method == "GET":
            resp = client.get(url, headers=headers)
        elif method == "POST":
            resp = client.post(url, headers=headers, json=body or {})
        elif method == "DELETE":
            resp = client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
    if resp.status_code == 401:
        raise ValueError("Cursor API authentication failed — check CURSOR_COMPOSER_1_5_API_KEY in .env")
    resp.raise_for_status()
    if resp.status_code == 204:
        return {}
    return resp.json()


def llm_invoke(
    system: str,
    user_message: str,
    max_tokens: int = 8192,
    model: str | None = None,
) -> str:
    """Send a prompt to Cursor Cloud Agent and return the assistant response text."""
    settings = get_settings()
    model = model or settings.cursor_model
    prompt_text = f"[SYSTEM INSTRUCTIONS — follow strictly]\n{system}\n\n[USER MESSAGE]\n{user_message}"

    # 1. Launch agent
    launch_body: dict[str, Any] = {
        "prompt": {"text": prompt_text},
        "model": model,
        "source": {"repository": settings.cursor_repo},
    }
    agent = _api("POST", "/v0/agents", launch_body, timeout=30.0)
    agent_id = agent["id"]

    # 2. Poll until finished
    try:
        deadline = time.time() + _MAX_POLL_SECONDS
        while time.time() < deadline:
            status_data = _api("GET", f"/v0/agents/{agent_id}")
            status = status_data.get("status", "")
            if status in ("FINISHED", "FAILED", "STOPPED"):
                break
            time.sleep(_POLL_INTERVAL)
        else:
            _api("POST", f"/v0/agents/{agent_id}/stop")
            raise TimeoutError("Cursor agent timed out")

        if status == "FAILED":
            raise RuntimeError(f"Cursor agent failed: {status_data.get('summary', 'unknown error')}")

        # 3. Get conversation — extract last assistant message
        conv = _api("GET", f"/v0/agents/{agent_id}/conversation")
        messages = conv.get("messages") or []
        for msg in reversed(messages):
            if msg.get("type") == "assistant_message":
                return (msg.get("text") or "").strip()
        return ""
    finally:
        # Clean up — delete the agent so we don't leak resources
        try:
            _api("DELETE", f"/v0/agents/{agent_id}")
        except Exception:
            pass


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
