from datetime import datetime, timezone

from src.services.locusgraph.service import locusgraph_service
from src.workflows.state import PoddState


async def store_events(state: PoddState) -> dict:
    pending = list(state.get("pending_events", []))
    user_id = state.get("user_id", "")

    pending.append(
        {
            "event_kind": "observation",
            "context_id": f"chat:{locusgraph_service.new_id()}",
            "related_to": [f"person:{user_id}"],
            "payload": {
                "kind": "conversation_turn",
                "data": {
                    "user_text": state.get("user_text", ""),
                    "assistant_text": state.get("assistant_text", ""),
                    "intent": state.get("intent", "unknown"),
                    "timestamp": locusgraph_service.now(),
                },
            },
        }
    )

    for event in pending:
        await locusgraph_service.store_event(
            event_kind=event["event_kind"],
            payload=event["payload"],
            context_id=event.get("context_id"),
            related_to=event.get("related_to", []),
            extends=event.get("extends", []),
            reinforces=event.get("reinforces", []),
            contradicts=event.get("contradicts", []),
        )

    return {"pending_events": []}
