# FinancePilot AI

![Next.js](https://img.shields.io/badge/Next.js-16.3-black?style=flat&logo=next.js)
![React](https://img.shields.io/badge/React-19.2-blue?style=flat&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat&logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=flat&logo=tailwind-css)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=flat&logo=pandas)

FinancePilot AI is an automated financial reconciliation system designed for modern commerce and digital payment workflows. It ingest multi-source transaction datasets from bank statements, payment gateways, settlement reports, and invoices, normalizes data schemas, performs automated record matching, evaluates configurable reconciliation rules to detect operational exceptions, and provides interactive dashboard visualizations along with AI-generated executive summary reports.

## Features

- **Multi-source CSV Upload**: Ingest and process transaction records from Bank Statements, Payment Gateways, Settlement Reports, and Invoices.
- **CSV Validation & Normalization**: Validate schema headers, handle file encodings (UTF-8, UTF-16, Latin-1), alias column headers, and enforce non-empty dataset rules.
- **Dynamic Reconciliation Engine**: Automatically group transaction records by transaction identifiers across all input datasets.
- **Rule-based Exception Detection**: Evaluate incoming records against nine specialized financial reconciliation rules to flag mismatches, duplicates, missing records, and delay anomalies.
- **Interactive Dashboard**: Render real-time reconciliation metrics, match rates, financial totals, status breakdowns, and rule distribution charts.
- **AI Executive Report**: Synthesize structured reconciliation outputs into natural-language executive summaries, risk assessments, and recommended operational actions.
- **REST APIs**: Modular FastAPI endpoints for file uploads, reconciliation execution, dashboard data retrieval, exception management, and AI interactions.
- **Real-time Metrics**: Compute accurate transaction counts, clean matched records, unmatched records, match rates, and financial totals directly from execution state.
- **Batch Processing**: Isolate each uploaded dataset into dedicated batch directories with independent execution state management.

## Project Architecture

The application is structured as a decoupled web application comprising a Next.js frontend and a FastAPI backend.

```
[ Frontend: Next.js + React Query ]
                │
                │ HTTP API Requests
                ▼
[ Backend: FastAPI REST Layer ]
                │
                ├─► [ Upload Service ] ──────► Saves CSVs to uploads/<batch_id>
                │
                ├─► [ Reconciliation Service ]
                │         │
                │         ├─► DatasetLoader
                │         ├─► RecordMatcher
                │         ├─► Rule Engine (9 Rules)
                │         └─► MetricsCalculator
                │
                ├─► [ StateStore & File Storage ]
                │
                └─► [ AI Service & Context Builder ] ──► LLM API (Groq / OpenRouter / Gemini)
```

### Data Flow

1. **Upload**: Users submit CSV files through the frontend interface or REST API. The `UploadService` validates formats, cleans headers, maps column aliases, and stores files in an isolated batch directory under `uploads/<batch_id>`.
2. **Validation**: Datasets are inspected to ensure mandatory columns exist and at least one data row is present. Empty or invalid files halt execution and return structured HTTP 400 responses.
3. **Batch Creation**: `StateStore` registers a new batch manifest and clears stale run references.
4. **Reconciliation Execution**: `DatasetLoader` loads normalized data, `RecordMatcher` groups transactions by `transaction_id`, and the engine applies all active reconciliation rules.
5. **Metrics & Storage**: `MetricsCalculator` computes transaction counts, match rates, exception counts, and financial totals. Execution results are persisted to `generated_reports/<run_id>.json`.
6. **Presentation**: The frontend queries `/api/v1/dashboard?run_id=<run_id>` to render metrics and charts, and invokes `/api/v1/ai/executive-report` to generate AI insights.

## Tech Stack

### Frontend
- **Framework**: Next.js 16.3, React 19.2
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4, Lucide React
- **State & Data Fetching**: TanStack React Query 5, Axios, Zustand
- **Forms & Validation**: React Hook Form, Zod
- **Charts & UI**: Recharts, Sonner

### Backend
- **Framework**: FastAPI, Uvicorn
- **Language**: Python 3.13
- **Data Processing**: Pandas, NumPy
- **Schema & Settings**: Pydantic v2, Pydantic Settings
- **Async I/O**: Asyncio, Aiofiles

### AI Integration
- **LLM Client Layer**: Multi-provider support (Groq, OpenRouter, Gemini, Anthropic)
- **Context Builder**: Dynamic prompt context builder using structured reconciliation state
- **Formatting**: Natural-language markdown reports styled for Indian Rupee (INR) financial standards

### Database & Storage
- **File System Storage**: In-memory `StateStore` backed by JSON report files in `generated_reports/` and file manifests in `uploads/`

## Project Structure

```
financepilot-ai/
├── backend/
│   ├── app/
│   │   ├── ai/                      # AI orchestration, prompt builders, LLM clients
│   │   ├── api/v1/                  # FastAPI router endpoints (upload, reconcile, dashboard, etc.)
│   │   ├── core/                    # App configuration, middleware, exceptions, dependencies
│   │   ├── data_generation/         # Synthetic dataset generator and anomaly injector
│   │   ├── reconciliation/          # Engine core: loader, matcher, metrics, report exporter
│   │   │   └── rules/               # Individual reconciliation rule implementations
│   │   ├── schemas/                 # Pydantic request and response models
│   │   ├── services/                # Business logic services (upload, reconciliation, dashboard, state)
│   │   └── main.py                  # FastAPI application entry point
│   ├── generated_reports/           # Persisted JSON reconciliation run reports
│   ├── uploads/                     # Isolated batch upload storage
│   └── requirements.txt             # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js App Router pages (dashboard, upload, exceptions, reports, AI)
│   │   ├── components/              # React UI components, navigation, charts, data tables
│   │   ├── hooks/                   # Custom React hooks (React Query data fetching hooks)
│   │   ├── lib/                     # API client config, endpoints, and service wrappers
│   │   └── types/                   # TypeScript interface and type definitions
│   ├── package.json                 # Node.js dependencies and scripts
│   └── next.config.ts               # Next.js configuration
├── datasets/                        # Reference CSV datasets
└── README.md                        # Project documentation
```

## Reconciliation Workflow

```
Upload CSVs
    │
    ▼
Validation
    │
    ▼
Batch Creation
    │
    ▼
Reconciliation Engine
    │
    ▼
Rule Evaluation
    │
    ▼
Metrics Calculation
    │
    ▼
Dashboard
    │
    ▼
AI Executive Report
```

1. **Upload CSVs**: Client posts Bank, Gateway, Settlement, and Invoice CSV files to `/api/v1/upload`.
2. **Validation**: `UploadService` validates file extension, size, encoding, headers, and row count.
3. **Batch Creation**: A unique `batch_id` is assigned and clean files are stored.
4. **Reconciliation Engine**: Client invokes `/api/v1/reconcile` with the `batch_id`.
5. **Rule Evaluation**: `RecordMatcher` links records across sources, and nine rules evaluate anomaly conditions.
6. **Metrics Calculation**: Matched transactions, unmatched transactions, match rates, and financial totals are calculated.
7. **Dashboard**: `/api/v1/dashboard` returns metrics, financial summaries, rule distributions, and recent exceptions.
8. **AI Executive Report**: `/api/v1/ai/executive-report` generates natural-language executive summaries and risk analysis.

## Supported Data Sources

| Source Name | Internal Key | Filename | Required Columns |
| :--- | :--- | :--- | :--- |
| **Bank Statement** | `bank` | `Bank.csv` | `bank_txn_id`, `transaction_id`, `date`, `amount`, `type` |
| **Payment Gateway** | `payment_gateway` | `Gateway.csv` | `gateway_txn_id`, `transaction_id`, `date`, `gross_amount`, `fee`, `status` |
| **Settlement Report** | `settlement` | `Settlement.csv` | `settlement_id`, `transaction_id`, `gateway_txn_id`, `settlement_date`, `gross_amount`, `net_amount`, `fee_deducted` |
| **Invoice Data** | `invoice` | `Invoice.csv` | `invoice_id`, `transaction_id`, `date`, `total_amount`, `status` |

## Reconciliation Rules

The reconciliation engine evaluates nine rules:

1. **Amount Mismatch** (`AMOUNT_MISMATCH`): Detects discrepancies between the bank credit amount and gateway gross amount.
2. **Duplicate Transaction** (`DUPLICATE_TRANSACTION`): Flags multiple records sharing the same transaction identifier within a single dataset.
3. **Missing Settlement** (`MISSING_SETTLEMENT`): Identifies gateway transactions that have not been settled by the processor.
4. **Missing Invoice** (`MISSING_INVOICE`): Identifies completed payment gateway transactions lacking a corresponding invoice record.
5. **Settlement Delay** (`LATE_SETTLEMENT`): Flags settlements where the time difference between transaction date and settlement date exceeds configured thresholds.
6. **Fee Mismatch** (`FEE_MISMATCH`): Identifies cases where gateway fee deductions deviate from contractual percentage ranges or settlement net calculations.
7. **Refund Verification** (`REFUND_VERIFICATION`): Verifies refund transactions against original charges and flags unverified refunds.
8. **Orphan Record** (`ORPHAN`): Detects transaction records that exist in only one dataset without cross-source references.
9. **Status Mismatch** (`STATUS_MISMATCH`): Flags conflicting transaction statuses across payment gateway, bank, and invoice records.

## Dashboard

The interactive dashboard provides key operational metrics:

- **Total Transactions**: Total number of distinct transaction groups processed.
- **Matched Transactions**: Count of transactions matched across datasets without reconciliation exceptions.
- **Unmatched Transactions**: Count of transactions containing exceptions or missing cross-source references.
- **Match Rate**: Percentage of clean matched transactions relative to total transactions.
- **Financial Summary**: Sum of total processed amount, matched amount, unmatched amount, and total discrepancy amount.
- **Exception Breakdown**: Visual charts showing distribution of exceptions grouped by rule type and severity.
- **Recent Exceptions**: Paginated preview table listing detected exceptions with details, amounts, differences, and suggested actions.

## AI Executive Report

The AI Executive Report component analyzes the reconciliation run outputs to generate:

- **Executive Summary**: High-level overview of total volume, processed transaction counts, and overall match rate.
- **Financial Summary**: Detailed metrics covering processed amount, settled funds, unmatched exposure, and total discrepancy amounts.
- **Exception Analysis**: Categorized breakdown of top exception drivers and recurring operational anomalies.
- **Operational Risks**: Identification of high-severity financial risks, orphan records, and fee discrepancies.
- **Recommended Actions**: Actionable recommendations for finance teams, such as contacting payment gateways or adjusting settlement schedules.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/upload` | Upload multi-source CSV files and return batch summary |
| `POST` | `/api/v1/upload/demo` | Generate and process synthetic demo dataset batch |
| `POST` | `/api/v1/reconcile` | Execute reconciliation engine for a specific batch |
| `GET` | `/api/v1/dashboard` | Fetch dashboard metrics, financial summary, and charts |
| `GET` | `/api/v1/exceptions` | Fetch paginated list of reconciliation exceptions |
| `GET` | `/api/v1/exceptions/{id}` | Fetch detailed information for a single exception |
| `PATCH` | `/api/v1/exceptions/{id}/resolve` | Update resolution status of an exception |
| `GET` | `/api/v1/reports` | List generated JSON reconciliation reports |
| `GET` | `/api/v1/settings` | Retrieve active application settings and thresholds |
| `GET` | `/api/v1/ai/provider` | Retrieve configured AI provider and model metadata |
| `POST` | `/api/v1/ai/explain` | Generate AI-powered explanation for a specific exception |
| `POST` | `/api/v1/ai/dashboard-summary` | Generate natural-language AI summary for dashboard |
| `POST` | `/api/v1/ai/executive-report` | Generate complete AI Executive Reconciliation Report |
| `POST` | `/api/v1/ai/chat` | Send conversational query to the AI reconciliation assistant |
| `GET` | `/health` | Application health check endpoint |

## Installation

### Prerequisites

- **Python**: Version 3.11 or higher (Python 3.13 recommended)
- **Node.js**: Version 18.0 or higher
- **npm**: Package manager

### Backend Setup

1. Navigate to the project root directory:
   ```bash
   cd financepilot-ai
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv backend/.venv
   # On Windows (PowerShell):
   .\backend\.venv\Scripts\Activate.ps1
   # On Linux / macOS:
   source backend/.venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

### Environment Variables

Create a `.env` file in the project root directory (or export environment variables):

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=groq/compound-mini

# Alternative LLM Providers (Optional)
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Application

1. Start the FastAPI backend server:
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. In a separate terminal, start the Next.js frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the web interface:
   - **Frontend UI**: `http://localhost:3000`
   - **Backend OpenAPI Docs**: `http://localhost:8000/docs`

## Example Workflow

1. **Upload Files**: Open `http://localhost:3000/upload` and drag and drop your `Bank.csv`, `Gateway.csv`, `Settlement.csv`, and `Invoice.csv` files.
2. **Execute Reconciliation**: Click **Upload & Reconcile**. The system validates files, stores the batch, runs the engine, and returns a unique `run_id`.
3. **View Dashboard**: Navigate to `http://localhost:3000/dashboard` to inspect total volume, match rates, financial totals, and rule distributions.
4. **Inspect Exceptions**: Go to `http://localhost:3000/exceptions` to view detected anomalies, filter by rule severity, and click **AI Explain** to generate exception explanations.
5. **Generate AI Report**: Open `http://localhost:3000/reports` or `http://localhost:3000/ai` to generate an AI Executive Summary covering operational risks and recommended actions.


## License

This project is licensed under the MIT License.
