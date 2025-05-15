from dotenv import load_dotenv
from celery import Celery
import os

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

celery_app.conf.task_track_started = True
import worker_tasks