import { useEffect, useMemo, useState } from 'react'
import { api, type GraphData, type GraphNode } from '@/lib/api'
import { useProject } from '@/lib/project-context'
import { GraphCanvas } from '@/components/graph/GraphCanvas'
import { NodeTypeFilter, NodeDetailPanelContent } from '@/components/graph/NodeTypeFilter'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Skeleton } from '@/components/ui/skeleton'
import { EmptyState } from '@/components/common/EmptyState'

export function GraphPage() {
  const { selected } = useProject()
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] })
  const [loading, setLoading] = useState(false)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)

  // Derive all unique node types from the data
  const allTypes = useMemo(
    () => [...new Set(graphData.nodes.map(n => n.type))].sort(),
    [graphData],
  )
  const [visibleTypes, setVisibleTypes] = useState<Set<string>>(new Set())

  // Keep visibleTypes in sync when new data loads
  useEffect(() => {
    setVisibleTypes(new Set(allTypes))
  }, [allTypes])

  useEffect(() => {
    if (!selected) return
    setLoading(true)
    api.getGraph(selected)
      .then(setGraphData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [selected])

  function toggleType(t: string) {
    setVisibleTypes(prev => {
      const next = new Set(prev)
      next.has(t) ? next.delete(t) : next.add(t)
      return next
    })
  }

  function handleShowAll() {
    setVisibleTypes(new Set(allTypes))
  }

  function handleHideAll() {
    setVisibleTypes(new Set())
  }

  const typeCounts = useMemo(
    () =>
      graphData.nodes.reduce<Record<string, number>>((acc, n) => {
        acc[n.type] = (acc[n.type] ?? 0) + 1
        return acc
      }, {}),
    [graphData],
  )

  function handleNodeClick(node: GraphNode) {
    setSelectedNode(node)
    setSheetOpen(true)
  }

  if (!selected) {
    return (
      <EmptyState
        heading="No project selected"
        body="Select a project from the header to visualise its dependency graph."
      />
    )
  }

  return (
    <div className="flex h-full gap-4">
      {/* Filter panel */}
      <aside className="w-48 shrink-0 space-y-4 overflow-y-auto">
        <div>
          <h1 className="text-lg font-bold">{selected}</h1>
          <p className="text-xs text-muted-foreground">
            {graphData.nodes.length.toLocaleString()} nodes ·{' '}
            {graphData.links.length.toLocaleString()} edges
          </p>
        </div>
        {loading
          ? Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-5 w-full" />)
          : <NodeTypeFilter types={allTypes} visible={visibleTypes} onToggle={toggleType} typeCounts={typeCounts} onShowAll={handleShowAll} onHideAll={handleHideAll} />}
      </aside>

      {/* Graph canvas */}
      <div className="flex-1 min-w-0 min-h-0">
        {loading
          ? <Skeleton className="w-full h-full rounded-md" />
          : (
            <GraphCanvas
              data={graphData}
              visibleTypes={visibleTypes}
              onNodeClick={handleNodeClick}
            />
            )}
      </div>

      {/* Detail sheet */}
      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Node Detail</SheetTitle>
          </SheetHeader>
          <div className="mt-4 px-1">
            <NodeDetailPanelContent node={selectedNode} />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
}
