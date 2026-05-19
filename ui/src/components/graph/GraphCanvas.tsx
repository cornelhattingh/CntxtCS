import { useCallback, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { GraphData, GraphNode } from '@/lib/api'
import { nodeColor } from './NodeTypeFilter'

interface GraphCanvasProps {
  data: GraphData
  visibleTypes: Set<string>
  onNodeClick: (node: GraphNode) => void
}

export function GraphCanvas({ data, visibleTypes, onNodeClick }: GraphCanvasProps) {
  const fgRef = useRef<{ zoomToFit: (ms: number) => void } | null>(null)

  // Filter nodes and links by visible types
  const filteredNodes = data.nodes.filter(n => visibleTypes.has(n.type))
  const filteredIds = new Set(filteredNodes.map(n => n.id))
  const filteredLinks = data.links.filter(
    l =>
      filteredIds.has(typeof l.source === 'object' ? (l.source as GraphNode).id : l.source) &&
      filteredIds.has(typeof l.target === 'object' ? (l.target as GraphNode).id : l.target),
  )

  const filtered = { nodes: filteredNodes, links: filteredLinks }

  const handleNodeClick = useCallback(
    (node: object) => onNodeClick(node as GraphNode),
    [onNodeClick],
  )

  return (
    <div className="w-full h-full rounded-md border bg-muted/20 overflow-hidden">
      <ForceGraph2D
        ref={fgRef as never}
        graphData={filtered}
        nodeId="id"
        nodeLabel="name"
        nodeColor={(n) => nodeColor((n as GraphNode).type)}
        nodeRelSize={5}
        linkColor={() => '#94a3b888'}
        linkWidth={0.8}
        onNodeClick={handleNodeClick}
        onEngineStop={() => fgRef.current?.zoomToFit(400)}
        warmupTicks={80}
        cooldownTicks={0}
      />
    </div>
  )
}
