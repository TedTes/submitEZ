/**
 * Submission TypeScript types matching backend models
 */

export interface Applicant {
    business_name: string
    fein?: string
    dba_name?: string
    naics_code?: string
    naics_description?: string
    business_type?: string
    years_in_business?: number
    description?: string
    contact_name?: string
    contact_title?: string
    email?: string
    phone?: string
    fax?: string
    website?: string
    mailing_address_line1?: string
    mailing_address_line2?: string
    mailing_city?: string
    mailing_state?: string
    mailing_zip?: string
    mailing_country?: string
    physical_address_line1?: string
    physical_address_line2?: string
    physical_city?: string
    physical_state?: string
    physical_zip?: string
    physical_country?: string
    metadata?: Record<string, any>
  }
  
  export interface PropertyLocation {
    location_number?: string
    address_line1: string
    address_line2?: string
    city: string
    state: string
    zip_code: string
    country?: string
    county?: string
    building_description?: string
    year_built?: number
    construction_type?: string
    number_of_stories?: number
    total_square_feet?: number
    occupancy_type?: string
    protection_class?: string
    distance_to_fire_station?: number
    distance_to_hydrant?: number
    sprinkler_system?: boolean
    alarm_system?: boolean
    security_system?: boolean
    fire_alarm?: boolean
    burglar_alarm?: boolean
    building_value?: number
    contents_value?: number
    business_income_value?: number
    total_insured_value?: number
    basement?: boolean
    basement_finished?: boolean
    roof_type?: string
    roof_year?: number
    heating_type?: string
    cooling_type?: string
    electrical_year?: number
    plumbing_year?: number
    updates_wiring?: boolean
    updates_plumbing?: boolean
    updates_heating?: boolean
    updates_roof?: boolean
    prior_losses?: boolean
    number_of_employees?: number
    hours_of_operation?: string
    metadata?: Record<string, any>
  }
  
  export interface Coverage {
    policy_type?: string
    effective_date?: string
    expiration_date?: string
    policy_term_months?: number
    building_limit?: number
    contents_limit?: number
    business_income_limit?: number
    extra_expense_limit?: number
    equipment_breakdown_limit?: number
    building_deductible?: number
    contents_deductible?: number
    business_income_deductible?: string
    wind_hail_deductible?: string
    flood_deductible?: number
    earthquake_deductible?: string
    all_other_perils_deductible?: number
    general_aggregate_limit?: number
    products_aggregate_limit?: number
    each_occurrence_limit?: number
    personal_injury_limit?: number
    medical_payments_limit?: number
    damage_to_premises_limit?: number
    property_in_transit?: number
    accounts_receivable?: number
    valuable_papers?: number
    fine_arts?: number
    signs?: number
    outdoor_property?: number
    debris_removal?: number
    pollutant_cleanup?: number
    spoilage?: number
    replacement_cost?: boolean
    actual_cash_value?: boolean
    agreed_value?: boolean
    blanket_coverage?: boolean
    inflation_guard?: boolean
    coinsurance_percentage?: number
    coinsurance_waived?: boolean
    ordinance_or_law_coverage?: number
    utility_services_time_element?: number
    electronic_data?: number
    employee_dishonesty?: number
    forgery?: number
    flood_coverage?: boolean
    earthquake_coverage?: boolean
    terrorism_coverage?: boolean
    cyber_coverage?: boolean
    estimated_annual_premium?: number
    premium_basis?: string
    premium_basis_amount?: number
    special_conditions?: string
    exclusions?: string[]
    endorsements?: string[]
    metadata?: Record<string, any>
  }
  
  export interface LossHistory {
    loss_date: string
    claim_number?: string
    loss_type?: string
    loss_description?: string
    cause_of_loss?: string
    loss_amount?: number
    paid_amount?: number
    reserved_amount?: number
    deductible?: number
    recoveries?: number
    claim_status: string
    date_reported?: string
    date_closed?: string
    days_to_close?: number
    location_affected?: string
    location_address?: string
    coverage_type?: string
    coverage_line?: string
    policy_number?: string
    claimant_name?: string
    claimant_type?: string
    injury_type?: string
    injury_description?: string
    medical_only?: boolean
    lost_time?: boolean
    at_fault?: boolean
    subrogation?: boolean
    litigation?: boolean
    fraud_suspected?: boolean
    catastrophe?: boolean
    catastrophe_code?: string
    adjuster_name?: string
    adjuster_company?: string
    notes?: string
    internal_notes?: string
    metadata?: Record<string, any>
  }
  
  export interface UploadedFile {
    filename: string
    original_filename: string
    storage_path: string
    url: string
    size_bytes: number
    content_type: string
    uploaded_at: string
  }
  
  export interface GeneratedFile {
    form_type: string
    filename: string
    local_path?: string
    storage_path: string
    url: string
    size_bytes: number
    generated_at: string
  }
  
  export interface ValidationError {
    field_path: string
    severity: 'error' | 'warning' | 'info'
    category: string
    message: string
    current_value?: any
    expected_value?: any
    suggested_fix?: string
    blocking?: boolean
  }
  
  export type SubmissionStatus =
    | 'draft'
    | 'uploaded'
    | 'extracting'
    | 'extracted'
    | 'validating'
    | 'validated'
    | 'generating'
    | 'completed'
    | 'error'
  
  export interface Submission {
    id: string
    client_name?: string
    status: SubmissionStatus
    applicant?: Applicant
    locations: PropertyLocation[]
    coverage?: Coverage
    loss_history: LossHistory[]
    uploaded_files: UploadedFile[]
    generated_files: GeneratedFile[]
    created_at: string
    updated_at: string
    submitted_at?: string
    extracted_at?: string
    validated_at?: string
    generated_at?: string
    validation_errors: ValidationError[]
    validation_warnings: ValidationError[]
    is_valid: boolean
    extraction_metadata: Record<string, any>
    extraction_confidence?: number
    broker_name?: string
    broker_email?: string
    carrier_name?: string
    effective_date_requested?: string
    notes?: string
    internal_notes?: string
    metadata: Record<string, any>
  }
  
  export interface SubmissionSummary {
    id: string
    client_name?: string
    status: SubmissionStatus
    applicant_name?: string
    total_locations: number
    total_losses: number
    total_tiv: number
    completeness: number
    is_valid: boolean
    validation_errors_count: number
    validation_warnings_count: number
    created_at: string
    updated_at: string
  }
  
  export interface SubmissionCreateRequest {
    client_name?: string
    broker_name?: string
    broker_email?: string
    carrier_name?: string
    notes?: string
  }
  
  export interface SubmissionUpdateRequest {
    client_name?: string
    applicant?: Partial<Applicant>
    locations?: PropertyLocation[]
    coverage?: Partial<Coverage>
    loss_history?: LossHistory[]
    broker_name?: string
    broker_email?: string
    carrier_name?: string
    notes?: string
  }