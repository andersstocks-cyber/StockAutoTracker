from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

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

rules: List[TriggerRule] = []

@app.get("/health")
def health():
    return {"status": "ok", "service": "StockAutoTracker API"}

@app.get("/api/triggers")
def get_triggers():
    return {"rules": rules}

@app.post("/api/triggers")
def create_trigger(rule: TriggerRule):
    rules.append(rule)
    return {"message": "Trigger rule created", "rule": rule}

@app.post("/api/check")
def evaluate_trigger(payload: TriggerCheckRequest):
    matches = []
    for rule in rules:
        if rule.ticker.upper() != payload.ticker.upper():
            continue

        value = None
        if rule.trigger_type == "rsi":
            value = payload.rsi
        elif rule.trigger_type == "volume":
            value = payload.volume
        elif rule.trigger_type == "percent_move":
            value = payload.percent_move

        if value is None:
            continue

        triggered = False
        if rule.comparator == "gt":
            triggered = value > rule.threshold
        elif rule.comparator == "lt":
            triggered = value < rule.threshold
        elif rule.comparator == "gte":
            triggered = value >= rule.threshold
        elif rule.comparator == "lte":
            triggered = value <= rule.threshold
        elif rule.comparator == "eq":
            triggered = value == rule.threshold

        if triggered:
            matches.append({
                "ticker": rule.ticker,
                "trigger_type": rule.trigger_type,
                "threshold": rule.threshold,
                "actual_value": value,
                "channels": rule.alert_channels,
            })

    return {"matches": matches}

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
        "status": "queued"
    }
