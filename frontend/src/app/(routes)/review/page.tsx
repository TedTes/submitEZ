'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { DataReviewTable } from '@/components/review/DataReviewTable'
import { ValidationErrors } from '@/components/review/ValidationErrors'
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
import { useValidation } from '@/hooks/useValidation'
import type { Submission } from '@/types/submission'
import { formatConfidence } from '@/lib/utils/format'

export default function ReviewPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const submissionId = searchParams.get('id')

  const [submission, setSubmission] = useState<Submission | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)
  const [activeTab, setActiveTab] = useState<
    'applicant' | 'locations' | 'coverage' | 'losses'
  >('applicant')

  const {
    validationResult,
    isValidating,
    validate,
    hasErrors,
    hasWarnings,
    errorCount,
    warningCount,
  } = useValidation()

  // Load submission
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

      // Auto-extract if status is 'uploaded'
      if (data.status === 'uploaded') {
        await handleExtract()
      }

      // Auto-validate if status is 'extracted'
      if (data.status === 'extracted') {
        await validate(submissionId)
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load submission')
    } finally {
      setLoading(false)
    }
  }

  const handleExtract = async () => {
    if (!submissionId) return

    try {
      setIsExtracting(true)
      await submissionAPI.extractData(submissionId)

      // Poll for completion
      const updatedSubmission = await submissionAPI.pollSubmissionStatus(
        submissionId,
        ['extracted', 'error']
      )

      setSubmission(updatedSubmission)

      // Auto-validate after extraction
      if (updatedSubmission.status === 'extracted') {
        await validate(submissionId)
      }
    } catch (err: any) {
      setError(err?.message || 'Extraction failed')
    } finally {
      setIsExtracting(false)
    }
  }

  const handleSave = async () => {
    if (!submissionId || !submission) return

    try {
      const updated = await submissionAPI.updateSubmission(submissionId, {
        applicant: submission.applicant,
        locations: submission.locations,
        coverage: submission.coverage,
        loss_history: submission.loss_history,
      })

      setSubmission(updated)

      // Re-validate after save
      await validate(submissionId)

      alert('Changes saved successfully')
    } catch (err: any) {
      alert(`Failed to save: ${err?.message}`)
    }
  }

  const handleValidate = async () => {
    if (!submissionId) return
    await validate(submissionId)
  }

  const handleGenerate = async () => {
    if (!submissionId) return

    try {
      await submissionAPI.generateForms(submissionId)

      // Navigate to download page
      router.push(`/download?id=${submissionId}`)
    } catch (err: any) {
      alert(`Failed to generate forms: ${err?.message}`)
    }
  }

  if (loading) {
    return (
      <div className="container max-w-7xl py-8 flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <Spinner size="lg" />
          <p className="text-muted-foreground">Loading submission...</p>
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

  const canGenerate =
    validationResult?.can_proceed_to_generation &&
    submission.status === 'validated'

  return (
    <div className="container max-w-7xl py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold tracking-tight">Review Data</h1>
          {submission.extraction_confidence !== undefined && (
            <Badge variant={submission.extraction_confidence >= 0.8 ? 'success' : 'warning'}>
              {formatConfidence(submission.extraction_confidence)} Confidence
            </Badge>
          )}
        </div>
        <p className="text-muted-foreground">
          Review and edit the extracted data before generating forms
        </p>
      </div>

      {/* Extraction in progress */}
      {isExtracting && (
        <Alert className="mb-6">
          <Spinner size="sm" className="mr-2" />
          <AlertTitle>Extracting Data</AlertTitle>
          <AlertDescription>
            Our AI is analyzing your documents. This may take a minute...
          </AlertDescription>
        </Alert>
      )}

      {/* Validation Summary */}
      {validationResult && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Validation Summary
              {isValidating && <Spinner size="sm" />}
            </CardTitle>
            <CardDescription>
              {validationResult.is_valid
                ? 'All validation checks passed'
                : 'Some issues need attention'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-2xl font-bold">
                  {validationResult.completeness_percentage}%
                </div>
                <div className="text-sm text-muted-foreground">Complete</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-destructive">
                  {errorCount}
                </div>
                <div className="text-sm text-muted-foreground">Errors</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-600">
                  {warningCount}
                </div>
                <div className="text-sm text-muted-foreground">Warnings</div>
              </div>
              <div>
                <div className="text-2xl font-bold">
                  {validationResult.can_proceed_to_generation ? '✓' : '✗'}
                </div>
                <div className="text-sm text-muted-foreground">Ready</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Validation Errors */}
      {(hasErrors || hasWarnings) && validationResult && (
        <ValidationErrors
          errors={validationResult.errors}
          warnings={validationResult.warnings}
          className="mb-6"
        />
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b">
        {['applicant', 'locations', 'coverage', 'losses'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-4 py-2 font-medium capitalize transition-colors ${
              activeTab === tab
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab}
            {tab === 'locations' && ` (${submission.locations.length})`}
            {tab === 'losses' && ` (${submission.loss_history.length})`}
          </button>
        ))}
      </div>

      {/* Data Tables */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          {activeTab === 'applicant' && submission.applicant && (
            <DataReviewTable
              data={submission.applicant}
              type="applicant"
              onChange={(updated) =>
                setSubmission({ ...submission, applicant: updated })
              }
            />
          )}
          {activeTab === 'locations' && (
            <DataReviewTable
              data={submission.locations}
              type="locations"
              onChange={(updated) =>
                setSubmission({ ...submission, locations: updated })
              }
            />
          )}
          {activeTab === 'coverage' && submission.coverage && (
            <DataReviewTable
              data={submission.coverage}
              type="coverage"
              onChange={(updated) =>
                setSubmission({ ...submission, coverage: updated })
              }
            />
          )}
          {activeTab === 'losses' && (
            <DataReviewTable
              data={submission.loss_history}
              type="losses"
              onChange={(updated) =>
                setSubmission({ ...submission, loss_history: updated })
              }
            />
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => router.push('/upload')}>
          Back to Upload
        </Button>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleValidate} disabled={isValidating}>
            {isValidating ? 'Validating...' : 'Re-validate'}
          </Button>
          <Button variant="secondary" onClick={handleSave}>
            Save Changes
          </Button>
          <Button onClick={handleGenerate} disabled={!canGenerate}>
            Generate Forms
          </Button>
        </div>
      </div>
    </div>
  )
}