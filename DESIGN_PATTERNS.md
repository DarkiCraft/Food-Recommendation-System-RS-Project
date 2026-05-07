## Design patterns in this project (Munchify-Backend)

This document lists the main software design / analysis patterns used in the codebase and where they appear.

### Layered architecture (aka n-tier / clean-ish layering)

**Intent**: separate responsibilities by layer so changes in one area don’t cascade everywhere.

**Where**:
- **Presentation/API layer**: `controllers/` (FastAPI routers/endpoints)
- **Business logic layer**: `services/` (domain workflows)
- **Data access layer**: `repos/` (SQLAlchemy queries/CRUD)
- **Persistence layer**: `models/` (SQLAlchemy table definitions)
- **Cross-cutting configuration/glue**: `main.py`, `dependencies.py`, `database.py`
- **Algorithm subsystem**: `recommender/`

### Dependency Injection (FastAPI Depends)

**Intent**: avoid manual wiring in controllers; improve testability by swapping implementations.

**Where**:
- `dependencies.py`: providers like `get_db`, `get_*_repo`, `get_*_service`
- `controllers/*.py`: `Depends(get_current_user)`, `Depends(get_activity_service)`, etc.

In tests, FastAPI’s `app.dependency_overrides` is used to replace dependencies.

### Repository Pattern

**Intent**: keep database access logic (queries) out of services/controllers.

**Where**:
- `repos/user.py`, `repos/item.py`, `repos/order.py`, `repos/rating.py`, `repos/interaction.py`

Repositories wrap a SQLAlchemy `Session` and expose methods like `get_by_id`, `get_by_user`, `create`, `delete`.

### Service Layer Pattern

**Intent**: centralize business rules/workflows and keep controllers thin.

**Where**:
- `services/auth.py`: signup/login workflow + password hashing + JWT creation
- `services/activity.py`: click/order/rate workflows and validations
- `services/admin.py`: admin workflows (create/delete/stats)
- `services/recommend.py`: orchestration of multiple recommender algorithms + blending

### Strategy Pattern (Recommender algorithms)

**Intent**: treat recommendation algorithms as interchangeable “strategies” with a common interface (`fit`, `recommend`).

**Where**:
- `recommender/popularity.py`
- `recommender/content.py`
- `recommender/svd.py`
- `recommender/ncf.py`

`services/recommend.py` composes multiple strategies and blends their outputs using weights (`W_*` env vars).

### Facade/Orchestrator

**Intent**: provide a single entry point to a complex subsystem.

**Where**:
- `RecommendationService` in `services/recommend.py` is a facade over 4 recommenders (Popularity, Content, SVD, NCF).

### DTOs (Data Transfer Objects) via Pydantic Schemas

**Intent**: define explicit request/response shapes and validation at system boundaries.

**Where**:
- `schemas/auth.py`, `schemas/activity.py`, `schemas/admin.py`, `schemas/recommend.py`

These schemas are the API contract between client ↔ server.

### Configuration via Environment Variables (12-factor style)

**Intent**: keep secrets and config out of code.

**Where**:
- `.env.example` documents required env vars
- `database.py`, `services/auth.py`, `services/recommend.py`, `dependencies.py` read env vars

### Notes on “microservices”

Although the code is modular, it currently runs as **one deployable FastAPI app** with **one database**.
That’s closer to a **modular monolith** than microservices.

To move toward microservices you’d typically introduce:
- separate deployables (process boundaries) per bounded context (auth/activity/recommend/admin)
- separate data ownership boundaries
- explicit inter-service communication (HTTP/gRPC/events)

