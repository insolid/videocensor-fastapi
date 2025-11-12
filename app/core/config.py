from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings

project_root = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    @computed_field
    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    jwt_secret_key: str
    jwt_expire_minutes: int
    jwt_algorithm: str

    yookassa_account_id: int
    yookassa_secret_key: str

    mail_username: str
    mail_password: str

    video_storage_path: Path = Path("/video-storage")
    yolo_model_path: Path = project_root / "censor-utils" / "gore-smoking-detector.pt"

    ban_words_dir: Path = project_root / "censor-utils" / "ban-words"

    # model_config = SettingsConfigDict(env_file=project_root / ".env")


settings = Settings()  # type: ignore
