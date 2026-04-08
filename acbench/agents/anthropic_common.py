"""Shared Anthropic Messages API helpers for ACBench agents."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def anthropic_messages_create(
    *,
    api_key: str,
    model: str,
    prompt: str,
    base_url: str = "https://api.anthropic.com",
    version: str = "2023-06-01",
    max_tokens: int = 4096,
) -> str:
    """Send one prompt to the Anthropic Messages API and return plain text."""

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    url = base_url.rstrip("/") + "/v1/messages"
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": version,
        },
        method="POST",
    )
    try:
        with urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:  # pragma: no cover - exercised against real APIs
        message = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Anthropic API request failed with HTTP {exc.code}: {message}") from exc
    except URLError as exc:  # pragma: no cover - exercised against real APIs
        raise ValueError(f"Anthropic API request failed: {exc.reason}") from exc

    return extract_text_from_message(body)


def extract_text_from_message(body: dict[str, Any]) -> str:
    """Flatten Anthropic message content blocks into one text string."""

    parts: list[str] = []
    for block in body.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            text = str(block.get("text", ""))
            if text:
                parts.append(text)
    return "\n".join(parts).strip()
