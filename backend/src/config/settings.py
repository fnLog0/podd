from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./podd_auth.db"
    )

    # JWT settings
    JWT_SECRET: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_MINUTES: int = Field(default=60)
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
