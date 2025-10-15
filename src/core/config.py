from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file_path = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn

    jwt_secret_key: str
    jwt_expire_minutes: int
    jwt_algorithm: str

    model_config = SettingsConfigDict(env_file=env_file_path)


settings = Settings()  # type: ignore
