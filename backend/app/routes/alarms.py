from fastapi import APIRouter

router = APIRouter(tags=["alarms"])


@router.post("/alarms")
async def create_alarm():
    return {"message": "not implemented"}


@router.get("/alarms")
async def get_alarms():
    return {"message": "not implemented"}


@router.put("/alarms/{alarm_id}")
async def update_alarm(alarm_id: str):
    return {"message": "not implemented"}


@router.delete("/alarms/{alarm_id}")
async def delete_alarm(alarm_id: str):
    return {"message": "not implemented"}


@router.get("/notifications")
async def get_notifications():
    return {"message": "not implemented"}


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    return {"message": "not implemented"}
