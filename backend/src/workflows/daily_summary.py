from datetime import datetime, timezone


async def generate_daily_summary(user_id: str) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()

    summary_event = {
        "event_kind": "observation",
        "payload": {
            "kind": "health_summary",
            "data": {
                "user_id": user_id,
                "summary": "Daily health summary placeholder.",
                "timestamp": timestamp,
            },
        },
    }

    return {
        "user_id": user_id,
        "summary": summary_event,
        "generated_at": timestamp,
    }
