import type { Dependency } from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface DependencyListProps {
  dependencies?: Dependency[]
  loading?: boolean
}

export function DependencyList({ dependencies, loading }: DependencyListProps) {
  return (
    <div>
      <h2 className="text-base font-semibold mb-3">NuGet Packages</h2>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Package</TableHead>
              <TableHead className="w-40">Version</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  </TableRow>
                ))
              : !dependencies || dependencies.length === 0
                ? (
                  <TableRow>
                    <TableCell colSpan={2} className="text-center text-muted-foreground py-8">
                      No dependencies found
                    </TableCell>
                  </TableRow>
                  )
                : dependencies.map(d => (
                  <TableRow key={d.name}>
                    <TableCell className="font-mono text-sm">{d.name}</TableCell>
                    <TableCell>
                      {d.version && (
                        <Badge variant="secondary" className="font-mono text-xs">
                          {d.version}
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
