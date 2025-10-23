import enum

from pydantic import BaseModel


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


class VideoJobRead(VideoJobCreate):
    id: int
    title: str | None = None
    input_video_path: str
    output_video_path: str | None = None
    status: str
