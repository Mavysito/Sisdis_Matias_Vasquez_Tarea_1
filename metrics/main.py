from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import os
import csv

app = FastAPI()
LOG_FILE = "data/metrics_log.csv"
if not os.path.exists(LOG_FILE):
    os.makedirs("data", exist_ok=True)
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["query", "zone", "source", "latency", "timestamp"])

class MetricEntry(BaseModel):
    query: str
    zone: str
    source: str
    latency: float

@app.post("/log")
def log_metric(entry: MetricEntry):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([entry.query, entry.zone, entry.source, entry.latency, pd.Timestamp.now()])
    return {"status": "ok"}


