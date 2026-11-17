from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

from app.db import init_db, get_all_triggers, save_trigger, evaluate_rule_matches
from app.poller import scheduler_service

app = FastAPI(title="StockAutoTracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TriggerRule(BaseModel):
    ticker: str = Field(..., min_length=1)
    trigger_type: Literal["rsi", "volume", "percent_move"]
    comparator: Literal["gt", "lt", "gte", "lte", "eq"]
    threshold: float
    window_minutes: int = 15
    enabled: bool = True
    alert_channels: List[Literal["iphone", "sms"]] = ["iphone", "sms"]


class TriggerCheckRequest(BaseModel):
    ticker: str
    rsi: Optional[float] = None
    volume: Optional[float] = None
    percent_move: Optional[float] = None


class AlertRequest(BaseModel):
    ticker: str
    trigger_type: str
    threshold: float
    comparator: str
    value: float


@app.on_event("startup")
def startup_event():
    init_db()
    scheduler_service.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler_service.stop()


@app.get("/health")
def health():
    return {"status": "ok", "service": "StockAutoTracker API"}


@app.get("/api/triggers")
def get_triggers():
    return {"rules": get_all_triggers()}


@app.post("/api/triggers")
def create_trigger(rule: TriggerRule):
    saved_rule = save_trigger(rule)
    return {"message": "Trigger rule created", "rule": saved_rule}


@app.post("/api/check")
def evaluate_trigger(payload: TriggerCheckRequest):
    return {"matches": evaluate_rule_matches(payload)}


@app.post("/api/alerts/test")
def send_alert(payload: AlertRequest):
    return {
        "message": "Alert dispatched",
        "ticker": payload.ticker,
        "trigger_type": payload.trigger_type,
        "threshold": payload.threshold,
        "comparator": payload.comparator,
        "value": payload.value,
        "channels": ["iphone", "sms"],
        "status": "queued",
    }


@app.get("/api/system/status")
def system_status():
    return {
        "scheduler_running": scheduler_service.is_running(),
        "interval_seconds": scheduler_service.interval_seconds,
    }
