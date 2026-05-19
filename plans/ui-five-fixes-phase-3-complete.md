## Phase 3 Complete: Empty States and Onboarding

Replaced bare "Select a project" text across all three pages with a proper `EmptyState` component. The Dashboard empty state includes the full setup CLI command in a monospace block with a one-click copy button — actionable first-run guidance. Explorer and Graph show a simpler version directing users to the header selector.

**Files created/changed:**
- `ui/src/components/common/EmptyState.tsx` — new: heading + body + optional copyCommand with copy-to-clipboard button
- `ui/src/pages/DashboardPage.tsx` — !selected branch now uses EmptyState with setup command
- `ui/src/pages/ExplorerPage.tsx` — !selected branch now uses EmptyState (no command)
- `ui/src/pages/GraphPage.tsx` — !selected branch now uses EmptyState (no command)
- `ui/src/components/common/__tests__/EmptyState.test.tsx` — new: 5 tests
- `ui/src/pages/__tests__/DashboardPage.emptystate.test.tsx` — new: 3 tests
- `ui/src/pages/__tests__/DashboardPage.test.tsx` — updated assertions to match new EmptyState
- `ui/src/pages/__tests__/ExplorerPage.test.tsx` — updated assertions to match new EmptyState

**Functions created/changed:**
- `EmptyState({ heading, body, copyCommand })` — new reusable component
- `DashboardPage` — !selected return replaced
- `ExplorerPage` — !selected return replaced
- `GraphPage` — !selected return replaced

**Tests created/changed:**
- `renders heading and body text`
- `does not render the command block when copyCommand is omitted`
- `renders the command text and copy button when copyCommand is provided`
- `copies the command to clipboard when the copy button is clicked`
- `shows the check icon (confirmation) after clicking copy`
- `shows EmptyState heading when no project is selected`
- `shows the setup command in the empty state`
- `shows the copy button in the Dashboard empty state`

**Review Status:** APPROVED

**Git Commit Message:**
```
feat: add EmptyState component with onboarding CLI command

- Create reusable EmptyState with heading, body, and optional copy command
- DashboardPage empty state shows setup CLI command with copy button
- ExplorerPage and GraphPage show contextual empty messages
- 8 new tests covering component rendering and clipboard copy
```
