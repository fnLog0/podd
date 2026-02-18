from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # CORS settings
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])

    # Database settings
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./podd_auth.db")

    # JWT settings
    JWT_SECRET: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_MINUTES: int = Field(default=60)
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7)

    # LocusGraph settings
    LOCUSGRAPH_API_KEY: str = Field(default="")
    LOCUSGRAPH_GRAPH_ID: str = Field(default="podd_health")

    # OpenAI settings
    OPENAI_API_KEY: str = Field(default="")

    # Sarvam settings
    SARVAM_API_KEY: str = Field(default="")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()