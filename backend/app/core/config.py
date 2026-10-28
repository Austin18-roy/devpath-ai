from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "DevPath AI Backend"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # RepoMind scan boundaries and security
    MAX_SCAN_FILES: int = 1000
    MAX_FILE_SIZE_BYTES: int = 1_000_000  # 1 MB
    ALLOWED_REPO_ROOTS: Union[List[str], str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v]
        return v

    @field_validator("ALLOWED_REPO_ROOTS", mode="before")
    @classmethod
    def assemble_allowed_roots(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [root.strip() for root in v.split(",") if root.strip()]
        elif isinstance(v, list):
            return [str(root).strip() for root in v]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
