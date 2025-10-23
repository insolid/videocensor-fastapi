import enum
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.schemas.query import CommonQueryParams


class VideojobQueryParams(CommonQueryParams):
    sort_by: Annotated[
        Literal["id", "created_at"],
        Field(serialization_alias="sort_columns"),
    ] = "id"


class VisualConfigCreate(BaseModel):
    smoking: bool = False
    gore: bool = False


class AudioConfigCreate(BaseModel):
    profanity: bool = False
    hate_speech: bool = False
    own_words: str | None = None


class Language(str, enum.Enum):
    EN = "en"
    RU = "ru"


class VideoJobCreate(BaseModel):
    language: Language
    visual_config: VisualConfigCreate | None = None
    audio_config: AudioConfigCreate | None = None


class VideoJobRead(BaseModel):
    id: int
    user_id: int
    title: str | None = None
    language: Language
    visual_config: VisualConfigCreate | None = None
    audio_config: AudioConfigCreate | None = None
    input_video_path: str | None = None
    output_video_path: str | None = None
    status: str

    created_at: datetime
    updated_at: datetime
