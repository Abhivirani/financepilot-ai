# `core/` — Cross-Cutting Configuration

Application-wide concerns that don't belong to any single feature:

- App settings / environment variable loading (e.g. `config.py`)
- Logging setup
- Security utilities (API key validation, CORS policy)
- Constants shared across layers

Nothing here should depend on `api/`, `services/`, or `domain/`.
