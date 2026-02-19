from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/appointments", tags=["appointments"], dependencies=[Depends(get_current_user)])


@router.post("")
async def create_appointment():
    return {"message": "not implemented"}


@router.get("")
async def get_appointments():
    return {"message": "not implemented"}


@router.put("/{appointment_id}")
async def update_appointment(appointment_id: str):
    return {"message": "not implemented"}
