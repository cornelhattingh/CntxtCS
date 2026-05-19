import { useState } from 'react'
import { FileCode2 } from 'lucide-react'
import type { FileInfo } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'

interface FileTreeProps {
  files: FileInfo[]
  loading: boolean
}

export function FileTree({ files, loading }: FileTreeProps) {
  const [filter, setFilter] = useState('')
  const filtered = files.filter(f =>
    !filter || (f.path ?? f.node_name).toLowerCase().includes(filter.toLowerCase()),
  )

  return (
    <div className="space-y-3">
      <Input
        placeholder="Search files…"
        value={filter}
        onChange={e => setFilter(e.target.value)}
        className="h-8 w-64"
      />
      <ScrollArea className="h-[480px] rounded-md border p-3">
        {loading
          ? Array.from({ length: 10 }).map((_, i) => <Skeleton key={i} className="h-4 w-full mb-2" />)
          : filtered.length === 0
            ? <p className="text-sm text-muted-foreground text-center py-8">No files found</p>
            : filtered.map(f => {
                const label = f.path ?? f.node_name
                return (
                  <div key={label} className="flex items-center gap-2 py-1 border-b last:border-0">
                    <FileCode2 className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span className="font-mono text-xs break-all">{label}</span>
                  </div>
                )
              })}
      </ScrollArea>
      <p className="text-xs text-muted-foreground">{filtered.length} of {files.length} files</p>
    </div>
  )
}
