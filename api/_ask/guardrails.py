"""Guardrails that run around the model: input validation, the pre-model
injection detector, and post-model cleaning.

Adapted from the simpul-desa `src/chat/guardrails.py`; the number
provenance check is left out because this corpus is prose.
"""

from __future__ import annotations

import base64
import re
from collections import Counter

from _ask import constants


class BadRequest(ValueError):
    """The request fails validation. The message is a short code, never user text."""


# --- Input validation ---------------------------------------------------------

_ROLES = {"user", "model"}


def validate(payload: object) -> tuple[str, list[dict]]:
    if not isinstance(payload, dict):
        raise BadRequest("not_an_object")
    question = payload.get("question")
    if not isinstance(question, str):
        raise BadRequest("question_missing")
    question = question.strip()
    if not question:
        raise BadRequest("question_empty")
    if len(question) > constants.MAX_QUESTION:
        raise BadRequest("question_too_long")
    history = payload.get("history", [])
    if not isinstance(history, list):
        raise BadRequest("history_not_a_list")
    if len(history) > constants.MAX_HISTORY:
        raise BadRequest("history_too_long")
    clean: list[dict] = []
    for turn in history:
        if not isinstance(turn, dict):
            raise BadRequest("turn_not_an_object")
        role, text = turn.get("role"), turn.get("text")
        if role not in _ROLES or not isinstance(text, str):
            raise BadRequest("turn_invalid")
        if len(text) > constants.MAX_TURN:
            raise BadRequest("turn_too_long")
        clean.append({"role": role, "text": text})
    return question, clean


# --- Question-likeness (before the model) ---------------------------------------

_GREETINGS = {
    "hi", "hello", "hey", "halo", "hai", "hallo", "tes", "test", "testing", "ok", "oke",
    "okay", "thanks", "thank", "makasih", "terima", "kasih", "ping", "yo", "p", "cek",
    "check", "coba", "woi", "woy", "bro", "sis", "min", "admin",
}
_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def looks_like_question(text: str) -> bool:
    """A cheap gate so "tes", "halo" or "???" never reach the model.

    Passes anything with two or more alphabetic words that is not only
    greetings or test words, and any single word that ends with a question
    mark (a term lookup such as "Verifier?"). Everything else is handled with
    a fixed sentence, which costs no quota and cannot fail.
    """
    words = [w.lower() for w in _WORD.findall(text)]
    if not words:
        return False
    if all(w in _GREETINGS for w in words):
        return False
    if len(words) >= 2:
        return True
    return text.rstrip().endswith("?")


# --- Injection detection (before the model) -----------------------------------

_INVISIBLE = re.compile(
    "[­​-‏﻿‪-‮⁠-⁩\U000e0000-\U000e007f]"
)
_SPACED_LETTERS = re.compile(r"\b(?:[A-Za-z][ \t]){2,}[A-Za-z]\b")

_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"abaikan\s+(semua\s+|seluruh\s+)?(instruksi|perintah|aturan)", re.I),
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|rules?|prompts?)", re.I),
    re.compile(r"(mode|modus)\s+developer|developer\s+mode", re.I),
    re.compile(r"system\s+override|new\s+instructions?\s*:", re.I),
    re.compile(
        r"(bocorkan|tuliskan|tunjukkan|reveal|print|show|repeat|output).{0,30}"
        r"(system\s*prompt|instruksi\s+sistem|system\s+instructions?)",
        re.I,
    ),
    re.compile(
        r"you\s+are\s+now\s+(a|an|the)?\s*(?!ask\s+idctf)"
        r"(ai\b|bot\b|chatbot|assistant|advisor|expert|model|agent|persona|character|hacker|doctor|judge)",
        re.I,
    ),
    re.compile(
        r"kamu\s+sekarang\s+(?:adalah\s+)?(?:seorang\s+|sebuah\s+)?"
        r"(ai\b|bot\b|chatbot|asisten|penasihat|pakar|ahli|model|agen|persona|karakter|hacker)",
        re.I,
    ),
    re.compile(r"do\s+anything\s+now|tanpa\s+(batasan|filter|sensor)\s+apa\s*pun", re.I),
]

_FUZZY_WORDS = ["abaikan", "instruksi", "ignore", "bypass", "override", "reveal", "jailbreak", "prompt", "instructions"]
_COMPACT_PHRASES = [
    "abaikansemuainstruksi",
    "abaikaninstruksisebelumnya",
    "ignoreallpreviousinstructions",
    "ignorepreviousinstructions",
]
_NON_LETTER = re.compile(r"[^a-z]+")
_BASE64_TOKEN = re.compile(r"[A-Za-z0-9+/=]{16,}")
_HEX_TOKEN = re.compile(r"[0-9a-fA-F]{20,}")


def strip_invisible(text: str) -> str:
    return _INVISIBLE.sub("", text)


def _collapse_spaced(text: str) -> str:
    return _SPACED_LETTERS.sub(lambda m: re.sub(r"[ \t]", "", m.group(0)), text)


def _score_patterns(target: str, label: str) -> tuple[int, list[str]]:
    score, reasons = 0, []
    for pattern in _PATTERNS:
        if pattern.search(target):
            score += 2
            reasons.append(f"{label}:{pattern.pattern[:30]}")
    return score, reasons


def _looks_like(word: str, ref: str) -> bool:
    """Typoglycemia: same first and last letter, middle letters shuffled, one letter off at most."""
    if word == ref:
        return True
    if len(word) < 4 or abs(len(word) - len(ref)) > 1:
        return False
    if word[0] != ref[0] or word[-1] != ref[-1]:
        return False
    a, b = Counter(word[1:-1]), Counter(ref[1:-1])
    return sum((a - b).values()) + sum((b - a).values()) <= 1


def _decode_base64(token: str) -> str | None:
    for candidate in (token, token + "=" * (-len(token) % 4)):
        try:
            return base64.b64decode(candidate, validate=True).decode("utf-8", errors="ignore")
        except ValueError:
            continue
    return None


def _decode_hex(token: str) -> list[str]:
    candidates = [token] if len(token) % 2 == 0 else [token[:-1], token[1:]]
    out = []
    for c in candidates:
        try:
            out.append(bytes.fromhex(c).decode("utf-8", errors="ignore"))
        except ValueError:
            continue
    return out


def injection_score(text: str) -> tuple[int, list[str]]:
    """Risk score and reasons (for the log, never for the user)."""
    visible = strip_invisible(text)
    normalized = re.sub(r"\s{2,}", " ", visible)
    score, reasons = _score_patterns(normalized, "main")

    collapsed = _collapse_spaced(visible)
    if collapsed != visible:
        s, r = _score_patterns(collapsed, "spaced")
        score, reasons = score + s, reasons + r

    compact = _NON_LETTER.sub("", visible.lower())
    for phrase in _COMPACT_PHRASES:
        if phrase in compact:
            score += 2
            reasons.append(f"compact:{phrase}")
            break

    exact: set[str] = set()
    fuzzy: set[str] = set()
    for token in re.findall(r"[A-Za-z]+", normalized):
        low = token.lower()
        for word in _FUZZY_WORDS:
            if low == word:
                exact.add(word)
                break
            if _looks_like(low, word):
                fuzzy.add(word)
                reasons.append(f"fuzzy:{word}~{token}")
                break
    score += len(fuzzy)
    if exact:
        score += 1
        reasons.append("exact:" + ",".join(sorted(exact)))

    for m in _BASE64_TOKEN.finditer(normalized):
        decoded = _decode_base64(m.group(0))
        if decoded:
            s, r = _score_patterns(decoded, "base64")
            score, reasons = score + s, reasons + r
    for m in _HEX_TOKEN.finditer(normalized):
        for decoded in _decode_hex(m.group(0)):
            s, r = _score_patterns(decoded, "hex")
            score, reasons = score + s, reasons + r
            if s:
                break
    return score, reasons


# --- Output cleaning (after the model) ----------------------------------------

_MD_MARKERS = re.compile(r"[#*_`>~]")
_IMG_HTML = re.compile(r"<img[^>]*>", re.I)
_HTML_TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^>]*)?/?>")
_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_BARE_URL = re.compile(r"\b\w+://\S+|\bwww\.\S+", re.I)
_MIN_LEAK_LINE = 30


def strip_markup(answer: str) -> str:
    """Links belong in `sources`, never in the prose: drop every path out."""
    out = _IMG_HTML.sub("", answer)
    out = _MD_IMAGE.sub("", out)
    out = _MD_LINK.sub(r"\1", out)
    out = _HTML_TAG.sub("", out)
    out = _BARE_URL.sub("", out)
    return out


def leaks_prompt(answer: str, template: str) -> bool:
    """True when a template line of 30+ characters appears verbatim in the answer."""
    folded = _collapse_spaced(_MD_MARKERS.sub("", answer))
    folded = re.sub(r"\s+", " ", folded).strip().lower()
    for line in template.splitlines():
        clean = re.sub(r"\s+", " ", _MD_MARKERS.sub("", line)).strip().lower()
        clean = clean.rstrip(".,;:!?")
        if len(clean) >= _MIN_LEAK_LINE and clean in folded:
            return True
    return False
