"""
Pydantic schemas for validation results and errors.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'


class ValidationCategory(str, Enum):
    """Validation error categories."""
    REQUIRED_FIELD = 'required_field'
    INVALID_FORMAT = 'invalid_format'
    INVALID_VALUE = 'invalid_value'
    INCONSISTENT_DATA = 'inconsistent_data'
    BUSINESS_RULE = 'business_rule'
    COMPLETENESS = 'completeness'
    CROSS_FIELD = 'cross_field'
    DATA_QUALITY = 'data_quality'


class ValidationIssueSchema(BaseModel):
    """Schema for a single validation issue."""
    
    field_path: str = Field(..., description="Path to field (e.g., 'applicant.business_name')")
    severity: ValidationSeverity = Field(..., description="Severity level")
    category: ValidationCategory = Field(..., description="Issue category")
    message: str = Field(..., description="Human-readable error message")
    
    current_value: Optional[Any] = Field(None, description="Current field value")
    expected_value: Optional[Any] = Field(None, description="Expected value or format")
    suggested_fix: Optional[str] = Field(None, description="Suggested correction")
    
    rule_id: Optional[str] = Field(None, description="Validation rule identifier")
    rule_description: Optional[str] = Field(None, description="Rule description")
    
    blocking: bool = Field(default=False, description="Whether this blocks submission")
    auto_fixable: bool = Field(default=False, description="Whether can be auto-fixed")
    
    related_fields: List[str] = Field(default_factory=list, description="Related field paths")
    
    documentation_url: Optional[str] = Field(None, description="Link to documentation")
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class FieldValidationSchema(BaseModel):
    """Schema for field-specific validation."""
    
    field_name: str = Field(..., description="Field name")
    field_path: str = Field(..., description="Full field path")
    is_valid: bool = Field(..., description="Whether field is valid")
    is_required: bool = Field(default=False, description="Whether field is required")
    is_present: bool = Field(default=False, description="Whether field has a value")
    
    errors: List[ValidationIssueSchema] = Field(default_factory=list)
    warnings: List[ValidationIssueSchema] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class EntityValidationSchema(BaseModel):
    """Schema for entity-level validation (applicant, location, etc.)."""
    
    entity_type: str = Field(..., description="Entity type (applicant, location, coverage, loss)")
    entity_id: Optional[str] = Field(None, description="Entity identifier")
    
    is_valid: bool = Field(..., description="Whether entity is valid")
    is_complete: bool = Field(..., description="Whether entity is complete")
    completeness_percentage: int = Field(default=0, ge=0, le=100)
    
    required_fields: List[str] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    invalid_fields: List[str] = Field(default_factory=list)
    
    field_validations: List[FieldValidationSchema] = Field(default_factory=list)
    
    errors: List[ValidationIssueSchema] = Field(default_factory=list)
    warnings: List[ValidationIssueSchema] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class ValidationResultSchema(BaseModel):
    """Complete validation result schema."""
    
    submission_id: str = Field(..., description="Submission identifier")
    validation_id: str = Field(..., description="Validation run identifier")
    
    is_valid: bool = Field(..., description="Overall validation status")
    is_complete: bool = Field(..., description="Whether submission is complete")
    completeness_percentage: int = Field(default=0, ge=0, le=100)
    
    can_proceed_to_generation: bool = Field(default=False, description="Ready for PDF generation")
    can_submit_to_carrier: bool = Field(default=False, description="Ready to submit")
    
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validation_duration_seconds: Optional[float] = Field(None, ge=0)
    
    # Entity Validations
    applicant_validation: Optional[EntityValidationSchema] = None
    location_validations: List[EntityValidationSchema] = Field(default_factory=list)
    coverage_validation: Optional[EntityValidationSchema] = None
    loss_validations: List[EntityValidationSchema] = Field(default_factory=list)
    
    # Aggregated Issues
    total_errors: int = Field(default=0, ge=0)
    total_warnings: int = Field(default=0, ge=0)
    total_info: int = Field(default=0, ge=0)
    blocking_errors: int = Field(default=0, ge=0)
    
    errors: List[ValidationIssueSchema] = Field(default_factory=list)
    warnings: List[ValidationIssueSchema] = Field(default_factory=list)
    info: List[ValidationIssueSchema] = Field(default_factory=list)
    
    # Business Rule Checks
    rules_checked: int = Field(default=0, ge=0)
    rules_passed: int = Field(default=0, ge=0)
    rules_failed: int = Field(default=0, ge=0)
    
    business_rule_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Data Quality Metrics
    data_quality_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall data quality score")
    field_completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class ValidationRequestSchema(BaseModel):
    """Schema for validation request."""
    
    submission_id: str = Field(..., description="Submission to validate")
    force_revalidation: bool = Field(default=False, description="Force re-validation")
    
    validation_level: str = Field(
        default='standard',
        description="Validation level (quick, standard, comprehensive)"
    )
    
    include_warnings: bool = Field(default=True, description="Include warnings in results")
    include_info: bool = Field(default=False, description="Include info messages")
    
    strict_mode: bool = Field(default=False, description="Strict validation mode")
    
    skip_business_rules: bool = Field(default=False, description="Skip business rule validation")
    skip_cross_field: bool = Field(default=False, description="Skip cross-field validation")
    
    custom_rules: List[str] = Field(default_factory=list, description="Additional custom rule IDs to apply")
    
    model_config = ConfigDict(from_attributes=True)


class ValidationSummarySchema(BaseModel):
    """Lightweight validation summary schema."""
    
    validation_id: str
    submission_id: str
    is_valid: bool
    is_complete: bool
    completeness_percentage: int = Field(ge=0, le=100)
    total_errors: int = Field(ge=0)
    total_warnings: int = Field(ge=0)
    blocking_errors: int = Field(ge=0)
    can_proceed_to_generation: bool
    validated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BusinessRuleSchema(BaseModel):
    """Schema for business rule definition."""
    
    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Rule name")
    rule_description: str = Field(..., description="Rule description")
    
    category: ValidationCategory = Field(..., description="Rule category")
    severity: ValidationSeverity = Field(..., description="Default severity")
    
    applies_to: List[str] = Field(..., description="Entities this rule applies to")
    
    blocking: bool = Field(default=False, description="Whether rule blocks submission")
    enabled: bool = Field(default=True, description="Whether rule is active")
    
    documentation_url: Optional[str] = Field(None, description="Rule documentation")
    
    model_config = ConfigDict(from_attributes=True)


class AutoFixSuggestionSchema(BaseModel):
    """Schema for automatic fix suggestions."""
    
    field_path: str = Field(..., description="Field to fix")
    issue_id: str = Field(..., description="Validation issue ID")
    
    current_value: Any = Field(..., description="Current value")
    suggested_value: Any = Field(..., description="Suggested corrected value")
    
    fix_type: str = Field(..., description="Type of fix (format, correct, complete)")
    fix_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in fix")
    
    fix_explanation: str = Field(..., description="Explanation of fix")
    
    apply_automatically: bool = Field(default=False, description="Safe to apply automatically")
    
    model_config = ConfigDict(from_attributes=True)


class ValidationComparisonSchema(BaseModel):
    """Schema for comparing validation results over time."""
    
    submission_id: str
    
    previous_validation_id: str
    current_validation_id: str
    
    previous_validated_at: datetime
    current_validated_at: datetime
    
    errors_added: int = Field(ge=0)
    errors_resolved: int = Field(ge=0)
    errors_unchanged: int = Field(ge=0)
    
    warnings_added: int = Field(ge=0)
    warnings_resolved: int = Field(ge=0)
    
    quality_score_change: float = Field(description="Change in quality score")
    completeness_change: int = Field(description="Change in completeness %")
    
    new_issues: List[ValidationIssueSchema] = Field(default_factory=list)
    resolved_issues: List[ValidationIssueSchema] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)