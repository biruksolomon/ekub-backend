from typing import List, Union
from pydantic import validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Ekub Backend"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "supersecretjwtkey_change_me_in_production_1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ekub_db"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./ekub.db"

    @validator("DATABASE_URL", pre=True, always=True)
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str) and v.strip():
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            return v
        return "sqlite+aiosqlite:///./ekub.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
