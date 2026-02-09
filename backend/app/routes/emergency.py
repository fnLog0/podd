from fastapi import APIRouter

router = APIRouter(prefix="/emergency-contacts", tags=["emergency"])


@router.post("")
async def create_emergency_contact():
    return {"message": "not implemented"}


@router.get("")
async def get_emergency_contacts():
    return {"message": "not implemented"}
