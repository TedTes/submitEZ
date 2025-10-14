/**
 * Project API client
 * All API methods for submission workflow operations
 */

import apiClient, { createFormData, downloadFile } from './client'
import { API_ENDPOINTS } from './types'
import type {
  ApiResponse,
  UploadResponse,
  ExtractionResponse,
  ValidationResponse,
  GenerationResponse,
  WorkflowResponse,
  DownloadPackage,
  StatisticsResponse,
  PaginatedResponse,
} from '@/types/api'
import type {
  Submission,
  SubmissionSummary,
  SubmissionCreateRequest,
  SubmissionUpdateRequest,
  SubmissionStatus,
} from '@/types/submission'

/**
 * Query parameters for listing submissions
 */
export interface ListSubmissionsParams {
  status?: SubmissionStatus
  limit?: number
  offset?: number
  sort_by?: 'created_at' | 'updated_at' | 'status'
  sort_order?: 'asc' | 'desc'
  search?: string
}

/**
 * Extract request parameters
 */
export interface ExtractParams {
  force_reextraction?: boolean
  llm_model?: string
  extraction_strategy?: 'fast' | 'accurate' | 'comprehensive'
  include_low_confidence?: boolean
}

/**
 * Validate request parameters
 */
export interface ValidateParams {
  strict_mode?: boolean
}

/**
 * Generate request parameters
 */
export interface GenerateParams {
  forms?: string[] // e.g., ['125', '140']
  carrier_name?: string
}

/**
 * Process workflow parameters
 */
export interface ProcessParams {
  skip_validation?: boolean
  skip_generation?: boolean
}

/**
 * Upload progress callback
 */
export type UploadProgressCallback = (progress: number) => void

/**
 * Submission API class
 */
class SubmissionAPI {
  /**
   * Create a new submission
   */
  async createSubmission(
    data?: SubmissionCreateRequest
  ): Promise<{ submission_id: string; status: string; created_at: string }> {
    const response = await apiClient.post<ApiResponse<{
        submission_id: string
        status: string
        created_at: string
      }>
    >(API_ENDPOINTS.SUBMISSIONS, data)

    return response.data as any
  }

  /**
   * Get submission by ID
   */
  async getSubmission(submissionId: string): Promise<Submission> {
    const response = await apiClient.get<ApiResponse<Submission>>(
      API_ENDPOINTS.SUBMISSION_BY_ID(submissionId)
    )

    return response.data as any
  }

  /**
   * List submissions with optional filters
   */
  async listSubmissions(
    params?: ListSubmissionsParams
  ): Promise<PaginatedResponse<SubmissionSummary>> {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<SubmissionSummary>>
    >(API_ENDPOINTS.SUBMISSIONS, { params })

    return response.data.data!
  }

  /**
   * Update submission data
   */
  async updateSubmission(
    submissionId: string,
    data: SubmissionUpdateRequest
  ): Promise<Submission> {
    const response = await apiClient.patch<ApiResponse<Submission>>(
      API_ENDPOINTS.SUBMISSION_BY_ID(submissionId),
      data
    )

    return response.data.data!
  }

  /**
   * Delete submission
   */
  async deleteSubmission(submissionId: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.SUBMISSION_BY_ID(submissionId))
  }

  /**
   * Upload files to submission
   */
  async uploadFiles(
    submissionId: string,
    files: File[],
    onProgress?: UploadProgressCallback
  ): Promise<UploadResponse> {
    const formData = createFormData({ files })

    const response = await apiClient.post<ApiResponse<UploadResponse>>(
      API_ENDPOINTS.SUBMISSION_UPLOAD(submissionId),
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress(percentCompleted)
          }
        },
      }
    )

    return response.data.data!
  }

  /**
   * Extract data from uploaded files
   */
  async extractData(
    submissionId: string,
    params?: ExtractParams
  ): Promise<ExtractionResponse> {
    const response = await apiClient.post<ApiResponse<ExtractionResponse>>(
      API_ENDPOINTS.SUBMISSION_EXTRACT(submissionId),
      params
    )

    return response.data.data!
  }

  /**
   * Validate submission data
   */
  async validateSubmission(
    submissionId: string,
    params?: ValidateParams
  ): Promise<ValidationResponse> {
    const response = await apiClient.post<ApiResponse<ValidationResponse>>(
      API_ENDPOINTS.SUBMISSION_VALIDATE(submissionId),
      params
    )

    return response.data.data!
  }

  /**
   * Generate ACORD and carrier forms
   */
  async generateForms(
    submissionId: string,
    params?: GenerateParams
  ): Promise<GenerationResponse> {
    const response = await apiClient.post<ApiResponse<GenerationResponse>>(
      API_ENDPOINTS.SUBMISSION_GENERATE(submissionId),
      params
    )

    return response.data.data!
  }

  /**
   * Get download package
   */
  async getDownloadPackage(submissionId: string): Promise<DownloadPackage> {
    const response = await apiClient.get<ApiResponse<DownloadPackage>>(
      API_ENDPOINTS.SUBMISSION_DOWNLOAD(submissionId)
    )

    return response.data.data!
  }

  /**
   * Download a specific file
   */
  async downloadFile(url: string, filename?: string): Promise<void> {
    await downloadFile(url, filename)
  }

  /**
   * Download all files as a zip
   */
  async downloadAllFiles(submissionId: string): Promise<void> {
    const downloadPackage = await this.getDownloadPackage(submissionId)

    // Download each file
    for (const file of downloadPackage.files) {
      await this.downloadFile(file.url, file.filename)
    }
  }

  /**
   * Execute complete workflow (extract -> validate -> generate)
   */
  async processWorkflow(
    submissionId: string,
    params?: ProcessParams
  ): Promise<WorkflowResponse> {
    const response = await apiClient.post<ApiResponse<WorkflowResponse>>(
      API_ENDPOINTS.SUBMISSION_PROCESS(submissionId),
      params
    )

    return response.data.data!
  }

  /**
   * Get project summary
   */
  async getSubmissionSummary(submissionId: string): Promise<SubmissionSummary> {
    const response = await apiClient.get<ApiResponse<SubmissionSummary>>(
      API_ENDPOINTS.SUBMISSION_SUMMARY(submissionId)
    )

    return response.data.data!
  }

  /**
   * Get project statistics
   */
  async getStatistics(): Promise<StatisticsResponse> {
    const response = await apiClient.get<ApiResponse<StatisticsResponse>>(
      API_ENDPOINTS.SUBMISSIONS_STATISTICS
    )

    return response.data.data!
  }

  /**
   * Check health status
   */
  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await apiClient.get<ApiResponse<{ status: string; service: string }>
      >(API_ENDPOINTS.HEALTH)

    return response.data.data!
  }

  /**
   * Get detailed health check
   */
  async getDetailedHealth(): Promise<{
    status: string
    service: string
    components: Record<string, any>
  }> {
    const response = await apiClient.get<ApiResponse<{
        status: string
        service: string
        components: Record<string, any>
      }>>
    (API_ENDPOINTS.HEALTH_DETAILED)

    return response.data.data!
  }

  /**
   * Poll submission status until completed or failed
   * Useful for long-running operations
   */
  async pollSubmissionStatus(
    submissionId: string,
    targetStatus: SubmissionStatus | SubmissionStatus[],
    options?: {
      interval?: number // ms between polls
      timeout?: number // ms before giving up
      onProgress?: (submission: Submission) => void
    }
  ): Promise<Submission> {
    const interval = options?.interval || 2000 // 2 seconds
    const timeout = options?.timeout || 300000 // 5 minutes
    const targetStatuses = Array.isArray(targetStatus)
      ? targetStatus
      : [targetStatus]

    const startTime = Date.now()

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const submission = await this.getSubmission(submissionId)

          // Call progress callback
          if (options?.onProgress) {
            options.onProgress(submission)
          }

          // Check if target status reached
          if (targetStatuses.includes(submission.status)) {
            resolve(submission)
            return
          }

          // Check if error status
          if (submission.status === 'error') {
            reject(new Error('Submission processing failed'))
            return
          }

          // Check timeout
          if (Date.now() - startTime > timeout) {
            reject(new Error('Polling timeout exceeded'))
            return
          }

          // Continue polling
          setTimeout(poll, interval)
        } catch (error) {
          reject(error)
        }
      }

      poll()
    })
  }

  /**
   * Convenience method: Create submission and upload files in one call
   */
  async createAndUpload(
    files: File[],
    metadata?: SubmissionCreateRequest,
    onProgress?: UploadProgressCallback
  ): Promise<{ submission: Submission; uploadResult: UploadResponse }> {
    // Create submission
    const { submission_id } = await this.createSubmission(metadata)

    // Upload files
    const uploadResult = await this.uploadFiles(
      submission_id,
      files,
      onProgress
    )

    // Get full submission
    const submission = await this.getSubmission(submission_id)

    return { submission, uploadResult }
  }

  /**
   * Convenience method: Full workflow from upload to download
   */
  async executeFullWorkflow(
    files: File[],
    metadata?: SubmissionCreateRequest,
    options?: {
      onUploadProgress?: UploadProgressCallback
      onStatusChange?: (status: SubmissionStatus) => void
      skipValidation?: boolean
    }
  ): Promise<{
    submission: Submission
    downloadPackage: DownloadPackage
  }> {
    // Create and upload
    const { submission_id } = await this.createSubmission(metadata)
    await this.uploadFiles(submission_id, files, options?.onUploadProgress)

    // Run workflow
    await this.processWorkflow(submission_id, {
      skip_validation: options?.skipValidation,
    })

    // Poll until completed
    const submission = await this.pollSubmissionStatus(
      submission_id,
      ['completed', 'error'],
      {
        onProgress: (s) => {
          if (options?.onStatusChange) {
            options.onStatusChange(s.status)
          }
        },
      }
    )

    // Get download package
    const downloadPackage = await this.getDownloadPackage(submission_id)

    return { submission, downloadPackage }
  }

  /**
   * Batch operations: Get multiple submissions
   */
  async getSubmissions(submissionIds: string[]): Promise<Submission[]> {
    const promises = submissionIds.map((id) => this.getSubmission(id))
    return Promise.all(promises)
  }

  /**
   * Batch operations: Delete multiple submissions
   */
  async deleteSubmissions(submissionIds: string[]): Promise<void> {
    const promises = submissionIds.map((id) => this.deleteSubmission(id))
    await Promise.all(promises)
  }

  /**
   * Search submissions by applicant name
   */
  async searchByApplicant(
    applicantName: string,
    limit = 20
  ): Promise<PaginatedResponse<SubmissionSummary>> {
    return this.listSubmissions({
      search: applicantName,
      limit,
    })
  }

  /**
   * Get submissions by status
   */
  async getByStatus(
    status: SubmissionStatus,
    limit = 50
  ): Promise<PaginatedResponse<SubmissionSummary>> {
    return this.listSubmissions({
      status,
      limit,
    })
  }

  /**
   * Get recent submissions
   */
  async getRecent(
    limit = 20
  ): Promise<PaginatedResponse<SubmissionSummary>> {
    return this.listSubmissions({
      limit,
      sort_by: 'created_at',
      sort_order: 'desc',
    })
  }

  /**
   * Retry failed submission
   */
  async retryFailedSubmission(submissionId: string): Promise<Submission> {
    const submission = await this.getSubmission(submissionId)

    if (submission.status !== 'error') {
      throw new Error('Can only retry failed submissions')
    }

    // Determine which step failed and retry from there
    if (submission.extracted_at) {
      // Extraction succeeded, retry validation/generation
      await this.validateSubmission(submissionId)
      await this.generateForms(submissionId)
    } else if (submission.uploaded_files.length > 0) {
      // Upload succeeded, retry extraction
      await this.extractData(submissionId)
      await this.validateSubmission(submissionId)
      await this.generateForms(submissionId)
    } else {
      throw new Error('Cannot retry - no files uploaded')
    }

    return this.getSubmission(submissionId)
  }
}

// Export singleton instance
const submissionAPI = new SubmissionAPI()
export default submissionAPI

// Also export class for testing
export { SubmissionAPI }