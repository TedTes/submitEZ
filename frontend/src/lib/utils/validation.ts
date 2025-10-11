/**
 * Client-side validation utilities
 */

import { FILE_UPLOAD } from '../constants'

/**
 * Validate email address
 */
export function isValidEmail(email: string): boolean {
  if (!email) return false

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (US format)
 */
export function isValidPhone(phone: string): boolean {
  if (!phone) return false

  const cleaned = phone.replace(/\D/g, '')
  return cleaned.length === 10 || (cleaned.length === 11 && cleaned.startsWith('1'))
}

/**
 * Validate FEIN (Federal Employer Identification Number)
 */
export function isValidFEIN(fein: string): boolean {
  if (!fein) return false

  const cleaned = fein.replace(/\D/g, '')

  if (cleaned.length !== 9) return false

  // Check invalid first two digits
  const invalidPrefixes = ['00', '07', '08', '09', '17', '18', '19', '78', '79']
  const prefix = cleaned.substring(0, 2)

  return !invalidPrefixes.includes(prefix)
}

/**
 * Validate ZIP code
 */
export function isValidZipCode(zip: string): boolean {
  if (!zip) return false

  const zipRegex = /^\d{5}(-\d{4})?$/
  return zipRegex.test(zip)
}

/**
 * Validate US state code
 */
export function isValidState(state: string): boolean {
  if (!state || state.length !== 2) return false

  const validStates = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'PR', 'VI', 'GU', 'AS', 'MP',
  ]

  return validStates.includes(state.toUpperCase())
}

/**
 * Validate NAICS code
 */
export function isValidNAICS(naics: string): boolean {
  if (!naics) return false

  const cleaned = naics.replace(/\D/g, '')
  return cleaned.length >= 2 && cleaned.length <= 6
}

/**
 * Validate year
 */
export function isValidYear(
  year: number | string,
  options?: { min?: number; max?: number }
): boolean {
  const yearNum = typeof year === 'string' ? parseInt(year, 10) : year

  if (isNaN(yearNum)) return false

  const currentYear = new Date().getFullYear()
  const min = options?.min || 1800
  const max = options?.max || currentYear + 1

  return yearNum >= min && yearNum <= max
}

/**
 * Validate URL
 */
export function isValidURL(url: string): boolean {
  if (!url) return false

  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Validate file type
 */
export function isValidFileType(file: File): boolean {
  const extension = `.${file.name.split('.').pop()?.toLowerCase()}` as '.pdf' | '.xlsx' |  '.xls'| '.docx'| '.doc'
  return FILE_UPLOAD.allowedExtensions.includes(extension)
}

/**
 * Validate file size
 */
export function isValidFileSize(file: File): boolean {
  return file.size <= FILE_UPLOAD.maxFileSize
}

/**
 * Validate file for upload
 */
export interface FileValidationResult {
  valid: boolean
  errors: string[]
}

export function validateFile(file: File): FileValidationResult {
  const errors: string[] = []

  if (!isValidFileType(file)) {
    errors.push(
      `Invalid file type. Allowed types: ${FILE_UPLOAD.allowedExtensions.join(', ')}`
    )
  }

  if (!isValidFileSize(file)) {
    errors.push(
      `File too large. Maximum size: ${FILE_UPLOAD.maxFileSize / (1024 * 1024)}MB`
    )
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * Validate multiple files
 */
export function validateFiles(files: File[]): FileValidationResult {
  const errors: string[] = []

  if (files.length > FILE_UPLOAD.maxFiles) {
    errors.push(`Too many files. Maximum: ${FILE_UPLOAD.maxFiles}`)
  }

  files.forEach((file, index) => {
    const result = validateFile(file)
    if (!result.valid) {
      errors.push(`File ${index + 1} (${file.name}): ${result.errors.join(', ')}`)
    }
  })

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * Validate currency amount
 */
export function isValidCurrency(amount: string | number): boolean {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return !isNaN(num) && num >= 0
}

/**
 * Validate required field
 */
export function isRequired(value: any): boolean {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  return true
}

/**
 * Validate minimum length
 */
export function hasMinLength(value: string, minLength: number): boolean {
  return value && value.length >= minLength || false
}

/**
 * Validate maximum length
 */
export function hasMaxLength(value: string, maxLength: number): boolean {
  return !value || value.length <= maxLength
}

/**
 * Validate numeric value
 */
export function isNumeric(value: string): boolean {
  return !isNaN(parseFloat(value)) && isFinite(Number(value))
}

/**
 * Validate integer value
 */
export function isInteger(value: string | number): boolean {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return Number.isInteger(num)
}

/**
 * Validate range
 */
export function isInRange(
  value: number,
  min: number,
  max: number
): boolean {
  return value >= min && value <= max
}

/**
 * Sanitize string (remove dangerous characters)
 */
export function sanitizeString(value: string): string {
  if (!value) return ''

  return value
    .trim()
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/\s+/g, ' ') // Normalize whitespace
}

/**
 * Clean phone number (remove non-numeric)
 */
export function cleanPhone(phone: string): string {
  return phone.replace(/\D/g, '')
}

/**
 * Clean FEIN (remove non-numeric)
 */
export function cleanFEIN(fein: string): string {
  return fein.replace(/\D/g, '')
}

/**
 * Clean ZIP code (remove non-numeric)
 */
export function cleanZipCode(zip: string): string {
  return zip.replace(/\D/g, '').substring(0, 9)
}