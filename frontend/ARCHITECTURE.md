# Frontend Architecture

## Folder Structure

LinkOps uses a feature-based frontend architecture under `frontend/`. The structure separates the application shell, shared components, feature workspaces, hooks, services, state, styles, theme tokens, constants, utilities, and types.

## Design System

The UI is governed by `docs/UI_UX_GUIDELINES.md`. All visual decisions should use design tokens rather than hardcoded values. The interface should remain dark-first, industrial, minimal, and enterprise-oriented.

## Workspace Philosophy

Each workspace represents a focused operational surface. Mission Control acts as the landing experience, while document, asset, knowledge, AI, analytics, and settings workspaces provide domain-specific flows. Future workspaces should reuse the same shell and component language.

## Component Hierarchy

- `app/`: route-level pages, metadata, loading, error, and not-found states
- `components/layout/`: application shell and layout composition
- `components/ui/`: base primitives
- `components/shared/`: reusable enterprise components
- `components/navigation/`: sidebar and navigation items
- `components/feedback/`: states such as loading, empty, error, modal, drawer, and upload surfaces
- `components/workspace/`: workspace-specific scaffolding and controls
- `features/`: domain-aligned feature entry points
- `styles/theme/tokens/`: design tokens and theme primitives

## Global Subsystems

### Command Palette
- Trigger: `Ctrl + K`
- Implementation: `components/workspace/command-palette.tsx`
- Scope: UI placeholder only (no backend commands)

### Global Search Interface
- Implementation: `components/workspace/global-search-modal.tsx`
- Scope: placeholder search modal for assets, documents, knowledge, and AI

### Global Notification Center
- Implementation: `components/feedback/notification-center.tsx`
- Support files: `constants/notifications.ts`
- Scope: unread badge, list, empty state, future integration placeholder

### Theme Management
- Modes: dark, light, system
- Persistence: `store/ui-store.ts` via local storage
- Behavior: shell applies persisted mode and resolves system preference when selected

### Layout Persistence
- Persisted state: sidebar collapse, active workspace label, theme mode
- Store: `store/ui-store.ts`

### Feature Flags Infrastructure
- Types: `types/feature-flags.ts`
- Defaults and helpers: `lib/feature-flags.ts`
- Runtime config mapping: `lib/config/app-config.ts`
- Example flags: `knowledgeGraph`, `liveMonitoring`, `iot`, `digitalTwin`, `maintenanceAI`

### Permissions Infrastructure
- Interfaces only
- Types: `types/permissions.ts`
- Roles: viewer, engineer, manager, admin

### API Client Architecture
- Reusable fetch wrapper: `services/api/client.ts`
- Scope: infrastructure only, no concrete API calls

### Toast Notification System
- Components: `components/feedback/toast.tsx`, `components/feedback/toast-provider.tsx`
- Variants: success, warning, error, info

### Reusable Empty and Loading States
- Empty states: `components/feedback/empty-states.tsx`
- Skeletons: `components/feedback/loading-skeletons.tsx`

### Error Boundary
- Component: `components/feedback/error-boundary.tsx`
- Integrated through: `app/providers.tsx`

### Frontend Middleware Placeholders
- Runtime middleware: `middleware.ts`
- Placeholder checks: `lib/middleware/auth.ts`, `lib/middleware/authorization.ts`, `lib/middleware/maintenance-mode.ts`

### Frontend Configuration
- App and environment config: `lib/config/app-config.ts`
- Includes environment mode, API base URL, feature flags, and metadata context

### App Providers
- Composition root: `app/providers.tsx`
- Includes query client, toast provider, and global error boundary

## Scalability

The architecture is intended to scale into a full enterprise product without redesigning the shell. New workspaces, components, and feature modules should be added by extending the existing patterns instead of introducing parallel UI languages.
