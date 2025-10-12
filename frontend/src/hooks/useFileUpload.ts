'use client'

import { useState, useCallback } from 'react'
import submissionAPI from '@/lib/api/submission-api'
import type { SubmissionCreateRequest } from '@/types/submission'
import type { UploadResponse } from '@/types/api'

interface UseFileUploadReturn {
  files: File[]
  uploadProgress: Record<number, number>
  isUploading: boolean
  error: string | null
  addFiles: (newFiles: File[]) => void
  removeFile: (index: number) => void
  clearFiles: () => void
  uploadFiles: (
    metadata?: SubmissionCreateRequest
  ) => Promise<{ submission_id: string; uploadResult: UploadResponse } | null>
}

export function useFileUpload(): UseFileUploadReturn {
  const [files, setFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<Record<number, number>>(
    {}
  )
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Add files to the list
  const addFiles = useCallback((newFiles: File[]) => {
    setFiles((prev) => {
      // Check for duplicates
      const existingNames = new Set(prev.map((f) => f.name))
      const uniqueFiles = newFiles.filter((f) => !existingNames.has(f.name))

      if (uniqueFiles.length !== newFiles.length) {
        console.warn('Some files were already added')
      }

      return [...prev, ...uniqueFiles]
    })
    setError(null)
  }, [])

  // Remove a file from the list
  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
    setUploadProgress((prev) => {
      const newProgress = { ...prev }
      delete newProgress[index]
      return newProgress
    })
    setError(null)
  }, [])

  // Clear all files
  const clearFiles = useCallback(() => {
    setFiles([])
    setUploadProgress({})
    setError(null)
  }, [])

  // Upload files
  const uploadFiles = useCallback(
    async (metadata?: SubmissionCreateRequest) => {
      if (files.length === 0) {
        setError('No files selected')
        return null
      }

      setIsUploading(true)
      setError(null)

      try {
        // Track progress for each file
        const onProgress = (progress: number) => {
          // Update all files with the same progress for simplicity
          // In production, you might want per-file progress
          const progressMap: Record<number, number> = {}
          files.forEach((_, index) => {
            progressMap[index] = progress
          })
          setUploadProgress(progressMap)
        }

        // Create submission and upload files
        const result = await submissionAPI.createAndUpload(
          files,
          metadata,
          onProgress
        )

        return {
          submission_id: result.submission.id,
          uploadResult: result.uploadResult,
        }
      } catch (err: any) {
        const errorMessage =
          err?.message || 'Failed to upload files. Please try again.'
        setError(errorMessage)
        console.error('Upload error:', err)
        return null
      } finally {
        setIsUploading(false)
      }
    },
    [files]
  )

  return {
    files,
    uploadProgress,
    isUploading,
    error,
    addFiles,
    removeFile,
    clearFiles,
    uploadFiles,
  }
}