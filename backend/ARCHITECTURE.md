# LinkOps Backend Architecture

LinkOps uses a FastAPI modular monolith foundation designed to evolve
toward event-driven services without forcing premature microservice complexity.

## Folder Responsibilities

- `app/main.py`: application composition root. It wires settings, logging,
  middleware, exception handlers, CORS, lifecycle hooks, and routers.
- `app/core`: cross-cutting platform primitives such as constants, settings,
  logging, and future security boundaries.
- `app/api`: HTTP transport layer. Versioned routers live under `api/v1` and
  should remain thin adapters over application/domain behavior.
- `app/middleware`: request-scoped infrastructure such as request IDs and
  automatic access logging.
- `app/shared`: reusable contracts such as response models, exception handlers,
  utilities, and future schemas.
- `app/database`: persistence adapter boundary. Database sessions, repositories,
  and migrations should be introduced here only when data models exist.
- `app/events`: event contracts and abstract publisher/subscriber interfaces.
  Concrete messaging is intentionally deferred.
- `app/tests`: backend tests.

## Design Decisions

The backend follows Clean Architecture so domain behavior can remain independent
from FastAPI, databases, queues, AI providers, and vendor SDKs. This keeps the
system testable and allows industrial modules such as asset intelligence,
knowledge graph, AI copilot, root cause analysis, compliance intelligence,
industrial IoT, live monitoring, and digital twin integration to grow behind
stable boundaries.

The event package prepares the application for document processing, OCR,
knowledge graph updates, MQTT ingestion, IoT telemetry, and AI workflow events.
Only abstract contracts exist today, which avoids coupling the foundation to a
broker before throughput, durability, and deployment needs are known.

Request IDs are assigned to every incoming request so logs, responses, errors,
and future distributed traces can be correlated across services. The
`X-Request-ID` response header gives clients and operators a stable reference
for support and incident analysis.

Standard response wrappers provide a consistent shape for future business APIs.
Existing root and health endpoints keep their original payloads for backward
compatibility, while exception handlers already return standardized errors.

Constants live in `app/core/constants.py` to avoid duplicated operational
defaults across the codebase. Centralizing values such as API version,
application metadata, logging format, upload limits, chunking defaults, and AI
model defaults makes future changes explicit and reviewable.
