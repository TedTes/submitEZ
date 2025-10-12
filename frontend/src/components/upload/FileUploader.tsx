'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'
import { FILE_UPLOAD } from '@/lib/constants'
import { validateFiles } from '@/lib/utils/validation'

interface FileUploaderProps {
  onFilesSelected: (files: File[]) => void
  disabled?: boolean
}

export function FileUploader({ onFilesSelected, disabled }: FileUploaderProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Validate files
      const validation = validateFiles(acceptedFiles)

      if (!validation.valid) {
        alert(`File validation failed:\n${validation.errors.join('\n')}`)
        return
      }

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const errors = rejectedFiles.map((f) => {
          const errorMessages = f.errors.map((e: any) => e.message).join(', ')
          return `${f.file.name}: ${errorMessages}`
        })
        alert(`Some files were rejected:\n${errors.join('\n')}`)
      }

      // Pass valid files to parent
      if (acceptedFiles.length > 0) {
        onFilesSelected(acceptedFiles)
      }
    },
    [onFilesSelected]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      accept: FILE_UPLOAD.allowedMimeTypes.reduce(
        (acc, mimeType) => ({ ...acc, [mimeType]: [] }),
        {}
      ),
      maxSize: FILE_UPLOAD.maxFileSize,
      maxFiles: FILE_UPLOAD.maxFiles,
      disabled,
    })

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors',
        isDragActive && !isDragReject && 'border-primary bg-primary/5',
        isDragReject && 'border-destructive bg-destructive/5',
        !isDragActive && !isDragReject && 'border-border hover:border-primary/50',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />

      {/* Icon */}
      <div className="flex justify-center mb-4">
        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
          <svg
            className="w-8 h-8 text-primary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
      </div>

      {/* Text */}
      <div className="space-y-2">
        {isDragActive ? (
          isDragReject ? (
            <p className="text-lg font-medium text-destructive">
              Some files are not supported
            </p>
          ) : (
            <p className="text-lg font-medium text-primary">
              Drop files here...
            </p>
          )
        ) : (
          <>
            <p className="text-lg font-medium">
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-muted-foreground">
              PDF, Excel, or Word documents • Max 16MB per file
            </p>
          </>
        )}
      </div>

      {/* Supported formats */}
      {!isDragActive && (
        <div className="mt-6 flex justify-center gap-4 text-xs text-muted-foreground">
          <span className="px-2 py-1 rounded bg-muted">.pdf</span>
          <span className="px-2 py-1 rounded bg-muted">.xlsx</span>
          <span className="px-2 py-1 rounded bg-muted">.xls</span>
          <span className="px-2 py-1 rounded bg-muted">.docx</span>
          <span className="px-2 py-1 rounded bg-muted">.doc</span>
        </div>
      )}
    </div>
  )
}