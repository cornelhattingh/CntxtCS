import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MetricGroup } from '../MetricGroup'

const metrics = [
  { label: 'Classes', value: 42, primary: true },
  { label: 'Interfaces', value: 7 },
]

describe('MetricGroup', () => {
  it('renders the group title', () => {
    render(<MetricGroup title="Types" metrics={metrics} />)
    expect(screen.getByText('Types')).toBeInTheDocument()
  })

  it('renders all metric labels', () => {
    render(<MetricGroup title="Types" metrics={metrics} />)
    expect(screen.getByText('Classes')).toBeInTheDocument()
    expect(screen.getByText('Interfaces')).toBeInTheDocument()
  })

  it('renders metric values as localized numbers', () => {
    render(<MetricGroup title="Types" metrics={metrics} />)
    expect(screen.getByText('42')).toBeInTheDocument()
    expect(screen.getByText('7')).toBeInTheDocument()
  })

  it('renders "—" for undefined values', () => {
    render(<MetricGroup title="Types" metrics={[{ label: 'Classes', value: undefined }]} />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('renders skeletons when loading is true', () => {
    const { container } = render(<MetricGroup title="Types" metrics={metrics} loading={true} />)
    // Skeletons are rendered instead of values when loading
    expect(container.querySelectorAll('[data-slot="skeleton"]').length).toBeGreaterThan(0)
  })
})
