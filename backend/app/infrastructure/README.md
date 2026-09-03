# `infrastructure/` — External Concerns

Everything that talks to the outside world. This layer implements interfaces
defined by the domain/services layers, keeping the core logic unaware of
*how* things are stored or computed.

- `parsers/` — CSV/schema parsing and validation for each source type (bank
  statement, payment gateway, settlement report, invoice data).
- `storage/` — reading/writing uploaded files and generated reports (local
  disk for the hackathon MVP; swappable for S3/GCS later).
- `ai/` — the AI client wrapper (e.g. Claude API calls) used to generate
  exception explanations and power the natural-language query feature. Kept
  isolated so the AI provider can be swapped without touching business logic.
