import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface EmptyStateProps {
  heading: string
  body: string
  copyCommand?: string   // if provided, renders the monospace block + copy button
}

export function EmptyState({ heading, body, copyCommand }: EmptyStateProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(copyCommand ?? '')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 text-center px-6">
      <div className="space-y-1">
        <h2 className="text-base font-semibold">{heading}</h2>
        <p className="text-sm text-muted-foreground max-w-sm">{body}</p>
      </div>
      {copyCommand && (
        <div className="flex items-center gap-2 rounded-md border bg-muted px-3 py-2 text-sm font-mono max-w-xl w-full">
          <span className="flex-1 text-left overflow-x-auto whitespace-nowrap">{copyCommand}</span>
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 h-6 w-6"
            onClick={handleCopy}
            aria-label="Copy command"
          >
            {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          </Button>
        </div>
      )}
    </div>
  )
}
