# Product

## Register

product

## Users

.NET developers running CntxtCS locally as a pre-flight step before handing a C# codebase to an AI agent (GitHub Copilot, Claude Code, Claude Desktop, etc.). The context of use is the gap between "I have a large codebase" and "I want an AI to reason accurately about it." The user is already in a technical workflow and wants to move fast: pick a project, orient quickly to its structure, then jump to a specific namespace, class, or dependency to confirm what the AI will receive.

## Product Purpose

CntxtCS analyzes C# codebases and generates structured knowledge graphs that reduce LLM token usage by approximately 75%. It exists because feeding raw source code to an AI is noisy and expensive; a knowledge graph is precise. Success on any given screen means the user can locate the structural fact they need in seconds and trust that the context they export is accurate.

## Brand Personality

Precise. Dense. Technical.

Voice: direct, zero fluff, confident without being loud. Labels are terse. Instructions are minimal. The tool trusts the user is a competent developer.

## Anti-references

- Corporate or enterprise-heavy UIs: no gradient banners, no oversized card grids, no KPI-dashboard chrome.
- SaaS hero-metric templates: big number + small label + supporting stats + accent gradient. The dashboard should surface structure, not celebrate activity.
- Anything that looks like it was scaffolded from an admin template and never rethought.

## Design Principles

1. **Information over decoration.** The interface exists to surface code structure. Every UI element earns its place by helping the user navigate or understand something concrete. Ornament is removed on sight.
2. **Density with clarity.** Like VS Code and Claude Code: pack meaningful information without inducing overload. Visual hierarchy does the work that whitespace alone cannot.
3. **Tool, not product.** The UI should feel like an extension of the development environment. No marketing chrome, no onboarding flows designed for conversion. The user is already here.
4. **Complexity on demand.** The interface is calm at rest. Detail is revealed through interaction — drill-down, hover, expand — not displayed all at once.
5. **Context is the product.** Every screen answers one question: "What will the AI see about this codebase?" The measure of success is how quickly the user can verify or find that answer.

## Accessibility & Inclusion

WCAG AA minimum. Keyboard navigability is a first-class concern given the developer audience. Support `prefers-reduced-motion`. Color is never the sole carrier of information (particularly in the graph view, where node types must be distinguishable by shape or label in addition to color).
