# FinancePilot AI - Backend API

This backend provides the HTTP API for the FinancePilot AI reconciliation engine. It is built using FastAPI.

## How to run backend

1. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. Start the FastAPI application:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## How to open Swagger

Once the backend is running, open your browser and navigate to:
[http://localhost:8000/docs](http://localhost:8000/docs)

This page displays the interactive OpenAPI (Swagger) documentation where you can test the endpoints.

## Available API endpoints

All endpoints are versioned under `/api/v1/`:

- **Health**
  - `GET /api/v1/health`: Returns system health, version, uptime, and module availability.
- **Upload**
  - `POST /api/v1/upload`: Upload CSV files (Bank, Gateway, Settlement, Invoice) and receive a validated batch ID.
- **Reconciliation**
  - `POST /api/v1/reconcile`: Trigger the reconciliation engine on the latest or specified batch ID.
- **Dashboard**
  - `GET /api/v1/dashboard`: Retrieve aggregated metrics, rule distribution, and financial summary charts.
- **Exceptions**
  - `GET /api/v1/exceptions`: List and filter reconciliation exceptions with pagination.
  - `GET /api/v1/exceptions/{id}`: Get detailed view of an exception, including AI explanations.
- **Settings**
  - `GET /api/v1/settings`: Get current reconciliation and AI settings.
  - `PUT /api/v1/settings`: Update settings.
- **AI**
  - `POST /api/v1/ai/explain`: Request AI explanation for an exception (Placeholder).

All responses follow a standard envelope containing `success`, `request_id`, and `data` (or `error`).
