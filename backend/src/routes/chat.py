from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat():
    return {"message": "not implemented"}


@router.get("/history")
async def chat_history():
    return {"message": "not implemented"}
