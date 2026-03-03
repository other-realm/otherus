"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
import os
load_dotenv('../.env')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "Other Us"
    app_env: str = "development"
    secret_key: str
    frontend_url: str = "http://localhost:8080"

    # Google OAuth
    google_client_id: str =os.getenv('GOOGLE_CLIENT_ID') # pyright: ignore[reportAssignmentType]
    google_client_secret: str =os.getenv('GOOGLE_CLIENT_SECRET') # pyright: ignore[reportAssignmentType]
    google_redirect_uri: str = os.getenv('GOOGLE_REDIRECT_URI') # pyright: ignore[reportAssignmentType]
    google_server_metadata_url: str = "https://accounts.google.com/.well-known/openid-configuration"

    # GitHub OAuth
    github_client_id: str =os.getenv('CLIENT_ID') # pyright: ignore[reportAssignmentType]
    github_client_secret: str = os.getenv('CLIENT_SECRET') # pyright: ignore[reportAssignmentType]

    # Redis
    redis_url: str = os.getenv('REDIS_URL') # type: ignore
    redis_password: str = os.getenv('REDIS_PASSWORD') # type: ignore
    redis_username: str = 'admin' 
    # RabbitMQ
    rabbitmq_url: str = os.getenv("RABBITMQ_URL") # type: ignore

    # ntfy.sh
    ntfy_base_url: str = "http://10.0.0.90:8765"
    ntfy_topic_prefix: str = "other-us"

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440


@lru_cache
def get_settings() -> Settings:
    return Settings()
