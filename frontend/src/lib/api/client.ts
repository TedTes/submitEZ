/**
 * Axios API client with base configuration and interceptors
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ApiError, ApiResponse } from '@/types/api'

// Get API URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

/**
 * Create configured axios instance
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
})

/**
 * Request interceptor
 * - Add authentication token if available
 * - Add request timestamp
 * - Log requests in development
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add timestamp for request tracking
    config.headers['X-Request-Time'] = new Date().toISOString()
    
    // Add authentication token if available (future implementation)
    // const token = localStorage.getItem('auth_token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    
    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      })
    }
    
    return config
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

/**
 * Response interceptor
 * - Handle successful responses
 * - Transform errors into standardized format
 * - Log responses in development
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      })
    }
    
    return response
  },
  (error: AxiosError<ApiError>) => {
    // Log error
    console.error('[API Response Error]', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      error: error.response?.data || error.message,
    })
    
    // Transform error into standardized format
    const apiError: ApiError = {
      error: error.response?.data?.error || 'UnknownError',
      message: error.response?.data?.message || error.message || 'An unexpected error occurred',
      status_code: error.response?.status || 500,
      path: error.config?.url,
      method: error.config?.method?.toUpperCase(),
    }
    
    // Handle specific error cases
    if (error.code === 'ECONNABORTED') {
      apiError.error = 'TimeoutError'
      apiError.message = 'Request timeout - please try again'
    } else if (error.code === 'ERR_NETWORK') {
      apiError.error = 'NetworkError'
      apiError.message = 'Network error - please check your connection'
    } else if (error.response?.status === 401) {
      // Handle unauthorized (future: redirect to login)
      apiError.message = 'Unauthorized - please log in'
    } else if (error.response?.status === 403) {
      apiError.message = 'Forbidden - you do not have permission'
    } else if (error.response?.status === 404) {
      apiError.message = 'Resource not found'
    } else if (error.response?.status === 413) {
      apiError.message = 'File too large - maximum 16MB per file'
    } else if (error.response?.status === 415) {
      apiError.message = 'Unsupported file type'
    } else if (error.response?.status === 422) {
      apiError.message = error.response?.data?.message || 'Validation error'
    } else if (error.response?.status === 500) {
      apiError.message = 'Server error - please try again later'
    } else if (error.response?.status === 503) {
      apiError.message = 'Service unavailable - please try again later'
    }
    
    return Promise.reject(apiError)
  }
)

/**
 * Helper function to create FormData for file uploads
 */
export const createFormData = (data: Record<string, any>): FormData => {
  const formData = new FormData()
  
  Object.entries(data).forEach(([key, value]) => {
    if (value instanceof FileList) {
      // Handle multiple files
      Array.from(value).forEach((file) => {
        formData.append(key, file)
      })
    } else if (value instanceof File) {
      // Handle single file
      formData.append(key, value)
    } else if (Array.isArray(value)) {
      // Handle arrays
      value.forEach((item) => {
        if (item instanceof File) {
          formData.append(key, item)
        } else {
          formData.append(key, JSON.stringify(item))
        }
      })
    } else if (typeof value === 'object' && value !== null) {
      // Handle objects
      formData.append(key, JSON.stringify(value))
    } else if (value !== undefined && value !== null) {
      // Handle primitives
      formData.append(key, String(value))
    }
  })
  
  return formData
}

/**
 * Helper function to handle file downloads
 */
export const downloadFile = async (url: string, filename?: string): Promise<void> => {
  try {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    })
    
    // Create blob URL
    const blob = new Blob([response.data])
    const blobUrl = window.URL.createObjectURL(blob)
    
    // Create temporary link and trigger download
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(blobUrl)
  } catch (error) {
    console.error('Download error:', error)
    throw error
  }
}

/**
 * Helper to check API health
 */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health')
    return response.status === 200
  } catch (error) {
    return false
  }
}

/**
 * Helper to format API error for display
 */
export const formatApiError = (error: ApiError): string => {
  return error.message || 'An unexpected error occurred'
}

/**
 * Helper to check if error is specific type
 */
export const isApiError = (error: any): error is ApiError => {
  return (
    error &&
    typeof error === 'object' &&
    'error' in error &&
    'message' in error &&
    'status_code' in error
  )
}

/**
 * Export configured client
 */
export default apiClient