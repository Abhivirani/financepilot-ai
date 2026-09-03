# `schemas/` — Data Transfer Objects (DTOs)

Pydantic models that define the *shape* of data crossing the API boundary:
request bodies, response payloads, and validation rules for uploaded files.

These are distinct from `domain/entities/`: schemas describe wire format
(JSON in/out of the API), while entities describe business meaning. Keeping
them separate means the API contract can evolve without changing core logic,
and vice versa.
