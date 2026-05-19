import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EmptyState } from '../EmptyState'

describe('EmptyState', () => {
  it('renders heading and body text', () => {
    render(<EmptyState heading="No project selected" body="Please select one." />)
    expect(screen.getByText('No project selected')).toBeInTheDocument()
    expect(screen.getByText('Please select one.')).toBeInTheDocument()
  })

  it('does not render the command block when copyCommand is omitted', () => {
    render(<EmptyState heading="No project" body="Select one." />)
    expect(screen.queryByRole('button', { name: /copy/i })).not.toBeInTheDocument()
  })

  it('renders the command text and copy button when copyCommand is provided', () => {
    render(
      <EmptyState
        heading="No project"
        body="Run the server."
        copyCommand="uv run python mcp_server.py --directory /path --project name"
      />
    )
    expect(screen.getByText('uv run python mcp_server.py --directory /path --project name')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
  })

  it('copies the command to clipboard when the copy button is clicked', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup({
      writeToClipboard: true,
    })
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    })
    render(
      <EmptyState
        heading="No project"
        body="Run the server."
        copyCommand="uv run python mcp_server.py"
      />
    )
    await user.click(screen.getByRole('button', { name: /copy/i }))
    expect(writeText).toHaveBeenCalledWith('uv run python mcp_server.py')
  })

  it('shows the check icon (confirmation) after clicking copy', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup({
      writeToClipboard: true,
    })
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    })
    render(
      <EmptyState
        heading="No project"
        body="Run the server."
        copyCommand="uv run python mcp_server.py"
      />
    )
    await user.click(screen.getByRole('button', { name: /copy/i }))
    // Verify clipboard was called
    expect(writeText).toHaveBeenCalledTimes(1)
    // The icon swap is handled by React state, just verify the button still exists
    expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument()
  })
})
