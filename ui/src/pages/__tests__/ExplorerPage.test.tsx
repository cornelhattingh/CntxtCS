import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { ExplorerPage } from '../ExplorerPage'
import * as api from '@/lib/api'
import * as projectContext from '@/lib/project-context'

// Mock the API module
vi.mock('@/lib/api', () => ({
  api: {
    getClasses: vi.fn(),
    getInterfaces: vi.fn(),
    getNamespaces: vi.fn(),
    getFiles: vi.fn(),
  },
}))

// Mock the project context
vi.mock('@/lib/project-context', () => ({
  useProject: vi.fn(),
}))

describe('ExplorerPage', () => {
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

    render(<ExplorerPage />)

    expect(screen.getByText('No project selected')).toBeInTheDocument()
  })

  it('shows error message when classes API fails', async () => {
    vi.mocked(projectContext.useProject).mockReturnValue({
      selected: 'test-project',
      projects: ['test-project'],
      setSelected: vi.fn(),
      loading: false,
    })

    // Mock API to reject with an error
    vi.mocked(api.api.getClasses).mockRejectedValue(new Error('500 Internal Server Error'))
    vi.mocked(api.api.getInterfaces).mockResolvedValue([])
    vi.mocked(api.api.getNamespaces).mockResolvedValue([])
    vi.mocked(api.api.getFiles).mockResolvedValue([])

    render(<ExplorerPage />)

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('500 Internal Server Error')).toBeInTheDocument()
    })
  })

  it('renders tabs when data loads successfully', async () => {
    vi.mocked(projectContext.useProject).mockReturnValue({
      selected: 'test-project',
      projects: ['test-project'],
      setSelected: vi.fn(),
      loading: false,
    })

    // Mock API to return valid data
    vi.mocked(api.api.getClasses).mockResolvedValue([
      { name: 'MyClass', access_modifier: 'public', modifiers: null, inherits: null },
    ])
    vi.mocked(api.api.getInterfaces).mockResolvedValue([
      { name: 'IMyInterface', access_modifier: 'public', inherits: null },
    ])
    vi.mocked(api.api.getNamespaces).mockResolvedValue(['MyNamespace'])
    vi.mocked(api.api.getFiles).mockResolvedValue([
      { node_name: 'MyFile.cs' },
    ])

    render(<ExplorerPage />)

    // Wait for tabs to render
    await waitFor(() => {
      expect(screen.getByText('Classes')).toBeInTheDocument()
      expect(screen.getByText('Interfaces')).toBeInTheDocument()
      expect(screen.getByText('Namespaces')).toBeInTheDocument()
      expect(screen.getByText('Files')).toBeInTheDocument()
    })
  })
})
