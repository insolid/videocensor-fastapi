from celery import Celery
from core.config import settings

from app.services.videojobs import VideoJobService

celery_app = Celery("worker", broker=settings.celery_broker_url)


@celery_app.task
def censor_video(vj_service: VideoJobService, tmp_dir: str, output_video_path: str):
    vj_service.censor_video(tmp_dir, output_video_path)
