from src.services.locusgraph_service import locusgraph_service
from src.workflows.state import PoddState


def agent_recommendation(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    user_text = state.get("user_text", "")
    record_id = locusgraph_service.new_id()

    pending = list(state.get("pending_events", []))
    pending.append({
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
    })

    return {
        "pending_events": pending,
        "assistant_text": f"Here are some recommendations based on your profile: {user_text}",
    }
