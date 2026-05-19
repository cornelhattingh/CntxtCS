import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { api, type Stats, type Dependency } from '@/lib/api'
import { useProject } from '@/lib/project-context'
import { MetricGroup } from '@/components/stats/MetricGroup'
import { DependencyList } from '@/components/stats/DependencyList'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/common/EmptyState'

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



  if (!selected) {
    return (
      <EmptyState
        heading="No project selected"
        body="Run the MCP server with a project directory to index your codebase, then select the project from the header."
        copyCommand="uv run python mcp_server.py --directory /path/to/project --project my-project"
      />
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

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <MetricGroup
          title="Structure"
          loading={loading}
          metrics={[
            { label: 'Source files', value: stats?.total_files },
            { label: 'Namespaces', value: stats?.total_namespaces },
          ]}
        />
        <MetricGroup
          title="Types"
          loading={loading}
          metrics={[
            { label: 'Classes', value: stats?.total_classes, primary: true },
            { label: 'Interfaces', value: stats?.total_interfaces },
            { label: 'Enums', value: stats?.total_enums },
            { label: 'Structs', value: stats?.total_structs },
          ]}
        />
        <MetricGroup
          title="Members"
          loading={loading}
          metrics={[
            { label: 'Methods', value: stats?.total_methods },
          ]}
        />
        <MetricGroup
          title="Dependencies"
          loading={loading}
          metrics={[
            { label: 'NuGet packages', value: stats?.total_dependencies },
            { label: 'Using directives', value: stats?.total_usings },
          ]}
        />
      </div>

      <Separator />

      <DependencyList dependencies={deps} loading={loading} />
    </div>
  )
}
