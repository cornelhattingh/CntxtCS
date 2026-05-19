import { Skeleton } from '@/components/ui/skeleton'

interface Metric {
  label: string
  value: number | undefined
  primary?: boolean   // if true, value gets slightly larger / bolder treatment
}

interface MetricGroupProps {
  title: string
  metrics: Metric[]
  loading?: boolean
}

export function MetricGroup({ title, metrics, loading }: MetricGroupProps) {
  return (
    <div className="rounded-md border bg-card p-4 space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{title}</h3>
      <div className="space-y-1.5">
        {metrics.map(({ label, value, primary }) => (
          <div key={label} className="flex items-baseline justify-between gap-2">
            <span className="text-sm text-muted-foreground">{label}</span>
            {loading ? (
              <Skeleton className="h-4 w-10" />
            ) : (
              <span
                className={
                  primary
                    ? 'text-base font-semibold tabular-nums'
                    : 'text-sm font-medium tabular-nums text-foreground'
                }
              >
                {value?.toLocaleString() ?? '—'}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
