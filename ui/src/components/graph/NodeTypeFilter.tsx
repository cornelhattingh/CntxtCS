import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import type { GraphNode } from '@/lib/api'

export const NODE_COLORS: Record<string, string> = {
  file: '#64748b',          // slate
  namespace: '#7c3aed',     // violet
  class: '#2563eb',         // blue
  interface: '#0891b2',     // cyan
  method: '#16a34a',        // green
  property: '#d97706',      // amber
  field: '#ea580c',         // orange
  dependency: '#dc2626',    // red
  enum: '#db2777',          // pink
  struct: '#0284c7',        // sky
  event: '#9333ea',         // purple
  enum_member: '#be185d',   // rose
  dependency_file: '#b45309', // amber-dark
}

const DEFAULT_COLOR = '#94a3b8'

export function nodeColor(type: string): string {
  return NODE_COLORS[type] ?? DEFAULT_COLOR
}

interface NodeTypeFilterProps {
  types: string[]
  visible: Set<string>
  onToggle: (type: string) => void
  typeCounts?: Record<string, number>
  onShowAll?: () => void
  onHideAll?: () => void
}

export function NodeTypeFilter({ types, visible, onToggle, typeCounts, onShowAll, onHideAll }: NodeTypeFilterProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          Node Types
        </p>
        {(onShowAll || onHideAll) && (
          <div className="flex gap-2">
            {onShowAll && (
              <button
                onClick={onShowAll}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                All
              </button>
            )}
            {onHideAll && (
              <button
                onClick={onHideAll}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                None
              </button>
            )}
          </div>
        )}
      </div>
      {types.map(t => (
        <label key={t} className="flex items-center gap-2 cursor-pointer">
          <Checkbox
            checked={visible.has(t)}
            onCheckedChange={() => onToggle(t)}
          />
          <span
            className="h-2.5 w-2.5 rounded-full shrink-0"
            style={{ background: nodeColor(t) }}
          />
          <span className="text-sm capitalize flex-1">{t.replace(/_/g, ' ')}</span>
          {typeCounts !== undefined && (
            <span className="text-xs text-muted-foreground tabular-nums">
              {typeCounts[t] ?? 0}
            </span>
          )}
        </label>
      ))}
    </div>
  )
}

interface NodeDetailPanelContentProps {
  node: GraphNode | null
}

export function NodeDetailPanelContent({ node }: NodeDetailPanelContentProps) {
  if (!node) return null
  const attrs = node.attributes ?? {}
  return (
    <div className="space-y-3 text-sm">
      <div className="flex flex-wrap gap-1">
        <Badge style={{ background: nodeColor(node.type) }} className="text-white text-xs">
          {node.type}
        </Badge>
      </div>
      <div>
        <p className="font-semibold text-base break-all">{node.name}</p>
        <p className="text-xs text-muted-foreground break-all mt-0.5">{node.id}</p>
      </div>
      {Object.entries(attrs)
        .filter(([, v]) => v != null && v !== '')
        .map(([k, v]) => (
          <div key={k}>
            <p className="text-xs font-medium text-muted-foreground capitalize">{k.replace(/_/g, ' ')}</p>
            <p className="break-all">{String(v)}</p>
          </div>
        ))}
    </div>
  )
}
