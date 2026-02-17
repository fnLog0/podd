from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # CORS settings
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./podd_auth.db")
    
    # JWT settings
    SECRET_KEY: str = Field(default="b74QV2qleLyS5/+mKXpHJKh62aEGZVK82VXR8wkwkcU=")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    JWT_EXPIRATION_MINUTES: int = Field(default=60)
    
    class Config:
        env_file = ".env"

settings = Settings()