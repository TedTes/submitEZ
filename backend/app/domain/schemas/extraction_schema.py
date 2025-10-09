"""
Pydantic schemas for data extraction results and metadata.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ExtractionStatus(str, Enum):
    """Extraction status enumeration."""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    PARTIAL = 'partial'


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration."""
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    UNKNOWN = 'unknown'


class ExtractedFieldSchema(BaseModel):
    """Schema for a single extracted field with metadata."""
    
    field_name: str = Field(..., description="Name of the extracted field")
    field_value: Any = Field(..., description="Extracted value")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score (0-1)")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.UNKNOWN)
    source_document: Optional[str] = Field(None, description="Source document filename")
    source_page: Optional[int] = Field(None, ge=1, description="Source page number")
    extraction_method: Optional[str] = Field(None, description="Method used for extraction (llm, ocr, parser)")
    needs_review: bool = Field(default=False, description="Flag if field needs manual review")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    model_config = ConfigDict(from_attributes=True)


class ExtractedApplicantSchema(BaseModel):
    """Schema for extracted applicant data with field-level confidence."""
    
    business_name: Optional[ExtractedFieldSchema] = None
    fein: Optional[ExtractedFieldSchema] = None
    dba_name: Optional[ExtractedFieldSchema] = None
    naics_code: Optional[ExtractedFieldSchema] = None
    naics_description: Optional[ExtractedFieldSchema] = None
    business_type: Optional[ExtractedFieldSchema] = None
    years_in_business: Optional[ExtractedFieldSchema] = None
    contact_name: Optional[ExtractedFieldSchema] = None
    contact_title: Optional[ExtractedFieldSchema] = None
    email: Optional[ExtractedFieldSchema] = None
    phone: Optional[ExtractedFieldSchema] = None
    website: Optional[ExtractedFieldSchema] = None
    
    mailing_address: Optional[ExtractedFieldSchema] = None
    physical_address: Optional[ExtractedFieldSchema] = None
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    model_config = ConfigDict(from_attributes=True)


class ExtractedPropertyLocationSchema(BaseModel):
    """Schema for extracted property location with confidence."""
    
    location_number: Optional[ExtractedFieldSchema] = None
    address: Optional[ExtractedFieldSchema] = None
    city: Optional[ExtractedFieldSchema] = None
    state: Optional[ExtractedFieldSchema] = None
    zip_code: Optional[ExtractedFieldSchema] = None
    
    year_built: Optional[ExtractedFieldSchema] = None
    construction_type: Optional[ExtractedFieldSchema] = None
    occupancy_type: Optional[ExtractedFieldSchema] = None
    total_square_feet: Optional[ExtractedFieldSchema] = None
    number_of_stories: Optional[ExtractedFieldSchema] = None
    
    building_value: Optional[ExtractedFieldSchema] = None
    contents_value: Optional[ExtractedFieldSchema] = None
    business_income_value: Optional[ExtractedFieldSchema] = None
    total_insured_value: Optional[ExtractedFieldSchema] = None
    
    protection_class: Optional[ExtractedFieldSchema] = None
    sprinkler_system: Optional[ExtractedFieldSchema] = None
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    model_config = ConfigDict(from_attributes=True)


class ExtractedCoverageSchema(BaseModel):
    """Schema for extracted coverage with confidence."""
    
    policy_type: Optional[ExtractedFieldSchema] = None
    effective_date: Optional[ExtractedFieldSchema] = None
    expiration_date: Optional[ExtractedFieldSchema] = None
    
    building_limit: Optional[ExtractedFieldSchema] = None
    contents_limit: Optional[ExtractedFieldSchema] = None
    business_income_limit: Optional[ExtractedFieldSchema] = None
    
    building_deductible: Optional[ExtractedFieldSchema] = None
    contents_deductible: Optional[ExtractedFieldSchema] = None
    
    general_aggregate_limit: Optional[ExtractedFieldSchema] = None
    each_occurrence_limit: Optional[ExtractedFieldSchema] = None
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    model_config = ConfigDict(from_attributes=True)


class ExtractedLossHistorySchema(BaseModel):
    """Schema for extracted loss history with confidence."""
    
    loss_date: Optional[ExtractedFieldSchema] = None
    claim_number: Optional[ExtractedFieldSchema] = None
    loss_type: Optional[ExtractedFieldSchema] = None
    loss_description: Optional[ExtractedFieldSchema] = None
    loss_amount: Optional[ExtractedFieldSchema] = None
    paid_amount: Optional[ExtractedFieldSchema] = None
    claim_status: Optional[ExtractedFieldSchema] = None
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    model_config = ConfigDict(from_attributes=True)


class DocumentExtractionSchema(BaseModel):
    """Schema for individual document extraction result."""
    
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: Optional[str] = Field(None, description="Detected document type (ACORD, Excel, etc.)")
    mime_type: str = Field(..., description="MIME type")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    
    extraction_status: ExtractionStatus = Field(default=ExtractionStatus.PENDING)
    extraction_started_at: Optional[datetime] = None
    extraction_completed_at: Optional[datetime] = None
    extraction_duration_seconds: Optional[float] = Field(None, ge=0)
    
    extracted_text: Optional[str] = Field(None, description="Raw extracted text")
    page_count: Optional[int] = Field(None, ge=1, description="Number of pages")
    
    fields_extracted: int = Field(default=0, ge=0, description="Number of fields extracted")
    fields_high_confidence: int = Field(default=0, ge=0, description="Fields with high confidence")
    fields_needs_review: int = Field(default=0, ge=0, description="Fields needing review")
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    extraction_errors: List[str] = Field(default_factory=list)
    extraction_warnings: List[str] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class ExtractionResultSchema(BaseModel):
    """Complete extraction result schema."""
    
    submission_id: str = Field(..., description="Submission identifier")
    extraction_id: str = Field(..., description="Unique extraction identifier")
    
    status: ExtractionStatus = Field(default=ExtractionStatus.PENDING)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[float] = Field(None, ge=0)
    
    documents_processed: List[DocumentExtractionSchema] = Field(default_factory=list)
    total_documents: int = Field(default=0, ge=0)
    successful_documents: int = Field(default=0, ge=0)
    failed_documents: int = Field(default=0, ge=0)
    
    extracted_applicant: Optional[ExtractedApplicantSchema] = None
    extracted_locations: List[ExtractedPropertyLocationSchema] = Field(default_factory=list)
    extracted_coverage: Optional[ExtractedCoverageSchema] = None
    extracted_losses: List[ExtractedLossHistorySchema] = Field(default_factory=list)
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.UNKNOWN)
    
    total_fields_extracted: int = Field(default=0, ge=0)
    fields_high_confidence: int = Field(default=0, ge=0)
    fields_medium_confidence: int = Field(default=0, ge=0)
    fields_low_confidence: int = Field(default=0, ge=0)
    fields_needs_review: int = Field(default=0, ge=0)
    
    llm_model_used: Optional[str] = Field(None, description="LLM model used for extraction")
    llm_tokens_used: Optional[int] = Field(None, ge=0, description="Total tokens consumed")
    llm_cost: Optional[float] = Field(None, ge=0, description="Estimated cost in USD")
    
    extraction_errors: List[str] = Field(default_factory=list)
    extraction_warnings: List[str] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class ExtractionRequestSchema(BaseModel):
    """Schema for extraction request."""
    
    submission_id: str = Field(..., description="Submission to extract")
    force_reextraction: bool = Field(default=False, description="Force re-extraction even if already extracted")
    llm_model: Optional[str] = Field(None, description="Override default LLM model")
    extraction_strategy: Optional[str] = Field(None, description="Extraction strategy (fast, accurate, comprehensive)")
    include_low_confidence: bool = Field(default=True, description="Include low confidence fields")
    
    model_config = ConfigDict(from_attributes=True)


class ExtractionSummarySchema(BaseModel):
    """Lightweight extraction summary schema."""
    
    extraction_id: str
    submission_id: str
    status: ExtractionStatus
    overall_confidence: float = Field(ge=0.0, le=1.0)
    total_documents: int = Field(ge=0)
    successful_documents: int = Field(ge=0)
    failed_documents: int = Field(ge=0)
    total_fields_extracted: int = Field(ge=0)
    fields_needs_review: int = Field(ge=0)
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)