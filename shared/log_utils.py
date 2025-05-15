import logging
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class InfluxDBLogHandler(logging.Handler):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
        self.url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
        self.db = os.getenv("INFLUXDB_DB", "logs")
        self.user = os.getenv("INFLUXDB_USER", "admin")
        self.password = os.getenv("INFLUXDB_PASS", "adminpass")

    def emit(self, record):
        try:
            message = self.format(record)
            timestamp = int(datetime.utcnow().timestamp() * 1e9)
            payload = f"log_event,service={self.service_name},level={record.levelname} message=\"{message}\" {timestamp}"
            requests.post(
                url=f"{self.url}/write?db={self.db}",
                data=payload.encode('utf-8'),
                auth=(self.user, self.password)
            )
        except Exception as e:
            print(f"[⚠] Failed to log to InfluxDB: {e}")