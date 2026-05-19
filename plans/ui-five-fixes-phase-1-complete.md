## Phase 1 Complete: Frontend Testing Setup + API Error Hardening

Added vitest + @testing-library/react to the UI project and fixed silently-swallowed API errors in DashboardPage and ExplorerPage. Users now see an actionable error message when the backend is unreachable, instead of silently empty tables.

**Files created/changed:**
- `ui/package.json` — added vitest, @testing-library/react, @testing-library/user-event, @testing-library/jest-dom, jsdom; added `test` script
- `ui/vite.config.ts` — added vitest `test` block (environment: jsdom, setupFiles)
- `ui/src/test-setup.ts` — new: imports @testing-library/jest-dom matchers
- `ui/src/pages/DashboardPage.tsx` — added `fetchError` state; changed silent `.catch()` to `Promise.all().catch()`; clears both `fetchError` and `scanError` on project change
- `ui/src/pages/ExplorerPage.tsx` — same error-capture pattern as DashboardPage
- `ui/src/pages/__tests__/DashboardPage.test.tsx` — new: 3 tests (empty state, API error, successful load)
- `ui/src/pages/__tests__/ExplorerPage.test.tsx` — new: 3 tests (empty state, API error, successful load)

**Functions created/changed:**
- `DashboardPage.loadData()` — now uses `Promise.all().catch(setFetchError)` + clears `scanError`
- `ExplorerPage` data-fetch `useEffect` — same error-capture pattern

**Tests created/changed:**
- `renders empty state when selected is null` (Dashboard + Explorer)
- `shows error message when API fails` (Dashboard + Explorer)
- `renders data when API succeeds` (Dashboard + Explorer)

**Review Status:** APPROVED

**Git Commit Message:**
```
feat: add vitest and surface API fetch errors in Dashboard and Explorer

- Install vitest, @testing-library/react, jsdom for frontend testing
- DashboardPage: catch Promise.all failure, show error message to user
- ExplorerPage: same error-surface pattern
- Clear scanError on project change to prevent stale error display
- 6 unit tests covering error states, empty states, and happy path
```
