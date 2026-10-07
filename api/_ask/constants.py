"""Fixed sentences and limits for Ask IDCTF.

DECLINE is injected into the prompt and matched by scripts/eval_ask.py, so
the model's refusals and the checker agree. Change it here and nowhere else.
"""

from typing import Final

DECLINE: Final[str] = (
    "I can only answer questions about the IDCTF documentation on this site."
)
FALLBACK: Final[str] = "I could not answer that. Try rewording the question."

MAX_QUESTION: Final[int] = 1000
MAX_HISTORY: Final[int] = 10
MAX_TURN: Final[int] = 2000
MAX_BODY: Final[int] = 64 * 1024

# injection_score at or above this returns DECLINE without calling the model.
BLOCK_SCORE: Final[int] = 2

RATE_LIMIT: Final[int] = 20
RATE_WINDOW_SECONDS: Final[int] = 600

TEMPERATURE: Final[float] = 0.2
GEMINI_TIMEOUT_SECONDS: Final[int] = 25

MODEL: Final[str] = "gemini-flash-latest"
MODEL_FALLBACK: Final[str] = "gemini-flash-lite-latest"
