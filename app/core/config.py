from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

root = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn

    jwt_secret_key: str
    jwt_expire_minutes: int
    jwt_algorithm: str

    yookassa_account_id: int
    yookassa_secret_key: str

    video_storage_path: Path = root / "storage"

    model_config = SettingsConfigDict(env_file=root / ".env")


settings = Settings()  # type: ignore
