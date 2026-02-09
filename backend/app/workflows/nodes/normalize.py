import re

from app.workflows.state import PoddState

HINDI_UNIT_MAP = {
    "मिलीलीटर": "ml",
    "मिलीग्राम": "mg",
    "ग्राम": "grams",
    "एमएल": "ml",
    "एमजी": "mg",
    "लीटर": "liters",
    "किलो": "kg",
    "चम्मच": "tsp",
}

FILLER_WORDS = {
    "um", "uh", "like", "you know", "so", "well", "actually",
    "basically", "hmm", "ok so", "acha", "haan", "toh",
}


def normalize_input(state: PoddState) -> dict:
    text = state.get("user_text", "").strip()

    for hindi, eng in HINDI_UNIT_MAP.items():
        text = text.replace(hindi, eng)

    pattern = r"\b(" + "|".join(re.escape(w) for w in FILLER_WORDS) + r")\b"
    text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    return {"user_text": text}
