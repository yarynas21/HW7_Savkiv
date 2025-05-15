import logging
import os
from fastapi import FastAPI, Request
from datetime import datetime
import re
import requests
from dotenv import load_dotenv
from shared.log_utils import InfluxDBLogHandler

app = FastAPI()

load_dotenv()

os.makedirs("logs", exist_ok=True)
os.makedirs("error_reports", exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

influx_handler = InfluxDBLogHandler("alert_service")
influx_handler.setFormatter(logging.Formatter("%(message)s"))

logger.addHandler(file_handler)
logger.addHandler(influx_handler)

def create_alert(alert_type: str, description: str):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"error_reports/{alert_type}_{now}.txt"
    with open(filename, "w") as f:
        f.write(f"Time: {now}\n")
        f.write(f"Type: {alert_type}\n")
        f.write(f"Description: {description}\n")

@app.post("/process")
async def process_data(request: Request):
    data = await request.json()
    logging.info(f"Processing data: {data}")
    text = str(data).lower()
    alerts = []

    if "password" in text or "secret" in text or "credentials" in text:
        alerts.append(("personal_data", f"Sensitive info: {data}"))
    if "fraud" in text or "scam" in text or "fake" in text:
        alerts.append(("fraud", f"Fraud attempt: {data}"))
    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,}\b', str(data)):
        alerts.append(("email_detected", f"Email found: {data}"))
    if re.search(r'\b\d{10,}\b', str(data)):
        alerts.append(("card_detected", f"Card number found: {data}"))

    for alert_type, description in alerts:
        create_alert(alert_type, description)

    return {"status": "processed", "alerts": [a[0] for a in alerts]}