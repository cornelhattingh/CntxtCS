## Phase 5 Complete: Graph Filter Controls

Added bulk All/None toggle buttons and per-type node counts to the graph filter panel. All new props are optional, keeping the component backward compatible. GraphPage computes type counts via useMemo and wires up the show/hide-all handlers.

**Files created/changed:**
- `ui/src/components/graph/NodeTypeFilter.tsx` — added `typeCounts?`, `onShowAll?`, `onHideAll?` props; added All/None ghost buttons above the type list; added count display next to each type label
- `ui/src/pages/GraphPage.tsx` — added `handleShowAll` and `handleHideAll` handlers; added `typeCounts` useMemo computed from `graphData.nodes.reduce(...)`; passed all three to NodeTypeFilter
- `ui/src/components/graph/__tests__/NodeTypeFilter.test.tsx` — new: 7 tests

**Functions created/changed:**
- `NodeTypeFilter` — extended with optional bulk toggle + count props
- `GraphPage.handleShowAll()` — new: sets `visibleTypes` to `new Set(allTypes)`
- `GraphPage.handleHideAll()` — new: sets `visibleTypes` to `new Set()`
- `GraphPage.typeCounts` — new useMemo: reduces `graphData.nodes` to `Record<string, number>`

**Tests created/changed:**
- `renders all type labels`
- `does not render All/None buttons when handlers are not provided`
- `renders All and None buttons when handlers are provided`
- `calls onShowAll when All button is clicked`
- `calls onHideAll when None button is clicked`
- `does not render counts when typeCounts is omitted`
- `renders per-type counts when typeCounts is provided`

**Review Status:** APPROVED

**Git Commit Message:**
```
feat: add All/None toggles and per-type counts to graph filter panel

- NodeTypeFilter: optional onShowAll, onHideAll, typeCounts props
- Show All/None buttons only when handlers are provided
- Render per-type counts when typeCounts prop is present
- GraphPage: compute typeCounts via useMemo, wire up show/hide all
- 7 new tests covering conditional rendering and click handlers
```
