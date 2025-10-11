/**
 * Application constants and configuration
 */

import type { SubmissionStatus } from '@/types/submission'
import type { ConfidenceLevel } from '@/types/extraction'

/**
 * Application metadata
 */
export const APP_CONFIG = {
  name: 'SubmitEZ',
  version: '1.0.0',
  description: 'AI-Powered Insurance Submission Automation',
  author: 'SubmitEZ Team',
} as const

/**
 * API configuration
 */
export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  timeout: 120000, // 2 minutes
  retryAttempts: 3,
  retryDelay: 1000,
} as const

/**
 * File upload configuration
 */
export const FILE_UPLOAD = {
  maxFileSize: 16 * 1024 * 1024, // 16MB
  maxFiles: 10,
  allowedExtensions: ['.pdf', '.xlsx', '.xls', '.docx', '.doc'],
  allowedMimeTypes: [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
  ],
} as const

/**
 * Submission status configuration
 */
export const SUBMISSION_STATUS: Record<SubmissionStatus,
  {
    label: string
    description: string
    color: string
    icon: string
  }
> = {
  draft: {
    label: 'Draft',
    description: 'Submission created but no files uploaded',
    color: 'gray',
    icon: '📝',
  },
  uploaded: {
    label: 'Uploaded',
    description: 'Files uploaded, ready for extraction',
    color: 'blue',
    icon: '📤',
  },
  extracting: {
    label: 'Extracting',
    description: 'AI is extracting data from documents',
    color: 'yellow',
    icon: '🔄',
  },
  extracted: {
    label: 'Extracted',
    description: 'Data extracted, ready for review',
    color: 'indigo',
    icon: '📊',
  },
  validating: {
    label: 'Validating',
    description: 'Validating submission data',
    color: 'purple',
    icon: '✓',
  },
  validated: {
    label: 'Validated',
    description: 'Data validated, ready for form generation',
    color: 'green',
    icon: '✅',
  },
  generating: {
    label: 'Generating',
    description: 'Generating ACORD and carrier forms',
    color: 'orange',
    icon: '📄',
  },
  completed: {
    label: 'Completed',
    description: 'All forms generated and ready for download',
    color: 'emerald',
    icon: '🎉',
  },
  error: {
    label: 'Error',
    description: 'An error occurred during processing',
    color: 'red',
    icon: '❌',
  },
}

/**
 * Confidence level configuration
 */
export const CONFIDENCE_LEVELS: Record<ConfidenceLevel,
  {
    label: string
    color: string
    threshold: number
  }
> = {
  high: {
    label: 'High Confidence',
    color: 'green',
    threshold: 0.8,
  },
  medium: {
    label: 'Medium Confidence',
    color: 'yellow',
    threshold: 0.5,
  },
  low: {
    label: 'Low Confidence',
    color: 'orange',
    threshold: 0.3,
  },
  unknown: {
    label: 'Unknown',
    color: 'gray',
    threshold: 0,
  },
}

/**
 * Validation severity configuration
 */
export const VALIDATION_SEVERITY = {
  error: {
    label: 'Error',
    color: 'red',
    icon: '❌',
    blocking: true,
  },
  warning: {
    label: 'Warning',
    color: 'yellow',
    icon: '⚠️',
    blocking: false,
  },
  info: {
    label: 'Info',
    color: 'blue',
    icon: 'ℹ️',
    blocking: false,
  },
} as const

/**
 * ACORD form types
 */
export const ACORD_FORMS = {
  '125': {
    name: 'ACORD 125',
    description: 'Commercial Insurance Application',
    coverageTypes: ['Property', 'General Liability'],
  },
  '140': {
    name: 'ACORD 140',
    description: 'Property Section',
    coverageTypes: ['Property'],
  },
  '126': {
    name: 'ACORD 126',
    description: 'Commercial General Liability',
    coverageTypes: ['General Liability'],
  },
  '130': {
    name: 'ACORD 130',
    description: "Workers' Compensation Application",
    coverageTypes: ["Workers' Compensation"],
  },
} as const

/**
 * US States
 */
export const US_STATES = [
  { code: 'AL', name: 'Alabama' },
  { code: 'AK', name: 'Alaska' },
  { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' },
  { code: 'CA', name: 'California' },
  { code: 'CO', name: 'Colorado' },
  { code: 'CT', name: 'Connecticut' },
  { code: 'DE', name: 'Delaware' },
  { code: 'FL', name: 'Florida' },
  { code: 'GA', name: 'Georgia' },
  { code: 'HI', name: 'Hawaii' },
  { code: 'ID', name: 'Idaho' },
  { code: 'IL', name: 'Illinois' },
  { code: 'IN', name: 'Indiana' },
  { code: 'IA', name: 'Iowa' },
  { code: 'KS', name: 'Kansas' },
  { code: 'KY', name: 'Kentucky' },
  { code: 'LA', name: 'Louisiana' },
  { code: 'ME', name: 'Maine' },
  { code: 'MD', name: 'Maryland' },
  { code: 'MA', name: 'Massachusetts' },
  { code: 'MI', name: 'Michigan' },
  { code: 'MN', name: 'Minnesota' },
  { code: 'MS', name: 'Mississippi' },
  { code: 'MO', name: 'Missouri' },
  { code: 'MT', name: 'Montana' },
  { code: 'NE', name: 'Nebraska' },
  { code: 'NV', name: 'Nevada' },
  { code: 'NH', name: 'New Hampshire' },
  { code: 'NJ', name: 'New Jersey' },
  { code: 'NM', name: 'New Mexico' },
  { code: 'NY', name: 'New York' },
  { code: 'NC', name: 'North Carolina' },
  { code: 'ND', name: 'North Dakota' },
  { code: 'OH', name: 'Ohio' },
  { code: 'OK', name: 'Oklahoma' },
  { code: 'OR', name: 'Oregon' },
  { code: 'PA', name: 'Pennsylvania' },
  { code: 'RI', name: 'Rhode Island' },
  { code: 'SC', name: 'South Carolina' },
  { code: 'SD', name: 'South Dakota' },
  { code: 'TN', name: 'Tennessee' },
  { code: 'TX', name: 'Texas' },
  { code: 'UT', name: 'Utah' },
  { code: 'VT', name: 'Vermont' },
  { code: 'VA', name: 'Virginia' },
  { code: 'WA', name: 'Washington' },
  { code: 'WV', name: 'West Virginia' },
  { code: 'WI', name: 'Wisconsin' },
  { code: 'WY', name: 'Wyoming' },
  { code: 'DC', name: 'District of Columbia' },
] as const

/**
 * Coverage types
 */
export const COVERAGE_TYPES = [
  'Property',
  'General Liability',
  'Commercial Auto',
  'Workers Compensation',
  'Professional Liability',
  'Cyber Liability',
  'Umbrella',
] as const

/**
 * Construction types
 */
export const CONSTRUCTION_TYPES = [
  'Frame',
  'Joisted Masonry',
  'Non-Combustible',
  'Masonry Non-Combustible',
  'Modified Fire Resistive',
  'Fire Resistive',
] as const

/**
 * Occupancy types
 */
export const OCCUPANCY_TYPES = [
  'Office',
  'Retail',
  'Warehouse',
  'Manufacturing',
  'Restaurant',
  'Apartment',
  'Mixed Use',
  'Other',
] as const

/**
 * Loss types
 */
export const LOSS_TYPES = [
  'Fire',
  'Water',
  'Wind',
  'Hail',
  'Theft',
  'Vandalism',
  'Bodily Injury',
  'Property Damage',
  'Product Liability',
  'Professional Error',
  'Cyber',
  'Other',
] as const

/**
 * Claim statuses
 */
export const CLAIM_STATUSES = [
  'Open',
  'Closed',
  'Pending',
  'Denied',
  'Withdrawn',
] as const

/**
 * Date format configurations
 */
export const DATE_FORMATS = {
  short: 'MMM d, yyyy',
  medium: 'MMM d, yyyy h:mm a',
  long: 'MMMM d, yyyy h:mm:ss a',
  iso: "yyyy-MM-dd'T'HH:mm:ss",
} as const

/**
 * Currency format configuration
 */
export const CURRENCY_CONFIG = {
  locale: 'en-US',
  currency: 'USD',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
} as const

/**
 * Pagination defaults
 */
export const PAGINATION = {
  defaultLimit: 20,
  maxLimit: 100,
  pageSizeOptions: [10, 20, 50, 100],
} as const

/**
 * Polling configuration
 */
export const POLLING_CONFIG = {
  interval: 2000, // 2 seconds
  timeout: 300000, // 5 minutes
  maxRetries: 150,
} as const

/**
 * Toast notification durations (ms)
 */
export const TOAST_DURATION = {
  success: 3000,
  error: 5000,
  warning: 4000,
  info: 3000,
} as const

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  authToken: 'submitez_auth_token',
  userPreferences: 'submitez_user_prefs',
  recentSubmissions: 'submitez_recent_submissions',
} as const

/**
 * Routes
 */
export const ROUTES = {
  home: '/',
  upload: '/upload',
  review: '/review',
  download: '/download',
  submissions: '/submissions',
  submission: (id: string) => `/submissions/${id}`,
} as const