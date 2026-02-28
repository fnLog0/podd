from langchain_core.messages import SystemMessage, HumanMessage

from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState
from src.workflows.llm import llm, SYSTEM_BASE, _format_memories

SYSTEM_PROMPT = (
    f"{SYSTEM_BASE}\n\n"
    "The user is logging medication intake. "
    "Confirm the medication was noted, remind them about dosage consistency, "
    "and encourage them to keep tracking. "
    "Never provide medical dosage advice — only acknowledge what they report."
)


async def agent_medication(state: PoddState) -> dict:
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
            "event_kind": "action",
            "context_id": f"medication_log:{record_id}",
            "related_to": [f"person:{user_id}", "medication:general"],
            "reinforces": ["recommendation:medication_adherence"],
            "payload": {
                "kind": "medication_taken",
                "data": {
                    "raw_text": user_text,
                    "record_id": record_id,
                    "timestamp": locusgraph_service.now(),
                },
            },
        }
    )

    return {
        "pending_events": pending,
        "assistant_text": response.content,
        "med_parse": {"raw_text": user_text, "record_id": record_id},
    }
