import time
from threading import Event, Thread
from typing import Dict, Any

from app.db import get_all_triggers, evaluate_rule_matches


class PollingService:
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = interval_seconds
        self._stop_event = Event()
        self._thread: Thread | None = None

    def _mock_market_snapshot(self) -> Dict[str, Dict[str, float]]:
        return {
            "AAPL": {"rsi": 72.0, "volume": 1500000.0, "percent_move": 4.6},
            "MSFT": {"rsi": 58.0, "volume": 980000.0, "percent_move": 1.8},
            "NVDA": {"rsi": 82.0, "volume": 2100000.0, "percent_move": 6.1},
        }

    def _dispatch_matches(self) -> None:
        snapshot = self._mock_market_snapshot()
        for ticker, values in snapshot.items():
            payload = type("Payload", (), values)()
            payload.ticker = ticker
            matches = evaluate_rule_matches(payload)
            if matches:
                print(f"[StockAutoTracker] Alert for {ticker}: {matches}")

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._dispatch_matches()
            except Exception as exc:  # pragma: no cover
                print(f"[StockAutoTracker] Poller error: {exc}")
            self._stop_event.wait(self.interval_seconds)

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()


scheduler_service = PollingService(interval_seconds=30)
