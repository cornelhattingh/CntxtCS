---
name: CntxtCS
description: C# knowledge graph viewer for LLM-ready codebase analysis
colors:
  signal-violet: "oklch(0.52 0.28 303)"
  signal-violet-dim: "oklch(0.65 0.22 300)"
  signal-violet-ghost: "oklch(0.52 0.28 303 / 0.1)"
  source-white: "oklch(1 0 0)"
  graphite-near: "oklch(0.985 0 0)"
  graphite-subtle: "oklch(0.97 0 0)"
  graphite-border: "oklch(0.922 0 0)"
  graphite-inactive: "oklch(0.556 0 0)"
  graphite-surface: "oklch(0.205 0 0)"
  graphite-deep: "oklch(0.145 0 0)"
  destructive: "oklch(0.577 0.245 27.325)"
  node-file: "#64748b"
  node-namespace: "#7c3aed"
  node-class: "#2563eb"
  node-interface: "#0891b2"
  node-method: "#16a34a"
  node-property: "#d97706"
  node-field: "#ea580c"
  node-dependency: "#dc2626"
  node-enum: "#db2777"
  node-struct: "#0284c7"
  node-event: "#9333ea"
typography:
  headline:
    fontFamily: "'Geist Variable', sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  title:
    fontFamily: "'Geist Variable', sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "'Geist Variable', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'Geist Variable', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.02em"
  mono:
    fontFamily: "ui-monospace, Consolas, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: "6px"
  md: "8px"
  lg: "10px"
  xl: "14px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-default:
    backgroundColor: "{colors.graphite-deep}"
    textColor: "{colors.source-white}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-default-hover:
    backgroundColor: "{colors.graphite-surface}"
    textColor: "{colors.source-white}"
    rounded: "{rounded.lg}"
  button-outline:
    backgroundColor: "{colors.source-white}"
    textColor: "{colors.graphite-deep}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.graphite-inactive}"
    rounded: "{rounded.lg}"
  button-ghost-hover:
    backgroundColor: "{colors.graphite-subtle}"
    textColor: "{colors.graphite-deep}"
    rounded: "{rounded.lg}"
  nav-item-active:
    backgroundColor: "{colors.graphite-deep}"
    textColor: "{colors.source-white}"
    rounded: "{rounded.lg}"
    padding: "8px 12px"
  nav-item-default:
    backgroundColor: "transparent"
    textColor: "{colors.graphite-inactive}"
    rounded: "{rounded.lg}"
    padding: "8px 12px"
  nav-item-hover:
    backgroundColor: "{colors.graphite-subtle}"
    textColor: "{colors.graphite-deep}"
    rounded: "{rounded.lg}"
  card:
    backgroundColor: "{colors.source-white}"
    textColor: "{colors.graphite-deep}"
    rounded: "{rounded.lg}"
    padding: "24px"
  input:
    backgroundColor: "{colors.source-white}"
    textColor: "{colors.graphite-deep}"
    rounded: "{rounded.lg}"
    padding: "0 12px"
    height: "32px"
---

# Design System: CntxtCS

## 1. Overview

**Creative North Star: "The Static Analyzer"**

CntxtCS operates like a static analysis tool applied to its own interface. The same qualities that make a compiler or linter valuable — precision, structured output, zero noise, authority — govern every design decision here. The interface does not celebrate itself. It processes, reports, navigates. When a developer opens CntxtCS, they are already in the middle of a workflow; the UI's job is to keep them there, not interrupt.

The aesthetic reference is VS Code's Explorer panel meeting Claude Code's terminal-adjacent calm: dense without being hostile, structured without being rigid, informative without being loud. This is not a SaaS dashboard showcasing its own activity. It is a working surface for working developers. Surfaces are restrained by default, with Signal Violet appearing precisely where the system needs to assert focus or signal interactivity.

The theme follows the user's environment (light / dark / system), with full support for tweakcn theme overrides. All tokens are carried in CSS custom properties; no value is hard-coded into components. The dark mode inverts the neutral ramp (Graphite Deep becomes the background; Source White becomes the primary surface accent) while Signal Violet shifts from saturated (`#aa3bff`) to its dimmed variant (`#c084fc`) to preserve legibility on dark grounds.

**Key Characteristics:**
- Single typeface (Geist Variable) across all contexts; weight is the hierarchy instrument
- Neutral base with Signal Violet as the sole intentional accent
- Flat-by-default surfaces; shadows appear only to communicate elevation or state
- Graph canvas node colors are categorical and independent of the UI palette
- Every label earns its place; metadata is muted, not absent

## 2. Colors: The Signal/Source Palette

A restrained neutral base with one saturated accent that earns its place by marking selection, focus, and the active system state.

### Primary
- **Signal Violet** (`oklch(0.52 0.28 303)` / `#aa3bff`): The sole intentional accent. Used for active-state indicators, focus rings, accent borders, and interactive highlights. Its ghost form (`signal-violet-ghost`, 10% opacity) fills accent background surfaces. In dark mode, shifts to **Signal Violet Dim** (`oklch(0.65 0.22 300)` / `#c084fc`) — reduced chroma to maintain contrast without glare.

### Secondary
- **Sidebar Active Blue** (`oklch(0.488 0.243 264.376)`): Appears only in the dark-mode sidebar as the active nav item background. It departs from Signal Violet intentionally to respect the indigo-shifted dark palette that tweakcn themes may override. Does not appear in light mode.

### Neutral
- **Source White** (`oklch(1 0 0)` / `#ffffff`): Page background in light mode; the lightest reachable surface.
- **Graphite Near** (`oklch(0.985 0 0)` / `#fafafa`): Sidebar background in light mode; elevated surface slightly offset from page.
- **Graphite Subtle** (`oklch(0.97 0 0)` / `#f5f5f5`): Muted backgrounds, hover fills for ghost buttons.
- **Graphite Border** (`oklch(0.922 0 0)` / `#ebebeb`): All structural dividers — sidebar edge, header bottom, card borders, tab separators.
- **Graphite Inactive** (`oklch(0.556 0 0)` / `#737373`): Muted text, inactive nav labels, metadata, icon fills at rest.
- **Graphite Surface** (`oklch(0.205 0 0)` / `#2e2e2e`): Active nav background in light mode; dark surface in cards when dark mode is on.
- **Graphite Deep** (`oklch(0.145 0 0)` / `#1c1c1c`): Primary text; the darkest reachable surface.

### Graph Node Palette (categorical, canvas-only)
These colors exist only in the force-graph canvas. They are not UI palette colors and must not bleed into surface design. Each maps to a C# construct type:

| Type | Color | Hex |
|---|---|---|
| namespace | Violet | `#7c3aed` |
| class | Blue | `#2563eb` |
| struct | Sky | `#0284c7` |
| interface | Cyan | `#0891b2` |
| method | Green | `#16a34a` |
| property | Amber | `#d97706` |
| field | Orange | `#ea580c` |
| event | Purple | `#9333ea` |
| enum | Pink | `#db2777` |
| enum_member | Rose | `#be185d` |
| dependency | Red | `#dc2626` |
| file | Slate | `#64748b` |

### Named Rules
**The One Accent Rule.** Signal Violet appears on ≤10% of any given screen. Every use must mark something: active state, focus ring, selection indicator, or the project's accent border. Decorative violet is disqualifying.

**The Graph Firewall Rule.** Node colors are categorical data. Never repurpose `#7c3aed` or `#2563eb` in surface UI — even if they appear to match violet or blue in the brand palette. The graph canvas is a data layer; the surface layer has its own color logic.

## 3. Typography

**Primary Font:** Geist Variable (`@fontsource-variable/geist`), sans-serif fallback
**Mono Font:** `ui-monospace, Consolas, monospace` (system stack)

No separate display or heading font. A single variable-font family controlled entirely through weight delivers the full hierarchy. This is consistent with VS Code, where one typeface does all the work.

**Character:** Geist Variable is clean and neutral at low weights, assertive and authoritative at 700. Its variable axis means transitions between states can be weight-animated without layout shift. At small sizes it reads with exceptional clarity — appropriate for a tool where 12px label text carries real information.

### Hierarchy
- **Headline** (700, 1.5rem / 24px, line-height 1.3, letter-spacing −0.01em): Page-level titles. One per route. Appears once, above the primary content.
- **Title** (600, 1.125rem / 18px, line-height 1.4): Section subheadings, selected node names in detail panels.
- **Body** (400, 0.875rem / 14px, line-height 1.5): Primary interface text, table cell content, list items. Max line length 65ch where text wraps.
- **Label** (500, 0.75rem / 12px, line-height 1.4, letter-spacing 0.02em): Metadata, column headers (often uppercase + tracking), muted-foreground contexts.
- **Mono** (400, 0.875rem / 14px, line-height 1.5): Code snippets, counters, fully-qualified type names, `tabular-nums` contexts.

### Named Rules
**The Weight Hierarchy Rule.** Scale alone does not create hierarchy. Every step up in visual prominence requires a weight increase (≥100 weight units above the step below). A 12px/500 label over a 14px/400 body is correct. A 14px/400 heading over 14px/400 body is invisible structure.

## 4. Elevation

This system is flat by default. Structural dividers (borders) establish spatial relationships on static surfaces. Shadows enter only when a surface is raised above the ambient layer — meaning it floats, responds to interaction, or needs to communicate that it can be dismissed.

### Shadow Vocabulary
- **Surface Rest**: no shadow. Borders only (`1px solid {colors.graphite-border}`). Cards, sidebar, header, tab containers.
- **Surface Raised** (`rgba(0,0,0,0.10) 0 10px 15px -3px, rgba(0,0,0,0.05) 0 4px 6px -2px`): For cards and panels that need to read as lifted above the page. Use sparingly — not every card is raised.
- **Overlay** (dark mode escalates: `rgba(0,0,0,0.40) 0 10px 15px -3px, rgba(0,0,0,0.25) 0 4px 6px -2px`): Dropdown menus, sheet panels, floating sidebars. Anything that occludes other content.

### Named Rules
**The Flat-By-Default Rule.** A surface is flat until proven otherwise. Elevation is earned by function, not applied for visual interest. If the surface neither floats nor occludes, it has no shadow.

## 5. Components

### Buttons
Clean, rectilinear, weight-forward. No gradient, no shadow, no movement unless state requires it.
- **Shape:** `rounded-lg` (10px). Consistent across all variants.
- **Default (Primary):** `background: graphite-deep` / `text: source-white`. Height 32px, padding 0 10px. Hover: shifts to `graphite-surface`.
- **Outline:** `background: source-white` / `border: graphite-border` / `text: graphite-deep`. Hover: fills `graphite-subtle`.
- **Ghost:** No background, no border. Text at `graphite-inactive`. Hover: fills `graphite-subtle`, text shifts to `graphite-deep`.
- **Destructive:** `background: destructive/10` / `text: destructive`. Never used for primary actions.
- **Focus:** `ring-3` with `signal-violet/50`. Keyboard focus is visible and styled with the accent.
- **Active:** `translate-y-px` on press (not aria-haspopup).

### Cards / Containers
The default Card uses a border (`graphite-border`) on a `source-white` background with no shadow. Shadow is applied only when the card needs to read as visually raised (i.e., interactive lift, detail panel, elevated content).
- **Corner Style:** `rounded-lg` (10px).
- **Background:** `source-white` (light) / `graphite-surface` (dark).
- **Shadow Strategy:** None by default. Use Surface Raised shadow only for explicitly elevated cards.
- **Border:** `1px solid graphite-border`.
- **Internal Padding:** `CardHeader` / `CardContent` use standard shadcn layout (16px vertical rhythm).

### Inputs / Fields
- **Style:** Thin stroke (`border: graphite-border`), `source-white` fill, `rounded-lg`.
- **Focus:** `border: ring`, `ring-3 ring-ring/50` — not Signal Violet on inputs (ring color is neutral to avoid over-accenting form fields).
- **Error:** `border-destructive`, `ring-destructive/20`.
- **Disabled:** `opacity-50`, `pointer-events-none`.

### Navigation Sidebar
The sidebar is 224px fixed, `graphite-near` background in light mode, bordered on the right with `graphite-border`. Nav items use the `rounded-lg` shape with tight internal padding (8px 12px).
- **Active:** `background: graphite-deep` / `text: source-white`. In dark mode: `background: oklch(0.488 0.243 264.376)` / `text: source-white`.
- **Default:** No background. `text: graphite-inactive`.
- **Hover:** `background: graphite-subtle` / `text: graphite-deep`.
- **Icon size:** 16×16px. Matches text baseline optically.
- **Footer:** 11px / label weight. `text: graphite-inactive`. "C# Knowledge Graph" identifier.

### Tabs
Standard shadcn tabs. `TabsList` uses `graphite-subtle` fill. Active trigger uses `source-white` with `graphite-surface` text; inactive uses transparent with `graphite-inactive` text. Count badges inside triggers are `text-xs opacity-70` — present but subordinate.

### Graph Canvas (Signature Component)
The force-directed graph canvas is a data visualization layer, not a UI surface. It renders on a `bg-muted/20` background (near-transparent graphite-subtle), bordered with `graphite-border`, `rounded-md`.
- Link lines: `#94a3b888` (slate-400 at ~53% opacity). Structural, not decorative.
- Node colors: categorical palette (see Colors § Graph Node Palette). Shape is circular, sized by `nodeRelSize: 5`.
- Node type filter panel (sidebar-within-graph): `text-xs / label` weight, color swatches via inline `background` style.
- Keyboard: `zoomToFit` fires on engine stop. Nodes are clickable (detail panel opens).

### Stat Metrics (Dashboard)
Stat cards show a count + label + icon. Three constraints to avoid the SaaS hero-metric anti-pattern: (1) no gradient accents on the value; (2) no large decorative number treatments; (3) value is `tabular-nums`, not display-scale.
- Value: `text-3xl font-bold tabular-nums` — legible, not theatrical.
- Label: `text-sm font-medium text-muted-foreground`.
- Icon: `muted-foreground` at 16×16px.

## 6. Do's and Don'ts

### Do:
- **Do** use Signal Violet exclusively for active states, focus rings, and accent borders. Its rarity is the point.
- **Do** use borders (`1px solid graphite-border`) as the default spatial separator. Shadows are earned, not automatic.
- **Do** use Geist Variable with weight contrast (≥100 units between hierarchy levels) rather than scale alone.
- **Do** keep `tabular-nums` on any numeric data that may change — counters, stat values, method counts.
- **Do** keep graph node colors isolated to the canvas layer. Never repurpose them as UI brand colors.
- **Do** ensure every interactive element has a visible keyboard focus state using the `ring-3 ring-signal-violet/50` pattern.
- **Do** reduce chroma on Signal Violet in dark mode (`#c084fc` instead of `#aa3bff`) to preserve legibility without glare.
- **Do** support `prefers-reduced-motion`: remove transitions and `translate-y-px` active effects when the preference is active.

### Don't:
- **Don't** add gradient banners, colored header bars, or accent fills to structural surfaces. The header and sidebar background are neutral.
- **Don't** use the SaaS hero-metric template: big number + small label + supporting stats + gradient accent. Stat cards use plain weight and color only.
- **Don't** use side-stripe borders (`border-left` > 1px as a colored accent) on cards, list items, or callouts. Use full borders, background tints, or nothing.
- **Don't** use gradient text (`background-clip: text`). Emphasis is weight or size, never gradient.
- **Don't** use glassmorphism effects for decoration. Blurs and translucency have no role in this system.
- **Don't** render graph node colors (`#7c3aed`, `#2563eb`, etc.) outside the graph canvas, even if they visually resemble the brand palette.
- **Don't** introduce a second typeface. Geist Variable handles all contexts. A second family adds visual noise without hierarchy benefit.
- **Don't** nest cards. A card inside a card is always a layout failure; flatten or use a section within the card.
- **Don't** treat every data group as a card. Tables, plain lists, and bordered sections are lower-noise alternatives for dense information.
