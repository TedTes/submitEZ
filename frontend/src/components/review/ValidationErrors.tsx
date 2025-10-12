'use client'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { ValidationError } from '@/types/submission'

interface ValidationErrorsProps {
  errors: ValidationError[]
  warnings: ValidationError[]
  className?: string
}

export function ValidationErrors({
  errors,
  warnings,
  className,
}: ValidationErrorsProps) {
  const hasErrors = errors.length > 0
  const hasWarnings = warnings.length > 0

  if (!hasErrors && !hasWarnings) {
    return null
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Errors */}
      {hasErrors && (
        <Alert variant="destructive">
          <AlertTitle className="flex items-center gap-2">
            <span className="text-lg">❌</span>
            {errors.length} Error{errors.length > 1 ? 's' : ''} Found
          </AlertTitle>
          <AlertDescription>
            <ul className="mt-2 space-y-2">
              {errors.map((error, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="font-mono text-xs mt-1">•</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <code className="text-xs bg-destructive/20 px-1 py-0.5 rounded">
                        {error.field_path}
                      </code>
                      {error.blocking && (
                        <Badge variant="destructive" className="text-xs">
                          Blocking
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm">{error.message}</p>
                    {error.suggested_fix && (
                      <p className="text-xs mt-1 text-muted-foreground">
                        💡 {error.suggested_fix}
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Warnings */}
      {hasWarnings && (
        <Alert variant="warning">
          <AlertTitle className="flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            {warnings.length} Warning{warnings.length > 1 ? 's' : ''}
          </AlertTitle>
          <AlertDescription>
            <ul className="mt-2 space-y-2">
              {warnings.map((warning, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="font-mono text-xs mt-1">•</span>
                  <div className="flex-1">
                    <code className="text-xs bg-yellow-100 dark:bg-yellow-900/20 px-1 py-0.5 rounded">
                      {warning.field_path}
                    </code>
                    <p className="text-sm mt-1">{warning.message}</p>
                  </div>
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}