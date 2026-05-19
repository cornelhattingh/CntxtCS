import { useState } from 'react'
import type { InterfaceInfo } from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface InterfaceTableProps {
  interfaces: InterfaceInfo[]
  loading: boolean
}

export function InterfaceTable({ interfaces, loading }: InterfaceTableProps) {
  const [filter, setFilter] = useState('')
  const filtered = interfaces.filter(i =>
    !filter || i.name.toLowerCase().includes(filter.toLowerCase()),
  )

  return (
    <div className="space-y-3">
      <Input
        placeholder="Search interfaces…"
        value={filter}
        onChange={e => setFilter(e.target.value)}
        className="h-8 w-64"
      />
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Interface</TableHead>
              <TableHead>Access</TableHead>
              <TableHead>Inherits</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    {[0, 1, 2].map(j => (
                      <TableCell key={j}><div className="h-4 bg-muted animate-pulse rounded" /></TableCell>
                    ))}
                  </TableRow>
                ))
              : filtered.length === 0
                ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground py-8">
                      No interfaces found
                    </TableCell>
                  </TableRow>
                  )
                : filtered.map(iface => (
                  <TableRow key={iface.name}>
                    <TableCell className="font-mono text-sm font-medium">{iface.name}</TableCell>
                    <TableCell>
                      {iface.access_modifier && (
                        <Badge variant="outline" className="text-xs">{iface.access_modifier}</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground font-mono">
                      {iface.inherits}
                    </TableCell>
                  </TableRow>
                ))}
          </TableBody>
        </Table>
      </div>
      <p className="text-xs text-muted-foreground">{filtered.length} of {interfaces.length} interfaces</p>
    </div>
  )
}
