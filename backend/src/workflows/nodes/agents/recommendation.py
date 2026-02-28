from langchain_core.messages import SystemMessage, HumanMessage

from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState
from src.workflows.llm import llm, SYSTEM_BASE, _format_memories

SYSTEM_PROMPT = (
    f"{SYSTEM_BASE}\n\n"
    "The user is asking for health or lifestyle recommendations. "
    "Use their past context (diet, medication, vitals) to tailor suggestions. "
    "Keep recommendations actionable and practical. "
    "Always remind them to verify with their healthcare provider."
)


async def agent_recommendation(state: PoddState) -> dict:
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
            "event_kind": "decision",
            "context_id": f"recommendation:{record_id}",
            "related_to": [f"person:{user_id}", "recommendation:general"],
            "payload": {
                "kind": "clinical_recommendation",
                "data": {
                    "query": user_text,
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
