import requests
from celery_app import celery_app

@celery_app.task(name="send_to_alert_service")
def send_to_alert_service(message: str):
    response = requests.post(
        "http://alert_service:8001/process",
        json={"message": message}
    )
    return response.json()