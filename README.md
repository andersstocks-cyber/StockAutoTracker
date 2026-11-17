# StockAutoTracker

A stock monitoring MVP with a React UI and a FastAPI backend.

## Current MVP scope
- Define stock trigger rules in the UI
- Support trigger types for:
  - RSI
  - Volume
  - Percentage move
- Store rules in memory / JSON-like backend data model
- Simulate a trigger check and return alert payloads
- Prepare for version 1 alert channels: iPhone + SMS
- Version 2 path is left for Avanza login + order placement

## Tech stack
- Frontend: React + Vite
- Backend: Python + FastAPI

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Then open the local Vite URL in the browser.

## Example backend endpoints
- `GET /health`
- `GET /api/triggers`
- `POST /api/triggers`
- `POST /api/check`
- `POST /api/alerts/test`

## Roadmap
1. Version 1: Alert on iPhone + SMS when a trigger condition is met
2. Version 2: Log in to Avanza and place an order using a predefined ticker symbol and approved risk settings
3. Add persisted storage, scheduler, secure secrets management, and trade confirmations
