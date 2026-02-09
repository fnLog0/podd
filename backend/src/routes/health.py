from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/health", tags=["health"], dependencies=[Depends(get_current_user)])


@router.get("/food/logs")
async def get_food_logs():
    return {"message": "not implemented"}


@router.post("/food/log")
async def create_food_log():
    return {"message": "not implemented"}


@router.get("/vitals")
async def get_vitals():
    return {"message": "not implemented"}


@router.post("/vitals")
async def create_vitals():
    return {"message": "not implemented"}


@router.get("/recommendations")
async def get_recommendations():
    return {"message": "not implemented"}


@router.get("/insights")
async def get_insights():
    return {"message": "not implemented"}
