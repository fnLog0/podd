from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState


def agent_medication(state: PoddState) -> dict:
    user_id = state.get("user_id", "")
    user_text = state.get("user_text", "")
    record_id = locusgraph_service.new_id()

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
        "assistant_text": f"Noted your medication: {user_text}",
        "med_parse": {"raw_text": user_text, "record_id": record_id},
    }
