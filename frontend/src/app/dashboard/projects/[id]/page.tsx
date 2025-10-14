'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ProjectHeader } from '@/components/projects/ProjectHeader'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Spinner } from '@/components/ui/spinner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useSubmission } from '@/hooks/useSubmission'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.id as string
  
  const { loadSubmission, currentSubmission } = useSubmission()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
  if (error || !currentSubmission) {
    return (
      <div className="container max-w-7xl py-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error || 'Project not found'}
          </AlertDescription>
        </Alert>
        <Button className="mt-4" onClick={() => router.push('/dashboard')}>
          Back to Projects
        </Button>
      </div>
    )
  }

  return (
    <div className="container max-w-7xl py-8">
      {/* Project Header */}
      <ProjectHeader project={currentSubmission} />

      {/* Main Content - will be added in subsequent commits */}
      <div className="space-y-6">
        {/* Status-based content rendering */}
        {currentSubmission.status === 'draft' && (
          <Card>
            <CardHeader>
              <CardTitle>Get Started</CardTitle>
              <CardDescription>
                Upload documents to begin processing this project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  File upload will be integrated in the next commit (COMMIT 64)
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {currentSubmission.status === 'uploaded' && (
          <Card>
            <CardHeader>
              <CardTitle>Processing</CardTitle>
              <CardDescription>
                Files uploaded, ready for extraction
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Extraction will start automatically or can be triggered manually
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {['extracting', 'validating', 'generating'].includes(currentSubmission.status) && (
          <Card>
            <CardHeader>
              <CardTitle>Processing</CardTitle>
              <CardDescription>
                Your project is being processed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Progress tracking will be added in COMMIT 65
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {['extracted', 'validated'].includes(currentSubmission.status) && (
          <Card>
            <CardHeader>
              <CardTitle>Review Data</CardTitle>
              <CardDescription>
                Review and edit extracted data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Data review interface will be integrated from existing review page
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {currentSubmission.status === 'completed' && (
          <Card>
            <CardHeader>
              <CardTitle>Completed</CardTitle>
              <CardDescription>
                Your forms are ready to download
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  Results view will be added in COMMIT 66
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {currentSubmission.status === 'error' && (
          <Card>
            <CardHeader>
              <CardTitle>Error</CardTitle>
              <CardDescription>
                Something went wrong
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert variant="destructive">
                <AlertDescription>
                  An error occurred during processing. Please try again or contact support.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}

        {/* Temporary navigation */}
        <Card>
          <CardHeader>
            <CardTitle>Temporary Navigation</CardTitle>
            <CardDescription>
              While we're building the unified view, you can still use the old pages
            </CardDescription>
          </CardHeader>
          <CardContent className="flex gap-3">
            <Button 
              variant="outline" 
              onClick={() => router.push(`/dashboard/upload?id=${projectId}`)}
            >
              Upload (Old)
            </Button>
            <Button 
              variant="outline" 
              onClick={() => router.push(`/dashboard/review?id=${projectId}`)}
            >
              Review (Old)
            </Button>
            <Button 
              variant="outline" 
              onClick={() => router.push(`/dashboard/download?id=${projectId}`)}
            >
              Download (Old)
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}