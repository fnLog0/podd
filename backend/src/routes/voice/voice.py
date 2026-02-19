from fastapi import APIRouter, Depends, File, UploadFile, WebSocket

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/voice", tags=["voice"], dependencies=[Depends(get_current_user)])


@router.post("/stream")
async def voice_stream(file: UploadFile = File(...)):
    return {"message": "not implemented - Saaras STT"}


@router.post("/synthesize")
async def voice_synthesize():
    return {"message": "not implemented - Bulbul TTS"}


@router.post("/conversation")
async def voice_conversation(file: UploadFile = File(...)):
    return {"message": "not implemented - Saaras STT -> LangGraph -> Bulbul TTS"}


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"message": "not implemented - Sarvam real-time voice"})
    await websocket.close()
