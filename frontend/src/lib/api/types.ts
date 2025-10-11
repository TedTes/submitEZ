/**
 * API client utility types and constants
 */

import { ApiError } from '@/types/api'

/**
 * HTTP Methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

/**
 * Request configuration
 */
export interface RequestConfig {
  headers?: Record<string, string>
  params?: Record<string, any>
  timeout?: number
  signal?: AbortSignal
}

/**
 * Upload progress callback
 */
export type UploadProgressCallback = (progress: number) => void

/**
 * File upload configuration
 */
export interface FileUploadConfig extends RequestConfig {
  onUploadProgress?: UploadProgressCallback
}

/**
 * Retry configuration
 */
export interface RetryConfig {
  maxRetries: number
  retryDelay: number
  retryableStatuses: number[]
}

/**
 * Default retry configuration
 */
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
}

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  // Health
  HEALTH: '/health',
  HEALTH_DETAILED: '/health/detailed',
  
  // Submissions
  SUBMISSIONS: '/api/submissions',
  SUBMISSION_BY_ID: (id: string) => `/api/submissions/${id}`,
  SUBMISSION_UPLOAD: (id: string) => `/api/submissions/${id}/upload`,
  SUBMISSION_EXTRACT: (id: string) => `/api/submissions/${id}/extract`,
  SUBMISSION_VALIDATE: (id: string) => `/api/submissions/${id}/validate`,
  SUBMISSION_GENERATE: (id: string) => `/api/submissions/${id}/generate`,
  SUBMISSION_DOWNLOAD: (id: string) => `/api/submissions/${id}/download`,
  SUBMISSION_PROCESS: (id: string) => `/api/submissions/${id}/process`,
  SUBMISSION_SUMMARY: (id: string) => `/api/submissions/${id}/summary`,
  SUBMISSIONS_STATISTICS: '/api/submissions/statistics',
} as const

/**
 * File type validation
 */
export const ALLOWED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
} as const

export const ALLOWED_FILE_EXTENSIONS = ['.pdf', '.xlsx', '.xls', '.docx', '.doc'] as const

/**
 * File size limits
 */
export const MAX_FILE_SIZE = 16 * 1024 * 1024 // 16MB
export const MAX_FILES_PER_UPLOAD = 10

/**
 * API response status codes
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  REQUEST_TIMEOUT: 408,
  CONFLICT: 409,
  PAYLOAD_TOO_LARGE: 413,
  UNSUPPORTED_MEDIA_TYPE: 415,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const

/**
 * Error categories
 */
export enum ErrorCategory {
  NETWORK = 'network',
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  NOT_FOUND = 'not_found',
  SERVER = 'server',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown',
}

/**
 * Helper to categorize API errors
 */
export const categorizeError = (error: ApiError): ErrorCategory => {
  const status = error.status_code
  
  if (error.error === 'NetworkError' || error.error === 'TimeoutError') {
    return ErrorCategory.NETWORK
  }
  
  if (status === HTTP_STATUS.UNAUTHORIZED) {
    return ErrorCategory.AUTHENTICATION
  }
  
  if (status === HTTP_STATUS.FORBIDDEN) {
    return ErrorCategory.AUTHORIZATION
  }
  
  if (status === HTTP_STATUS.NOT_FOUND) {
    return ErrorCategory.NOT_FOUND
  }
  
  if (
    status === HTTP_STATUS.BAD_REQUEST ||
    status === HTTP_STATUS.UNPROCESSABLE_ENTITY ||
    status === HTTP_STATUS.UNSUPPORTED_MEDIA_TYPE
  ) {
    return ErrorCategory.VALIDATION
  }
  
  if (
    status === HTTP_STATUS.REQUEST_TIMEOUT ||
    status === HTTP_STATUS.GATEWAY_TIMEOUT
  ) {
    return ErrorCategory.TIMEOUT
  }
  
  if (status >= 500) {
    return ErrorCategory.SERVER
  }
  
  return ErrorCategory.UNKNOWN
}

/**
 * Helper to check if error is retryable
 */
export const isRetryableError = (error: ApiError): boolean => {
  return DEFAULT_RETRY_CONFIG.retryableStatuses.includes(error.status_code)
}

/**
 * Helper to format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * Helper to validate file type
 */
export const isValidFileType = (file: File): boolean => {
  const extension = `.${file.name.split('.').pop()?.toLowerCase()}`
  return ALLOWED_FILE_EXTENSIONS.includes(extension as any)
}

/**
 * Helper to validate file size
 */
export const isValidFileSize = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE
}

/**
 * File validation result
 */
export interface FileValidationResult {
  valid: boolean
  error?: string
}

/**
 * Validate file for upload
 */
export const validateFile = (file: File): FileValidationResult => {
  if (!isValidFileType(file)) {
    return {
      valid: false,
      error: `Invalid file type. Allowed types: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`,
    }
  }
  
  if (!isValidFileSize(file)) {
    return {
      valid: false,
      error: `File too large. Maximum size: ${formatFileSize(MAX_FILE_SIZE)}`,
    }
  }
  
  return { valid: true }
}