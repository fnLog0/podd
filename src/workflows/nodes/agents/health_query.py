from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState


def agent_health_query(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    user_text = state.get("user_text", "")
    lg_context = state.get("lg_context", {})
    memories = lg_context.get("memories", [])

    record_id = locusgraph_service.new_id()

    pending = list(state.get("pending_events", []))
    pending.append(
        {
            "event_kind": "observation",
            "context_id": f"health_query:{record_id}",
            "related_to": [f"person:{user_id}", "vital:general"],
            "payload": {
                "kind": "health_query",
                "data": {
                    "query": user_text,
                    "context_used": len(memories),
                    "record_id": record_id,
                    "timestamp": locusgraph_service.now(),
                },
            },
        }
    )

    return {
        "pending_events": pending,
        "assistant_text": f"Based on your health records, here's what I found about: {user_text}",
    }
