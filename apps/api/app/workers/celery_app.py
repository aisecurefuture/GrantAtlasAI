from celery import Celery

from app.core.config import settings

celery_app = Celery("grantatlas", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="grantatlas.healthcheck")
def healthcheck() -> str:
    return "ok"

