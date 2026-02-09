from fastapi import APIRouter

router = APIRouter(prefix="/meditation", tags=["meditation"])


@router.get("/sessions")
async def get_sessions():
    return {"message": "not implemented"}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return {"message": "not implemented"}


@router.post("/log")
async def create_meditation_log():
    return {"message": "not implemented"}


@router.get("/history")
async def get_meditation_history():
    return {"message": "not implemented"}
