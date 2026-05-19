import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'

interface NamespaceListProps {
  namespaces: string[]
  loading: boolean
}

export function NamespaceList({ namespaces, loading }: NamespaceListProps) {
  const [filter, setFilter] = useState('')
  const filtered = namespaces.filter(n => !filter || n.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="space-y-3">
      <Input
        placeholder="Search namespaces…"
        value={filter}
        onChange={e => setFilter(e.target.value)}
        className="h-8 w-64"
      />
      <ScrollArea className="h-[480px] rounded-md border p-3">
        {loading
          ? Array.from({ length: 10 }).map((_, i) => <Skeleton key={i} className="h-4 w-full mb-2" />)
          : filtered.length === 0
            ? <p className="text-sm text-muted-foreground text-center py-8">No namespaces found</p>
            : filtered.map(ns => (
              <p key={ns} className="font-mono text-sm py-1 border-b last:border-0">{ns}</p>
            ))}
      </ScrollArea>
      <p className="text-xs text-muted-foreground">{filtered.length} of {namespaces.length} namespaces</p>
    </div>
  )
}
