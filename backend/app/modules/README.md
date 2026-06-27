# Modules

This directory contains feature-oriented backend modules for LinkOps.

## Module Responsibilities

### Authentication
Owns identity and access boundaries when the feature is introduced.

### Documents
Owns document ingestion, classification, retrieval, and metadata concerns.

### Assets
Owns asset records, operational context, and asset-centric workflows.

### Knowledge
Owns knowledge organization, references, and industrial semantic context.

### Analytics
Owns platform analytics, reporting, and insights boundaries.

### Copilot
Owns conversational and guided assistance workflows.

### Dashboard
Owns summary views and operational presentation boundaries.

### Future Monitoring
Reserved for live monitoring, alerting, and operational signal workflows.

## Folder Convention
Each module should stay focused on a single responsibility and avoid importing framework concerns into business logic.
