from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from app.api.deps.auth import CurrentUserDep
from app.core.db import SessionDep
from app.models.base import Base
from app.models.videojobs import VideoJob


class VideoJobByIDFromUrl:
    """Videojob for current user by id from URL"""

    def __init__(self, *select_in_load: InstrumentedAttribute[Base]):
        self.select_in_load = select_in_load

    async def __call__(
        self,
        db: SessionDep,
        id: int,
        cur_user: CurrentUserDep,
    ) -> VideoJob:
        vj = await db.scalar(
            select(VideoJob)
            .where(VideoJob.id == id, VideoJob.user == cur_user)
            .options(*[selectinload(field) for field in self.select_in_load])
        )
        if not vj:
            raise HTTPException(404, "Item not found")
        return vj


async def get_uploaded_video_file(file: UploadFile) -> UploadFile:
    allowed_file_types = {"video/mp4", "video/mpeg"}
    if file.content_type not in allowed_file_types:
        msg = f"Invalid file type. Allowed types: {', '.join(allowed_file_types)}"
        raise HTTPException(400, msg)
    return file
