import { NavLink } from 'react-router-dom'
import { BarChart3, Network, BookOpen, Box } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Dashboard', icon: BarChart3 },
  { to: '/graph', label: 'Graph', icon: Network },
  { to: '/explorer', label: 'Explorer', icon: BookOpen },
]

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r bg-sidebar flex flex-col">
      <div className="flex items-center gap-2 px-5 py-4 border-b">
        <Box className="h-5 w-5 text-primary" />
        <span className="font-semibold text-sm tracking-tight">CntxtCS</span>
      </div>
      <nav className="flex flex-col gap-0.5 p-2 flex-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-3 border-t">
        <p className="text-[11px] text-muted-foreground">C# Knowledge Graph</p>
      </div>
    </aside>
  )
}
