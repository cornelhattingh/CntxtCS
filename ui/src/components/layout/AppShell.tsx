import type { ReactNode } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { ProjectSelector } from './ProjectSelector'

export function AppShell({ children }: { children?: ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-3 border-b shrink-0">
          <span className="text-sm font-medium text-muted-foreground">Project</span>
          <ProjectSelector />
        </header>
        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">
          {children ?? <Outlet />}
        </main>
      </div>
    </div>
  )
}
