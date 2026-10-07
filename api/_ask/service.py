"""One request, end to end. Pure: time, environment, transport and corpus
are passed in, so the tests drive it without a network.

Order: origin, parse, validate, question-likeness, rate limit, injection detector, corpus,
model, parse model JSON, clean answer, leak check, validate sources.
"""

from __future__ import annotations

import json
import logging
import time
from urllib.parse import urlparse

from _ask import access, constants, corpus, gemini, guardrails, prompt

logger = logging.getLogger("ask")

LIMITER = access.Limiter(constants.RATE_LIMIT, constants.RATE_WINDOW_SECONDS)


def normalize_url(url: str) -> str:
    path = urlparse(url.strip()).path if "://" in url else url.strip().split("#", 1)[0]
    path = path.split("#", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return path


def validate_sources(sources: object, published: set[str]) -> list[dict]:
    if not isinstance(sources, list):
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for item in sources:
        if not isinstance(item, dict):
            continue
        url, title = item.get("url"), item.get("title")
        if not isinstance(url, str) or not isinstance(title, str):
            continue
        norm = normalize_url(url)
        if norm in published and norm not in seen:
            seen.add(norm)
            out.append({"title": title.strip()[:200], "url": norm})
    return out


def _decline() -> dict:
    return {"answer": constants.DECLINE, "sources": []}


def _fallback() -> dict:
    return {"answer": constants.FALLBACK, "sources": []}


def _parse_reply(text: str) -> tuple[str, object] | None:
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("answer"), str):
        return None
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        return None
    return data["answer"], sources


def handle(
    raw_body: bytes,
    headers: dict[str, str],
    env: dict,
    *,
    now: float | None = None,
    call=None,
    corpus_loader=None,
) -> tuple[int, dict]:
    now = time.monotonic() if now is None else now
    lower = {k.lower(): v for k, v in headers.items()}

    if not access.origin_allowed(lower.get("origin"), lower.get("host"), env.get("VERCEL_ENV")):
        return 403, {"error": "forbidden"}

    try:
        payload = json.loads(raw_body.decode("utf-8"))
        question, history = guardrails.validate(payload)
    except (ValueError, guardrails.BadRequest) as exc:
        logger.info("bad request: %s", getattr(exc, "args", [""])[0] if exc.args else "")
        return 400, {"error": "bad_request"}

    if not guardrails.looks_like_question(question):
        return 200, {"answer": constants.NOT_A_QUESTION, "sources": [], "declined": True}

    if not LIMITER.allow(access.client_key(lower), now):
        return 429, {"error": "rate_limited"}

    joined = "\n".join([t["text"] for t in history] + [question])
    score, reasons = guardrails.injection_score(joined)
    if score >= constants.BLOCK_SCORE:
        kinds = sorted({r.split(":", 1)[0] for r in reasons})
        logger.info("injection blocked score=%d kinds=%s", score, kinds)
        return 200, {"answer": constants.DECLINE, "sources": [], "declined": True}

    loader = corpus_loader or corpus.load
    if not env.get("ASK_CORPUS_DIR") and not env.get("VERCEL_URL") and lower.get("host"):
        # The deployment host serves /ask/ too; this keeps the corpus fetch working
        # when the project does not expose Vercel's system variables.
        env = dict(env, VERCEL_URL=lower["host"])
    try:
        corpus_text, published = loader(env)
    except OSError as exc:
        logger.error("corpus unavailable: %s", exc)
        return 503, {"error": "unavailable"}

    models = (
        env.get("ASK_MODEL") or constants.MODEL,
        env.get("ASK_MODEL_FALLBACK") or constants.MODEL_FALLBACK,
    )
    started = time.monotonic()
    try:
        reply = gemini.ask_model(
            prompt.system_instruction(corpus_text),
            prompt.build_contents(question, history),
            models=models,
            call=call,
        )
    except gemini.MissingKey:
        logger.error("GEMINI_API_KEY is not set")
        return 503, {"error": "unavailable"}
    except gemini.VendorError as exc:
        logger.error("gemini failed on both models: %s", exc)
        return 503, {"error": "unavailable"}
    logger.info("model=%s ms=%d", reply.model, int((time.monotonic() - started) * 1000))

    if reply.text is None:
        return 200, _fallback()
    parsed = _parse_reply(reply.text)
    if parsed is None:
        logger.warning("model reply did not match the schema")
        return 200, _fallback()
    answer, sources = parsed

    answer = guardrails.strip_markup(guardrails.strip_invisible(answer)).strip()
    if guardrails.leaks_prompt(answer, prompt.TEMPLATE):
        logger.warning("prompt leak suppressed")
        return 200, _decline()
    if answer == constants.DECLINE:
        return 200, _decline()
    if not answer:
        return 200, _fallback()
    return 200, {"answer": answer, "sources": validate_sources(sources, published)}
