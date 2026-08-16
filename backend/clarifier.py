# clarifier.py — the ambiguity rule list + detector (Phase 3)
# Each entry is a tuple: (vague word, hint about what is unclear).
# When a question contains one of these words, the system knows
# it may need to ask a clarifying question before writing SQL.
import re

import llm
import prompts

AMBIGUOUS_WORDS = [
    ("best",     "by total revenue, order count, or average order?"),
    ("top",      "by which metric?"),
    ("recent",   "in the last 7 days, 30 days, or this month?"),
    ("large",    "above what order amount?"),
    ("high",     "above what amount?"),
    ("popular",  "most used, or generating most revenue?"),
    ("frequent", "how many orders counts as frequent?"),
    ("good",     "high spend, or never-cancelled orders?"),
]


def detect_ambiguity(question):
    """Return [(word, hint)] for every ambiguous word in the question.
    Empty list = the question seems clear (no vague words found)."""
    found = []
    for word, hint in AMBIGUOUS_WORDS:
        if re.search(rf"\b{word}\b", question, re.IGNORECASE):
            found.append((word, hint))
    return found


def judge_ambiguity(question):
    """Ask Gemini whether a question is ambiguous. Returns dict:
    {"ambiguous": bool, "reason": str}."""
    reply = llm.ask_json(prompts.build_ambiguity_prompt(question))
    if not isinstance(reply, dict):          # defensive: malformed reply?
        return {"ambiguous": False, "reason": ""}
    return {
        "ambiguous": reply.get("ambiguous", False),
        "reason": reply.get("reason", ""),
    }


def analyze(question):
    """Combined verdict: should we ask the user a clarifying question?
    Fast path: rules find a vague word -> True immediately (no AI call).
    Slow path: rules are clear -> ask Gemini (catches novel phrasing)."""
    rules = detect_ambiguity(question)
    if rules:                                    # fast path: already know
        return {"should_ask": True,
                "reasons": [hint for _, hint in rules]}

    ai = judge_ambiguity(question)               # slow path: deep judge
    reasons = [ai["reason"]] if ai["ambiguous"] and ai["reason"] else []
    return {"should_ask": ai["ambiguous"], "reasons": reasons}