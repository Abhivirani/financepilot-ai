# FinancePilot AI

**AI-powered Finance Operations Assistant** — built for the **Razorpay AI
Buildathon 2026**, Track: *AI Finance Controller*.

> Status: 🏗️ Project scaffold only. No application logic has been written
> yet — see [Roadmap](#roadmap).

---

## Overview

Finance teams reconcile transactions across banks, payment gateways,
settlement reports, and invoices largely by hand — comparing records,
chasing mismatches, and writing up exception reports. FinancePilot AI
automates this end-to-end:

1. **Ingest** transaction data from multiple CSV sources.
2. **Validate** each file's schema before processing.
3. **Match** transactions across sources.
4. **Detect** duplicates, missing settlements, incorrect amounts, and
   missing records.
5. **Calculate** reconciliation metrics (match rate and related KPIs).
6. **Explain** unresolved exceptions in plain language using AI.
7. **Report** results through an interactive dashboard and operational
   summary reports.

Everything runs on synthetic data — no live banking or payment APIs are
involved (see [Scope](#project-scope)).

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI, Pandas |
| AI | Anthropic Claude (via the Messages API) |
| Frontend | Next.js (App Router), React, TypeScript, Tailwind CSS |
| Data | CSV files (synthetic datasets, `datasets/`) |
| Infra | Docker & docker-compose |
| CI | GitHub Actions |

Architecture: the backend follows **Clean Architecture** — domain logic is
isolated from frameworks, storage, and the AI provider so each can evolve or
be swapped independently. See `backend/app/README.md` for the layer
breakdown.

---

## Project Structure

```
financepilot-ai/
├── .github/workflows/     # CI pipelines
├── backend/               # FastAPI service (Clean Architecture)
│   └── app/
│       ├── api/           # HTTP routes (presentation layer)
│       ├── core/          # config, logging, security
│       ├── domain/        # entities & value objects (business rules)
│       ├── services/      # use cases / application layer
│       ├── infrastructure/# parsers, storage, AI client
│       ├── schemas/       # request/response DTOs
│       └── utils/         # shared helpers
├── frontend/              # Next.js dashboard
│   └── src/
│       ├── app/           # routes/pages
│       ├── components/    # UI components
│       ├── hooks/         # custom React hooks
│       ├── lib/           # API client & helpers
│       ├── types/         # shared TS types
│       └── styles/        # global styles
├── datasets/              # synthetic sample data (bank/gateway/settlement/invoice)
├── docs/                  # architecture & API documentation
├── demo/                  # demo video/script for submission
├── screenshots/           # UI screenshots for README/deck
├── docker-compose.yml
└── README.md
```

Every folder above contains its own `README.md` explaining its responsibility
in more detail.

---

## MVP Features

**Core**
- [ ] CSV Upload
- [ ] Data Validation
- [ ] Transaction Matching
- [ ] Settlement Verification
- [ ] Duplicate Detection
- [ ] Exception Detection
- [ ] AI Explanation
- [ ] Dashboard

**Stretch Goals**
- [ ] Finance Chatbot (natural-language queries over uploaded data)
- [ ] CFO Summary Report
- [ ] Export to PDF
- [ ] Export to Excel
- [ ] User Authentication
- [ ] Multi-user Support
- [ ] Historical Reports

**Out of Scope**
- Live Razorpay APIs
- Bank APIs
- Real merchant data
- Production payment systems

---

## Project Scope

**Included:** transaction reconciliation, exception detection, AI
explanation, dashboard, report generation.

**Excluded:** real payment processing, live banking APIs, merchant
onboarding, payment execution, fraud prediction, production accounting
integrations.

---

## Roadmap

- [x] **Phase 0 — Scaffold**: folder structure, `.gitignore`, README,
      `docker-compose.yml` skeleton *(this commit)*
- [ ] **Phase 1 — Data layer**: synthetic dataset generation (≥50
      transactions), CSV schema validation, parsers
- [ ] **Phase 2 — Domain & matching**: entities, matching algorithm,
      duplicate/exception detection rules
- [ ] **Phase 3 — API**: FastAPI endpoints for upload, reconciliation run,
      metrics, exceptions, reports
- [ ] **Phase 4 — AI layer**: Claude-powered exception explanations and
      natural-language querying
- [ ] **Phase 5 — Frontend**: upload flow, dashboard, exception views
- [ ] **Phase 6 — Reporting**: operational summary report generation
- [ ] **Phase 7 — Polish**: Docker end-to-end run, docs, demo recording

---

## Setup Instructions

> These steps assume Phase 1+ has been implemented. Right now the repo only
> contains the folder scaffold, so `pip install` / `npm install` will work,
> but there's no running app yet.

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional, for containerized run)
- An Anthropic API key (for the AI explanation feature)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in ANTHROPIC_API_KEY
# uvicorn app.main:app --reload  # once app/main.py exists
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### With Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

---

## Success Metrics

- Match rate
- Number of detected exceptions
- Processing time (target: batches of 50–500 transactions, fast)
- AI explanation quality
- Dashboard usability
- Overall user experience

---

## Target Users

Finance Operations Executive · Reconciliation Analyst · Risk Analyst ·
Finance Manager · CFO

---

## License

TBD (add a license before public release if required by the hackathon rules).

---

## Project Architecture

The backend follows a scalable Clean Architecture, extending the domain and infrastructure layers with dedicated modules for reconciliation, data generation, and AI. See `docs/ADR/` for detailed architectural decisions.

## Development Workflow

1. Ensure you have the [prerequisites](#prerequisites) installed.
2. Create a new branch for your feature or bugfix (see [Git Branch Strategy](#git-branch-strategy)).
3. Write code, add tests, and ensure the application runs locally.
4. Submit a Pull Request against the `main` branch.

## Git Branch Strategy

We follow a simple feature-branch workflow:
- `main` - Stable, deployable code.
- `feat/feature-name` - New features and enhancements.
- `fix/bug-name` - Bug fixes.
- `docs/topic` - Documentation updates.

## Milestones

Our development is tracked across 10 milestones. Please see [docs/ROADMAP.md](docs/ROADMAP.md) for the complete breakdown of phases from Project Setup to Demo.

## Future Work

- Fully integrated Finance Chatbot
- Advanced predictive analytics
- Real-time webhooks for live payment gateways
- Multi-tenant user authentication and RBAC

## Screenshots

*(Placeholder for UI screenshots - add to `screenshots/` directory)*

## Demo

*(Placeholder for Demo video link - add to `demo/` directory)*

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests. For reporting bugs or requesting features, please use the provided GitHub issue templates.
