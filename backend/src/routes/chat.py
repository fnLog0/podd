from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])


@router.post("")
async def chat():
    return {"message": "not implemented"}


@router.get("/history")
async def chat_history():
    return {"message": "not implemented"}
