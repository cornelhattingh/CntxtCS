import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { NodeTypeFilter } from '../NodeTypeFilter'

const types = ['class', 'interface', 'method']
const visible = new Set(['class', 'interface', 'method'])
const onToggle = vi.fn()
const onShowAll = vi.fn()
const onHideAll = vi.fn()

describe('NodeTypeFilter', () => {
  it('renders all type labels', () => {
    render(<NodeTypeFilter types={types} visible={visible} onToggle={onToggle} />)
    expect(screen.getByText('class')).toBeInTheDocument()
    expect(screen.getByText('interface')).toBeInTheDocument()
    expect(screen.getByText('method')).toBeInTheDocument()
  })

  it('does not render All/None buttons when handlers are not provided', () => {
    render(<NodeTypeFilter types={types} visible={visible} onToggle={onToggle} />)
    expect(screen.queryByText('All')).not.toBeInTheDocument()
    expect(screen.queryByText('None')).not.toBeInTheDocument()
  })

  it('renders All and None buttons when handlers are provided', () => {
    render(
      <NodeTypeFilter
        types={types}
        visible={visible}
        onToggle={onToggle}
        onShowAll={onShowAll}
        onHideAll={onHideAll}
      />
    )
    expect(screen.getByText('All')).toBeInTheDocument()
    expect(screen.getByText('None')).toBeInTheDocument()
  })

  it('calls onShowAll when All button is clicked', async () => {
    const user = userEvent.setup()
    const showAll = vi.fn()
    render(
      <NodeTypeFilter
        types={types}
        visible={visible}
        onToggle={onToggle}
        onShowAll={showAll}
        onHideAll={vi.fn()}
      />
    )
    await user.click(screen.getByText('All'))
    expect(showAll).toHaveBeenCalledTimes(1)
  })

  it('calls onHideAll when None button is clicked', async () => {
    const user = userEvent.setup()
    const hideAll = vi.fn()
    render(
      <NodeTypeFilter
        types={types}
        visible={visible}
        onToggle={onToggle}
        onShowAll={vi.fn()}
        onHideAll={hideAll}
      />
    )
    await user.click(screen.getByText('None'))
    expect(hideAll).toHaveBeenCalledTimes(1)
  })

  it('does not render counts when typeCounts is omitted', () => {
    render(<NodeTypeFilter types={types} visible={visible} onToggle={onToggle} />)
    // No numeric text from counts
    expect(screen.queryByText('5')).not.toBeInTheDocument()
  })

  it('renders per-type counts when typeCounts is provided', () => {
    const typeCounts = { class: 12, interface: 3, method: 47 }
    render(
      <NodeTypeFilter
        types={types}
        visible={visible}
        onToggle={onToggle}
        typeCounts={typeCounts}
      />
    )
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('47')).toBeInTheDocument()
  })
})
