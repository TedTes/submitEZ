'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { DocumentPreview } from '@/components/download/DocumentPreview'
import { DownloadButton } from '@/components/download/DownloadButton'
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
import { Badge } from '@/components/ui/badge'
import submissionAPI from '@/lib/api/submission-api'
import type { DownloadPackage } from '@/types/api'
import type { Submission } from '@/types/submission'
import { formatFileSize, formatDateTime } from '@/lib/utils/format'

export default function DownloadPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const submissionId = searchParams.get('id')

  const [submission, setSubmission] = useState<Submission | null>(null)
  const [downloadPackage, setDownloadPackage] = useState<DownloadPackage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedFileUrl, setSelectedFileUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!submissionId) {
      setError('No submission ID provided')
      setLoading(false)
      return
    }

    loadSubmission()
  }, [submissionId])

  const loadSubmission = async () => {
    if (!submissionId) return

    try {
      setLoading(true)
      const data = await submissionAPI.getSubmission(submissionId)
      setSubmission(data)

      // Check if generation is needed
      if (data.status === 'validated') {
        await handleGenerate()
      } else if (data.status === 'completed') {
        await loadDownloadPackage()
      } else if (data.status === 'generating') {
        await pollForCompletion()
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load submission')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!submissionId) return

    try {
      setIsGenerating(true)
      await submissionAPI.generateForms(submissionId)

      // Poll for completion
      await pollForCompletion()
    } catch (err: any) {
      setError(err?.message || 'Generation failed')
    } finally {
      setIsGenerating(false)
    }
  }

  const pollForCompletion = async () => {
    if (!submissionId) return

    try {
      const updatedSubmission = await submissionAPI.pollSubmissionStatus(
        submissionId,
        ['completed', 'error'],
        {
          onProgress: (s) => setSubmission(s),
        }
      )

      setSubmission(updatedSubmission)

      if (updatedSubmission.status === 'completed') {
        await loadDownloadPackage()
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to complete generation')
    }
  }

  const loadDownloadPackage = async () => {
    if (!submissionId) return

    try {
      const pkg = await submissionAPI.getDownloadPackage(submissionId)
      setDownloadPackage(pkg)

      // Set first file as preview
      if (pkg.files.length > 0) {
        setSelectedFileUrl(pkg.files[0].url)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load download package')
    }
  }

  const handleDownloadAll = async () => {
    if (!submissionId) return

    try {
      await submissionAPI.downloadAllFiles(submissionId)
    } catch (err: any) {
      alert(`Failed to download files: ${err?.message}`)
    }
  }

  const handleStartNew = () => {
    router.push('/upload')
  }

  if (loading) {
    return (
      <div className="container max-w-7xl py-8 flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <Spinner size="lg" />
          <p className="text-muted-foreground">
            {isGenerating ? 'Generating forms...' : 'Loading...'}
          </p>
        </div>
      </div>
    )
  }

  if (error || !submission) {
    return (
      <div className="container max-w-7xl py-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error || 'Submission not found'}</AlertDescription>
        </Alert>
        <Button className="mt-4" onClick={() => router.push('/upload')}>
          Return to Upload
        </Button>
      </div>
    )
  }

  const isCompleted = submission.status === 'completed' && downloadPackage

  return (
    <div className="container max-w-7xl py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold tracking-tight">
            Download Submission
          </h1>
          <Badge
            variant={isCompleted ? 'success' : 'default'}
            className="text-sm"
          >
            {submission.status}
          </Badge>
        </div>
        <p className="text-muted-foreground">
          {isCompleted
            ? 'Your submission package is ready to download'
            : 'Generating your submission package...'}
        </p>
      </div>

      {/* Generation in progress */}
      {isGenerating && (
        <Alert className="mb-6">
          <Spinner size="sm" className="mr-2" />
          <AlertTitle>Generating Forms</AlertTitle>
          <AlertDescription>
            Creating ACORD forms and carrier applications. This may take a
            minute...
          </AlertDescription>
        </Alert>
      )}

      {/* Success message */}
      {isCompleted && (
        <Alert variant="success" className="mb-6">
          <AlertTitle>✓ Generation Complete</AlertTitle>
          <AlertDescription>
            All forms have been generated successfully. You can now download your
            submission package.
          </AlertDescription>
        </Alert>
      )}

      {/* Package Summary */}
      {downloadPackage && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Submission Package</CardTitle>
            <CardDescription>
              {downloadPackage.applicant_name || 'Submission'} •{' '}
              {downloadPackage.total_files} file
              {downloadPackage.total_files > 1 ? 's' : ''}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Completed {formatDateTime(downloadPackage.completed_at)}
              </div>
              <DownloadButton
                onClick={handleDownloadAll}
                variant="default"
                size="lg"
              >
                Download All Files
              </DownloadButton>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Files Grid */}
      {downloadPackage && downloadPackage.files.length > 0 && (
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* File List */}
          <Card>
            <CardHeader>
              <CardTitle>Generated Files</CardTitle>
              <CardDescription>Click to preview or download</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {downloadPackage.files.map((file, index) => (
                  <div
                    key={index}
                    className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors hover:bg-muted/50 ${
                      selectedFileUrl === file.url ? 'bg-muted' : ''
                    }`}
                    onClick={() => setSelectedFileUrl(file.url)}
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="text-2xl">📄</div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">
                          {file.form_type}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {file.filename} • {formatFileSize(file.size_bytes)}
                        </div>
                      </div>
                    </div>
                    <DownloadButton
                      onClick={async (e) => {
                        e.stopPropagation()
                        await submissionAPI.downloadFile(file.url, file.filename)
                      }}
                      variant="ghost"
                      size="sm"
                    >
                      Download
                    </DownloadButton>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>
                {selectedFileUrl
                  ? 'PDF preview (if supported by browser)'
                  : 'Select a file to preview'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedFileUrl ? (
                <DocumentPreview url={selectedFileUrl} />
              ) : (
                <div className="flex items-center justify-center h-[500px] bg-muted/30 rounded-lg">
                  <p className="text-muted-foreground">No file selected</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => router.push(`/review?id=${submissionId}`)}>
          Back to Review
        </Button>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => router.push('/')}>
            Return Home
          </Button>
          <Button onClick={handleStartNew}>Start New Submission</Button>
        </div>
      </div>

      {/* Submission Summary */}
      {submission.applicant && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Submission Details</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="font-medium text-muted-foreground">Applicant</dt>
                <dd>{submission.applicant.business_name}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">FEIN</dt>
                <dd>{submission.applicant.fein || 'N/A'}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">
                  Locations
                </dt>
                <dd>{submission.locations.length}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">
                  Loss History
                </dt>
                <dd>{submission.loss_history.length}</dd>
              </div>
              {submission.carrier_name && (
                <div>
                  <dt className="font-medium text-muted-foreground">Carrier</dt>
                  <dd>{submission.carrier_name}</dd>
                </div>
              )}
              {submission.broker_name && (
                <div>
                  <dt className="font-medium text-muted-foreground">Broker</dt>
                  <dd>{submission.broker_name}</dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>
      )}
    </div>
  )
}