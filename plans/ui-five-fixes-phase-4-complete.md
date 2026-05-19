## Phase 4 Complete: Dashboard Reshape

Replaced the 9-card StatCard hero-metrics grid with 4 compact `MetricGroup` components in a responsive 2-column layout. All 9 original stats are preserved across 4 semantic groups (Structure, Types, Members, Dependencies). `StatCard.tsx` is retained untouched.

**Files created/changed:**
- `ui/src/components/stats/MetricGroup.tsx` — new: grouped metric rows with label/value pairs, optional primary emphasis, loading skeletons
- `ui/src/pages/DashboardPage.tsx` — removed 9-card StatCard grid; added 4 MetricGroup components in `grid grid-cols-1 sm:grid-cols-2`; removed unused lucide icon imports and StatCard import
- `ui/src/components/stats/__tests__/MetricGroup.test.tsx` — new: 5 tests (title, labels, values, undefined, loading skeletons)
- `ui/src/pages/__tests__/DashboardPage.metricgroup.test.tsx` — new: 2 tests (4 group titles render, no old StatCard labels)
- `ui/src/pages/__tests__/DashboardPage.test.tsx` — updated assertions for new metric labels

**Functions created/changed:**
- `MetricGroup({ title, metrics, loading })` — new component
- `DashboardPage` — metrics block replaced; imports cleaned up

**Tests created/changed:**
- `renders the group title`
- `renders all metric labels`
- `renders metric values as localized numbers`
- `renders "—" for undefined values`
- `renders skeletons when loading is true`
- `renders the 4 MetricGroup section titles`
- `does not render any StatCard elements`

**Review Status:** APPROVED

**Git Commit Message:**
```
feat: replace StatCard grid with compact MetricGroup layout in Dashboard

- Create MetricGroup component with label/value rows and loading skeletons
- Dashboard now shows 4 groups: Structure, Types, Members, Dependencies
- Remove 9 individual stat cards and unused lucide icon imports
- StatCard.tsx retained for potential future use
- 7 new tests covering component rendering and dashboard integration
```
