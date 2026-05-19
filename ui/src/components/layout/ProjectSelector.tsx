import { useProject } from '@/lib/project-context'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

export function ProjectSelector() {
  const { projects, selected, setSelected, loading } = useProject()

  if (loading) return <Skeleton className="h-8 w-40" />
  if (projects.length === 0) return <span className="text-sm text-muted-foreground">No projects</span>

  return (
    <Select value={selected ?? ''} onValueChange={(v: string | null) => { if (v) setSelected(v) }}>
      <SelectTrigger className="w-48 h-8 text-sm">
        <SelectValue placeholder="Select project…" />
      </SelectTrigger>
      <SelectContent>
        {projects.map(p => (
          <SelectItem key={p} value={p}>
            {p}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
