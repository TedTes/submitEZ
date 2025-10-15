'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Upload, File, Trash2, Download, CheckCircle2, Clock, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'
import { useSubmission } from '@/hooks/useSubmission'
import { ProcessingProgress } from '@/components/projects/ProcessingProgress'
import { ProjectResults } from '@/components/projects/ProjectResults'
import { formatFileSize, formatDateTime } from '@/lib/utils/format'
import { PROJECT_STATUS } from '@/lib/constants'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.id as string
  
  const { 
    loadSubmission, 
    currentSubmission, 
    uploadFiles, 
    extractData,
    isUploading,
    isExtracting,
    error: submissionError,
  } = useSubmission()
  
  // Local state
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<Record<number, number>>({})
  const [isDragging, setIsDragging] = useState(false)

  // Load project on mount
  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        setError(null)
        await loadSubmission(projectId)
      } catch (err: any) {
        setError(err?.message || 'Failed to load project')
      } finally {
        setLoading(false)
      }
    }
    
    if (projectId) {
      load()
    }
  }, [projectId, loadSubmission])

  // File handling
  const getFileIcon = (contentType?: string, filename?: string) => {
    if (contentType?.includes('pdf') || filename?.endsWith('.pdf')) return '📄'
    if (contentType?.includes('sheet') || filename?.match(/\.(xlsx?|xls)$/)) return '📊'
    if (contentType?.includes('word') || filename?.match(/\.(docx?|doc)$/)) return '📝'
    return '📎'
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setSelectedFiles(prev => [...prev, ...files])
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files || [])
    setSelectedFiles(prev => [...prev, ...files])
  }

  const removeSelectedFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
    setUploadProgress(prev => {
      const newProgress = { ...prev }
      delete newProgress[index]
      return newProgress
    })
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return
    
    try {
      setError(null)
      
      // Upload files
      await uploadFiles(projectId, selectedFiles, (progress) => {
        const progressMap: Record<number, number> = {}
        selectedFiles.forEach((_, index) => {
          progressMap[index] = progress
        })
        setUploadProgress(progressMap)
      })
      
      // Reload project to show uploaded files
      await loadSubmission(projectId)
      
      // Clear selection
      setSelectedFiles([])
      setUploadProgress({})
      
    } catch (err: any) {
      setError(err?.message || 'Failed to upload files')
    }
  }

  const handleStartProcessing = async () => {
    if (!currentSubmission) return
    
    try {
      setError(null)
      
      // Start extraction
      await extractData(projectId)
      
      // Reload to show updated status
      await loadSubmission(projectId)
      
    } catch (err: any) {
      setError(err?.message || 'Failed to start processing')
    }
  }

  const handleDeleteFile = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) return
    
    // TODO: Implement file deletion API endpoint
    alert('File deletion not yet implemented in backend')
  }

  // Loading state
  if (loading) {
    return (
      <div className="container max-w-7xl py-8 flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <Spinner size="lg" />
          <p className="text-muted-foreground">Loading project...</p>
        </div>
      </div>
    )
  }

  // Error state (no submission found)
  if (error && !currentSubmission) {
    return (
      <div className="container max-w-7xl py-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button className="mt-4" onClick={() => router.push('/dashboard')}>
          Back to Projects
        </Button>
      </div>
    )
  }

  if (!currentSubmission) {
    return (
      <div className="container max-w-7xl py-8">
        <Alert variant="destructive">
          <AlertTitle>Not Found</AlertTitle>
          <AlertDescription>Project not found</AlertDescription>
        </Alert>
        <Button className="mt-4" onClick={() => router.push('/dashboard')}>
          Back to Projects
        </Button>
      </div>
    )
  }

  const statusConfig = PROJECT_STATUS[currentSubmission.status] || PROJECT_STATUS.draft
  const clientName = currentSubmission.client_name || currentSubmission.applicant?.business_name || 'Untitled Project'
  const uploadedFiles = currentSubmission.uploaded_files || []
  const hasUploadedFiles = uploadedFiles.length > 0
  const canUpload = ['draft', 'uploaded', 'error'].includes(currentSubmission.status)
  const isProcessing = ['extracting', 'validating', 'generating'].includes(currentSubmission.status)
  const isCompleted = currentSubmission.status === 'completed'

  return (
    <div className="container max-w-7xl py-8">
      {/* Breadcrumb */}
      <nav className="flex items-center space-x-2 text-sm text-muted-foreground mb-6">
        <button 
          onClick={() => router.push('/dashboard')}
          className="hover:text-foreground transition-colors"
        >
          Projects
        </button>
        <span>›</span>
        <span className="text-foreground font-medium">{clientName}</span>
      </nav>

      {/* Error Alert */}
      {(error || submissionError) && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error || submissionError}</AlertDescription>
        </Alert>
      )}

      {/* Processing State */}
      {isProcessing && (
        <ProcessingProgress 
          currentStatus={currentSubmission.status}
          fileCount={uploadedFiles.length}
        />
      )}

      {/* Completed State */}
      {isCompleted && (
        <ProjectResults 
          project={currentSubmission}
          onUpdate={async (updated) => {
            await loadSubmission(projectId)
          }}
        />
      )}

      {/* Files Section (only show if not completed) */}
      {!isCompleted && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Documents</CardTitle>
                <CardDescription>
                  Upload all relevant documents for this project
                </CardDescription>
              </div>
              {canUpload && (
                <>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    id="add-files-input"
                    accept=".pdf,.xlsx,.xls,.docx,.doc"
                    disabled={isUploading}
                  />
                  <label htmlFor="add-files-input">
                    <Button
                      disabled={isUploading}
                      asChild
                    >
                      <span className="cursor-pointer">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Files
                      </span>
                    </Button>
                  </label>
                </>
              )}
            </div>
          </CardHeader>

          <CardContent>
            {/* Selected Files Preview - Show when files are selected */}
            {selectedFiles.length > 0 && (
              <div className="mb-6 space-y-2">
                <h3 className="text-sm font-medium mb-2">
                  Selected Files ({selectedFiles.length})
                </h3>
                {selectedFiles.map((file, index) => {
                  const progress = uploadProgress[index]
                  const isFileUploading = progress !== undefined && progress < 100

                  return (
                    <div
                      key={`${file.name}-${index}`}
                      className="flex items-center gap-4 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <span className="text-2xl">
                        {getFileIcon(file.type, file.name)}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 dark:text-gray-100 truncate">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(file.size)}
                        </p>
                        {isFileUploading && (
                          <div className="mt-2">
                            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-600 transition-all duration-300"
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              Uploading... {progress}%
                            </p>
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => removeSelectedFile(index)}
                        disabled={isUploading}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )
                })}
                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    {isUploading ? (
                      <>
                        <Spinner size="sm" className="mr-2" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        Upload {selectedFiles.length} File
                        {selectedFiles.length !== 1 ? 's' : ''}
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSelectedFiles([])
                      setUploadProgress({})
                    }}
                    disabled={isUploading}
                    className="px-6 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    Clear All
                  </Button>
                </div>
              </div>
            )}

            {/* Uploaded Files List - Show if files exist and no files selected */}
            {hasUploadedFiles && selectedFiles.length === 0 && (
              <div className="space-y-3">
                {uploadedFiles.map((file: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center gap-4 p-4 border rounded-lg hover:shadow-md transition-all group"
                  >
                    <span className="text-3xl">
                      {getFileIcon(file.content_type, file.filename)}
                    </span>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium truncate">
                          {file.original_filename}
                        </p>
                        <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                      </div>
                      <div className="flex items-center gap-3 text-sm text-muted-foreground">
                        <span>{formatFileSize(file.size_bytes)}</span>
                        <span>•</span>
                        <span>Uploaded {formatDateTime(file.uploaded_at)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a
                        href={file.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-muted-foreground hover:text-primary transition-colors"
                        title="Download"
                      >
                        <Download className="w-5 h-5" />
                      </a>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteFile(file.original_filename)}
                        className="text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="w-5 h-5" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Drop Zone - Only show if no files uploaded and no files selected */}
            {!hasUploadedFiles && selectedFiles.length === 0 && (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`p-12 border-2 border-dashed rounded-lg transition-all ${
                  isDragging 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950' 
                    : 'border-gray-300 bg-gray-50 dark:bg-gray-900'
                }`}
              >
                <div className="text-center">
                  <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Drop files here or click to browse
                  </h3>
                  <p className="text-sm text-gray-500 mb-6">
                    Supports PDF, Excel, and Word documents (max 16MB each)
                  </p>
                  {canUpload && (
                    <>
                      <input
                        type="file"
                        multiple
                        onChange={handleFileSelect}
                        className="hidden"
                        id="empty-state-upload"
                        accept=".pdf,.xlsx,.xls,.docx,.doc"
                        disabled={isUploading}
                      />
                      <label
                        htmlFor="empty-state-upload"
                        className="inline-block px-6 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        Browse Files
                      </label>
                    </>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      {hasUploadedFiles && canUpload && !isProcessing && (
        <div className="mt-6 flex gap-4">
          <Button 
            onClick={handleStartProcessing}
            disabled={isExtracting}
            className="flex-1"
          >
            {isExtracting ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Processing...
              </>
            ) : (
              'Start Processing'
            )}
          </Button>
          <Button 
            variant="outline"
            onClick={() => router.push('/dashboard')}
          >
            Save Draft
          </Button>
        </div>
      )}
    </div>
  )
}