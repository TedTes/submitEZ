'use client'

import { useEffect, useState } from 'react'
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
import { Input } from '@/components/ui/input'
import submissionAPI from '@/lib/api/submission-api'
import type { SubmissionSummary } from '@/types/submission'
import { formatDateTime } from '@/lib/utils/format'
import { SUBMISSION_STATUS } from '@/lib/constants'

export default function SubmissionsPage() {
  const router = useRouter()
  const [submissions, setSubmissions] = useState<SubmissionSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadSubmissions()
  }, [])

  const loadSubmissions = async () => {
    try {
      setLoading(true)
      const result = await submissionAPI.listSubmissions({ limit: 50 })
      setSubmissions(result.items)
    } catch (error) {
      console.error('Failed to load submissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredSubmissions = submissions.filter((s) =>
    s.applicant_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="container max-w-7xl py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            All Submissions
          </h1>
          <p className="text-muted-foreground">
            Manage and track all your insurance submissions
          </p>
        </div>
        <Link href="/dashboard/upload">
          <Button>New Submission</Button>
        </Link>
      </div>

      {/* Search */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <Input
            placeholder="Search by applicant name or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </CardContent>
      </Card>

      {/* Submissions List */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredSubmissions.length} Submission
            {filteredSubmissions.length !== 1 ? 's' : ''}
          </CardTitle>
          <CardDescription>
            Click on any submission to view details
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Loading submissions...</p>
            </div>
          ) : filteredSubmissions.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                {searchQuery
                  ? 'No submissions match your search'
                  : 'No submissions yet'}
              </p>
              {!searchQuery && (
                <Link href="/dashboard/upload">
                  <Button>Create First Submission</Button>
                </Link>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                  onClick={() => {
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
                    View
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