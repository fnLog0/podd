from fastapi import APIRouter

router = APIRouter(prefix="/medication", tags=["medication"])


@router.post("/log")
async def create_medication_log():
    return {"message": "not implemented"}


@router.get("/schedule")
async def get_medication_schedule():
    return {"message": "not implemented"}


@router.post("/schedule")
async def create_medication_schedule():
    return {"message": "not implemented"}
