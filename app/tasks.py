import os

from sqlalchemy import create_engine
from sqlalchemy.orm import selectinload, sessionmaker

from app.celery import celery_app
from app.core.config import settings
from app.models.videojobs import Status, VideoJob
from app.services.videojobs import VideoJobService

pg_dsn = settings.postgres_dsn
sync_engine = create_engine(str(pg_dsn).replace("asyncpg", "psycopg2"))
sync_session = sessionmaker(bind=sync_engine, expire_on_commit=False, autoflush=False)


@celery_app.task
def censor_video(videojob_id: int, tmp_dir: str, output_video_path: str):
    with sync_session() as db:
        vj = db.get(
            VideoJob,
            videojob_id,
            options=[
                selectinload(VideoJob.audio_config),
                selectinload(VideoJob.visual_config),
            ],
        )
    if not vj:
        raise ValueError(f"VideoJob with id {videojob_id} not found")

    vj_service = VideoJobService(vj)
    try:
        vj_service.censor_video(tmp_dir, output_video_path)
        success = True
    except:
        success = False

    with sync_session() as db:
        vj = db.merge(vj)
        if success:
            vj.status = Status.COMPLETED
            vj.output_video_path = output_video_path
            vj.size = round(os.path.getsize(output_video_path) / (1024 * 1024), 2)
        else:
            vj.status = Status.FAILED
        db.commit()
