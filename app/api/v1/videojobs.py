from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db import SessionDep
from app.models.videojobs import AudioConfig, VideoJob, VisualConfig
from app.schemas.videojobs import VideoJobCreate, VideoJobRead

router = APIRouter(prefix="/videojobs", tags=["videojobs"])


@router.get("/", response_model=list[VideoJobRead])
async def get_videojobs(db: SessionDep):
    jobs = await db.scalars(
        select(VideoJob).options(
            selectinload(VideoJob.visual_config), selectinload(VideoJob.audio_config)
        )
    )
    return jobs.all()


@router.post("/", response_model=VideoJobRead)
async def create_videojob(db: SessionDep, videojob: VideoJobCreate):
    vc = VisualConfig(**videojob.visual_config.model_dump())
    ac = AudioConfig(**videojob.audio_config.model_dump())
    job = VideoJob(
        language=videojob.language,
        visual_config=vc,
        audio_config=ac,
        input_video_path="path/to/input/video.mp4",
    )
    db.add(job)
    db.add(vc)
    db.add(ac)
    await db.commit()
    return job
