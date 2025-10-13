'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { FileUploader } from '@/components/upload/FileUploader'
import { FileList } from '@/components/upload/FileList'
import { useFileUpload } from '@/hooks/useFileUpload'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Spinner } from '@/components/ui/spinner'

export default function UploadPage() {
  const router = useRouter()
  const {
    files,
    uploadProgress,
    isUploading,
    error,
    addFiles,
    removeFile,
    clearFiles,
    uploadFiles,
  } = useFileUpload()

  const [metadata, setMetadata] = useState({
    broker_name: '',
    broker_email: '',
    carrier_name: '',
    notes: '',
  })

  const handleUpload = async () => {
    if (files.length === 0) return

    try {
      const result = await uploadFiles(metadata)

      if (result?.submission_id) {
        // Navigate to review page
        router.push(`/review?id=${result.submission_id}`)
      }
    } catch (err) {
      // Error is handled by the hook
      console.error('Upload failed:', err)
    }
  }

  const hasFiles = files.length > 0
  const canUpload = hasFiles && !isUploading

  return (
    <div className="container max-w-5xl py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Upload Documents
        </h1>
        <p className="text-muted-foreground">
          Upload ACORD forms, Excel schedules, loss runs, or any submission
          documents. Our AI will extract all the data automatically.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Upload Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <div className="grid gap-6">
        {/* File Uploader */}
        <Card>
          <CardHeader>
            <CardTitle>Select Files</CardTitle>
            <CardDescription>
              Drag and drop files or click to browse. Maximum 10 files, 16MB
              each.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FileUploader onFilesSelected={addFiles} disabled={isUploading} />
          </CardContent>
        </Card>

        {/* File List */}
        {hasFiles && (
          <Card>
            <CardHeader>
              <CardTitle>Selected Files ({files.length})</CardTitle>
              <CardDescription>
                Review your files before uploading
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileList
                files={files}
                onRemove={removeFile}
                uploadProgress={uploadProgress}
                disabled={isUploading}
              />
            </CardContent>
          </Card>
        )}

        {/* Metadata Form */}
        {hasFiles && (
          <Card>
            <CardHeader>
              <CardTitle>Submission Details (Optional)</CardTitle>
              <CardDescription>
                Add details to help organize this submission
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label
                      htmlFor="broker_name"
                      className="text-sm font-medium"
                    >
                      Broker Name
                    </label>
                    <input
                      id="broker_name"
                      type="text"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      placeholder="John Smith"
                      value={metadata.broker_name}
                      onChange={(e) =>
                        setMetadata({ ...metadata, broker_name: e.target.value })
                      }
                      disabled={isUploading}
                    />
                  </div>
                  <div className="space-y-2">
                    <label
                      htmlFor="broker_email"
                      className="text-sm font-medium"
                    >
                      Broker Email
                    </label>
                    <input
                      id="broker_email"
                      type="email"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      placeholder="john@agency.com"
                      value={metadata.broker_email}
                      onChange={(e) =>
                        setMetadata({
                          ...metadata,
                          broker_email: e.target.value,
                        })
                      }
                      disabled={isUploading}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="carrier_name" className="text-sm font-medium">
                    Carrier Name
                  </label>
                  <input
                    id="carrier_name"
                    type="text"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    placeholder="Hartford, Travelers, etc."
                    value={metadata.carrier_name}
                    onChange={(e) =>
                      setMetadata({ ...metadata, carrier_name: e.target.value })
                    }
                    disabled={isUploading}
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="notes" className="text-sm font-medium">
                    Notes
                  </label>
                  <textarea
                    id="notes"
                    className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    placeholder="Add any notes about this submission..."
                    value={metadata.notes}
                    onChange={(e) =>
                      setMetadata({ ...metadata, notes: e.target.value })
                    }
                    disabled={isUploading}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        {hasFiles && (
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={clearFiles}
              disabled={isUploading}
            >
              Clear All
            </Button>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => router.push('/')}
                disabled={isUploading}
              >
                Cancel
              </Button>
              <Button onClick={handleUpload} disabled={!canUpload}>
                {isUploading ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Uploading...
                  </>
                ) : (
                  `Upload ${files.length} File${files.length > 1 ? 's' : ''}`
                )}
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Help Text */}
      {!hasFiles && (
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p className="mb-2">
            <strong>Supported formats:</strong> PDF, Excel (.xlsx, .xls), Word
            (.docx, .doc)
          </p>
          <p>
            <strong>Maximum size:</strong> 16MB per file • <strong>Maximum files:</strong> 10
          </p>
        </div>
      )}
    </div>
  )
}