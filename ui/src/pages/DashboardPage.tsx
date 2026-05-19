import { useEffect, useState } from 'react'
import {
  FileCode2,
  Layers,
  FunctionSquare,
  Braces,
  Boxes,
  ListOrdered,
  Shapes,
  Package2,
  Import,
  RefreshCw,
} from 'lucide-react'
import { api, type Stats, type Dependency } from '@/lib/api'
import { useProject } from '@/lib/project-context'
import { StatCard } from '@/components/stats/StatCard'
import { DependencyList } from '@/components/stats/DependencyList'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'

export function DashboardPage() {
  const { selected } = useProject()
  const [stats, setStats] = useState<Stats | null>(null)
  const [deps, setDeps] = useState<Dependency[]>([])
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [scanError, setScanError] = useState<string | null>(null)
  const [fetchError, setFetchError] = useState<string | null>(null)

  const loadData = (project: string) => {
    setLoading(true)
    setStats(null)
    setDeps([])
    setFetchError(null)
    setScanError(null)
    Promise.all([
      api.getStats(project),
      api.getDependencies(project),
    ]).then(([s, d]) => {
      setStats(s)
      setDeps(d ?? [])
    }).catch(err => {
      setFetchError(err instanceof Error ? err.message : 'Failed to load project data. Is the server running?')
    }).finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!selected) return
    loadData(selected)
  }, [selected])

  const handleFullScan = async () => {
    if (!selected || scanning) return
    setScanning(true)
    setScanError(null)
    try {
      await api.reanalyze(selected)
      // Poll scan-status until the background job finishes
      const poll = async () => {
        try {
          const status = await api.getScanStatus(selected)
          if (status.scanning) {
            setTimeout(poll, 2000)
          } else {
            if (status.error) setScanError(status.error)
            else loadData(selected)
            setScanning(false)
          }
        } catch {
          setScanning(false)
        }
      }
      setTimeout(poll, 2000)
    } catch (err) {
      setScanError(err instanceof Error ? err.message : 'Scan failed')
      setScanning(false)
    }
  }

  const metrics: Array<{ title: string; key: keyof Stats; icon: React.ReactNode }> = [
    { title: 'Source Files', key: 'total_files', icon: <FileCode2 className="h-4 w-4" /> },
    { title: 'Classes', key: 'total_classes', icon: <Layers className="h-4 w-4" /> },
    { title: 'Methods', key: 'total_methods', icon: <FunctionSquare className="h-4 w-4" /> },
    { title: 'Interfaces', key: 'total_interfaces', icon: <Braces className="h-4 w-4" /> },
    { title: 'Namespaces', key: 'total_namespaces', icon: <Boxes className="h-4 w-4" /> },
    { title: 'Enums', key: 'total_enums', icon: <ListOrdered className="h-4 w-4" /> },
    { title: 'Structs', key: 'total_structs', icon: <Shapes className="h-4 w-4" /> },
    { title: 'Dependencies', key: 'total_dependencies', icon: <Package2 className="h-4 w-4" /> },
    { title: 'Using Directives', key: 'total_usings', icon: <Import className="h-4 w-4" /> },
  ]

  if (!selected) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Select a project to get started
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{selected}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Codebase overview</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleFullScan}
          disabled={scanning}
          className="shrink-0 gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${scanning ? 'animate-spin' : ''}`} />
          {scanning ? 'Scanning…' : 'Full Scan'}
        </Button>
      </div>

      {scanError && (
        <p className="text-sm text-destructive">{scanError}</p>
      )}

      {fetchError && (
        <p className="text-sm text-destructive">{fetchError}</p>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {metrics.map(m => (
          <StatCard
            key={m.key}
            title={m.title}
            value={stats?.[m.key] as number}
            icon={m.icon}
            loading={loading}
          />
        ))}
      </div>

      <Separator />

      <DependencyList dependencies={deps} loading={loading} />
    </div>
  )
}
