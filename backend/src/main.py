from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Standard imports using the 'src' prefix
from src.config import settings
from src.database import create_tables
from src.models import RefreshToken, User
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
    voice,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts and creates the DB tables
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

# API Routes
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(health.health_router, prefix="/api")
app.include_router(medication.medication_router, prefix="/api")
app.include_router(medication.medication_schedule_router, prefix="/api")
app.include_router(health.food_log_router, prefix="/api")
app.include_router(health.vitals_router, prefix="/api")
app.include_router(health.tracking_router, prefix="/api")
app.include_router(meditation.router, prefix="/api")
app.include_router(alarms.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(emergency.router, prefix="/api")


@app.get("/")
async def root():
    return {"name": "Podd Health Assistant", "version": "0.1.0"}
