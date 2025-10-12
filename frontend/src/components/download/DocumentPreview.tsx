'use client'

import { useState } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface DocumentPreviewProps {
  url: string
  className?: string
}

export function DocumentPreview({ url, className }: DocumentPreviewProps) {
  const [error, setError] = useState(false)

  // Check if browser supports PDF preview
  const supportsPdfPreview =
    typeof window !== 'undefined' &&
    navigator.pdfViewerEnabled !== false

  if (!supportsPdfPreview) {
    return (
      <Alert>
        <AlertDescription>
          PDF preview is not supported in your browser. Please download the file
          to view it.
        </AlertDescription>
      </Alert>
    )
  }

  if (error) {
    return (
      <Alert variant="warning">
        <AlertDescription>
          Unable to load preview. Please download the file to view it.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className={className}>
      <iframe
        src={url}
        className="w-full h-[500px] border rounded-lg"
        title="Document Preview"
        onError={() => setError(true)}
      />
    </div>
  )
}