from langchain_core.messages import SystemMessage, HumanMessage

from src.workflows.state import PoddState, Intent
from src.workflows.llm import llm

INTENT_SYSTEM_PROMPT = """\
You are an intent classifier for a health assistant app called Podd.

Given a user message, classify it into exactly ONE of these intents:
- food_tracking: user is logging, mentioning, or asking about food they ate/will eat
- medication: user is logging, mentioning, or asking about medicines/tablets/prescriptions
- health_query: user is asking about health metrics, vitals, symptoms, or diagnosis
- recommendation: user is asking for suggestions, advice, recipes, or "what should I do/eat"
- general_chat: greetings, small talk, or anything that doesn't fit the above

Respond with ONLY the intent name, nothing else. No punctuation, no explanation.

Examples:
- "I ate 2 roti and dal" -> food_tracking
- "took my BP medicine" -> medication
- "what is my blood pressure trend" -> health_query
- "suggest a healthy breakfast" -> recommendation
- "hello how are you" -> general_chat
- "maine dawai kha li" -> medication
- "kya khau aaj" -> recommendation
- "mera weight kitna hai" -> health_query
"""

VALID_INTENTS: set[str] = {
    "food_tracking",
    "medication",
    "health_query",
    "recommendation",
    "general_chat",
}


async def router_intent(state: PoddState) -> dict:
    text = state.get("user_text", "")

    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=text),
    ]
    response = await llm.ainvoke(messages)
    raw = response.content.strip().lower()

    intent: Intent = raw if raw in VALID_INTENTS else "general_chat"
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
