from langchain_core.messages import SystemMessage, HumanMessage

from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState
from src.workflows.llm import llm, SYSTEM_BASE, _format_memories

SYSTEM_PROMPT = (
    f"{SYSTEM_BASE}\n\n"
    "You are handling a general conversation. Be helpful, empathetic, and "
    "guide the user toward health-related features you offer: food tracking, "
    "medication tracking, health queries, and recommendations."
)


async def agent_general_chat(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    user_text = state.get("user_text", "")
    lg_context = state.get("lg_context", {})
    memories = lg_context.get("memories", [])
    record_id = locusgraph_service.new_id()

    context_block = _format_memories(memories)
    messages = [
        SystemMessage(content=f"{SYSTEM_PROMPT}\n\nUser context:\n{context_block}"),
        HumanMessage(content=user_text),
    ]
    response = await llm.ainvoke(messages)

    pending = list(state.get("pending_events", []))
    pending.append(
        {
            "event_kind": "observation",
            "context_id": f"chat:{record_id}",
            "related_to": [f"person:{user_id}"],
            "payload": {
                "kind": "general_chat",
                "data": {
                    "user_text": user_text,
                    "record_id": record_id,
                    "timestamp": locusgraph_service.now(),
                },
            },
        }
    )

    return {
        "pending_events": pending,
        "assistant_text": response.content,
    }
