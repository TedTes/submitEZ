'use client'

import { useState } from 'react'
import { Button, type ButtonProps } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'

interface DownloadButtonProps extends ButtonProps {
  onClick: (e: React.MouseEvent) => Promise<void> | void
  children: React.ReactNode
}

export function DownloadButton({
  onClick,
  children,
  disabled,
  ...props
}: DownloadButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  const handleClick = async (e: React.MouseEvent) => {
    if (isDownloading || disabled) return

    try {
      setIsDownloading(true)
      await onClick(e)
    } catch (error) {
      console.error('Download error:', error)
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <Button
      onClick={handleClick}
      disabled={disabled || isDownloading}
      {...props}
    >
      {isDownloading ? (
        <>
          <Spinner size="sm" className="mr-2" />
          Downloading...
        </>
      ) : (
        <>
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          {children}
        </>
      )}
    </Button>
  )
}