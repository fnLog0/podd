from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile():
    return {"message": "not implemented"}


@router.put("")
async def update_profile():
    return {"message": "not implemented"}
