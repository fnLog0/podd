from fastapi import APIRouter

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.post("/water/log")
async def create_water_log():
    return {"message": "not implemented"}


@router.get("/water/history")
async def get_water_history():
    return {"message": "not implemented"}


@router.post("/sleep/log")
async def create_sleep_log():
    return {"message": "not implemented"}


@router.get("/sleep/history")
async def get_sleep_history():
    return {"message": "not implemented"}


@router.post("/exercise/log")
async def create_exercise_log():
    return {"message": "not implemented"}


@router.get("/exercise/history")
async def get_exercise_history():
    return {"message": "not implemented"}


@router.post("/mood/log")
async def create_mood_log():
    return {"message": "not implemented"}


@router.get("/mood/history")
async def get_mood_history():
    return {"message": "not implemented"}
