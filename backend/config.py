from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/spaceeye"
    redis_url: str = "redis://localhost:6379/0"
    email_inpe: str = ""
    temp_dir: str = "/tmp/spaceeye"
    cache_ttl_days: int = 7
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
