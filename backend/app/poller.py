import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent.parent / "stockautotracker.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                comparator TEXT NOT NULL,
                threshold REAL NOT NULL,
                window_minutes INTEGER NOT NULL DEFAULT 15,
                enabled INTEGER NOT NULL DEFAULT 1,
                alert_channels TEXT NOT NULL DEFAULT '["iphone","sms"]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _alert_channels_to_list(raw_value: str) -> List[str]:
    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (TypeError, json.JSONDecodeError):
        pass
    return ["iphone", "sms"]


def _trigger_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "ticker": row["ticker"],
        "trigger_type": row["trigger_type"],
        "comparator": row["comparator"],
        "threshold": row["threshold"],
        "window_minutes": row["window_minutes"],
        "enabled": bool(row["enabled"]),
        "alert_channels": _alert_channels_to_list(row["alert_channels"]),
        "created_at": row["created_at"],
    }


def save_trigger(rule: BaseModel) -> Dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO triggers (
                ticker,
                trigger_type,
                comparator,
                threshold,
                window_minutes,
                enabled,
                alert_channels
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rule.ticker.upper(),
                rule.trigger_type,
                rule.comparator,
                rule.threshold,
                rule.window_minutes,
                int(rule.enabled),
                json.dumps(rule.alert_channels),
            ),
        )
        trigger_id = cursor.lastrowid

    return get_trigger_by_id(trigger_id)


def get_trigger_by_id(trigger_id: int) -> Dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM triggers WHERE id = ?",
            (trigger_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Trigger with id={trigger_id} not found")
    return _trigger_row_to_dict(row)


def get_all_triggers() -> List[Dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM triggers ORDER BY created_at DESC"
        ).fetchall()
    return [_trigger_row_to_dict(row) for row in rows]


def _payload_value(payload: Any, field_name: str) -> Any:
    if isinstance(payload, dict):
        return payload.get(field_name)
    return getattr(payload, field_name, None)


def evaluate_rule_matches(payload: Any) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    payload_ticker = _payload_value(payload, "ticker")

    for rule in get_all_triggers():
        if not rule["enabled"]:
            continue
        if payload_ticker is None:
            continue
        if rule["ticker"].upper() != str(payload_ticker).upper():
            continue

        value = None
        trigger_type = rule["trigger_type"]
        if trigger_type == "rsi":
            value = _payload_value(payload, "rsi")
        elif trigger_type == "volume":
            value = _payload_value(payload, "volume")
        elif trigger_type == "percent_move":
            value = _payload_value(payload, "percent_move")

        if value is None:
            continue

        comparator = rule["comparator"]
        triggered = False
        if comparator == "gt":
            triggered = value > rule["threshold"]
        elif comparator == "lt":
            triggered = value < rule["threshold"]
        elif comparator == "gte":
            triggered = value >= rule["threshold"]
        elif comparator == "lte":
            triggered = value <= rule["threshold"]
        elif comparator == "eq":
            triggered = value == rule["threshold"]

        if triggered:
            matches.append(
                {
                    "ticker": rule["ticker"],
                    "trigger_type": trigger_type,
                    "threshold": rule["threshold"],
                    "actual_value": value,
                    "channels": rule["alert_channels"],
                    "window_minutes": rule["window_minutes"],
                }
            )

    return matches
