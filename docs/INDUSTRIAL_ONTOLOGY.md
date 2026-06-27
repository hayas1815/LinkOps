# Industrial Ontology

This document describes future domain entities for LinkOps. It is architectural guidance only and does not define implementation.

## Core Entities

### Asset
Represents a tracked industrial asset with operational context.
Relationships: belongs to a plant, contains equipment, and connects to maintenance, inspections, incidents, and documents.

### Equipment
Represents physical or logical equipment associated with an asset.
Relationships: belongs to an asset, may contain sensors, and can be linked to failures and maintenance records.

### Plant
Represents a site or facility.
Relationships: contains areas, pipelines, assets, and operational documents.

### Area
Represents a logical or physical subdivision of a plant.
Relationships: belongs to a plant and groups assets, equipment, and sensors.

### Pipeline
Represents a transport or process pipeline.
Relationships: belongs to a plant or area and can connect valves, pumps, and monitoring points.

### Valve
Represents a controllable flow component.
Relationships: belongs to a pipeline or equipment group and can be associated with incidents or maintenance.

### Pump
Represents a fluid movement component.
Relationships: belongs to a plant, area, or pipeline and can be linked to failures, inspections, and maintenance records.

### Motor
Represents a drive or motion component.
Relationships: belongs to equipment and can be monitored by sensors and inspections.

### Sensor
Represents a data-producing monitoring point.
Relationships: belongs to equipment, asset, area, or pipeline and can support telemetry and live monitoring.

### Maintenance Record
Represents corrective or preventive maintenance activity.
Relationships: belongs to an asset or equipment and may reference failures, inspections, engineers, and SOPs.

### Inspection
Represents an inspection event or assessment.
Relationships: belongs to an asset, equipment, or facility area and may produce findings and follow-up maintenance.

### Failure
Represents a component failure or degradation event.
Relationships: links to equipment, asset, incident, and maintenance record entities.

### Incident
Represents an operational event requiring attention.
Relationships: can be linked to assets, equipment, failures, engineers, and regulations.

### Engineer
Represents a human operator or technical specialist.
Relationships: can author maintenance records, inspections, SOPs, and incident notes.

### SOP
Represents a standard operating procedure.
Relationships: can apply to assets, equipment, inspections, incidents, and compliance workflows.

### Drawing
Represents a technical drawing or schematic.
Relationships: can describe plant, area, pipeline, or equipment structure and be linked to documents.

### Document
Represents a source document or knowledge artifact.
Relationships: can reference any domain entity and store operational context, revisions, and attachments.

### Regulation
Represents a compliance requirement or external rule.
Relationships: can apply to plants, assets, equipment, SOPs, incidents, inspections, and documents.

## Relationship Model
- Plants contain areas.
- Areas contain assets, equipment, sensors, and pipelines.
- Assets own equipment and operational context.
- Equipment may have sensors, failures, inspections, and maintenance records.
- Pipelines connect flow-control and monitoring components.
- Incidents and failures cross-reference affected assets, equipment, engineers, and regulations.
- Documents, drawings, and SOPs provide supporting knowledge for all operational entities.
