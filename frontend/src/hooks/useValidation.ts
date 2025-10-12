'use client'

import { useState } from 'react'
import submissionAPI from '@/lib/api/submission-api'
import type { ValidationResponse } from '@/types/api'

interface UseValidationReturn {
  validationResult: ValidationResponse | null
  isValidating: boolean
  error: string | null
  validate: (submissionId: string) => Promise<void>
  hasErrors: boolean
  hasWarnings: boolean
  errorCount: number
  warningCount: number
  canProceed: boolean
}

export function useValidation(): UseValidationReturn {
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null)
  const [isValidating, setIsValidating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validate = async (submissionId: string) => {
    try {
      setIsValidating(true)
      setError(null)

      const result = await submissionAPI.validateSubmission(submissionId)
      setValidationResult(result)
    } catch (err: any) {
      const errorMessage = err?.message || 'Validation failed'
      setError(errorMessage)
      console.error('Validation error:', err)
    } finally {
      setIsValidating(false)
    }
  }

  return {
    validationResult,
    isValidating,
    error,
    validate,
    hasErrors: (validationResult?.total_errors || 0) > 0,
    hasWarnings: (validationResult?.total_warnings || 0) > 0,
    errorCount: validationResult?.total_errors || 0,
    warningCount: validationResult?.total_warnings || 0,
    canProceed: validationResult?.can_proceed_to_generation || false,
  }
}