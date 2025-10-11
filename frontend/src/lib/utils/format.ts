/**
 * Formatting utilities
 */

import { CURRENCY_CONFIG } from '../constants'

/**
 * Format currency amount
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  options?: Partial<typeof CURRENCY_CONFIG>
): string {
  if (amount === null || amount === undefined) return '$0'

  const numericAmount = typeof amount === 'string' ? parseFloat(amount) : amount

  if (isNaN(numericAmount)) return '$0'

  return new Intl.NumberFormat(CURRENCY_CONFIG.locale, {
    style: 'currency',
    currency: CURRENCY_CONFIG.currency,
    minimumFractionDigits: options?.minimumFractionDigits ?? CURRENCY_CONFIG.minimumFractionDigits,
    maximumFractionDigits: options?.maximumFractionDigits ?? CURRENCY_CONFIG.maximumFractionDigits,
    ...options,
  }).format(numericAmount)
}

/**
 * Format number with commas
 */
export function formatNumber(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return '0'

  const numericValue = typeof value === 'string' ? parseFloat(value) : value

  if (isNaN(numericValue)) return '0'

  return new Intl.NumberFormat('en-US').format(numericValue)
}

/**
 * Format percentage
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 0
): string {
  if (value === null || value === undefined) return '0%'

  return `${value.toFixed(decimals)}%`
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * Format date
 */
export function formatDate(
  date: string | Date | null | undefined,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (isNaN(dateObj.getTime())) return ''

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }

  return dateObj.toLocaleDateString('en-US', options || defaultOptions)
}

/**
 * Format date with time
 */
export function formatDateTime(
  date: string | Date | null | undefined,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (isNaN(dateObj.getTime())) return ''

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }

  return dateObj.toLocaleString('en-US', options || defaultOptions)
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000)

  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`

  return formatDate(dateObj)
}

/**
 * Format phone number
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return ''

  // Remove all non-numeric characters
  const cleaned = phone.replace(/\D/g, '')

  // Format as (XXX) XXX-XXXX
  if (cleaned.length === 10) {
    return `(${cleaned.substring(0, 3)}) ${cleaned.substring(3, 6)}-${cleaned.substring(6)}`
  }

  // Format as +X (XXX) XXX-XXXX for international
  if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+1 (${cleaned.substring(1, 4)}) ${cleaned.substring(4, 7)}-${cleaned.substring(7)}`
  }

  return phone
}

/**
 * Format FEIN (Federal Employer Identification Number)
 */
export function formatFEIN(fein: string | null | undefined): string {
  if (!fein) return ''

  const cleaned = fein.replace(/\D/g, '')

  if (cleaned.length === 9) {
    return `${cleaned.substring(0, 2)}-${cleaned.substring(2)}`
  }

  return fein
}

/**
 * Format ZIP code
 */
export function formatZipCode(zip: string | null | undefined): string {
  if (!zip) return ''

  const cleaned = zip.replace(/\D/g, '')

  if (cleaned.length === 9) {
    return `${cleaned.substring(0, 5)}-${cleaned.substring(5)}`
  }

  return cleaned.substring(0, 5)
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text
  return `${text.substring(0, maxLength)}...`
}

/**
 * Capitalize first letter of each word
 */
export function titleCase(text: string): string {
  if (!text) return ''

  return text
    .toLowerCase()
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Convert snake_case to Title Case
 */
export function snakeToTitle(text: string): string {
  if (!text) return ''

  return text
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

/**
 * Format address
 */
export function formatAddress(address: {
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  zip_code?: string
}): string {
  const parts = []

  if (address.address_line1) parts.push(address.address_line1)
  if (address.address_line2) parts.push(address.address_line2)

  const cityStateZip = [address.city, address.state, address.zip_code]
    .filter(Boolean)
    .join(', ')

  if (cityStateZip) parts.push(cityStateZip)

  return parts.join('\n')
}

/**
 * Format address on single line
 */
export function formatAddressOneLine(address: {
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  zip_code?: string
}): string {
  return formatAddress(address).replace(/\n/g, ', ')
}

/**
 * Format confidence score as percentage
 */
export function formatConfidence(score: number | null | undefined): string {
  if (score === null || score === undefined) return '0%'
  return `${Math.round(score * 100)}%`
}

/**
 * Format duration in seconds to human readable
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  return `${hours}h ${minutes}m`
}

/**
 * Format list with commas and "and"
 */
export function formatList(items: string[]): string {
  if (items.length === 0) return ''
  if (items.length === 1) return items[0]
  if (items.length === 2) return `${items[0]} and ${items[1]}`

  const lastItem = items[items.length - 1]
  const otherItems = items.slice(0, -1).join(', ')

  return `${otherItems}, and ${lastItem}`
}