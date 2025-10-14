'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ProjectHeader } from '@/components/projects/ProjectHeader'
import { FileUploader } from '@/components/upload/FileUploader'
import { FileList } from '@/components/upload/FileList'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Spinner } from '@/components/ui/spinner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useSubmission } from '@/hooks/useSubmission'
import { ProcessingProgress } from '@/components/projects/ProcessingProgress'
import { ProjectResults } from '@/components/projects/ProjectResults'

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
  } = useSubmission()
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<Record<number, number>>({})

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

  // Handle file selection
  const handleFilesSelected = (newFiles: File[]) => {
    setFiles([...files, ...newFiles])
  }

  // Handle file removal
  const handleRemoveFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  // Handle submit
  const handleSubmit = async () => {
    if (files.length === 0) return
    
    try {
      setError(null)
      
      // Upload files
      await uploadFiles(projectId, files, (progress) => {
        // Set progress for all files
        const progressMap: Record<number, number> = {}
        files.forEach((_, index) => {
          progressMap[index] = progress
        })
        setUploadProgress(progressMap)
      })
      
      // Start extraction
      await extractData(projectId)
      
      // Reload project
      await loadSubmission(projectId)
      
      // Clear files
      setFiles([])
      setUploadProgress({})
      
    } catch (err: any) {
      setError(err?.message || 'Failed to process files')
    }
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

  // Error state
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

  const canUpload = ['draft', 'uploaded', 'error'].includes(currentSubmission.status)
  const isProcessing = ['extracting', 'validating', 'generating'].includes(currentSubmission.status)

  return (
    <div className="container max-w-7xl py-8">
      {/* Project Header */}
      <ProjectHeader project={currentSubmission} />

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Processing Alert */}
      {isProcessing && (
        <Alert className="mb-6">
          <Spinner size="sm" className="mr-2" />
          <AlertTitle>Processing</AlertTitle>
          <AlertDescription>
            Your project is being processed. This may take a few minutes...
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <div className="space-y-6">
        {/* File Upload Section */}
        {canUpload && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Upload Documents</CardTitle>
                <CardDescription>
                  Add all documents for this client's submission
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* File Uploader */}
                <FileUploader
                  onFilesSelected={handleFilesSelected}
                  disabled={isUploading || isExtracting}
                />
                
                {/* Tips */}
                <div className="bg-blue-50 dark:bg-blue-950 rounded-lg p-4">
                  <p className="text-sm font-medium mb-2">💡 Tip: Upload all documents at once</p>
                  <p className="text-sm text-muted-foreground">
                    Our AI works best when it can analyze all documents together. Include ACORD forms, 
                    schedules, loss runs, and any other relevant documents.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* File List */}
            {files.length > 0 && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Selected Files ({files.length})</CardTitle>
                      <CardDescription>
                        Review your files before submitting
                      </CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => document.getElementById('file-input')?.click()}
                      disabled={isUploading || isExtracting}
                    >
                      Add More Files
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                <FileList
  files={files}
  onRemove={handleRemoveFile}
  uploadProgress={uploadProgress}
  disabled={isUploading || isExtracting}
/>
                </CardContent>
              </Card>
            )}

            {/* Submit Button */}
            {files.length > 0 && (
              <div className="flex justify-end">
                <Button
                  size="lg"
                  onClick={handleSubmit}
                  disabled={files.length === 0 || isUploading || isExtracting}
                >
                 {isUploading
  ? 'Uploading...'
  : isExtracting
  ? 'Extracting Data...'
  : `Submit ${files.length} File${files.length !== 1 ? 's' : ''}`}
                </Button>
              </div>
            )}
          </>
        )}

        {/* Processing State */}
        {isProcessing && (
  <ProcessingProgress 
    currentStatus={currentSubmission.status}
    fileCount={currentSubmission.uploaded_files?.length || 0}
  />
)}

        {/* Extracted/Validated State */}
        {['extracted', 'validated'].includes(currentSubmission.status) && (
          <Card>
            <CardHeader>
              <CardTitle>Data Extracted</CardTitle>
              <CardDescription>
                Review and validate the extracted data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Data review interface will be integrated soon. 
                  For now, use the temporary navigation below.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}
    
{/* Completed State */}
{currentSubmission.status === 'completed' && (
  <ProjectResults 
    project={currentSubmission}
    onUpdate={(updated) => {
      // Reload the submission after update
      loadSubmission(projectId)
    }}
  />
)}
 
      </div>
    </div>
  )
}