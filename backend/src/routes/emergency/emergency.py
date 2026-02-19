from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/emergency-contacts", tags=["emergency"], dependencies=[Depends(get_current_user)])


@router.post("")
async def create_emergency_contact():
    return {"message": "not implemented"}


@router.get("")
async def get_emergency_contacts():
    return {"message": "not implemented"}
