import os
import secrets
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "BeliMang!"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))
    database_url: str = "sqlite:///./test.db"
    jwt_expiration_minutes: int = 60

    # MinIO configuration
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_secure: bool = False
    minio_bucket: str = "upload"
    minio_public_url: str = "localhost:9001"

    class Config:
        env_file = ".env"


settings = Settings()
