import enum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Language(str, enum.Enum):
    EN = "en"
    RU = "ru"


class Status(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoJob(Base):
    __tablename__ = "videojob"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str | None] = mapped_column()
    size: Mapped[float | None] = mapped_column()
    language: Mapped[Language] = mapped_column(Enum(Language))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PROCESSING)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="videojobs")

    visual_setting_id: Mapped[int | None] = mapped_column(
        ForeignKey("visual_setting.id")
    )
    visual_setting: Mapped["VisualSetting"] = relationship(back_populates="videojobs")

    audio_setting_id: Mapped[int | None] = mapped_column(ForeignKey("audio_setting.id"))
    audio_setting: Mapped["AudioSetting"] = relationship(back_populates="videojobs")


class VisualSetting(Base):
    __tablename__ = "visual_setting"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    smoking: Mapped[bool] = mapped_column(default=False)
    gore: Mapped[bool] = mapped_column(default=False)
    videojobs: Mapped[list["VideoJob"]] = relationship(back_populates="visual_setting")


class AudioSetting(Base):
    __tablename__ = "audio_setting"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profanity: Mapped[bool] = mapped_column(default=False)
    hate_speech: Mapped[bool] = mapped_column(default=False)
    own_words: Mapped[str] = mapped_column(default="")
    videojobs: Mapped[list["VideoJob"]] = relationship(back_populates="audio_setting")
