import enum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Status(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Language(str, enum.Enum):
    EN = "en"
    RU = "ru"


class VideoJob(Base):
    __tablename__ = "videojob"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column()
    size: Mapped[float | None] = mapped_column()
    language: Mapped[Language] = mapped_column(Enum(Language))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING.value)
    input_video_path: Mapped[str | None] = mapped_column()
    output_video_path: Mapped[str | None] = mapped_column()

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    user: Mapped["User"] = relationship(back_populates="videojobs")

    visual_config_id: Mapped[int | None] = mapped_column(
        ForeignKey("visual_config.id", ondelete="SET NULL")
    )
    visual_config: Mapped["VisualConfig"] = relationship()

    audio_config_id: Mapped[int | None] = mapped_column(
        ForeignKey("audio_config.id", ondelete="SET NULL")
    )
    audio_config: Mapped["AudioConfig"] = relationship()


class VisualConfig(Base):
    __tablename__ = "visual_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    smoking: Mapped[bool] = mapped_column(default=False)
    gore: Mapped[bool] = mapped_column(default=False)


class AudioConfig(Base):
    __tablename__ = "audio_config"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profanity: Mapped[bool] = mapped_column(default=False)
    hate_speech: Mapped[bool] = mapped_column(default=False)
    own_words: Mapped[str | None] = mapped_column()
