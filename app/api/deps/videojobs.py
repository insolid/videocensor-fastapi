from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.db import SessionDep
from app.models.videojobs import VideoJob

from .auth import CurrentUserDep


class VideoJobByIDFromUrl:
    def __init__(self, *select_in_load):
        self.select_in_load = select_in_load

    async def __call__(
        self, db: SessionDep, id: int, cur_user: CurrentUserDep
    ) -> VideoJob:
        vj = await db.scalar(
            select(VideoJob)
            .where(VideoJob.id == id, VideoJob.user == cur_user)
            .options(*[selectinload(field) for field in self.select_in_load])
        )
        if not vj:
            raise HTTPException(404, "Item not found")
        return vj
