# `services/` — Application / Use-Case Layer

Orchestrates domain objects to fulfill a specific use case requested by the
API layer. Each planned use case will get its own module, e.g.:

- `ingestion_service.py` — validate & parse uploaded CSVs
- `matching_service.py` — cross-reference transactions across sources
- `exception_service.py` — detect duplicates, missing settlements, amount
  mismatches, missing records
- `metrics_service.py` — compute match rate and reconciliation KPIs
- `explanation_service.py` — call the AI layer to explain unresolved
  exceptions in plain language
- `report_service.py` — assemble the operational summary report
- `chat_service.py` — natural-language querying over uploaded data

Services depend on `domain/` entities and on interfaces implemented by
`infrastructure/`, but never on `api/`.
