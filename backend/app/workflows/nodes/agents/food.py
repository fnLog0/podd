from app.services.locusgraph_service import locusgraph_service
from app.workflows.state import PoddState


def agent_food_tracking(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    user_text = state.get("user_text", "")
    record_id = locusgraph_service.new_id()

    pending = list(state.get("pending_events", []))
    pending.append({
        "event_kind": "observation",
        "context_id": f"food:{record_id}",
        "related_to": [f"person:{user_id}", "vital:nutrition"],
        "payload": {
            "kind": "food_intake",
            "data": {
                "raw_text": user_text,
                "record_id": record_id,
                "timestamp": locusgraph_service.now(),
            },
        },
    })

    return {
        "pending_events": pending,
        "assistant_text": f"Got it! I've logged your food: {user_text}",
        "food_parse": {"raw_text": user_text, "record_id": record_id},
    }
