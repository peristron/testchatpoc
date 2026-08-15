from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterator

import requests


CONNECT_TIMEOUT_SECONDS = 15
READ_TIMEOUT_SECONDS = 180


@dataclass(frozen=True)
class Provider:
    name: str
    api_key_secret: str
    base_url: str
    default_model: str
    model_secret: str


class ChatAPIError(RuntimeError):
    """A provider error that is safe to display to the app user."""


def _error_for_status(provider_name: str, status_code: int) -> ChatAPIError:
    if status_code == 401:
        message = f"{provider_name} rejected the configured API key."
    elif status_code in {402, 403}:
        message = (
            f"{provider_name} denied this request. Check account access and billing."
        )
    elif status_code == 429:
        message = f"{provider_name} is rate-limiting requests. Please try again shortly."
    elif status_code >= 500:
        message = f"{provider_name} is temporarily unavailable. Please try again."
    else:
        message = f"{provider_name} could not complete the request (HTTP {status_code})."
    return ChatAPIError(message)


def stream_chat(
    *,
    provider: Provider,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> Iterator[str]:
    """Yield final-answer text from an OpenAI-compatible streaming endpoint."""
    url = f"{provider.base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    try:
        with requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
        ) as response:
            if not response.ok:
                raise _error_for_status(provider.name, response.status_code)

            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue

                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue

                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    break

                try:
                    event = json.loads(data)
                    choices = event.get("choices") or []
                    delta = choices[0].get("delta", {}) if choices else {}
                    content = delta.get("content")
                except (AttributeError, IndexError, json.JSONDecodeError, TypeError):
                    continue

                if content:
                    yield str(content)
    except ChatAPIError:
        raise
    except requests.Timeout as exc:
        raise ChatAPIError(
            f"{provider.name} took too long to respond. Please try again."
        ) from exc
    except requests.RequestException as exc:
        raise ChatAPIError(
            f"Could not connect to {provider.name}. Please try again."
        ) from exc
