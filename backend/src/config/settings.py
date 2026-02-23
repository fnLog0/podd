from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Backend project root (backend/)
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # CORS settings
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    # Database settings (default: SQLite in backend directory)
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{_BACKEND_DIR / 'podd_auth.db'}"
    )

    # JWT settings
    JWT_SECRET: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_MINUTES: int = Field(default=1440)  # 24 hours for development
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7)

    # LocusGraph settings
    LOCUSGRAPH_SERVER_URL: str = Field(default="https://api-dev.locusgraph.com")
    LOCUSGRAPH_AGENT_SECRET: str = Field(default="")
    LOCUSGRAPH_GRAPH_ID: str = Field(default="")
    USE_LOCUSGRAPH_MOCK: bool = Field(
        default=False, description="Use mock LocusGraph in development"
    )

    # OpenAI settings
    OPENAI_API_KEY: str = Field(default="")

    # Sarvam settings
    SARVAM_API_KEY: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
    )


settings = Settings()
