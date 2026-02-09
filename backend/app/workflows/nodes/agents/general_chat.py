from app.services.locusgraph_service import locusgraph_service
from app.workflows.state import PoddState


def agent_general_chat(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    record_id = locusgraph_service.new_id()

    pending = list(state.get("pending_events", []))
    pending.append({
        "event_kind": "observation",
        "context_id": f"chat:{record_id}",
        "related_to": [f"person:{user_id}"],
        "payload": {
            "kind": "general_chat",
            "data": {
                "user_text": state.get("user_text", ""),
                "record_id": record_id,
                "timestamp": locusgraph_service.now(),
            },
        },
    })

    return {
        "pending_events": pending,
        "assistant_text": (
            "I'm Podd, your health assistant! "
            "I can help you track food, medications, and answer health questions."
        ),
    }
