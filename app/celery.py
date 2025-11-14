from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.celery_broker_url,
    include=["app.tasks"],
)
