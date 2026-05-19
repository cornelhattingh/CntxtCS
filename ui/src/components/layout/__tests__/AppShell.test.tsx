import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AppShell } from '../AppShell'

// Mock child components to isolate AppShell
vi.mock('../Sidebar', () => ({ Sidebar: () => <div data-testid="sidebar" /> }))
vi.mock('../ProjectSelector', () => ({ ProjectSelector: () => <div data-testid="project-selector" /> }))
vi.mock('../PageTitle', () => ({ PageTitle: () => <div data-testid="page-title" /> }))

describe('AppShell', () => {
  const renderWithRouter = (initialPath = '/') =>
    render(
      <MemoryRouter initialEntries={[initialPath]}>
        <AppShell />
      </MemoryRouter>
    )

  it('renders the header with PageTitle on the left', () => {
    renderWithRouter()
    expect(screen.getByTestId('page-title')).toBeInTheDocument()
  })

  it('renders the header with ProjectSelector on the right', () => {
    renderWithRouter()
    expect(screen.getByTestId('project-selector')).toBeInTheDocument()
  })

  it('does not render the static "Project" text', () => {
    renderWithRouter()
    expect(screen.queryByText('Project')).not.toBeInTheDocument()
  })

  it('renders the sidebar', () => {
    renderWithRouter()
    expect(screen.getByTestId('sidebar')).toBeInTheDocument()
  })
})
