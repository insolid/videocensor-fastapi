import os
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastcrud import JoinConfig

from app.api.deps.auth import CurrentUserDep
from app.api.deps.videojobs import VideoJobByIDFromUrl
from app.core.config import settings
from app.core.db import SessionDep
from app.models.videojobs import AudioConfig, Status, VideoJob, VisualConfig
from app.schemas.videojobs import (
    VideoJobCreate,
    VideojobQueryParams,
    VideoJobRead,
    VideoJobReadShort,
    VideoJobUpdate,
)
from app.utils.fastcrud import CustomFastCRUD

from ..deps.auth import user_has_active_subscription
from ..deps.videojobs import get_uploaded_video_file

router = APIRouter(prefix="/videojobs", tags=["videojobs"])
videojob_crud = CustomFastCRUD(model=VideoJob)


@router.get(
    "/{id}",
    response_model=VideoJobRead,
    name="videojobs:get_one",
)
async def get_videojob(
    videojob: Annotated[
        VideoJob,
        Depends(VideoJobByIDFromUrl(VideoJob.visual_config, VideoJob.audio_config)),
    ],
):
    return videojob


@router.get(
    "/",
    response_model=list[VideoJobRead],
    name="videojobs:list",
)
async def list_videojobs(
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
        user=cur_user,
        **q.model_dump(),
    )


@router.post(
    "/",
    response_model=VideoJobRead,
    name="videojobs:create",
    status_code=201,
    dependencies=[Depends(user_has_active_subscription)],
)
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


@router.patch(
    "/{id}",
    response_model=VideoJobRead,
    name="videojobs:update",
    dependencies=[Depends(user_has_active_subscription)],
)
async def update_videojob(
    db: SessionDep,
    vj: Annotated[
        VideoJob,
        Depends(VideoJobByIDFromUrl(VideoJob.visual_config, VideoJob.audio_config)),
    ],
    vj_data: VideoJobUpdate,
):
    if vj.status != Status.PENDING:
        raise HTTPException(400, "Only pending videojobs can be updated")

    data = vj_data.model_dump(exclude_unset=True)
    visual_config = data.pop("visual_config", None)
    audio_config = data.pop("audio_config", None)

    for field, value in data.items():
        setattr(vj, field, value)

    # Update related visual and audio configs if provided
    if visual_config:
        for field, value in visual_config.items():
            setattr(vj.visual_config, field, value)
    if audio_config:
        for field, value in audio_config.items():
            setattr(vj.audio_config, field, value)

    await db.commit()
    return vj


@router.post(
    "/{id}/upload-file",
    response_model=VideoJobReadShort,
    name="videojobs:upload_file",
    dependencies=[Depends(user_has_active_subscription)],
)
async def upload_video_file(
    file: Annotated[UploadFile, Depends(get_uploaded_video_file)],
    db: SessionDep,
    vj: Annotated[VideoJob, Depends(VideoJobByIDFromUrl())],
    cur_user: CurrentUserDep,
):
    if vj.status != Status.PENDING:
        raise HTTPException(400, "Only pending videojobs can be updated")

    file_dir = settings.video_storage_path / cur_user.email
    file_name = f"{vj.id}_{file.filename}"
    file_path = file_dir / file_name
    os.makedirs(file_dir, exist_ok=True)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    vj.input_video_path = str(file_path)
    vj.status = Status.PROCESSING
    vj.title = file_name
    await db.commit()
    # TODO: run celery task to process the video
    return vj
