try:
    from celery import Celery
    from backend.core.config import settings

    celery_app = Celery(
        "drishtirf_workers",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
    )
except Exception:
    # Celery / Redis not available — pipeline runs inline via results.py
    celery_app = None
