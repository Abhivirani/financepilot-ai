# FinancePilot AI

**An AI-assisted financial reconciliation platform for automating transaction matching, exception detection, and reporting.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini-AI-8E75B2?style=flat-square&logo=googlegemini&logoColor=white)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Docker](#docker)
- [API Overview](#api-overview)
- [Screenshots](#screenshots)
- [Demo Workflow](#demo-workflow)
- [Future Roadmap](#future-roadmap)
- [Contributors](#contributors)
- [License](#license)

---

## Overview

### Why FinancePilot AI Exists

Financial reconciliation is one of the most repetitive and error-prone processes in finance and accounting operations. Teams routinely spend hours manually comparing ledgers, bank statements, and transaction records to identify mismatches, duplicates, and discrepancies. FinancePilot AI was built to remove this manual burden by combining a structured reconciliation engine with AI-assisted analysis.

### The Business Problem

Organizations handling financial transactions face recurring challenges:

- Manual reconciliation is slow and inconsistent across teams
- Discrepancies and exceptions are often discovered late
- Root-cause analysis of mismatches requires domain expertise
- Reporting is fragmented and time-consuming to produce
- Existing tools are either too rigid (fixed rule sets) or too opaque (black-box automation)

### The Solution

FinancePilot AI provides a configurable reconciliation platform that:

- Ingests transaction datasets and applies systematic matching logic
- Flags exceptions using a modular, extensible rule engine
- Uses Gemini AI to explain exceptions and summarize reports in plain language
- Presents results through a clean, actionable dashboard and exceptions inbox

### Key Capabilities

- End-to-end reconciliation workflow from upload to report
- Rule-based exception detection with clear audit trails
- AI-generated explanations for flagged discrepancies
- REST API layer for integration with external systems
- Modern, responsive frontend for finance teams to review and act on results

---

## Features

### Backend

- **Synthetic Dataset Generator** — Generates realistic sample transaction datasets for testing and demonstration purposes
- **Reconciliation Engine** — Core engine that compares transaction sets and identifies matches, mismatches, and gaps
- **Modular Rule Engine** — Pluggable rule definitions that determine how discrepancies are classified
- **Exception Detection** — Identifies and categorizes transactions that fail reconciliation rules
- **REST APIs** — FastAPI-based endpoints exposing all core platform functionality
- **Report Generation** — Produces structured reconciliation reports from processed data

### Frontend

- **Dashboard** — Central view summarizing reconciliation status and key metrics
- **Upload Workflow** — Guided interface for uploading transaction datasets
- **Exceptions Inbox** — Dedicated view for reviewing and resolving flagged exceptions
- **Reports** — Interface for generating and viewing reconciliation reports
- **AI Assistant** — Conversational interface for querying reconciliation results and exceptions
- **Settings** — Configuration panel for rules, preferences, and platform behavior

### AI

- **Gemini-Powered Explanations** — Natural-language explanations of why a transaction was flagged
- **Exception Analysis** — AI-assisted interpretation of exception patterns
- **Report Summaries** — Automatically generated plain-language summaries of reconciliation reports
- **Prompt Architecture** — Structured prompt templates designed for consistent, grounded AI responses tied to reconciliation data

---

## Architecture

```
                         ┌───────────────────┐
                         │     Frontend       │
                         │   (Next.js + TS)   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │      FastAPI        │
                         │   (REST API Layer)  │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Reconciliation      │
                         │      Engine          │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    Rule Engine       │
                         │  (Modular Rules)      │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │      Reports          │
                         │   (Generation Layer)   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │     Gemini AI          │
                         │ (Explanations/Summaries)│
                         └───────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, TailwindCSS |
| Backend | Python, FastAPI |
| AI | Google Gemini AI |
| Database / Storage | To be finalized based on deployment target |
| Charts | Recharts / Chart.js (frontend visualization) |
| State Management | React Context / Hooks |
| Testing | Pytest (backend), Jest (frontend) |
| Deployment | Docker, Docker Compose |

---

## Project Structure

```
financepilot-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── reconcile.py
│   │   │   ├── dashboard.py
│   │   │   ├── exceptions.py
│   │   │   ├── reports.py
│   │   │   ├── settings.py
│   │   │   └── ai.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── engine/
│   │   │   ├── reconciliation_engine.py
│   │   │   ├── rule_engine.py
│   │   │   └── exception_detector.py
│   │   ├── services/
│   │   │   ├── dataset_generator.py
│   │   │   ├── report_service.py
│   │   │   └── gemini_service.py
│   │   ├── models/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── upload/
│   │   │   ├── exceptions/
│   │   │   ├── reports/
│   │   │   ├── assistant/
│   │   │   └── settings/
│   │   ├── components/
│   │   ├── lib/
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/financepilot-ai.git
cd financepilot-ai
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Variables

Create a `.env` file in the `backend/` directory based on `.env.example`:

```env
GEMINI_API_KEY=your_gemini_api_key
APP_ENV=development
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 5. Running the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 6. Running the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000` and the backend API at `http://localhost:8000`.

---

## Docker

FinancePilot AI is designed to be containerized for consistent local development and deployment.

- A `docker-compose.yml` file will orchestrate the backend, frontend, and any supporting services as separate containers.
- Each service (`backend`, `frontend`) will have its own `Dockerfile` for building isolated images.
- Environment variables will be passed into containers via `.env` files referenced in `docker-compose.yml`.
- Once configured, the full stack will be runnable with a single command:

```bash
docker-compose up --build
```

Note: Docker configuration files are planned as part of the platform's deployment setup and will be added as the project progresses.

---

## API Overview

### `/upload`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload transaction dataset(s) for reconciliation |
| GET | `/upload/status/{id}` | Check the status of an uploaded dataset |

### `/reconcile`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/reconcile/run` | Trigger the reconciliation engine on uploaded data |
| GET | `/reconcile/{id}` | Retrieve the results of a reconciliation run |

### `/dashboard`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Retrieve summary metrics for the dashboard |
| GET | `/dashboard/status` | Retrieve overall reconciliation status |

### `/exceptions`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/exceptions` | List all detected exceptions |
| GET | `/exceptions/{id}` | Retrieve details of a specific exception |
| PATCH | `/exceptions/{id}` | Update the status/resolution of an exception |

### `/reports`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/reports/generate` | Generate a reconciliation report |
| GET | `/reports/{id}` | Retrieve a generated report |

### `/settings`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/settings` | Retrieve current platform configuration |
| PUT | `/settings` | Update platform configuration and rule settings |

### `/ai`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ai/explain` | Get an AI-generated explanation for a flagged exception |
| POST | `/ai/summarize` | Get an AI-generated summary of a report |
| POST | `/ai/query` | Ask the AI Assistant a question about reconciliation data |

---

## Screenshots

> Screenshots will be added as the interface is finalized.

**Dashboard**

`![Dashboard](docs/screenshots/dashboard.png)`

**Upload**

`![Upload](docs/screenshots/upload.png)`

**Exceptions**

`![Exceptions](docs/screenshots/exceptions.png)`

**Reports**

`![Reports](docs/screenshots/reports.png)`

**AI Assistant**

`![AI Assistant](docs/screenshots/ai-assistant.png)`

**Swagger (API Docs)**

`![Swagger](docs/screenshots/swagger.png)`

---

## Demo Workflow

A typical end-to-end reconciliation flow in FinancePilot AI:

1. **Upload CSVs** — User uploads one or more transaction datasets through the Upload Workflow
2. **Run Reconciliation** — The Reconciliation Engine processes the datasets and applies matching logic
3. **Dashboard** — Summary metrics and reconciliation status are displayed on the Dashboard
4. **Exceptions** — Flagged discrepancies appear in the Exceptions Inbox for review
5. **AI Explanation** — The user requests an AI-generated explanation for a specific exception
6. **Reports** — A final reconciliation report is generated, optionally including an AI-written summary

```
Upload CSVs
    ↓
Run Reconciliation
    ↓
Dashboard
    ↓
Exceptions
    ↓
AI Explanation
    ↓
Reports
```

---

## Future Roadmap

- Multi-tenant support for managing multiple organizations within a single deployment
- Authentication and role-based access control
- Background job processing for large-scale reconciliation runs
- Vector database integration for improved AI context retrieval
- Streaming AI responses for real-time assistant interactions
- Advanced analytics and trend detection across reconciliation history

---

## Contributors

Contributions are welcome. If you would like to contribute to FinancePilot AI:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your branch and open a Pull Request

Please open an issue first to discuss significant changes before submitting a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).
