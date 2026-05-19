import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../DashboardPage'

vi.mock('@/lib/project-context', () => ({
  useProject: () => ({ selected: 'TestProject', projects: ['TestProject'], setSelected: vi.fn() }),
}))
vi.mock('@/lib/api', () => ({
  api: {
    getStats: vi.fn().mockResolvedValue({
      total_files: 10, total_classes: 25, total_methods: 100,
      total_interfaces: 5, total_namespaces: 3, total_enums: 2,
      total_structs: 1, total_dependencies: 8, total_usings: 40,
    }),
    getDependencies: vi.fn().mockResolvedValue([]),
  },
}))

describe('DashboardPage metric groups', () => {
  it('renders the 4 MetricGroup section titles', async () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByText('Structure')).toBeInTheDocument()
      expect(screen.getByText('Types')).toBeInTheDocument()
      expect(screen.getByText('Members')).toBeInTheDocument()
      expect(screen.getByText('Dependencies')).toBeInTheDocument()
    })
  })

  it('does not render any StatCard elements', async () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    await waitFor(() => {
      // StatCard renders a data-testid or a specific structure; we verify by checking
      // that the old grid class pattern is gone
      expect(screen.queryByText('Source Files')).not.toBeInTheDocument()
    })
  })
})
