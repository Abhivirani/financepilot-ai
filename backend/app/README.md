# Backend — `app/`

This is the root Python package for the FinancePilot AI backend, organized using
**Clean Architecture**. Dependencies only point *inward*: `api` depends on
`services`, `services` depend on `domain`, but `domain` depends on nothing else
in this project. This keeps business rules (matching/reconciliation logic)
independent of frameworks, databases, and AI providers, so any of those can be
swapped later without rewriting the core logic.

Layers, from outermost to innermost:

| Layer | Folder | Depends on |
|---|---|---|
| Presentation | `api/` | `services`, `schemas` |
| Application (use cases) | `services/` | `domain` |
| Domain (business rules) | `domain/` | nothing |
| Infrastructure (I/O, AI, storage) | `infrastructure/` | `domain` (implements its interfaces) |
| DTOs / contracts | `schemas/` | — |
| Cross-cutting config | `core/` | — |
| Shared helpers | `utils/` | — |

No application logic has been implemented yet — this file exists purely to
document the intended structure for contributors.
