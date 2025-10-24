"""Celery worker initialization.

This module initializes the Celery task queue for background tasks.
"""
from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "scribes",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Import tasks modules
celery_app.autodiscover_tasks(["app.workers.tasks"], force=True)


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")
