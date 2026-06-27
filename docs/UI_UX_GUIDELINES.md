# UI/UX Guidelines

## LinkOps Design System

Product Name: LinkOps

Tagline: Connect. Understand. Operate.

Description: Industrial Knowledge Intelligence Platform

This document is the official design reference for LinkOps. It defines the visual language, layout behavior, component philosophy, and user experience rules that every developer, designer, and AI agent should follow when creating interfaces for the platform.

## 1. Brand Philosophy

### Mission
LinkOps helps industrial teams understand complex operational environments by turning fragmented knowledge, assets, documents, and signals into clear, actionable interfaces.

### Vision
LinkOps should become the trusted operational intelligence layer for industrial organizations. The experience must make dense information easier to understand, faster to act on, and safer to operate.

### Design Philosophy
The interface must feel like enterprise software built for engineers, operators, analysts, and technical leaders. It should communicate trust, reliability, precision, and operational control.

The UI should always feel:
- Trustworthy
- Reliable
- Engineering-focused
- Operationally intelligent
- Enterprise-grade

The UI should never feel like:
- A consumer app
- A gaming interface
- A crypto dashboard
- A flashy admin template

### Core Principles
- Clarity over decoration
- Structure over novelty
- Precision over ornament
- Consistency over experimentation
- Functionality over visual noise
- Accessibility as a baseline, not an add-on
- Scalable patterns over one-off screens

## 2. Brand Identity

### Product Name
LinkOps

### Tagline
Connect. Understand. Operate.

### Brand Personality
- Professional
- Technical
- Reliable
- Intelligent
- Minimal
- Confident

### Tone of Interface
The product should communicate calm authority. It should feel composed, deliberate, and highly structured. Avoid playful microcopy, exaggerated visual effects, and unnecessary decorative elements.

## 3. Color System

LinkOps uses a restrained enterprise palette with strong contrast, clear hierarchy, dark theme first behavior, and no gradients.

### Core Colors
- Background: #0B1220
- Sidebar: #111827
- Cards: #111A2E
- Panels: #0F172A
- Borders: #24324A
- Text Primary: #F8FAFC
- Text Secondary: #94A3B8

### Functional Colors
- Primary Blue: #3B82F6
- Success Green: #22C55E
- Warning Amber: #F59E0B
- Danger Red: #EF4444
- Info Cyan: #06B6D4
- Neutral Gray: #94A3B8

### Usage Rules
- Use one primary accent color consistently across actions and active states.
- Reserve danger colors for destructive, failure, or critical operational states.
- Use status colors sparingly and only when they add clarity.
- Never rely on color alone to communicate meaning.
- Never use gradients for core product UI.
- Use dark surfaces for the default product experience.

### Recommended Token Groups
- `color.background`
- `color.sidebar`
- `color.card`
- `color.panel`
- `color.border`
- `color.text.primary`
- `color.text.secondary`
- `color.brand.primary`
- `color.status.success`
- `color.status.warning`
- `color.status.danger`
- `color.status.info`
- `color.neutral`

## 4. Typography

Typography should feel modern, technical, and readable in dense enterprise environments.

### Primary Font
Inter, system-ui, sans-serif

### Monospace Font
JetBrains Mono, ui-monospace, SFMono-Regular, monospace

### Heading Sizes
- H1: 40px / 48px / semibold
- H2: 32px / 40px / semibold
- H3: 24px / 32px / semibold
- H4: 20px / 28px / semibold

### Body Sizes
- Body Large: 16px / 24px
- Body Default: 14px / 22px
- Body Small: 12px / 18px

### Caption
- 12px / 16px
- Used for metadata, helper text, and secondary labels

### Button Text
- 14px / 20px
- Medium weight
- Sentence case

### Code Blocks
- 13px / 20px
- Monospace font
- Use for identifiers, payloads, configuration, and technical snippets

### Typography Rules
- Prefer sentence case for labels and buttons.
- Use uppercase only for compact status labels and technical badges.
- Do not overuse bold text.
- Maintain strong line-height for long operational content.

## 5. Spacing System

LinkOps uses an 8px grid system.

### Spacing Scale
- 4px
- 8px
- 12px
- 16px
- 24px
- 32px
- 48px
- 64px

### Spacing Rules
- Use 4px only for micro adjustments.
- Use 8px for compact component spacing.
- Use 16px and 24px for standard layout rhythm.
- Use 32px and 48px for section separation.
- Use 64px only for major page-level separation.

## 6. Border Radius

Border radius should stay controlled and professional.

### Radius Values
- Buttons: 8px
- Cards: 12px
- Dialogs: 16px
- Panels: 12px
- Inputs: 8px

### Radius Rules
- Do not use overly rounded shapes.
- Keep controls visually grounded and enterprise-oriented.

## 7. Shadows

Shadows should be subtle and functional, not decorative.

### Shadow Levels
- Small: light elevation for compact surfaces
- Medium: elevated cards and hoverable panels
- Large: dialogs, overlays, and high-emphasis containers
- Focus: accessible ring or outline treatment rather than a heavy shadow

### Shadow Rules
- Shadows should separate layers, not create drama.
- Avoid deep, soft, or colorful shadows.
- Focus states must remain visible in high-contrast environments.

## 8. Iconography

LinkOps uses Lucide Icons.

### Icon Usage
- Use one icon library only.
- Keep icon style consistent across the entire platform.
- Use icons to support recognition, not to replace labels.
- Pair icons with text in critical navigation and action areas.

### Icon Rules
- Do not mix Lucide with other icon sets.
- Use the same stroke weight across all icons.
- Avoid decorative icon overload.

## 9. Component Philosophy

Every component should be:
- Reusable
- Composable
- Accessible
- Typed
- Responsive

### Component Rules
- Avoid duplication.
- Build from shared primitives.
- Keep behavior and styling separable where possible.
- Make state explicit.
- Favor configuration over hardcoded variants.

### Preferred Patterns
- Single-purpose components
- Strong prop typing
- Controlled and uncontrolled modes where appropriate
- Clear empty, loading, and error states

## 10. Page Layout

### Sidebar
- Use a persistent sidebar for primary navigation in desktop layouts.
- Keep sidebar hierarchy shallow and predictable.
- Group related workspaces together.
- Highlight active section clearly.

### Top Navigation
- Reserve top navigation for global search, user actions, context switching, and system-level controls.
- Avoid cluttering the top bar with secondary actions.

### Workspace Layout
- Use a structured, modular workspace layout.
- Prioritize information hierarchy over visual complexity.
- Keep the main content area the strongest visual anchor.

### Content Width
- Default content width should support readability in dense enterprise screens.
- Avoid ultra-wide text blocks.
- Use measured max widths for long-form content.

### Page Header
- Use a concise title, supporting description, and primary action area.
- Keep page headers informative but not oversized.

### Section Header
- Use section headers to separate major content groups.
- Keep hierarchy visible without repeating unnecessary labels.

### Cards
- Use cards for grouped content, summary metrics, and isolated panels.
- Cards should create visual rhythm without overwhelming the page.

### Empty States
- Explain what the user is looking at.
- Clarify the next possible action.
- Avoid decorative emptiness.

### Loading States
- Use skeletons, placeholders, or progress indicators.
- Preserve layout stability during loading.
- Do not use flashy loading animations.

## 11. Workspaces

LinkOps workspaces define the primary product shells and future modules.

### Current and Planned Workspaces
- Mission Control
- Knowledge Workspace
- Document Workspace
- Asset Workspace
- AI Workspace
- Analytics Workspace
- Settings
- Live Monitoring
- Maintenance Intelligence
- Compliance
- Digital Twin

### Workspace Rules
- Each workspace should have a clear responsibility.
- Keep cross-workspace patterns consistent.
- Avoid designing each workspace as a unique product.
- Use shared navigation and layout structure across workspaces.

## 12. Table Design

Tables are core to enterprise workflows and must remain usable at scale.

### Required Behaviors
- Sorting
- Filtering
- Pagination
- Sticky Header
- Search
- Selection

### Table Rules
- Keep headers visible during scroll when data density is high.
- Support row-level actions without clutter.
- Make selected state obvious.
- Ensure tables degrade gracefully on smaller screens.

## 13. Forms

### Inputs
- Use clear labels.
- Keep placeholders short and helpful.
- Avoid relying on placeholder text as the only instruction.

### Dropdowns
- Use dropdowns for finite, well-defined options.
- Support keyboard navigation and searchable options when lists are long.

### Validation
- Validate inline when possible.
- Explain the issue in simple, direct language.
- Keep validation close to the field.

### Error Messages
- Be specific.
- Explain how to fix the issue.
- Avoid generic failure language.

### Buttons
- Use a single primary action per form section when possible.
- Avoid competing primary buttons.
- Place destructive actions with clear separation and confirmation where needed.

## 14. Status Colors

Status colors must map to operational meaning and remain consistent.

- Success: green
- Warning: amber
- Critical: red
- Offline: neutral gray
- Processing: blue
- Queued: cyan or neutral blue-gray
- Uploading: blue
- AI Running: cyan

### Status Rules
- Use labels alongside color.
- Do not invent new meanings for existing colors.
- Keep the same status tone throughout the product.

## 15. Motion

Motion should support understanding, not entertainment.

### Motion Rules
- Maximum duration: 200ms
- Use subtle transitions only
- Prefer linear, ease-out, or standard easing

### Allowed
- Fade
- Expand
- Collapse
- Hover

### Not Allowed
- Bounce
- Spin
- Flash

### Motion Guidance
- Motion should clarify state changes.
- Avoid movement that distracts from operational work.
- Use animation to guide attention, not to impress.

## 16. Accessibility

Accessibility is a product requirement.

### Requirements
- Keyboard Navigation
- ARIA Labels
- Contrast
- Focus States
- Screen Readers

### Accessibility Rules
- Ensure strong contrast for text and controls.
- Make focus states visible and predictable.
- All interactive controls must be keyboard reachable.
- Provide descriptive labels for icons and non-text content.
- Support screen reader comprehension with semantic markup.

## 17. Responsiveness

### Desktop First
Desktop is the primary experience for LinkOps because the product is built for operational and analytical workflows.

### Tablet
Tablet layouts should preserve hierarchy and navigation clarity.

### Mobile
Mobile should support essential operational views, summaries, and quick actions without forcing desktop complexity into a small screen.

### Responsive Rules
- Preserve clarity before compactness.
- Collapse secondary navigation thoughtfully.
- Keep key actions accessible on smaller breakpoints.

## 18. Design Rules

- Never hardcode colors.
- Always use design tokens.
- Never duplicate components.
- Prefer composition.
- Maintain consistency.

### Additional Rules
- Use clear visual hierarchy.
- Keep enterprise workflows efficient.
- Avoid decorative patterns that do not improve usability.
- Design for scale, not just the first screen.

## 19. Future UI Modules

Future interfaces should reuse the same design language and component system.

### Planned Modules
- Industrial IoT Dashboard
- Knowledge Graph Viewer
- Digital Twin
- Predictive Maintenance
- Compliance Center
- Plant Monitor
- Mission Control

### Module Guidance
- Modules should feel like part of one platform.
- Do not create separate design languages per module.
- Share patterns for navigation, table states, alerts, filtering, and detail views.

## 20. Conclusion

The LinkOps design system exists to make the platform scalable, consistent, and maintainable as the product grows. A disciplined UI language reduces design drift, lowers implementation complexity, and gives every team a stable reference for new features.

By standardizing color, typography, spacing, motion, accessibility, layouts, and component behavior, LinkOps can deliver an enterprise-quality user experience that feels reliable today and remains coherent as the platform expands into future industrial intelligence modules.
