from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"], dependencies=[Depends(get_current_user)])


@router.get("")
async def get_profile():
    return {"message": "not implemented"}


@router.put("")
async def update_profile():
    return {"message": "not implemented"}
