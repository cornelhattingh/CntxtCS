import { useState } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from '@tanstack/react-table'
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'
import type { ClassInfo } from '@/lib/api'
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
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'

const col = createColumnHelper<ClassInfo>()

const columns = [
  col.accessor('name', {
    header: 'Class Name',
    cell: info => <span className="font-medium font-mono text-sm">{info.getValue()}</span>,
  }),
  col.accessor('access_modifier', {
    header: 'Access',
    cell: info => info.getValue()
      ? <Badge variant="outline" className="text-xs">{info.getValue()}</Badge>
      : null,
  }),
  col.accessor('modifiers', {
    header: 'Modifiers',
    cell: info => info.getValue()
      ? <span className="text-xs text-muted-foreground">{info.getValue()}</span>
      : null,
  }),
  col.accessor('inherits', {
    header: 'Inherits',
    cell: info => info.getValue()
      ? <span className="text-xs font-mono text-muted-foreground">{info.getValue()}</span>
      : null,
  }),
]

interface ClassTableProps {
  classes: ClassInfo[]
  loading: boolean
}

export function ClassTable({ classes, loading }: ClassTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: 'name', desc: false }])
  const [globalFilter, setGlobalFilter] = useState('')
  const [selected, setSelected] = useState<ClassInfo | null>(null)
  const [open, setOpen] = useState(false)

  const table = useReactTable({
    data: classes,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  const SortIcon = ({ id }: { id: string }) => {
    const sort = sorting.find(s => s.id === id)
    if (!sort) return <ChevronsUpDown className="h-3 w-3 opacity-40" />
    return sort.desc
      ? <ChevronDown className="h-3 w-3" />
      : <ChevronUp className="h-3 w-3" />
  }

  return (
    <div className="space-y-3">
      <Input
        placeholder="Search classes…"
        value={globalFilter}
        onChange={e => setGlobalFilter(e.target.value)}
        className="h-8 w-64"
      />
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map(hg => (
              <TableRow key={hg.id}>
                {hg.headers.map(header => (
                  <TableHead
                    key={header.id}
                    className="cursor-pointer select-none"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      <SortIcon id={header.id} />
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {loading
              ? Array.from({ length: 8 }).map((_, i) => (
                  <TableRow key={i}>
                    {columns.map((_, j) => (
                      <TableCell key={j}><div className="h-4 bg-muted animate-pulse rounded" /></TableCell>
                    ))}
                  </TableRow>
                ))
              : table.getRowModel().rows.length === 0
                ? (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="text-center text-muted-foreground py-8">
                      No classes found
                    </TableCell>
                  </TableRow>
                  )
                : table.getRowModel().rows.map(row => (
                  <TableRow
                    key={row.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => { setSelected(row.original); setOpen(true) }}
                  >
                    {row.getVisibleCells().map(cell => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
          </TableBody>
        </Table>
      </div>
      <p className="text-xs text-muted-foreground">
        {table.getFilteredRowModel().rows.length} of {classes.length} classes
      </p>

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle className="font-mono">{selected?.name}</SheetTitle>
          </SheetHeader>
          <div className="mt-4 space-y-3 text-sm px-1">
            {selected?.access_modifier && (
              <div>
                <p className="text-xs text-muted-foreground">Access</p>
                <Badge variant="outline">{selected.access_modifier}</Badge>
              </div>
            )}
            {selected?.modifiers && (
              <div>
                <p className="text-xs text-muted-foreground">Modifiers</p>
                <p>{selected.modifiers}</p>
              </div>
            )}
            {selected?.inherits && (
              <div>
                <p className="text-xs text-muted-foreground">Inherits / Implements</p>
                <p className="font-mono">{selected.inherits}</p>
              </div>
            )}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
}
