import asyncio

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery("grantatlas", broker=settings.redis_url, backend=settings.redis_url)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "ingest-grants-gov-nightly": {
        "task": "grantatlas.ingest_grants_gov",
        "schedule": crontab(hour=6, minute=0),
    },
    "ingest-sam-gov-nightly": {
        "task": "grantatlas.ingest_sam_gov",
        "schedule": crontab(hour=6, minute=30),
    },
}


@celery_app.task(name="grantatlas.healthcheck")
def healthcheck() -> str:
    return "ok"


@celery_app.task(name="grantatlas.ingest_grants_gov")
def ingest_grants_gov_task() -> dict:
    from app.services.ingestion import ingest_grants_gov_for_all_tenants

    return asyncio.run(ingest_grants_gov_for_all_tenants())


@celery_app.task(name="grantatlas.ingest_sam_gov")
def ingest_sam_gov_task() -> dict:
    from app.services.ingestion import ingest_sam_gov_for_all_tenants

    return asyncio.run(ingest_sam_gov_for_all_tenants())
