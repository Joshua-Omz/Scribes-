"""Celery tasks for background processing.

This module defines tasks that run in the background using Celery.
"""
from app.workers.worker import celery_app


@celery_app.task
def example_task(param):
    """
    Example task for demonstration.
    
    Args:
        param: A parameter to process
    """
    return f"Task completed with parameter: {param}"
