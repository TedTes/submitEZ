'use client'

import { Progress } from '@/components/ui/progress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type { SubmissionStatus } from '@/types/submission'

interface ProcessingStep {
  key: SubmissionStatus
  label: string
  icon: string
}

const STEPS: ProcessingStep[] = [
  { key: 'uploaded', label: 'Uploaded', icon: '📤' },
  { key: 'extracting', label: 'Extracting', icon: '🤖' },
  { key: 'validating', label: 'Validating', icon: '✅' },
  { key: 'generating', label: 'Generating', icon: '📄' },
]

interface ProcessingProgressProps {
  currentStatus: SubmissionStatus
  fileCount?: number
}

export function ProcessingProgress({
  currentStatus,
  fileCount = 0,
}: ProcessingProgressProps) {
  // Calculate progress percentage
  const currentStepIndex = STEPS.findIndex((s) => s.key === currentStatus)
  const progress = currentStepIndex >= 0 
    ? ((currentStepIndex + 1) / STEPS.length) * 100 
    : 0

  // Get status message
  const getStatusMessage = () => {
    switch (currentStatus) {
      case 'uploaded':
        return 'Files uploaded successfully'
      case 'extracting':
        return `Extracting data from ${fileCount} document${fileCount !== 1 ? 's' : ''}...`
      case 'validating':
        return 'Validating extracted data...'
      case 'generating':
        return 'Generating ACORD forms...'
      default:
        return 'Processing...'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Processing Your Project</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        <div className="space-y-2">
          <Progress value={progress} className="h-2" />
          <p className="text-sm text-muted-foreground text-center">
            {Math.round(progress)}% Complete
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-4 gap-2">
          {STEPS.map((step, index) => {
            const isCompleted = currentStepIndex > index
            const isCurrent = currentStepIndex === index
            const isPending = currentStepIndex < index

            return (
              <div
                key={step.key}
                className={cn(
                  'flex flex-col items-center gap-2 p-3 rounded-lg transition-colors',
                  isCompleted && 'bg-green-50 dark:bg-green-950',
                  isCurrent && 'bg-blue-50 dark:bg-blue-950',
                  isPending && 'bg-muted/50'
                )}
              >
                <div
                  className={cn(
                    'text-3xl transition-all',
                    isCurrent && 'animate-pulse'
                  )}
                >
                  {isCompleted ? '✓' : step.icon}
                </div>
                <span
                  className={cn(
                    'text-xs font-medium text-center',
                    isCompleted && 'text-green-700 dark:text-green-400',
                    isCurrent && 'text-blue-700 dark:text-blue-400',
                    isPending && 'text-muted-foreground'
                  )}
                >
                  {step.label}
                </span>
              </div>
            )
          })}
        </div>

        {/* Status Message */}
        <div className="text-center p-4 bg-muted/50 rounded-lg">
          <p className="text-sm font-medium">{getStatusMessage()}</p>
          <p className="text-xs text-muted-foreground mt-1">
            This usually takes 1-3 minutes
          </p>
        </div>
      </CardContent>
    </Card>
  )
}