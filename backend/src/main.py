from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import create_tables
from src.models import RefreshToken, User  # noqa: F401 - register models for create_all
from src.routes import (
    alarms,
    appointments,
    auth,
    chat,
    emergency,
    health,
    medication,
    meditation,
    profile,
    tracking,
    voice,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title="Podd Health Assistant", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(medication.router, prefix="/api")
app.include_router(tracking.router, prefix="/api")
app.include_router(meditation.router, prefix="/api")
app.include_router(alarms.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(emergency.router, prefix="/api")


@app.get("/")
async def root():
    return {"name": "Podd Health Assistant", "version": "0.1.0"}
