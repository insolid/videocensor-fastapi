from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile
from fastcrud import JoinConfig

from app.core.db import SessionDep
from app.models.videojobs import AudioConfig, VideoJob, VisualConfig
from app.schemas.videojobs import VideoJobCreate, VideojobQueryParams, VideoJobRead
from app.utils.fastcrud import CustomFastCRUD

from ..deps.auth import CurrentUserDep
from ..deps.videojobs import VideoJobByIDFromUrl

router = APIRouter(prefix="/videojobs", tags=["videojobs"])
videojob_crud = CustomFastCRUD(model=VideoJob)


@router.get("/{id}", response_model=VideoJobRead)
async def get_videojob(
    videojob: Annotated[
        VideoJob,
        Depends(VideoJobByIDFromUrl(VideoJob.visual_config, VideoJob.audio_config)),
    ],
):
    return videojob


@router.get("/", response_model=list[VideoJobRead])
async def get_videojobs(
    db: SessionDep,
    q: Annotated[VideojobQueryParams, Query()],
    cur_user: CurrentUserDep,
):
    return await videojob_crud.get_multi_joined(
        db=db,
        nest_joins=True,
        joins_config=[
            JoinConfig(
                model=VisualConfig,
                join_on=VisualConfig.id == VideoJob.visual_config_id,
                join_prefix="visual_config",
            ),
            JoinConfig(
                model=AudioConfig,
                join_on=AudioConfig.id == VideoJob.audio_config_id,
                join_prefix="audio_config",
            ),
        ],
        **q.model_dump(),
        user=cur_user,
    )


@router.post("/", response_model=VideoJobRead)
async def create_videojob(
    db: SessionDep,
    videojob: VideoJobCreate,
    cur_user: CurrentUserDep,
):
    vj = VideoJob(language=videojob.language, user=cur_user)
    if videojob.visual_config:
        vj.visual_config = VisualConfig(**videojob.visual_config.model_dump())
    if videojob.audio_config:
        vj.audio_config = AudioConfig(**videojob.audio_config.model_dump())

    db.add(vj)
    await db.commit()
    return vj


@router.post("/{id}/upload-file")
async def upload_video_file(
    file: UploadFile,
    db: SessionDep,
    videojob: Annotated[VideoJob, Depends(VideoJobByIDFromUrl())],
):
    videojob.output_video_path = f"/path/to/videos/{file.filename}"
    await db.commit()
    return videojob
