from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/medication", tags=["medication"], dependencies=[Depends(get_current_user)])


@router.post("/log")
async def create_medication_log():
    return {"message": "not implemented"}


@router.get("/schedule")
async def get_medication_schedule():
    return {"message": "not implemented"}


@router.post("/schedule")
async def create_medication_schedule():
    return {"message": "not implemented"}
