"""The call to Gemini: primary alias once, fallback alias once, no pauses.

Vendor errors (SDK APIError, transport errors, timeouts) trigger the
fallback; anything else is a bug in this code and propagates. The SDK is
imported inside `call_gemini` so the unit tests run without it loaded.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Callable

from _ask import constants, prompt

logger = logging.getLogger("ask")


class VendorError(Exception):
    """Gemini or the network failed. Message is for the log only."""


class MissingKey(Exception):
    """GEMINI_API_KEY is not set."""


@dataclass
class ModelReply:
    text: str | None
    model: str
    blocked_reason: str | None


CallFn = Callable[[str, str, list[dict]], ModelReply]


def _client_factory(api_key: str):
    from google import genai

    return genai.Client(api_key=api_key)


def _safety_settings():
    from google.genai import types

    threshold = types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    return [
        types.SafetySetting(category=c, threshold=threshold)
        for c in (
            types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        )
    ]


def call_gemini(model: str, system: str, contents: list[dict]) -> ModelReply:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise MissingKey()
    import httpx
    from google.genai import errors, types

    client = _client_factory(key)
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=constants.TEMPERATURE,
        safety_settings=_safety_settings(),
        response_mime_type="application/json",
        response_schema=prompt.RESPONSE_SCHEMA,
        # No tools are passed, but the SDK still logs an AFC notice per call unless told off.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        http_options=types.HttpOptions(timeout=constants.GEMINI_TIMEOUT_SECONDS * 1000),
    )
    parts = [
        types.Content(role=c["role"], parts=[types.Part.from_text(text=c["text"])])
        for c in contents
    ]
    try:
        resp = client.models.generate_content(model=model, contents=parts, config=config)
        text = resp.text or None
    except (errors.APIError, httpx.HTTPError, TimeoutError) as exc:
        raise VendorError(type(exc).__name__) from exc
    if text:
        return ModelReply(text=text, model=model, blocked_reason=None)
    finish = resp.candidates[0].finish_reason if getattr(resp, "candidates", None) else None
    feedback = getattr(resp, "prompt_feedback", None)
    block = getattr(feedback, "block_reason", None) if feedback else None
    reason = f"finish={finish} block={block}"
    logger.warning("empty reply from %s: %s", model, reason)
    return ModelReply(text=None, model=model, blocked_reason=reason)


def ask_model(
    system: str,
    contents: list[dict],
    *,
    models: tuple[str, str],
    call: CallFn | None = None,
) -> ModelReply:
    call = call or call_gemini
    last: VendorError | None = None
    for model in models:
        try:
            return call(model, system, contents)
        except VendorError as exc:
            last = exc
            logger.warning("vendor error on %s: %s", model, exc)
    if last is None:
        raise VendorError("no models configured")
    raise last
