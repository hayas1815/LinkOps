# Database

LinkOps is designed for multiple persistence models.

The data layer is expected to support asset intelligence, knowledge graph, AI copilot, root cause analysis, compliance intelligence, industrial IoT, live monitoring, and digital twin integration without changing the platform's architectural boundaries.

## Planned Persistence Boundaries

- PostgreSQL for transactional platform data.
- Neo4j for knowledge graph relationships.
- Vector storage for semantic retrieval and RAG.
- Object storage for documents, media, and generated artifacts.
- Redis for cache, coordination, and future queue support.

## Design Principles

- Keep database adapters outside domain logic.
- Avoid leaking persistence models into API contracts.
- Use migrations once data models are introduced.
- Maintain clear ownership for each database boundary.

No database models or migrations are implemented in this skeleton.
