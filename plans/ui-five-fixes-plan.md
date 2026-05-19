# Plan: CntxtCS UI — Five Critique Fixes

Implement all five priority issues from the impeccable critique across five bounded phases, each following TDD. Lays a frontend testing foundation first (vitest), then works from structural fixes (error handling, header) to surface improvements (dashboard, onboarding, graph filter).

**Revisions from approval:**
- Dashboard: two-column MetricGroup layout confirmed.
- Empty state command: full command string + copy button (best UX for local tool).
- Header: keep in place for future use; ProjectSelector stays in header. Phase 2 becomes header chrome cleanup (remove "Project" label, add page context to left side).

---

## Phases (5)

### Phase 1: Frontend Testing Setup + API Error Hardening

- **Objective:** Add vitest + @testing-library/react to the UI project. Fix silently-swallowed API errors in DashboardPage and ExplorerPage so users see actionable messages instead of empty tables.
- **Files/Functions to Modify/Create:**
  - `ui/package.json` — add vitest, @testing-library/react, @testing-library/user-event, jsdom
  - `ui/vite.config.ts` — add vitest `test` block (environment: jsdom)
  - `ui/src/test-setup.ts` (new) — @testing-library/jest-dom setup
  - `ui/src/pages/DashboardPage.tsx` — add `fetchError` state; change `.catch(() => null)` / `.catch(() => [])` to capture and display errors
  - `ui/src/pages/ExplorerPage.tsx` — add `fetchError` state; same error capture pattern
  - `ui/src/pages/__tests__/DashboardPage.test.tsx` (new)
  - `ui/src/pages/__tests__/ExplorerPage.test.tsx` (new)
- **Tests to Write:**
  - `renders error message when stats API returns 500`
  - `renders error message when dependencies API returns 500`
  - `renders error message when classes API returns 500`
  - `renders empty table (not error) when API returns empty array`
  - `error message includes recovery hint text about server`
- **Steps:**
  1. Install vitest, jsdom, @testing-library/react, @testing-library/user-event, @testing-library/jest-dom into `ui/`.
  2. Add `test` block to `ui/vite.config.ts`; create `ui/src/test-setup.ts`.
  3. Write failing tests for error states in DashboardPage and ExplorerPage (mock `fetch` to reject).
  4. Run tests to confirm they fail (red).
  5. In `DashboardPage.tsx`, change error-swallowing catches to `setFetchError(err instanceof Error ? err.message : 'Failed to load data')`. Render an inline error message above content when set.
  6. Apply the same pattern in `ExplorerPage.tsx`.
  7. Run tests — confirm they pass (green).
  8. Run `npm run lint`.

---

### Phase 2: Header Chrome Cleanup

- **Objective:** Remove the redundant static "Project" label from the header. Add the current route name to the left side of the header, giving it purpose as a page-identity bar rather than dead chrome. ProjectSelector stays on the right.
- **Files/Functions to Modify/Create:**
  - `ui/src/components/layout/AppShell.tsx` — replace `<span>Project</span>` with a route-aware page title component
  - `ui/src/components/layout/PageTitle.tsx` (new) — reads current route, returns the display name
  - `ui/src/components/layout/__tests__/AppShell.test.tsx` (new)
  - `ui/src/components/layout/__tests__/PageTitle.test.tsx` (new)
- **Tests to Write:**
  - `AppShell header renders PageTitle on the left and ProjectSelector on the right`
  - `AppShell header does not render static "Project" text`
  - `PageTitle renders "Dashboard" when route is "/"`
  - `PageTitle renders "Graph" when route is "/graph"`
  - `PageTitle renders "Explorer" when route is "/explorer"`
- **Steps:**
  1. Write failing tests for the updated header structure and PageTitle.
  2. Run tests to confirm they fail (red).
  3. Create `PageTitle.tsx`: use `useLocation()` from react-router-dom, map pathnames to display names (`/` → "Dashboard", `/graph` → "Graph", `/explorer` → "Explorer").
  4. In `AppShell.tsx`, replace `<span className="text-sm font-medium text-muted-foreground">Project</span>` with `<PageTitle />`.
  5. Run tests — confirm they pass (green).
  6. Run `npm run lint`.

---

### Phase 3: Empty States and Onboarding

- **Objective:** Replace dead-end "Select a project" centered text with purposeful empty states. When no projects exist, show a setup command (full CLI command + copy button). When projects exist but none is selected, prompt selection with a clear reference to the header selector.
- **Files/Functions to Modify/Create:**
  - `ui/src/components/common/EmptyState.tsx` (new) — icon, heading, body, optional `copyCommand` prop
  - `ui/src/pages/DashboardPage.tsx` — replace bare return with `<EmptyState>`
  - `ui/src/pages/ExplorerPage.tsx` — replace bare return with `<EmptyState>`
  - `ui/src/pages/GraphPage.tsx` — replace bare return with `<EmptyState>`
  - `ui/src/lib/project-context.tsx` — check if `projects.length === 0` state is already exposed (likely is via `projects` array)
  - `ui/src/components/common/__tests__/EmptyState.test.tsx` (new)
- **Tests to Write:**
  - `EmptyState renders heading and body message`
  - `EmptyState renders copy button when copyCommand is provided`
  - `EmptyState copy button writes command to clipboard`
  - `EmptyState does not render copy button when copyCommand is omitted`
  - `DashboardPage renders EmptyState when selected is null and projects exist`
  - `DashboardPage renders setup EmptyState when projects list is empty`
- **Steps:**
  1. Create `EmptyState.tsx`: accepts `heading`, `body`, optional `copyCommand`. Renders a centered layout with an icon, the heading, body text, and (when `copyCommand` is provided) a monospace code block + "Copy" button using `navigator.clipboard.writeText`.
  2. Write failing tests.
  3. Run tests to confirm they fail (red).
  4. Update `DashboardPage.tsx`: when `projects.length === 0` show setup EmptyState with the `mcp_server.py` CLI command; when `selected === null` (but projects exist) show "Select a project from the dropdown above to view its codebase overview."
  5. Apply the same two-state empty state pattern to `ExplorerPage.tsx` and `GraphPage.tsx`.
  6. Run tests — confirm they pass (green).
  7. Run `npm run lint`.

---

### Phase 4: Dashboard Reshape — Structured Codebase Summary

- **Objective:** Replace the 9-identical-card `StatCard` grid with a two-column structured `MetricGroup` layout. Group metrics by concern: Structure (files, namespaces), Types (classes, interfaces, enums, structs), Members (methods), Dependencies (NuGet packages, using directives). No card per metric; compact rows. Visually emphasize the metric that signals complexity (class count gets primary weight).
- **Files/Functions to Modify/Create:**
  - `ui/src/components/stats/MetricGroup.tsx` (new) — group label + compact metric rows
  - `ui/src/pages/DashboardPage.tsx` — replace `grid + StatCard.map()` with two-column MetricGroup layout
  - `ui/src/components/stats/__tests__/MetricGroup.test.tsx` (new)
  - `ui/src/pages/__tests__/DashboardPage.test.tsx` — extend with new structure assertions
- **Tests to Write:**
  - `MetricGroup renders group label`
  - `MetricGroup renders all metric rows with label and value`
  - `MetricGroup renders skeleton placeholders when loading is true`
  - `MetricGroup marks primary metric row with elevated visual weight`
  - `DashboardPage renders four MetricGroup sections`
  - `DashboardPage does not render any StatCard component`
- **Steps:**
  1. Design `MetricGroup.tsx`: a `<section>` with a small-caps group label row and compact `<dl>` (definition list) rows for each metric. `primary?: boolean` prop on each metric entry. Skeleton mode renders placeholder rows.
  2. Write failing tests.
  3. Run tests to confirm they fail (red).
  4. Implement `MetricGroup.tsx`.
  5. Rewrite the metrics block in `DashboardPage.tsx`: remove the responsive `grid` and `metrics.map()`, add four `<MetricGroup>` components arranged in a two-column CSS grid. Keep Full Scan button and `DependencyList` below.
  6. Run tests — confirm they pass (green).
  7. Run `npm run lint`.

---

### Phase 5: Graph Filter — Bulk Toggle + Per-Type Node Counts

- **Objective:** Add "All" and "None" toggle controls at the top of the node type filter panel. Display the per-type node count in muted styling next to each label. Pass count data from GraphPage into NodeTypeFilter.
- **Files/Functions to Modify/Create:**
  - `ui/src/components/graph/NodeTypeFilter.tsx` — add `typeCounts` prop + `onShowAll` / `onHideAll` handlers + bulk toggle UI
  - `ui/src/pages/GraphPage.tsx` — compute `typeCounts` via `useMemo`, add `handleShowAll` / `handleHideAll`, pass to `NodeTypeFilter`
  - `ui/src/components/graph/__tests__/NodeTypeFilter.test.tsx` (new)
- **Tests to Write:**
  - `NodeTypeFilter renders "All" and "None" controls`
  - `clicking "None" calls onHideAll`
  - `clicking "All" calls onShowAll`
  - `NodeTypeFilter renders count in muted text when typeCounts provided`
  - `NodeTypeFilter renders labels without counts when typeCounts is omitted`
- **Steps:**
  1. Write failing tests for the updated `NodeTypeFilter` component interface.
  2. Run tests to confirm they fail (red).
  3. Update `NodeTypeFilter` props: add `typeCounts?: Record<string, number>`, `onShowAll: () => void`, `onHideAll: () => void`.
  4. Add a header row above the type list: `"All"` and `"None"` as `<button>` elements styled as ghost links, calling their respective handlers.
  5. Render per-type count as `(n)` in `text-muted-foreground text-xs` after each label when `typeCounts` is provided.
  6. In `GraphPage.tsx`, compute `typeCounts` via `useMemo`: `graphData.nodes.reduce(...)` keyed by type. Add `handleShowAll` (`setVisibleTypes(new Set(allTypes))`) and `handleHideAll` (`setVisibleTypes(new Set())`). Pass all to `NodeTypeFilter`.
  7. Run tests — confirm they pass (green).
  8. Run `npm run lint`.
