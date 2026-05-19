import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ProjectProvider } from '@/lib/project-context'
import { AppShell } from '@/components/layout/AppShell'
import { DashboardPage } from '@/pages/DashboardPage'
import { GraphPage } from '@/pages/GraphPage'
import { ExplorerPage } from '@/pages/ExplorerPage'

export default function App() {
  return (
    <BrowserRouter>
      <ProjectProvider>
        <AppShell>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/explorer" element={<ExplorerPage />} />
          </Routes>
        </AppShell>
      </ProjectProvider>
    </BrowserRouter>
  )
}
