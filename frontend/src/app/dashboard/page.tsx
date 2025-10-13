'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useSubmission, useRecentSubmissions } from '@/hooks/useSubmission'
import { formatDateTime } from '@/lib/utils/format'
import { SUBMISSION_STATUS } from '@/lib/constants'

export default function DashboardPage() {
  const router = useRouter()
  const { loadRecentSubmissions } = useSubmission()
  const recentSubmissions = useRecentSubmissions()

  useEffect(() => {
    loadRecentSubmissions()
  }, [loadRecentSubmissions])

  return (
    <div className="container max-w-7xl py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Welcome to SubmitEZ
        </h1>
        <p className="text-muted-foreground">
          Start a new submission or continue working on an existing one
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📤</span>
            </div>
            <CardTitle>New Submission</CardTitle>
            <CardDescription>
              Upload documents to start a new submission
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/upload">
              <Button className="w-full">Start New</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📋</span>
            </div>
            <CardTitle>View Submissions</CardTitle>
            <CardDescription>
              Browse all your submissions and their status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/submissions">
              <Button variant="outline" className="w-full">
                View All
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <CardTitle>Statistics</CardTitle>
            <CardDescription>
              View your submission analytics and insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              Coming Soon
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Submissions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Submissions</CardTitle>
          <CardDescription>
            Your latest submissions and their current status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recentSubmissions.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                No submissions yet. Start your first submission to get started!
              </p>
              <Link href="/dashboard/upload">
                <Button>Create First Submission</Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                  onClick={() => {
                    // Navigate based on status
                    if (submission.status === 'completed') {
                      router.push(`/dashboard/download?id=${submission.id}`)
                    } else if (
                      submission.status === 'extracted' ||
                      submission.status === 'validated'
                    ) {
                      router.push(`/dashboard/review?id=${submission.id}`)
                    } else {
                      router.push(`/dashboard/upload?id=${submission.id}`)
                    }
                  }}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium truncate">
                        {submission.applicant_name || 'Untitled Submission'}
                      </h3>
                      <Badge
                        variant={
                          submission.status === 'completed'
                            ? 'success'
                            : submission.status === 'error'
                            ? 'destructive'
                            : 'default'
                        }
                      >
                        {SUBMISSION_STATUS[submission.status]?.label ||
                          submission.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>ID: {submission.id.slice(0, 8)}</span>
                      <span>
                        {submission.total_locations} location
                        {submission.total_locations !== 1 ? 's' : ''}
                      </span>
                      <span>{formatDateTime(submission.created_at)}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    {submission.status === 'completed'
                      ? 'Download'
                      : 'Continue'}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}