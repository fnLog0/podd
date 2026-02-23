import re

from src.workflows.state import PoddState, Intent

FOOD_KEYWORDS = {
    "khana",
    "roti",
    "chawal",
    "eaten",
    "ate",
    "breakfast",
    "lunch",
    "dinner",
    "food",
    "meal",
}

MED_KEYWORDS = {
    "medicine",
    "dawai",
    "tablet",
    "goli",
    "prescription",
}

HEALTH_KEYWORDS = {
    "blood pressure",
    "sugar",
    "bp",
    "weight",
    "symptoms",
    "diagnosis",
}

RECOMMENDATION_KEYWORDS = {
    "suggest",
    "recommend",
    "recipe",
    "kya khau",
    "what should i eat",
}


def _match_keywords(text: str, keywords: set[str]) -> bool:
    lower = text.lower()
    return any(re.search(r"\b" + re.escape(k) + r"\b", lower) for k in keywords)


def router_intent(state: PoddState) -> dict:
    text = state.get("user_text", "")
    intent: Intent

    if _match_keywords(text, RECOMMENDATION_KEYWORDS):
        intent = "recommendation"
    elif _match_keywords(text, HEALTH_KEYWORDS):
        intent = "health_query"
    elif _match_keywords(text, MED_KEYWORDS):
        intent = "medication"
    elif _match_keywords(text, FOOD_KEYWORDS):
        intent = "food_tracking"
    else:
        intent = "general_chat"

    return {"intent": intent}


def route_to_agent(state: PoddState) -> str:
    intent = state.get("intent", "general_chat")
    mapping = {
        "food_tracking": "agent_food_tracking",
        "medication": "agent_medication",
        "health_query": "agent_health_query",
        "recommendation": "agent_recommendation",
        "general_chat": "agent_general_chat",
        "unknown": "agent_general_chat",
    }
    return mapping.get(intent, "agent_general_chat")
