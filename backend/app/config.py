"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load .env if it exists
load_dotenv('.env')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "Other Us"
    app_env: str = "development"
    secret_key: str = os.getenv("SECRET_KEY", "default_secret_key_for_dev_only")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:8765")

    # Google OAuth
    google_client_id: str = os.getenv('GOOGLE_CLIENT_ID', "mock_google_id")
    google_client_secret: str = os.getenv('GOOGLE_CLIENT_SECRET', "mock_google_secret")
    google_redirect_uri: str = os.getenv('GOOGLE_REDIRECT_URI', "http://localhost:8765/auth")
    google_server_metadata_url: str = "https://accounts.google.com/.well-known/openid-configuration"

    # GitHub OAuth
    github_client_id: str = os.getenv('GITHUB_CLIENT_ID', "mock_github_id")
    github_client_secret: str = os.getenv('GITHUB_CLIENT_SECRET', "mock_github_secret")
    github_redirect_uri: str = os.getenv('GITHUB_REDIRECT_URI', "http://localhost:8765/auth")

    # Redis
    redis_url: str = os.getenv('REDIS_URL', "redis://localhost:6379")
    redis_password: str = os.getenv('REDIS_PASSWORD', "")
    redis_username: str = 'admin' 
    
    # RabbitMQ
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    # ntfy.sh
    ntfy_base_url: str = os.getenv("NTFY_BASE_URL", "https://ntfy.sh")
    ntfy_topic_prefix: str = os.getenv("NTFY_TOPIC_PREFIX", "other-us")

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440


@lru_cache
def get_settings() -> Settings:
    return Settings()
