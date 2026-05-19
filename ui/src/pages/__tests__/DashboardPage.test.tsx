import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { DashboardPage } from '../DashboardPage'
import * as api from '@/lib/api'
import * as projectContext from '@/lib/project-context'

// Mock the API module
vi.mock('@/lib/api', () => ({
  api: {
    getStats: vi.fn(),
    getDependencies: vi.fn(),
    reanalyze: vi.fn(),
    getScanStatus: vi.fn(),
  },
}))

// Mock the project context
vi.mock('@/lib/project-context', () => ({
  useProject: vi.fn(),
}))

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows empty state when selected is null', () => {
    vi.mocked(projectContext.useProject).mockReturnValue({
      selected: null,
      projects: [],
      setSelected: vi.fn(),
      loading: false,
    })

    render(<DashboardPage />)

    expect(screen.getByText('Select a project to get started')).toBeInTheDocument()
  })

  it('shows error message when stats API fails', async () => {
    vi.mocked(projectContext.useProject).mockReturnValue({
      selected: 'test-project',
      projects: ['test-project'],
      setSelected: vi.fn(),
      loading: false,
    })

    // Mock API to reject with an error
    vi.mocked(api.api.getStats).mockRejectedValue(new Error('500 Internal Server Error'))
    vi.mocked(api.api.getDependencies).mockResolvedValue([])

    render(<DashboardPage />)

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('500 Internal Server Error')).toBeInTheDocument()
    })
  })

  it('renders stat groups when data loads successfully', async () => {
    vi.mocked(projectContext.useProject).mockReturnValue({
      selected: 'test-project',
      projects: ['test-project'],
      setSelected: vi.fn(),
      loading: false,
    })

    // Mock API to return valid data
    vi.mocked(api.api.getStats).mockResolvedValue({
      total_files: 10,
      total_classes: 5,
      total_methods: 20,
      total_interfaces: 3,
      total_namespaces: 2,
      total_enums: 1,
      total_structs: 0,
      total_dependencies: 4,
      total_usings: 15,
    })
    vi.mocked(api.api.getDependencies).mockResolvedValue([
      { name: 'System.Text.Json', version: '8.0.0' },
    ])

    render(<DashboardPage />)

    // Wait for stat cards to render
    await waitFor(() => {
      expect(screen.getByText('Source Files')).toBeInTheDocument()
      expect(screen.getByText('10')).toBeInTheDocument()
      expect(screen.getByText('Classes')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
    })
  })
})
