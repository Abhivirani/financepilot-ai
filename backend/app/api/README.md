# `api/` — Presentation Layer

HTTP entry points (FastAPI routers). This layer is responsible only for:

- Receiving requests and validating input shape (via `schemas/`)
- Calling the appropriate use case in `services/`
- Serializing the response

It must **not** contain reconciliation, matching, or business logic — that
belongs in `services/` and `domain/`.

`v1/endpoints/` is where versioned route modules will live (e.g.
`upload.py`, `reconciliation.py`, `reports.py`, `chat.py`), one file per
resource, once implementation begins.
