import logging
import os
from worker_tasks import send_to_alert_service
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI
import requests
from pydantic import BaseModel
from shared.log_utils import InfluxDBLogHandler
from celery.result import AsyncResult
from celery_app import celery_app

app = FastAPI()

load_dotenv()
ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://alert_service:8001/process")

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File logging
file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# InfluxDB logging
influx_handler = InfluxDBLogHandler("api_service")
influx_handler.setFormatter(logging.Formatter("%(message)s"))

logger.addHandler(file_handler)
logger.addHandler(influx_handler)

class RequestData(BaseModel):
    message: str

@app.post("/submit")
async def submit_data(data: RequestData):
    logging.info(f"Received data: {data.dict()}")
    task = send_to_alert_service.delay(data.message)
    return {"task_id": task.id, "status": "submitted"}


@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "state": task.state,
        "result": task.result if task.state == "SUCCESS" else None
    }