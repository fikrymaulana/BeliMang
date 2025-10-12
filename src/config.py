import os
import secrets
import logging

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Configure logging
logger = logging.getLogger(__name__)

# Check if we're in Kubernetes by looking for Kubernetes service environment variables
is_kubernetes = any(key in os.environ for key in [
    'DATABASE_URL', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB'
])

logger.info(f"Raw DATABASE_URL env var: {os.getenv('DATABASE_URL')}")
logger.info(f"is_kubernetes: {is_kubernetes}")

if not is_kubernetes:
    logger.info("Loading .env file for local development")
    load_dotenv()
else:
    logger.info("Kubernetes environment detected, using environment variables")
    # Check if .env file exists (created during deployment)
    if os.path.exists('.env'):
        logger.info(".env file found - created during deployment for compatibility")
        logger.info("But using environment variables as priority")


class Settings(BaseSettings):
    app_name: str = "BeliMang!"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))

    # Prioritize Kubernetes environment variables over .env file
    database_url: str = os.getenv(
        "DATABASE_URL"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate configuration after initialization
        self._validate_configuration()
    jwt_expiration_minutes: int = 60

    # MinIO configuration - prioritize environment variables
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    minio_secure: bool = os.getenv("MINIO_SECURE", "False").lower() in ("true", "1")
    minio_bucket: str = os.getenv("MINIO_BUCKET", "upload")
    minio_public_url: str = os.getenv("MINIO_PUBLIC_URL", "localhost:9001")

    class Config:
        # Only use .env file for local development
        env_file = ".env" if not is_kubernetes else None


    def _validate_configuration(self):
        """Validate that the configuration is appropriate for the environment."""
        if not self.database_url.startswith("postgresql://") and not self.database_url.startswith("postgresql+asyncpg://"):
            logger.error("Database URL must be PostgreSQL!")
            logger.error(f"Current DATABASE_URL: {self.database_url}")
            logger.error("Make sure DATABASE_URL environment variable points to PostgreSQL")
        elif is_kubernetes and not self.database_url.startswith("postgresql://postgres-service"):
            logger.warning(f"Database URL doesn't point to Kubernetes service: {self.database_url}")
            logger.info("Expected format: postgresql://username:password@postgres-service:5432/database")


settings = Settings()

# Log configuration for debugging
logger.info("=== Configuration Loaded ===")
logger.info(f"Environment: {'Kubernetes' if is_kubernetes else 'Local Development'}")
logger.info(f"App Name: {settings.app_name}")
logger.info(f"Debug Mode: {settings.debug}")
logger.info(f"Database URL: {settings.database_url}")
logger.info(f"JWT Expiration: {settings.jwt_expiration_minutes} minutes")
logger.info(f"MinIO Endpoint: {settings.minio_endpoint}")
logger.info(f"MinIO Access Key: {settings.minio_access_key}")
logger.info(f"MinIO Bucket: {settings.minio_bucket}")
logger.info(f"MinIO Public URL: {settings.minio_public_url}")

# Show which configuration sources are being used
if is_kubernetes:
    logger.info("Configuration Sources: Kubernetes Environment Variables")
    if os.path.exists('.env'):
        logger.info("Note: .env file exists (created during deployment) but environment variables take priority")
else:
    logger.info("Configuration Sources: .env file")

logger.info("=== Configuration Complete ===")
