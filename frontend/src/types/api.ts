/**
 * API Response types
 */

import { Submission, SubmissionSummary } from './submission'

export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
  status_code?: number
}

export interface ApiError {
  error: string
  message: string
  status_code: number
  path?: string
  method?: string
  payload?: Record<string, any>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export interface UploadResponse {
  submission_id: string
  total_files: number
  successful_uploads: number
  failed_uploads: number
  uploaded_files: Array<{
    filename: string
    original_filename: string
    storage_path: string
    url: string
    size_bytes: number
    content_type: string
    uploaded_at: string
  }>
  errors: Array<{
    filename: string
    error: string
  }>
}

export interface ExtractionResponse {
  extraction_id: string
  submission_id: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'partial'
  overall_confidence: number
  extracted_data: {
    applicant?: any
    locations?: any[]
    coverage?: any
    loss_history?: any[]
  }
  duration_seconds: number
  started_at: string
  completed_at: string
}

export interface ValidationResponse {
  validation_id: string
  submission_id: string
  is_valid: boolean
  is_complete: boolean
  completeness_percentage: number
  can_proceed_to_generation: boolean
  can_submit_to_carrier: boolean
  total_errors: number
  total_warnings: number
  total_info: number
  blocking_errors: number
  errors: Array<{
    field_path: string
    severity: 'error' | 'warning' | 'info'
    category: string
    message: string
    blocking?: boolean
  }>
  warnings: Array<{
    field_path: string
    severity: 'error' | 'warning' | 'info'
    category: string
    message: string
  }>
  validated_at: string
}

export interface GenerationResponse {
  generation_id: string
  submission_id: string
  status: 'completed' | 'failed'
  total_forms: number
  successful_forms: number
  failed_forms: number
  generated_files: Array<{
    form_type: string
    filename: string
    storage_path: string
    url: string
    size_bytes: number
    generated_at: string
  }>
  errors: Array<{
    form_type: string
    error: string
  }>
  started_at: string
  completed_at: string
  duration_seconds: number
}

export interface WorkflowResponse {
  submission_id: string
  overall_status: 'completed' | 'failed' | 'partial'
  steps: {
    extraction?: {
      status: 'completed' | 'failed'
      confidence?: number
      error?: string
    }
    validation?: {
      status: 'completed' | 'failed'
      is_valid?: boolean
      errors?: number
      error?: string
    }
    generation?: {
      status: 'completed' | 'failed'
      files_generated?: number
      error?: string
    }
  }
}

export interface DownloadPackage {
  submission_id: string
  status: string
  applicant_name?: string
  total_files: number
  files: Array<{
    form_type: string
    filename: string
    storage_path: string
    url: string
    size_bytes: number
    generated_at: string
  }>
  created_at: string
  completed_at?: string
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  service: string
  version: string
  timestamp: string
  components?: Record<string, any>
}

export interface StatisticsResponse {
  statistics: {
    total: number
    by_status: Record<string, number>
  }
  timestamp: string
}