from src.workflows.state import PoddState


def format_response(state: PoddState) -> dict:
    text = state.get("assistant_text", "")
    locale = state.get("locale", "en-IN")

    if locale == "hi-IN" and text and not _contains_hindi(text):
        text = f"[hi-IN] {text}"

    return {"assistant_text": text}


def _contains_hindi(text: str) -> bool:
    return any("\u0900" <= ch <= "\u097f" for ch in text)
