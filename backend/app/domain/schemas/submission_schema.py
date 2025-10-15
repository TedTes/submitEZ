"""
Pydantic schemas for Submission validation and serialization.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class ApplicantSchema(BaseModel):
    """Applicant validation schema."""
    
    business_name: str = Field(..., min_length=1, max_length=255)
    fein: Optional[str] = Field(None, pattern=r'^\d{2}-?\d{7}$')
    dba_name: Optional[str] = Field(None, max_length=255)
    naics_code: Optional[str] = Field(None, pattern=r'^\d{2,6}$')
    naics_description: Optional[str] = Field(None, max_length=500)
    business_type: Optional[str] = Field(None, max_length=100)
    years_in_business: Optional[int] = Field(None, ge=0, le=200)
    description: Optional[str] = Field(None, max_length=2000)
    
    contact_name: Optional[str] = Field(None, max_length=200)
    contact_title: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    fax: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    
    mailing_address_line1: Optional[str] = Field(None, max_length=255)
    mailing_address_line2: Optional[str] = Field(None, max_length=255)
    mailing_city: Optional[str] = Field(None, max_length=100)
    mailing_state: Optional[str] = Field(None, min_length=2, max_length=2)
    mailing_zip: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')
    mailing_country: str = Field(default='USA', max_length=100)
    
    physical_address_line1: Optional[str] = Field(None, max_length=255)
    physical_address_line2: Optional[str] = Field(None, max_length=255)
    physical_city: Optional[str] = Field(None, max_length=100)
    physical_state: Optional[str] = Field(None, min_length=2, max_length=2)
    physical_zip: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')
    physical_country: str = Field(default='USA', max_length=100)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class PropertyLocationSchema(BaseModel):
    """Property location validation schema."""
    
    location_number: Optional[str] = Field(None, max_length=50)
    
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default='USA', max_length=100)
    county: Optional[str] = Field(None, max_length=100)
    
    building_description: Optional[str] = Field(None, max_length=500)
    year_built: Optional[int] = Field(None, ge=1700, le=2100)
    construction_type: Optional[str] = Field(None, max_length=100)
    number_of_stories: Optional[int] = Field(None, ge=1, le=200)
    total_square_feet: Optional[int] = Field(None, ge=0)
    occupancy_type: Optional[str] = Field(None, max_length=100)
    
    protection_class: Optional[str] = Field(None, max_length=10)
    distance_to_fire_station: Optional[float] = Field(None, ge=0)
    distance_to_hydrant: Optional[int] = Field(None, ge=0)
    sprinkler_system: Optional[bool] = None
    alarm_system: Optional[bool] = None
    security_system: Optional[bool] = None
    fire_alarm: Optional[bool] = None
    burglar_alarm: Optional[bool] = None
    
    building_value: Optional[Decimal] = Field(None, ge=0)
    contents_value: Optional[Decimal] = Field(None, ge=0)
    business_income_value: Optional[Decimal] = Field(None, ge=0)
    total_insured_value: Optional[Decimal] = Field(None, ge=0)
    
    basement: Optional[bool] = None
    basement_finished: Optional[bool] = None
    roof_type: Optional[str] = Field(None, max_length=100)
    roof_year: Optional[int] = Field(None, ge=1900, le=2100)
    heating_type: Optional[str] = Field(None, max_length=100)
    cooling_type: Optional[str] = Field(None, max_length=100)
    electrical_year: Optional[int] = Field(None, ge=1900, le=2100)
    plumbing_year: Optional[int] = Field(None, ge=1900, le=2100)
    updates_wiring: Optional[bool] = None
    updates_plumbing: Optional[bool] = None
    updates_heating: Optional[bool] = None
    updates_roof: Optional[bool] = None
    
    prior_losses: Optional[bool] = None
    number_of_employees: Optional[int] = Field(None, ge=0)
    hours_of_operation: Optional[str] = Field(None, max_length=200)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class CoverageSchema(BaseModel):
    """Coverage validation schema."""
    
    policy_type: Optional[str] = Field(None, max_length=100)
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    policy_term_months: Optional[int] = Field(default=12, ge=1, le=60)
    
    building_limit: Optional[Decimal] = Field(None, ge=0)
    contents_limit: Optional[Decimal] = Field(None, ge=0)
    business_income_limit: Optional[Decimal] = Field(None, ge=0)
    extra_expense_limit: Optional[Decimal] = Field(None, ge=0)
    equipment_breakdown_limit: Optional[Decimal] = Field(None, ge=0)
    
    building_deductible: Optional[Decimal] = Field(None, ge=0)
    contents_deductible: Optional[Decimal] = Field(None, ge=0)
    business_income_deductible: Optional[str] = Field(None, max_length=50)
    wind_hail_deductible: Optional[str] = Field(None, max_length=50)
    flood_deductible: Optional[Decimal] = Field(None, ge=0)
    earthquake_deductible: Optional[str] = Field(None, max_length=50)
    all_other_perils_deductible: Optional[Decimal] = Field(None, ge=0)
    
    general_aggregate_limit: Optional[Decimal] = Field(None, ge=0)
    products_aggregate_limit: Optional[Decimal] = Field(None, ge=0)
    each_occurrence_limit: Optional[Decimal] = Field(None, ge=0)
    personal_injury_limit: Optional[Decimal] = Field(None, ge=0)
    medical_payments_limit: Optional[Decimal] = Field(None, ge=0)
    damage_to_premises_limit: Optional[Decimal] = Field(None, ge=0)
    
    property_in_transit: Optional[Decimal] = Field(None, ge=0)
    accounts_receivable: Optional[Decimal] = Field(None, ge=0)
    valuable_papers: Optional[Decimal] = Field(None, ge=0)
    fine_arts: Optional[Decimal] = Field(None, ge=0)
    signs: Optional[Decimal] = Field(None, ge=0)
    outdoor_property: Optional[Decimal] = Field(None, ge=0)
    debris_removal: Optional[Decimal] = Field(None, ge=0)
    pollutant_cleanup: Optional[Decimal] = Field(None, ge=0)
    spoilage: Optional[Decimal] = Field(None, ge=0)
    
    replacement_cost: Optional[bool] = None
    actual_cash_value: Optional[bool] = None
    agreed_value: Optional[bool] = None
    blanket_coverage: Optional[bool] = None
    inflation_guard: Optional[bool] = None
    
    coinsurance_percentage: Optional[int] = Field(None, ge=0, le=100)
    coinsurance_waived: Optional[bool] = None
    
    ordinance_or_law_coverage: Optional[Decimal] = Field(None, ge=0)
    utility_services_time_element: Optional[Decimal] = Field(None, ge=0)
    electronic_data: Optional[Decimal] = Field(None, ge=0)
    employee_dishonesty: Optional[Decimal] = Field(None, ge=0)
    forgery: Optional[Decimal] = Field(None, ge=0)
    
    flood_coverage: Optional[bool] = None
    earthquake_coverage: Optional[bool] = None
    terrorism_coverage: Optional[bool] = None
    cyber_coverage: Optional[bool] = None
    
    estimated_annual_premium: Optional[Decimal] = Field(None, ge=0)
    premium_basis: Optional[str] = Field(None, max_length=100)
    premium_basis_amount: Optional[Decimal] = Field(None, ge=0)
    
    special_conditions: Optional[str] = Field(None, max_length=2000)
    exclusions: List[str] = Field(default_factory=list)
    endorsements: List[str] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class LossHistorySchema(BaseModel):
    """Loss history validation schema."""
    
    loss_date: date
    claim_number: Optional[str] = Field(None, max_length=100)
    loss_type: Optional[str] = Field(None, max_length=100)
    loss_description: Optional[str] = Field(None, max_length=2000)
    cause_of_loss: Optional[str] = Field(None, max_length=200)
    
    loss_amount: Optional[Decimal] = Field(None, ge=0)
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    reserved_amount: Optional[Decimal] = Field(None, ge=0)
    deductible: Optional[Decimal] = Field(None, ge=0)
    recoveries: Optional[Decimal] = Field(None, ge=0)
    
    claim_status: str = Field(default='Open', max_length=50)
    date_reported: Optional[date] = None
    date_closed: Optional[date] = None
    days_to_close: Optional[int] = Field(None, ge=0)
    
    location_affected: Optional[str] = Field(None, max_length=200)
    location_address: Optional[str] = Field(None, max_length=500)
    coverage_type: Optional[str] = Field(None, max_length=100)
    coverage_line: Optional[str] = Field(None, max_length=100)
    policy_number: Optional[str] = Field(None, max_length=100)
    
    claimant_name: Optional[str] = Field(None, max_length=200)
    claimant_type: Optional[str] = Field(None, max_length=100)
    injury_type: Optional[str] = Field(None, max_length=100)
    injury_description: Optional[str] = Field(None, max_length=1000)
    medical_only: Optional[bool] = None
    lost_time: Optional[bool] = None
    
    at_fault: Optional[bool] = None
    subrogation: Optional[bool] = None
    litigation: Optional[bool] = None
    fraud_suspected: Optional[bool] = None
    catastrophe: Optional[bool] = None
    catastrophe_code: Optional[str] = Field(None, max_length=50)
    
    adjuster_name: Optional[str] = Field(None, max_length=200)
    adjuster_company: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionCreateSchema(BaseModel):
    """Schema for creating a new submission."""
    user_id: str
    client_name: Optional[str] = Field(None, max_length=200, description="Client/project name")
    broker_name: Optional[str] = Field(None, max_length=200)
    broker_email: Optional[str] = Field(None, max_length=255)
    carrier_name: Optional[str] = Field(None, max_length=200)
    effective_date_requested: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=5000)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionUpdateSchema(BaseModel):
    """Schema for updating a submission."""
    user_id: str
    client_name: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=50)
    applicant: Optional[ApplicantSchema] = None
    locations: Optional[List[PropertyLocationSchema]] = None
    coverage: Optional[CoverageSchema] = None
    loss_history: Optional[List[LossHistorySchema]] = None
    broker_name: Optional[str] = Field(None, max_length=200)
    broker_email: Optional[str] = Field(None, max_length=255)
    carrier_name: Optional[str] = Field(None, max_length=200)
    effective_date_requested: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=5000)
    internal_notes: Optional[str] = Field(None, max_length=5000)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionResponseSchema(BaseModel):
    """Schema for submission API responses."""
    
    id: str
    user_id: str
    status: str
    client_name: Optional[str] = None
    applicant: Optional[ApplicantSchema] = None
    locations: List[PropertyLocationSchema] = Field(default_factory=list)
    coverage: Optional[CoverageSchema] = None
    loss_history: List[LossHistorySchema] = Field(default_factory=list)
    
    uploaded_files: List[Dict[str, Any]] = Field(default_factory=list)
    generated_files: List[Dict[str, Any]] = Field(default_factory=list)
    
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    extracted_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list)
    validation_warnings: List[Dict[str, Any]] = Field(default_factory=list)
    is_valid: bool = False
    
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
    extraction_confidence: Optional[float] = None
    
    broker_name: Optional[str] = None
    broker_email: Optional[str] = None
    carrier_name: Optional[str] = None
    effective_date_requested: Optional[str] = None
    
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionSummarySchema(BaseModel):
    """Schema for submission list/summary responses."""
    
    id: str
    user_id: str
    client_name: Optional[str] = None
    status: str
    applicant_name: Optional[str] = None
    total_locations: int = 0
    total_losses: int = 0
    total_tiv: float = 0.0
    completeness: int = 0
    is_valid: bool = False
    validation_errors_count: int = 0
    validation_warnings_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)