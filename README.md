# FinancePilot AI

**AI-Powered Transaction Reconciliation & Finance Operations Assistant**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![AI Powered](https://img.shields.io/badge/AI-Groq%20%7C%20Gemini%20%7C%20OpenRouter-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://groq.com/)

---

## 📌 Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Features](#3-features)
- [4. System Architecture](#4-system-architecture)
- [5. Tech Stack](#5-tech-stack)
- [6. Repository Folder Structure](#6-repository-folder-structure)
- [7. Installation & Local Setup](#7-installation--local-setup)
- [8. End-to-End Usage Workflow](#8-end-to-end-usage-workflow)
- [9. Reconciliation Engine & Rules](#9-reconciliation-engine--rules)
- [10. Dashboard Metrics & Analytics](#10-dashboard-metrics--analytics)
- [11. AI Architecture & Capabilities](#11-ai-architecture--capabilities)
- [12. Sample Benchmark Dataset](#12-sample-benchmark-dataset)
- [13. Interface Screenshots](#13-interface-screenshots)
- [14. Future Roadmap](#14-future-roadmap)
- [15. Contributors](#15-contributors)
- [16. License](#16-license)
- [17. Acknowledgements](#17-acknowledgements)

---

## 1. Project Overview

**FinancePilot AI** is an enterprise-grade finance operations platform that automates complex multi-system transaction reconciliation. Financial teams traditionally spend countless hours manually cross-referencing ledgers, bank statements, payment gateway logs, and invoices to identify operational discrepancies. FinancePilot AI eliminates this manual overhead through a hybrid architecture combining a high-performance **deterministic reconciliation engine** with **generative AI reasoning**.

The platform ingests multi-source data files (Bank statements, Payment Gateway logs, Settlement feeds, and Invoices), performs automatic file schema validation, executes 4-way transaction matching, and flags operational exceptions. By maintaining strict separation of concerns, FinancePilot AI guarantees **100% mathematical accuracy** during transaction matching while leveraging Large Language Models (LLMs) to synthesize executive summaries, generate root-cause exception explanations, and power a conversational finance assistant.

Whether deployed for daily e-commerce reconciliation, marketplace payout auditing, or corporate financial compliance, FinancePilot AI transforms fragmented financial data into actionable executive insights.

---

## 2. Problem Statement

Modern financial operations rely on disparate third-party systems—banks, payment gateways (e.g., Razorpay, Stripe), settlement aggregators, and billing engines. Each system generates independent reports with unique schemas, subtle timing differences, and fee deductions.

### The Operational Challenge

Finance and accounting teams encounter recurring bottlenecks:

- ⏱️ **Time-Intensive Manual Audit**: Reconciling thousands of rows across 4 independent spreadsheets takes hours or days.
- 💸 **Unmatched Financial Leakage**: Amount mismatches, hidden gateway fees, and missing payouts go undetected.
- 🔁 **Duplicate Charges & Delays**: Accidental double charges and delayed settlement payouts impact cash flow visibility.
- 📑 **Fragmented Documentation**: Invoices missing corresponding gateway captures lead to tax and audit compliance risks.
- ❌ **Human Error & Lack of Context**: Manual cross-referencing often misclassifies root causes, making resolution slow.

### How FinancePilot AI Solves It

FinancePilot AI automates end-to-end reconciliation through a single unified platform:

1. **Automated 4-Way Matching**: Joins records across Bank, Gateway, Settlement, and Invoice feeds using `transaction_id` as the primary key.
2. **Deterministic Rule Engine**: Evaluates transactions against 7 distinct anomaly rules (Amount Mismatches, Fee Deviations, Duplicates, Missing Settlements, Missing Invoices, Settlement Delays).
3. **AI-Powered Root Cause Insights**: Synthesizes human-readable anomaly explanations and recommended corrective actions.
4. **Real-Time Analytics Dashboard**: Displays high-level financial metrics, match rates, volume totals, and exception distribution charts.

---

## 3. Features

### Core Platform Capabilities

- ✅ **Multi-File Upload**: Supports drag-and-drop ingestion of Bank, Gateway, Settlement, and Invoice CSV files.
- ✅ **Automatic Schema Validation**: Validates required columns, file sizes, encoding, and data types before processing.
- ✅ **Multi-Source 4-Way Reconciliation**: Joins Bank, Gateway, Settlement, and Invoice datasets seamlessly.
- ✅ **Deterministic Transaction Matching**: Matches records strictly by primary `transaction_id` key.
- ✅ **Automated Exception Classification**: Categorizes anomalies into logical severity levels (HIGH, MEDIUM, LOW).
- ✅ **Amount Mismatch Detection**: Identifies gross transaction discrepancies down to exact Indian Rupee (₹) amounts.
- ✅ **Fee Mismatch & Tolerance Check**: Validates gateway fee percentages against configured bounds (1% – 3%).
- ✅ **Duplicate Gateway Detection**: Flags duplicate gateway captures and identifies primary key collisions.
- ✅ **Missing Settlement Detection**: Flags successful gateway transactions missing corresponding bank payouts.
- ✅ **Missing Invoice Detection**: Flags captured transactions lacking generated customer invoices.
- ✅ **Settlement Delay Detection**: Monitors payout timeliness and flags delayed settlement windows.
- ✅ **AI Exception Explanations**: Generates contextual, natural-language root cause analysis for every exception.
- ✅ **AI Executive Summary**: Produces one-click executive summaries formatted for Indian currency (INR / ₹).
- ✅ **AI Finance Chat Assistant**: Conversational assistant capable of answering natural-language queries about reconciliation datasets.
- ✅ **Interactive Analytics Dashboard**: Real-time visualization of match rates, volume totals, and exception breakdowns.
- ✅ **Dynamic Charting**: Rendered using Recharts for visual breakdown of exception distributions.
- ✅ **Filtered Exceptions Inbox**: Dedicated view with category filters, search capabilities, and detail inspection modals.
- ✅ **CSV Export**: One-click export of reconciliation exception reports for audit documentation.
- ✅ **Settings & Rule Management**: Configurable rule tolerances, AI provider selection (Groq, Gemini, OpenRouter), and system parameters.

---

## 4. System Architecture

FinancePilot AI adopts a decoupled micro-architecture separating deterministic calculation from generative AI services.

```mermaid
flowchart TD
    subgraph Client ["Frontend (Next.js 16 + React + Tailwind)"]
        UI[User / Finance Analyst]
        Dash[Dashboard & Exceptions Inbox]
        ChatUI[AI Chat Assistant]
    end

    subgraph API ["Backend API Layer (FastAPI)"]
        UploadEP["/api/v1/upload"]
        ReconcileEP["/api/v1/reconcile"]
        DashEP["/api/v1/dashboard"]
        AIEP["/api/v1/ai"]
    end

    subgraph Core ["Deterministic Engine"]
        Val[Validator & Schema Inspector]
        Matcher[Record Matcher (Join on transaction_id)]
        RuleEng[Modular Rule Engine]
        Metrics[KPI & Volume Calculator]
    end

    subgraph AI ["AI Reasoning Layer"]
        PromptBld[Context & Prompt Builder]
        MultiProvider[Multi-Provider LLM Client]
        LLM[Groq / Gemini / OpenRouter]
    end

    subgraph Store ["Persistence Layer"]
        StateStore[StateStore / Report Storage]
    end

    UI -->|Upload CSVs| UploadEP
    UploadEP --> Val
    Val -->|Validated Data| ReconcileEP
    ReconcileEP --> Matcher
    Matcher --> RuleEng
    RuleEng --> Metrics
    Metrics --> StateStore

    Dash -->|Fetch Metrics| DashEP
    DashEP --> StateStore

    ChatUI -->|Natural Language Query| AIEP
    AIEP --> PromptBld
    PromptBld --> StateStore
    PromptBld --> MultiProvider
    MultiProvider --> LLM
    LLM -->|Formatted Response| ChatUI
```

---

## 5. Tech Stack

| Layer | Technology | Details / Usage |
| :--- | :--- | :--- |
| **Frontend Framework** | **Next.js 16** | App Router, React 19, TypeScript |
| **Styling & Components** | **Tailwind CSS + shadcn/ui** | Modern responsive design system, Lucide icons |
| **State Management** | **TanStack Query (React Query)** | Server-state caching and async mutations |
| **Data Visualization** | **Recharts** | Interactive exception breakdown bar charts |
| **Backend Framework** | **FastAPI** | High-performance Python async REST API |
| **Language & Runtime** | **Python 3.13** | Typed Pydantic v2 schemas & domain models |
| **Data Processing** | **Pandas & NumPy** | In-memory CSV parsing, joins, and numerical evaluation |
| **AI Orchestration** | **Custom Multi-Provider Client** | Support for Groq (Llama-3/Compound-Mini), Gemini, OpenRouter |
| **Persistence** | **StateStore** | JSON-based run storage & verification report logging |
| **Testing** | **Pytest** | Comprehensive 46-test unit & integration suite |
| **Containerization** | **Docker & Docker Compose** | Multi-container orchestration ready |

---

## 6. Repository Folder Structure

```
financepilot-ai/
├── assets/                          # Static project assets, banners, and diagrams
├── backend/                         # FastAPI backend application
│   ├── app/
│   │   ├── ai/                      # LLM integration, prompt templates, and AI services
│   │   │   ├── prompts/             # System and template markdown prompts
│   │   │   ├── ai_service.py        # Core AI service layer
│   │   │   ├── context_builder.py   # Grounded financial context builder
│   │   │   ├── llm_client.py        # Multi-provider LLM client (Groq/Gemini/OpenRouter)
│   │   │   └── prompt_builder.py    # Dynamic prompt formatter
│   │   ├── api/                     # REST API route handlers
│   │   │   └── v1/                  # API v1 endpoints (upload, reconcile, dashboard, exceptions, ai, settings)
│   │   ├── core/                    # Core configuration and global exception handlers
│   │   │   ├── config.py            # Environment configuration
│   │   │   └── exceptions.py        # Unified API exception handling
│   │   ├── data_generation/         # Deterministic benchmark synthetic dataset generator
│   │   │   ├── generator.py         # 50-transaction benchmark generator
│   │   │   ├── validator.py         # Dataset integrity validator
│   │   │   └── anomaly_injector.py   # Financial anomaly injector
│   │   ├── reconciliation/          # Core deterministic reconciliation engine
│   │   │   ├── rules/               # Modular rule definitions (amount, fee, duplicate, missing, delay)
│   │   │   ├── engine.py            # Orchestrator rule evaluator
│   │   │   ├── matcher.py           # 4-way transaction join matcher
│   │   │   └── metrics.py           # Financial KPI and volume calculator
│   │   ├── schemas/                 # Pydantic data schemas
│   │   ├── services/                # Business logic services (dashboard, exceptions, upload, reconcile)
│   │   ├── utils/                   # Utility helpers (currency formatting, date parsing)
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── tests/                       # Pytest test suite (46 tests)
│   ├── Dockerfile                   # Backend Docker container definition
│   └── requirements.txt             # Python dependencies
├── datasets/                        # Benchmark datasets and reports
│   └── generated/
│       ├── csv/                     # Benchmark CSV feeds (Bank, Gateway, Settlement, Invoice)
│       └── reports/                 # Generation audit reports
├── frontend/                        # Next.js 16 frontend web application
│   ├── src/
│   │   ├── app/                     # Next.js App Router pages (dashboard, upload, exceptions, reports, ai, settings)
│   │   ├── components/              # React UI components (ai, charts, shell, table, ui)
│   │   ├── hooks/                   # Custom React hooks (useApi)
│   │   ├── lib/                     # Client utilities and API configuration
│   │   └── styles/                  # Global CSS styles
│   ├── package.json                 # Frontend dependencies and scripts
│   └── Dockerfile                   # Frontend Docker container definition
├── docker-compose.yml               # Multi-service Docker compose file
├── FinancePilot_Verification_Report.md # Verification report artifact
├── CODE_OF_CONDUCT.md               # Community guidelines
├── CONTRIBUTING.md                  # Contribution instructions
├── LICENSE                          # MIT License
└── README.md                        # Platform documentation
```

---

## 7. Installation & Local Setup

### Prerequisites

- **Python**: 3.11+ (Python 3.13 recommended)
- **Node.js**: v18.x or v20.x+
- **npm**: v9.x+
- **Git**

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/Abhivirani/financepilot-ai.git
cd financepilot-ai
```

---

### Step 2: Backend Setup

1. Navigate to the backend directory and create a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables by creating `.env`:
   ```env
   APP_ENV=development
   PORT=8000
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   DEFAULT_LLM_PROVIDER=groq
   DEFAULT_LLM_MODEL=groq/compound-mini
   ```

5. Run the FastAPI development server:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *The API will be available at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

---

### Step 3: Frontend Setup

1. Open a new terminal tab, navigate to `frontend`:
   ```bash
   cd frontend
   npm install
   ```

2. Configure frontend environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   *The frontend dashboard will be accessible at `http://localhost:3000`.*

---

### Running with Docker Compose (Optional)

Run both services seamlessly with Docker:

```bash
docker-compose up --build
```

---

## 8. End-to-End Usage Workflow

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────────┐
│  1. Upload CSVs │ ───► │  2. Auto Validate │ ───► │ 3. Reconcile Engine  │
└─────────────────┘      └──────────────────┘      └──────────────────────┘
                                                               │
┌─────────────────┐      ┌──────────────────┐                  ▼
│  6. AI Summary  │ ◄─── │ 5. Review Inbox  │ ◄─── ┌──────────────────────┐
│     & Chat      │      │   & Exceptions   │      │ 4. Executive Dash    │
└─────────────────┘      └──────────────────┘      └──────────────────────┘
        │
        ▼
┌─────────────────┐
│ 7. Export CSV   │
│   & Reports     │
└─────────────────┘
```

1. **Upload Files**: Navigate to `/upload` and select 4 CSV files (`Bank.csv`, `Gateway.csv`, `Settlement.csv`, `Invoice.csv`) or click **Use Demo Dataset**.
2. **Schema & File Validation**: The system validates file encoding, required headers, non-empty content, and data types.
3. **Reconciliation Execution**: The deterministic engine executes 4-way matching across transaction records.
4. **Dashboard Analysis**: Review top-level KPIs (Total Transactions, Match Rate, Bank Volume, Settlement Volume, Unmatched Volume).
5. **Exceptions Inbox**: Inspect flagged discrepancies categorized by severity, rule type, amount differences, clear explanatory reasons, and suggested actions.
6. **AI Assistant & Explanations**: Click **Explain** on any exception for AI root cause breakdown or use the AI Assistant to ask natural language questions.
7. **Export & Reporting**: Generate executive summaries or export exception records to CSV for audit compliance.

---

## 9. Reconciliation Engine & Rules

FinancePilot AI evaluates transactions using strict, deterministic financial rules:

### 1. Primary Matching Rule
- **Transaction ID Join**: Records are joined across feeds strictly by `transaction_id`. Never matched by arbitrary indexes, row order, or amounts.

### 2. Amount Mismatch Rule (`AMOUNT_MISMATCH`)
- **Severity**: `HIGH`
- **Evaluation**: Compares Bank transaction amount against Payment Gateway gross amount.
- **Description Format**: `Bank: ₹7,453.00, Gateway: ₹7,393.22, Difference: ₹59.78`
- **Suggested Action**: `Manual Review`

### 3. Fee Mismatch Rule (`FEE_MISMATCH`)
- **Severity**: `HIGH`
- **Evaluation**: Calculates gateway fee percentage `(fee / gross_amount)` and verifies it stays within allowed bounds (1.0% – 3.0%).
- **Descriptions**:
  - `Gateway fee 7.59% exceeds allowed range (1%-3%)`
  - `Gateway fee 0.59% below allowed range (1%-3%)`
- **Suggested Action**: `Escalate Payment Gateway`
- **Difference Column**: Displayed as `N/A` (percentage-based rule).

### 4. Duplicate Gateway Rule (`DUPLICATE_TRANSACTION`)
- **Severity**: `HIGH`
- **Evaluation**: Identifies multiple gateway records referencing the same `transaction_id`.
- **Description Format**: `Gateway Transaction ID GW_TXN1047_1 appears twice in Gateway.csv. Duplicate transaction detected.`
- **Suggested Action**: `Remove Duplicate Record`
- **Gateway Amount**: Equal to Bank Amount; **Difference**: `—`

### 5. Missing Settlement Rule (`MISSING_SETTLEMENT`)
- **Severity**: `HIGH`
- **Evaluation**: Flags captured successful gateway transactions lacking a corresponding settlement payout.
- **Description**: `Settlement record not found.`
- **Suggested Action**: `Investigate Settlement Batch`
- **Gateway Amount**: `—`; **Difference**: `—`

### 6. Missing Invoice Rule (`MISSING_INVOICE`)
- **Severity**: `MEDIUM`
- **Evaluation**: Flags captured transactions lacking a generated customer billing invoice.
- **Description**: `Invoice record not found.`
- **Suggested Action**: `Regenerate Invoice`
- **Gateway Amount**: `—`; **Difference**: `—`

### 7. Settlement Delay Rule (`LATE_SETTLEMENT`)
- **Severity**: `LOW`
- **Evaluation**: Measures elapsed days between gateway capture date and settlement payout date against allowed threshold (1 day).
- **Description**: `Settlement delayed by 3 days.`
- **Suggested Action**: `Manual Review`
- **Gateway Amount**: Equal to Bank Amount; **Difference**: `—`

---

## 10. Dashboard Metrics & Analytics

The Dashboard presents an audit-ready view of reconciliation results:

| Metric | Benchmark Target | Formula / Description |
| :--- | :--- | :--- |
| **Total Transactions** | **50** | Total unique transaction records evaluated |
| **Matched Transactions** | **38** | Clean transactions with zero flagged exceptions |
| **Unmatched Transactions** | **12** | Total transactions with one or more flagged anomalies |
| **Match Rate** | **76.00%** | `(Matched Transactions / Total Transactions) * 100` |
| **Bank Volume** | **₹4,68,600.81** | Total monetary volume processed in Bank statements |
| **Settlement Volume** | **₹4,47,827.04** | Exact `SUM(net_amount)` across all settlement records |
| **Unmatched Volume** | **₹88,954.94** | Total monetary volume associated with unmatched records |
| **Processing Time** | **~25 ms** | Engine execution speed (excluding network latency) |
| **Throughput** | **~2,000 txns/sec** | Transaction processing velocity |

### Exception Distribution Breakdown

- 🔴 **Amount Mismatch**: 4 (33.3%)
- 🟠 **Fee Mismatch**: 2 (16.7%)
- 🔴 **Duplicate Gateway**: 2 (16.7%)
- 🔴 **Missing Settlement**: 2 (16.7%)
- 🟡 **Missing Invoice**: 1 (8.3%)
- 🔵 **Settlement Delay**: 1 (8.3%)
- **Total Exceptions**: 12 (100.0%)

---

## 11. AI Architecture & Capabilities

FinancePilot AI implements a **Grounded AI Pattern**. The generative AI layer is NEVER allowed to compute financial math or infer transaction status independently. Instead, it reads structured JSON context produced by the deterministic engine.

```
┌─────────────────────────────────┐
│ Deterministic Engine Execution  │
└────────────────┬────────────────┘
                 │ (Produces Structured JSON Context)
                 ▼
┌─────────────────────────────────┐
│  Context & Prompt Builder       │  ──► Enforces Indian Rupee (INR / ₹) Formatting
└────────────────┬────────────────┘  ──► Inject Exact Metric Facts & Rule Definitions
                 │
                 ▼
┌─────────────────────────────────┐
│ Multi-Provider LLM Client       │  ──► Primary: Groq (Llama-3 / Compound-Mini)
└────────────────┬────────────────┘  ──► Fallback: Gemini AI / OpenRouter
                 │
                 ▼
┌─────────────────────────────────┐
│ Grounded Natural Language Output│  ──► Executive Summaries & Chat Answers
└─────────────────────────────────┘
```

### AI Features Overview

1. **AI Executive Summary**: Generates single-click C-level summaries highlighting volume totals, match rates, critical risk areas, and action items formatted for Indian Rupee (INR / ₹).
2. **AI Exception Explanation**: Synthesizes human-readable root-cause explanations when reviewing individual flagged anomalies in the Exceptions Inbox.
3. **AI Finance Chat Assistant**: An interactive assistant trained on the active reconciliation run context, answering natural language queries like *"What is our unmatched volume?"* or *"Why was TXN1043 flagged?"*
4. **AI Executive Report**: Produces comprehensive financial reconciliation reports combining metric breakdown tables with AI risk assessments.

---

## 12. Sample Benchmark Dataset

The repository includes a deterministic synthetic benchmark dataset located in `datasets/generated/csv/`:

- `Bank.csv` (50 rows)
- `Gateway.csv` (52 rows - includes 2 duplicates)
- `Settlement.csv` (48 rows - missing 2 payouts)
- `Invoice.csv` (49 rows - missing 1 invoice)

### Benchmark Financial Targets

- **Total Transactions**: 50
- **Matched / Unmatched**: 38 Matched / 12 Unmatched (76.00% Match Rate)
- **Bank Volume**: ₹4,68,600.81
- **Settlement Volume**: ₹4,47,827.04
- **Unmatched Volume**: ₹88,954.94
- **Anomalies Represented**: 4 Amount Mismatches, 2 Fee Mismatches, 2 Duplicate Gateways, 2 Missing Settlements, 1 Missing Invoice, 1 Settlement Delay.

*This dataset is 100% deterministic and suitable for automated testing and QA verification.*

---

## 13. Interface Screenshots

> *Screenshots placeholders for UI navigation and submission showcase.*

### Analytics Dashboard
![Analytics Dashboard](assets/screenshots/dashboard.png)
*Central dashboard displaying total transaction KPIs, volume cards, match rate progress, and exception breakdown charts.*

---

### CSV Ingestion & Validation
![Upload Interface](assets/screenshots/upload.png)
*Drag-and-drop multi-file upload screen with automatic file schema and encoding validation.*

---

### Exceptions Inbox
![Exceptions Inbox](assets/screenshots/exceptions.png)
*Filterable table displaying all 12 exceptions with rule tags, exact amounts, reasons, suggested actions, and severity badges.*

---

### AI Finance Chat Assistant
![AI Chat Assistant](assets/screenshots/ai_chat.png)
*Conversational AI assistant answering grounded queries regarding reconciliation runs.*

---

### Executive Report
![Executive Report](assets/screenshots/report.png)
*Generated financial report featuring metric tables and AI risk summaries.*

---

## 14. Future Roadmap

- [ ] **Excel (.xlsx/.xls) Support**: Ingest multi-tab workbook files directly.
- [ ] **Role-Based Access Control (RBAC)**: Fine-grained permissions for Analysts, Auditors, and Managers.
- [ ] **Database Integration**: Enterprise persistence with PostgreSQL, Prisma, and Redis caching.
- [ ] **Direct Gateway Webhooks**: Live API integrations with Razorpay, Stripe, and PayU.
- [ ] **Stream Reconciliation**: Real-time transaction matching via Kafka / EventBridge.
- [ ] **ML Anomaly Scoring**: Unsupervised ML models for predictive fraud detection.
- [ ] **Cloud Deployment**: One-click Terraform scripts for AWS (ECS/Fargate) and GCP (Cloud Run).

---

## 15. Contributors

We welcome open-source contributions! Meet the core team behind FinancePilot AI:

<table align="center">
  <tr>
    <td align="center" width="33%">
      <a href="https://github.com/Abhivirani">
        <img src="https://github.com/Abhivirani.png" width="100px;" alt="Abhi Virani"/><br />
        <sub><b>Abhi Virani</b></sub>
      </a><br />
      🤖 Lead Engineer & Architect
    </td>
    <td align="center" width="33%">
      <a href="https://github.com/Abhivirani">
        <img src="https://avatar.iran.liara.run/public/boy?username=contributor2" width="100px;" alt="Contributor 2"/><br />
        <sub><b>Full Stack Developer</b></sub>
      </a><br />
      🎨 Frontend & Analytics UI
    </td>
    <td align="center" width="33%">
      <a href="https://github.com/Abhivirani">
        <img src="https://avatar.iran.liara.run/public/girl?username=contributor3" width="100px;" alt="Contributor 3"/><br />
        <sub><b>AI Systems Specialist</b></sub>
      </a><br />
      ⚡ Prompting & LLM Pipeline
    </td>
  </tr>
</table>

---

## 16. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 17. Acknowledgements

FinancePilot AI is built upon awesome open-source technologies:

- **[Next.js](https://nextjs.org/)** — React framework for production.
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance Python web framework.
- **[Tailwind CSS](https://tailwindcss.com/)** — Utility-first CSS framework.
- **[shadcn/ui](https://ui.shadcn.com/)** — Beautifully designed UI components.
- **[Groq](https://groq.com/)** — Fast LLaMA inference engine.
- **[Google Gemini](https://ai.google.dev/)** — Multimodal generative AI models.
- **[OpenRouter](https://openrouter.ai/)** — Unified LLM API provider platform.
- **[Recharts](https://recharts.org/)** — Redefined chart library built with React and D3.

---

<p align="center">
  <b>FinancePilot AI</b> • Built with ❤️ for Buildathon & Financial Operations Teams
</p>
