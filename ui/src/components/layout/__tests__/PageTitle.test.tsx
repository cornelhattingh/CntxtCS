import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { PageTitle } from '../PageTitle'

const renderAt = (path: string) =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <PageTitle />
    </MemoryRouter>
  )

describe('PageTitle', () => {
  it('renders "Dashboard" at route "/"', () => {
    renderAt('/')
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders "Graph" at route "/graph"', () => {
    renderAt('/graph')
    expect(screen.getByText('Graph')).toBeInTheDocument()
  })

  it('renders "Explorer" at route "/explorer"', () => {
    renderAt('/explorer')
    expect(screen.getByText('Explorer')).toBeInTheDocument()
  })

  it('renders the title with muted styling class', () => {
    const { container } = renderAt('/')
    const el = container.firstChild as HTMLElement
    expect(el.className).toMatch(/font-medium/)
  })
})
