'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import submissionAPI from '@/lib/api/submission-api'
import type {
  Submission,
  SubmissionStatus,
  SubmissionSummary,
  SubmissionCreateRequest,
} from '@/types/submission'
import type {
  UploadResponse,
  ExtractionResponse,
  ValidationResponse,
  GenerationResponse,
} from '@/types/api'

/**
 * Submission workflow state
 */
interface SubmissionState {
  // Current Project
  currentSubmission: Submission | null
  currentSubmissionId: string | null

  // Workflow states
  isUploading: boolean
  isExtracting: boolean
  isValidating: boolean
  isGenerating: boolean
  isProcessing: boolean

  // Results
  uploadResult: UploadResponse | null
  extractionResult: ExtractionResponse | null
  validationResult: ValidationResponse | null
  generationResult: GenerationResponse | null

  // Progress tracking
  uploadProgress: number
  workflowStep: 'upload' | 'extract' | 'validate' | 'generate' | 'download' | null

  // Errors
  error: string | null

  // Recent projects
  recentSubmissions: SubmissionSummary[]
}

/**
 * Submission workflow actions
 */
interface SubmissionActions {
  // Project management
  setCurrentSubmission: (submission: Submission | null) => void
  loadSubmission: (id: string) => Promise<Submission | null>
  createSubmission: (metadata?: SubmissionCreateRequest) => Promise<string | null>
  updateSubmission: (id: string, data: any) => Promise<void>
  deleteSubmission: (id: string) => Promise<void>

  // Workflow steps
  uploadFiles: (
    submissionId: string,
    files: File[],
    onProgress?: (progress: number) => void
  ) => Promise<UploadResponse | null>
  extractData: (submissionId: string) => Promise<ExtractionResponse | null>
  validateSubmission: (submissionId: string) => Promise<ValidationResponse | null>
  generateForms: (submissionId: string) => Promise<GenerationResponse | null>

  // Complete workflow
  executeFullWorkflow: (
    files: File[],
    metadata?: SubmissionCreateRequest,
    options?: {
      onUploadProgress?: (progress: number) => void
      onStatusChange?: (status: SubmissionStatus) => void
    }
  ) => Promise<Submission | null>

  // Recent projects
  loadRecentSubmissions: () => Promise<void>
  addToRecentSubmissions: (submission: Submission) => void

  // Utilities
  clearError: () => void
  resetWorkflow: () => void
  setWorkflowStep: (step: SubmissionState['workflowStep']) => void
}

/**
 * Combined store type
 */
type SubmissionStore = SubmissionState & SubmissionActions

/**
 * Initial state
 */
const initialState: SubmissionState = {
  currentSubmission: null,
  currentSubmissionId: null,
  isUploading: false,
  isExtracting: false,
  isValidating: false,
  isGenerating: false,
  isProcessing: false,
  uploadResult: null,
  extractionResult: null,
  validationResult: null,
  generationResult: null,
  uploadProgress: 0,
  workflowStep: null,
  error: null,
  recentSubmissions: [],
}

/**
 * Submission workflow store
 */
export const useSubmission = create<SubmissionStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Set current project
      setCurrentSubmission: (submission) => {
        set({
          currentSubmission: submission,
          currentSubmissionId: submission?.id || null,
        })

        if (submission) {
          get().addToRecentSubmissions(submission)
        }
      },

      // Load project by ID
      loadSubmission: async (id) => {
        try {
          set({ error: null })
          const submission = await submissionAPI.getSubmission(id)
          get().setCurrentSubmission(submission)
          return submission
        } catch (err: any) {
          const errorMessage = err?.message || 'Failed to load submission'
          set({ error: errorMessage })
          return null
        }
      },

      // Create new submission
      createSubmission: async (metadata) => {
        try {
          set({ error: null })
          const result = await submissionAPI.createSubmission(metadata)
          set({ currentSubmissionId: result.submission_id })
          return result.submission_id
        } catch (err: any) {
          const errorMessage = err?.message || 'Failed to create submission'
          set({ error: errorMessage })
          return null
        }
      },

      // Update submission
      updateSubmission: async (id, data) => {
        try {
          set({ error: null })
          const updated = await submissionAPI.updateSubmission(id, data)
          get().setCurrentSubmission(updated)
        } catch (err: any) {
          const errorMessage = err?.message || 'Failed to update submission'
          set({ error: errorMessage })
          throw err
        }
      },

      // Delete submission
      deleteSubmission: async (id) => {
        try {
          set({ error: null })
          await submissionAPI.deleteSubmission(id)

          // Remove from recent submissions
          const recentSubmissions = get().recentSubmissions.filter(
            (s) => s.id !== id
          )
          set({ recentSubmissions })

          // Clear current if it's the deleted one
          if (get().currentSubmissionId === id) {
            set({ currentSubmission: null, currentSubmissionId: null })
          }
        } catch (err: any) {
          const errorMessage = err?.message || 'Failed to delete submission'
          set({ error: errorMessage })
          throw err
        }
      },

      // Upload files
      uploadFiles: async (submissionId, files, onProgress) => {
        try {
          set({
            isUploading: true,
            workflowStep: 'upload',
            uploadProgress: 0,
            error: null,
          })

          const result = await submissionAPI.uploadFiles(
            submissionId,
            files,
            (progress) => {
              set({ uploadProgress: progress })
              onProgress?.(progress)
            }
          )

          set({ uploadResult: result })

          // Reload submission
          await get().loadSubmission(submissionId)

          return result
        } catch (err: any) {
          const errorMessage = err?.message || 'Upload failed'
          set({ error: errorMessage })
          return null
        } finally {
          set({ isUploading: false, uploadProgress: 0 })
        }
      },

      // Extract data
      extractData: async (submissionId) => {
        try {
          set({
            isExtracting: true,
            workflowStep: 'extract',
            error: null,
          })

          const result = await submissionAPI.extractData(submissionId)
          set({ extractionResult: result })

          // Poll for completion
          const submission = await submissionAPI.pollSubmissionStatus(
            submissionId,
            ['extracted', 'error']
          )

          get().setCurrentSubmission(submission)

          return result
        } catch (err: any) {
          const errorMessage = err?.message || 'Extraction failed'
          set({ error: errorMessage })
          return null
        } finally {
          set({ isExtracting: false })
        }
      },

      // Validate submission
      validateSubmission: async (submissionId) => {
        try {
          set({
            isValidating: true,
            workflowStep: 'validate',
            error: null,
          })

          const result = await submissionAPI.validateSubmission(submissionId)
          set({ validationResult: result })

          // Reload submission
          await get().loadSubmission(submissionId)

          return result
        } catch (err: any) {
          const errorMessage = err?.message || 'Validation failed'
          set({ error: errorMessage })
          return null
        } finally {
          set({ isValidating: false })
        }
      },

      // Generate forms
      generateForms: async (submissionId) => {
        try {
          set({
            isGenerating: true,
            workflowStep: 'generate',
            error: null,
          })

          const result = await submissionAPI.generateForms(submissionId)
          set({ generationResult: result })

          // Poll for completion
          const submission = await submissionAPI.pollSubmissionStatus(
            submissionId,
            ['completed', 'error']
          )

          get().setCurrentSubmission(submission)

          return result
        } catch (err: any) {
          const errorMessage = err?.message || 'Generation failed'
          set({ error: errorMessage })
          return null
        } finally {
          set({ isGenerating: false })
        }
      },

      // Execute full workflow
      executeFullWorkflow: async (files, metadata, options) => {
        try {
          set({
            isProcessing: true,
            error: null,
            workflowStep: 'upload',
          })

          // Create submission
          const submissionId = await get().createSubmission(metadata)
          if (!submissionId) {
            throw new Error('Failed to create submission')
          }

          // Upload files
          set({ workflowStep: 'upload' })
          await get().uploadFiles(
            submissionId,
            files,
            options?.onUploadProgress
          )

          // Extract data
          set({ workflowStep: 'extract' })
          options?.onStatusChange?.('extracting')
          await get().extractData(submissionId)

          // Validate
          set({ workflowStep: 'validate' })
          options?.onStatusChange?.('validating')
          const validationResult = await get().validateSubmission(submissionId)

          if (!validationResult?.can_proceed_to_generation) {
            throw new Error('Validation failed - cannot proceed to generation')
          }

          // Generate forms
          set({ workflowStep: 'generate' })
          options?.onStatusChange?.('generating')
          await get().generateForms(submissionId)

          // Load final submission
          set({ workflowStep: 'download' })
          const submission = await get().loadSubmission(submissionId)

          return submission
        } catch (err: any) {
          const errorMessage = err?.message || 'Workflow failed'
          set({ error: errorMessage })
          return null
        } finally {
          set({ isProcessing: false })
        }
      },

      // Load recent submissions
      loadRecentSubmissions: async () => {
        try {
          const result = await submissionAPI.getRecent(10)
          set({ recentSubmissions: result.items })
        } catch (err: any) {
          console.error('Failed to load recent submissions:', err)
        }
      },

      // Add to recent submissions
      addToRecentSubmissions: (submission) => {
        const recentSubmissions = get().recentSubmissions
        const summary: SubmissionSummary = {
            id: submission.id,
            status: submission.status,
            applicant_name: submission.applicant?.business_name,
            total_locations: submission.locations?.length || 0,
            total_losses: submission.loss_history?.length || 0,
            total_tiv: submission.locations?.reduce((sum, loc) => sum + (loc.total_insured_value || 0), 0) || 0,
            completeness: 0, // Can be calculated from validation result if available
            is_valid: submission.is_valid || false,
            validation_errors_count: submission.validation_errors?.length || 0,
            validation_warnings_count: submission.validation_warnings?.length || 0,
            created_at: submission.created_at,
            updated_at: submission.updated_at,
          }
        const filtered = recentSubmissions.filter((s) => s.id !== submission.id)
        const updated = [summary, ...filtered].slice(0, 10)
        set({ recentSubmissions: updated })
      },

      // Clear error
      clearError: () => {
        set({ error: null })
      },

      // Reset workflow
      resetWorkflow: () => {
        set({
          ...initialState,
          recentSubmissions: get().recentSubmissions, // Keep recent submissions
        })
      },

      // Set workflow step
      setWorkflowStep: (step) => {
        set({ workflowStep: step })
      },
    }),
    {
      name: 'submitez-submission-store',
      partialize: (state) => ({
        // Only persist these fields
        currentSubmissionId: state.currentSubmissionId,
        recentSubmissions: state.recentSubmissions,
      }),
    }
  )
)

/**
 * Selector hooks for specific state slices
 */

// Current submission selectors
export const useCurrentSubmission = () =>
  useSubmission((state) => state.currentSubmission)

export const useCurrentSubmissionId = () =>
  useSubmission((state) => state.currentSubmissionId)

// Workflow state selectors
export const useIsUploading = () => useSubmission((state) => state.isUploading)
export const useIsExtracting = () => useSubmission((state) => state.isExtracting)
export const useIsValidating = () => useSubmission((state) => state.isValidating)
export const useIsGenerating = () => useSubmission((state) => state.isGenerating)
export const useIsProcessing = () => useSubmission((state) => state.isProcessing)

// Progress selectors
export const useUploadProgress = () => useSubmission((state) => state.uploadProgress)
export const useWorkflowStep = () => useSubmission((state) => state.workflowStep)

// Results selectors
export const useValidationResult = () =>
  useSubmission((state) => state.validationResult)
export const useGenerationResult = () =>
  useSubmission((state) => state.generationResult)

// Error selector
export const useSubmissionError = () => useSubmission((state) => state.error)

// Recent submissions selector
export const useRecentSubmissions = () =>
  useSubmission((state) => state.recentSubmissions)

// Computed selectors
export const useIsWorkflowActive = () =>
  useSubmission(
    (state) =>
      state.isUploading ||
      state.isExtracting ||
      state.isValidating ||
      state.isGenerating ||
      state.isProcessing
  )

export const useCanProceedToGeneration = () =>
  useSubmission((state) => state.validationResult?.can_proceed_to_generation || false)