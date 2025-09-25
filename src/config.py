import secrets
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "BeliMang!"
    debug: bool = False
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))
    database_url: str = "sqlite:///./test.db"
    jwt_expiration_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()