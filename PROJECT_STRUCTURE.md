# Project Structure

## Top-Level Folders

### `backend/`
Purpose: backend application foundation for LinkOps.
Responsibilities: API transport, core configuration, middleware, shared contracts, domain modules, integration boundaries, workers, and persistence adapters.
Future modules: authentication, documents, assets, knowledge, analytics, copilot, monitoring, graph orchestration, and industrial integrations.

### `docs/`
Purpose: product, architecture, and domain documentation.
Responsibilities: explain the platform vision, domain model, technical direction, and future design boundaries.
Future modules: ontology, AI agents, deployment standards, API contracts, and operational runbooks.

### `frontend/`
Purpose: frontend application foundation.
Responsibilities: UI shell, feature modules, shared components, layout, styling, state, and browser-facing presentation.
Future modules: dashboard, documents, assets, knowledge, copilot, analytics, monitoring, and operational workflows.

### `infra/`
Purpose: infrastructure and platform delivery assets.
Responsibilities: deployment scaffolding, environment conventions, runtime packaging, and future enterprise platform automation.
Future modules: Kubernetes manifests, CI/CD templates, secrets handling, and environment overlays.

### `scripts/`
Purpose: operational and developer automation.
Responsibilities: local setup helpers, build scripts, maintenance tasks, and repeatable team workflows.
Future modules: bootstrap scripts, release utilities, data import helpers, and environment validation tools.

### `docker/`
Purpose: container-oriented support files.
Responsibilities: compose fragments, image helpers, and container runtime conventions.
Future modules: service-specific build assets and deployment packaging helpers.

### `.github/`
Purpose: repository automation and developer experience assets.
Responsibilities: issue templates, pull request templates, workflows, and repository policy artifacts.
Future modules: CI pipelines, release workflows, dependency automation, and code-quality checks.

## Repository Direction

LinkOps is intentionally organized as a modular enterprise foundation. Each top-level folder should remain focused on one responsibility so future teams can add capabilities without blurring boundaries or coupling delivery concerns to product behavior.
