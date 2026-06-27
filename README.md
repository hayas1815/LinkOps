# LinkOps

Industrial Knowledge Intelligence Platform

Connect. Understand. Operate.

LinkOps is the enterprise foundation for industrial knowledge intelligence. It is designed to connect operational documents, asset context, engineering knowledge, compliance references, and future live signals into a single governed platform.

## Project Vision

LinkOps transforms fragmented industrial knowledge into a unified operational intelligence platform by connecting documents, assets, maintenance history, engineering knowledge, compliance records, and future real-time sensor data into a single AI-powered system.

## Problem Statement

Industrial teams typically work across disconnected documents, tribal knowledge, asset records, maintenance history, and compliance artifacts. That fragmentation slows down search, investigation, decision-making, and operational readiness.

LinkOps is intended to reduce that fragmentation without forcing premature complexity.

## Architecture Overview

The repository follows Clean Architecture, Domain Driven Design, SOLID principles, feature-based modularity, event-driven design, and a future microservice-ready structure. The backend remains the primary implementation surface until frontend development begins.

## Technology Stack

- Backend: Python, FastAPI, Pydantic
- Frontend: Next.js, React, TypeScript
- Database: PostgreSQL
- Knowledge Graph: Neo4j
- Vector Database: vector storage layer
- Storage: object storage, Redis
- AI: agent boundaries, prompt management, retrieval architecture
- Deployment: Docker, Docker Compose, Kubernetes-ready structure

## Project Structure

The repository is organized as a modular monorepo with clear separation between application code, documentation, infrastructure, and developer tooling.

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for the full folder-by-folder breakdown.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the long-term product phases.

## How to Run

Backend development environment:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The application exposes the root endpoint at `/` and health endpoint at `/health`. Swagger UI is available at `/docs`.

## Future Vision

The planned platform direction includes:

- Asset Intelligence
- Knowledge Graph
- AI Copilot
- Root Cause Analysis
- Compliance Intelligence
- Industrial IoT
- Live Monitoring
- Digital Twin Integration

## Contribution

Contribution expectations are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

See [LICENSE](LICENSE).

