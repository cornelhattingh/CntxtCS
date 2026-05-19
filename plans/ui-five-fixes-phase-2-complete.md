## Phase 2 Complete: Header Chrome Cleanup

Removed the static "Project" label from the AppShell header and replaced it with a route-aware `PageTitle` component. The header now shows the current page name (Dashboard / Graph / Explorer) on the left and `ProjectSelector` on the right. No other layout changes made.

**Files created/changed:**
- `ui/src/components/layout/PageTitle.tsx` — new: reads `useLocation().pathname`, maps to display name
- `ui/src/components/layout/AppShell.tsx` — replaced `<span>Project</span>` with `<PageTitle />`
- `ui/src/components/layout/__tests__/PageTitle.test.tsx` — new: 4 tests for route-to-title mapping + styling
- `ui/src/components/layout/__tests__/AppShell.test.tsx` — new: 4 tests for composition and absence of static label

**Functions created/changed:**
- `PageTitle()` — new component; uses `useLocation()` to return current page display name

**Tests created/changed:**
- `renders "Dashboard" at route "/"`
- `renders "Graph" at route "/graph"`
- `renders "Explorer" at route "/explorer"`
- `renders the title with muted styling class`
- `renders the header with PageTitle on the left`
- `renders the header with ProjectSelector on the right`
- `does not render the static "Project" text`
- `renders the sidebar`

**Review Status:** APPROVED

**Git Commit Message:**
```
feat: replace static header label with route-aware PageTitle component

- Remove static "Project" span from AppShell header
- Add PageTitle component that reads useLocation to display page name
- Dashboard / Graph / Explorer routes all resolved
- 8 new tests covering component rendering and route mapping
```
