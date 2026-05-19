import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../DashboardPage'

vi.mock('@/lib/project-context', () => ({
  useProject: () => ({ selected: null, projects: [], setSelected: vi.fn() }),
}))
vi.mock('@/lib/api', () => ({ api: {} }))

describe('DashboardPage empty state', () => {
  it('shows EmptyState heading when no project is selected', () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    expect(screen.getByText('No project selected')).toBeInTheDocument()
  })

  it('shows the setup command in the empty state', () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    expect(screen.getByText(/uv run python mcp_server\.py/)).toBeInTheDocument()
  })

  it('shows the copy button in the Dashboard empty state', () => {
    render(<MemoryRouter><DashboardPage /></MemoryRouter>)
    expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
  })
})
