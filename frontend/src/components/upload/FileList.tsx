'use client'

import { formatFileSize } from '@/lib/utils/format'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface FileListProps {
  files: File[]
  onRemove: (index: number) => void
  uploadProgress?: Record<number, number>
  disabled?: boolean
}

export function FileList({
  files,
  onRemove,
  uploadProgress = {},
  disabled,
}: FileListProps) {
  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()

    switch (ext) {
      case 'pdf':
        return '📄'
      case 'xlsx':
      case 'xls':
        return '📊'
      case 'docx':
      case 'doc':
        return '📝'
      default:
        return '📎'
    }
  }

  return (
    <div className="space-y-2">
      {files.map((file, index) => {
        const progress = uploadProgress[index]
        const isUploading = progress !== undefined && progress < 100

        return (
          <div
            key={`${file.name}-${index}`}
            className="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            {/* Icon */}
            <div className="text-3xl">{getFileIcon(file.name)}</div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-medium truncate">{file.name}</p>
                <Badge variant="secondary" className="text-xs">
                  {formatFileSize(file.size)}
                </Badge>
              </div>

              {/* Progress Bar */}
              {isUploading && (
                <div className="space-y-1">
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Uploading... {progress}%
                  </p>
                </div>
              )}

              {!isUploading && progress === 100 && (
                <p className="text-sm text-green-600">✓ Uploaded</p>
              )}
            </div>

            {/* Remove Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onRemove(index)}
              disabled={disabled || isUploading}
              className="text-muted-foreground hover:text-destructive"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </Button>
          </div>
        )
      })}
    </div>
  )
}