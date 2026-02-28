from typing import TypedDict, Literal, Optional, Any

Intent = Literal[
    "food_tracking",
    "medication",
    "health_query",
    "recommendation",
    "general_chat",
    "unknown",
]


class PoddState(TypedDict, total=False):
    user_id: str
    locale: str
    channel: Literal["text", "voice"]
    user_text: str
    normalized_text: str
    intent: Intent
    context_query: str
    context_ids: list[str]
    lg_context: dict[str, Any]
    pending_events: list[dict[str, Any]]
    assistant_text: str
    food_parse: Optional[dict[str, Any]]
    med_parse: Optional[dict[str, Any]]
    flags: dict[str, Any]
    errors: list[str]
