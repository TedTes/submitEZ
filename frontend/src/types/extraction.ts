/**
 * Frontend extraction types
 * Mirrors backend extraction schemas for type safety
 */

export type ExtractionStatus = 
  | 'pending' 
  | 'in_progress' 
  | 'completed' 
  | 'failed' 
  | 'partial'

export type ConfidenceLevel = 
  | 'high' 
  | 'medium' 
  | 'low' 
  | 'unknown'

export interface ExtractedField<T = any> {
  field_name: string
  field_value: T
  confidence_score: number // 0.0 - 1.0
  confidence_level: ConfidenceLevel
  source_document?: string
  source_page?: number
  extraction_method?: 'llm' | 'ocr' | 'parser'
  needs_review: boolean
  notes?: string
}

export interface ExtractedApplicant {
  business_name?: ExtractedField<string>
  fein?: ExtractedField<string>
  dba_name?: ExtractedField<string>
  naics_code?: ExtractedField<string>
  naics_description?: ExtractedField<string>
  business_type?: ExtractedField<string>
  years_in_business?: ExtractedField<number>
  contact_name?: ExtractedField<string>
  contact_title?: ExtractedField<string>
  email?: ExtractedField<string>
  phone?: ExtractedField<string>
  website?: ExtractedField<string>
  mailing_address?: ExtractedField<string>
  physical_address?: ExtractedField<string>
  overall_confidence: number
}

export interface ExtractedPropertyLocation {
  location_number?: ExtractedField<number>
  location_name?: ExtractedField<string>
  address_line1?: ExtractedField<string>
  address_line2?: ExtractedField<string>
  city?: ExtractedField<string>
  state?: ExtractedField<string>
  zip_code?: ExtractedField<string>
  county?: ExtractedField<string>
  building_number?: ExtractedField<string>
  occupancy_type?: ExtractedField<string>
  construction_type?: ExtractedField<string>
  year_built?: ExtractedField<number>
  number_of_stories?: ExtractedField<number>
  total_area_sq_ft?: ExtractedField<number>
  building_value?: ExtractedField<number>
  contents_value?: ExtractedField<number>
  business_income_value?: ExtractedField<number>
  total_insured_value?: ExtractedField<number>
  protection_class?: ExtractedField<string>
  sprinkler_system?: ExtractedField<boolean>
  alarm_system?: ExtractedField<boolean>
  overall_confidence: number
}

export interface ExtractedCoverage {
  policy_type?: ExtractedField<string>
  coverage_type?: ExtractedField<string>
  effective_date?: ExtractedField<string>
  expiration_date?: ExtractedField<string>
  building_limit?: ExtractedField<number>
  contents_limit?: ExtractedField<number>
  business_income_limit?: ExtractedField<number>
  extra_expense_limit?: ExtractedField<number>
  general_aggregate?: ExtractedField<number>
  per_occurrence?: ExtractedField<number>
  deductible?: ExtractedField<number>
  coinsurance_percentage?: ExtractedField<number>
  valuation_type?: ExtractedField<string>
  overall_confidence: number
}

export interface ExtractedLossHistory {
  loss_date?: ExtractedField<string>
  claim_number?: ExtractedField<string>
  loss_type?: ExtractedField<string>
  loss_description?: ExtractedField<string>
  cause_of_loss?: ExtractedField<string>
  loss_amount?: ExtractedField<number>
  paid_amount?: ExtractedField<number>
  reserved_amount?: ExtractedField<number>
  deductible?: ExtractedField<number>
  claim_status?: ExtractedField<string>
  date_reported?: ExtractedField<string>
  date_closed?: ExtractedField<string>
  location_affected?: ExtractedField<string>
  coverage_type?: ExtractedField<string>
  claimant_name?: ExtractedField<string>
  injury_type?: ExtractedField<string>
  at_fault?: ExtractedField<boolean>
  subrogation?: ExtractedField<boolean>
  litigation?: ExtractedField<boolean>
  overall_confidence: number
}

export interface DocumentExtraction {
  document_id: string
  filename: string
  file_type: string
  status: ExtractionStatus
  confidence: number
  processing_duration_seconds: number
  extraction_method: 'llm' | 'ocr' | 'parser' | 'hybrid'
  error_message?: string
  metadata: Record<string, any>
}

export interface ExtractionResult {
  submission_id: string
  extraction_id: string
  status: ExtractionStatus
  started_at: string
  completed_at?: string
  total_duration_seconds?: number
  
  // Documents processed
  documents_processed: DocumentExtraction[]
  total_documents: number
  successful_documents: number
  failed_documents: number
  
  // Extracted data
  extracted_applicant?: ExtractedApplicant
  extracted_locations: ExtractedPropertyLocation[]
  extracted_coverage?: ExtractedCoverage
  extracted_losses: ExtractedLossHistory[]
  
  // Confidence metrics
  overall_confidence: number
  overall_confidence_level: ConfidenceLevel
  
  // Field statistics
  total_fields_extracted: number
  fields_high_confidence: number
  fields_medium_confidence: number
  fields_low_confidence: number
  fields_needs_review: number
  
  // LLM metadata
  llm_model_used?: string
  llm_tokens_used?: number
  llm_cost?: number
  
  // Errors and warnings
  extraction_errors: string[]
  extraction_warnings: string[]
  
  metadata: Record<string, any>
}

export interface ExtractionRequest {
  submission_id: string
  force_reextraction?: boolean
  llm_model?: string
  extraction_strategy?: 'fast' | 'accurate' | 'comprehensive'
  include_low_confidence?: boolean
}

export interface ExtractionSummary {
  extraction_id: string
  submission_id: string
  status: ExtractionStatus
  overall_confidence: number
  total_documents: number
  successful_documents: number
  failed_documents: number
  total_fields_extracted: number
  fields_needs_review: number
  started_at: string
  completed_at?: string
}

// Helper type for working with extracted fields
export type ExtractedFieldValue<T> = T | undefined

// Utility function types for extraction operations
export interface ExtractionHelpers {
  getFieldValue: <T = any>(field?: ExtractedField<T>) => T | undefined
  getConfidence: (field?: ExtractedField) => number
  needsReview: (field?: ExtractedField) => boolean
  isHighConfidence: (field?: ExtractedField) => boolean
  formatFieldForDisplay: (field?: ExtractedField) => string
}

// Confidence thresholds
export const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.8,
  MEDIUM: 0.5,
  LOW: 0.3,
} as const

// Helper to determine confidence level from score
export const getConfidenceLevelFromScore = (score: number): ConfidenceLevel => {
  if (score >= CONFIDENCE_THRESHOLDS.HIGH) return 'high'
  if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return 'medium'
  if (score >= CONFIDENCE_THRESHOLDS.LOW) return 'low'
  return 'unknown'
}

// Helper to extract field value
export const getFieldValue = <T = any>(field?: ExtractedField<T>): T | undefined => {
  return field?.field_value
}

// Helper to check if field needs review
export const fieldNeedsReview = (field?: ExtractedField): boolean => {
  return field?.needs_review || false
}

// Helper to check if field has high confidence
export const isHighConfidence = (field?: ExtractedField): boolean => {
  return (field?.confidence_score ?? 0) >= CONFIDENCE_THRESHOLDS.HIGH
}