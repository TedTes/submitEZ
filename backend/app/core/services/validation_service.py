"""
Validation service for business rules and data validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from app.domain.models import Submission, Applicant, PropertyLocation, Coverage, LossHistory
from app.domain.schemas.validation_schema import (
    ValidationSeverity,
    ValidationCategory,
    ValidationIssueSchema,
    FieldValidationSchema,
    EntityValidationSchema,
    ValidationResultSchema
)
from app.utils.validation_utils import (
    is_valid_email,
    is_valid_phone,
    is_valid_fein,
    is_valid_zip,
    is_valid_state,
    is_valid_naics,
    is_valid_year,
    is_valid_currency,
    is_not_empty
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationService:
    """
    Service for validating submission data against business rules.
    
    Performs:
    - Field-level validation
    - Entity-level validation
    - Cross-field validation
    - Business rule validation
    - Completeness checking
    """
    
    def __init__(self):
        """Initialize validation service."""
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration."""
        return {
            'required_fields': {
                'applicant': ['business_name'],
                'location': ['address_line1', 'city', 'state', 'zip_code'],
                'coverage': ['effective_date', 'expiration_date']
            },
            'minimum_values': {
                'building_value': 0,
                'contents_value': 0,
                'year_built': 1800
            },
            'maximum_values': {
                'year_built': datetime.now().year + 1
            }
        }
    
    def validate_submission(
        self,
        submission: Submission,
        strict_mode: bool = False
    ) -> ValidationResultSchema:
        """
        Validate complete submission.
        
        Args:
            submission: Submission entity to validate
            strict_mode: Enable strict validation rules
            
        Returns:
            ValidationResultSchema with results
        """
        validation_id = str(uuid4())
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting validation for submission {submission.id}")
            
            errors: List[ValidationIssueSchema] = []
            warnings: List[ValidationIssueSchema] = []
            info: List[ValidationIssueSchema] = []
            
            # Validate applicant
            applicant_validation = None
            if submission.applicant:
                applicant_validation = self.validate_applicant(submission.applicant, strict_mode)
                errors.extend(applicant_validation.errors)
                warnings.extend(applicant_validation.warnings)
            else:
                errors.append(ValidationIssueSchema(
                    field_path='applicant',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.REQUIRED_FIELD,
                    message='Applicant information is required',
                    blocking=True
                ))
            
            # Validate locations
            location_validations = []
            if submission.locations:
                for i, location in enumerate(submission.locations):
                    loc_validation = self.validate_location(location, strict_mode, i)
                    location_validations.append(loc_validation)
                    errors.extend(loc_validation.errors)
                    warnings.extend(loc_validation.warnings)
            else:
                errors.append(ValidationIssueSchema(
                    field_path='locations',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.REQUIRED_FIELD,
                    message='At least one property location is required',
                    blocking=True
                ))
            
            # Validate coverage
            coverage_validation = None
            if submission.coverage:
                coverage_validation = self.validate_coverage(submission.coverage, strict_mode)
                errors.extend(coverage_validation.errors)
                warnings.extend(coverage_validation.warnings)
            else:
                warnings.append(ValidationIssueSchema(
                    field_path='coverage',
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.REQUIRED_FIELD,
                    message='Coverage information is recommended'
                ))
            
            # Validate loss history
            loss_validations = []
            for i, loss in enumerate(submission.loss_history):
                loss_validation = self.validate_loss(loss, strict_mode, i)
                loss_validations.append(loss_validation)
                errors.extend(loss_validation.errors)
                warnings.extend(loss_validation.warnings)
            
            # Cross-field validation
            cross_field_issues = self._validate_cross_fields(submission)
            errors.extend([i for i in cross_field_issues if i.severity == ValidationSeverity.ERROR])
            warnings.extend([i for i in cross_field_issues if i.severity == ValidationSeverity.WARNING])
            info.extend([i for i in cross_field_issues if i.severity == ValidationSeverity.INFO])
            
            # Business rules validation
            business_rule_issues = self._validate_business_rules(submission, strict_mode)
            errors.extend([i for i in business_rule_issues if i.severity == ValidationSeverity.ERROR])
            warnings.extend([i for i in business_rule_issues if i.severity == ValidationSeverity.WARNING])
            
            # Calculate metrics
            is_valid = len([e for e in errors if e.blocking]) == 0
            completeness = self._calculate_completeness(submission)
            blocking_errors = len([e for e in errors if e.blocking])
            
            # Build result
            result = ValidationResultSchema(
                submission_id=submission.id,
                validation_id=validation_id,
                is_valid=is_valid,
                is_complete=completeness >= 80,
                completeness_percentage=completeness,
                can_proceed_to_generation=is_valid and completeness >= 80,
                can_submit_to_carrier=is_valid and completeness >= 95,
                validated_at=datetime.utcnow(),
                validation_duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
                applicant_validation=applicant_validation,
                location_validations=location_validations,
                coverage_validation=coverage_validation,
                loss_validations=loss_validations,
                total_errors=len(errors),
                total_warnings=len(warnings),
                total_info=len(info),
                blocking_errors=blocking_errors,
                errors=errors,
                warnings=warnings,
                info=info,
                data_quality_score=self._calculate_quality_score(errors, warnings, completeness),
                field_completion_rate=completeness
            )
            
            logger.info(
                f"Validation completed: {result.total_errors} errors, "
                f"{result.total_warnings} warnings, {result.completeness_percentage}% complete"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            raise
    
    def validate_applicant(
        self,
        applicant: Applicant,
        strict_mode: bool = False
    ) -> EntityValidationSchema:
        """Validate applicant entity."""
        errors: List[ValidationIssueSchema] = []
        warnings: List[ValidationIssueSchema] = []
        field_validations: List[FieldValidationSchema] = []
        
        # Business name
        if not applicant.business_name:
            errors.append(ValidationIssueSchema(
                field_path='applicant.business_name',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Business name is required',
                blocking=True
            ))
        
        # FEIN
        if applicant.fein:
            if not is_valid_fein(applicant.fein):
                errors.append(ValidationIssueSchema(
                    field_path='applicant.fein',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.INVALID_FORMAT,
                    message='Invalid FEIN format (expected XX-XXXXXXX)',
                    current_value=applicant.fein
                ))
        elif strict_mode:
            warnings.append(ValidationIssueSchema(
                field_path='applicant.fein',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.REQUIRED_FIELD,
                message='FEIN is recommended for commercial insurance'
            ))
        
        # NAICS
        if applicant.naics_code and not is_valid_naics(applicant.naics_code):
            warnings.append(ValidationIssueSchema(
                field_path='applicant.naics_code',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.INVALID_FORMAT,
                message='Invalid NAICS code format',
                current_value=applicant.naics_code
            ))
        
        # Email
        if applicant.email and not is_valid_email(applicant.email):
            errors.append(ValidationIssueSchema(
                field_path='applicant.email',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_FORMAT,
                message='Invalid email address format',
                current_value=applicant.email
            ))
        
        # Phone
        if applicant.phone and not is_valid_phone(applicant.phone):
            warnings.append(ValidationIssueSchema(
                field_path='applicant.phone',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.INVALID_FORMAT,
                message='Invalid phone number format',
                current_value=applicant.phone
            ))
        
        # Address validation
        if not applicant.has_complete_mailing_address() and not applicant.has_complete_physical_address():
            errors.append(ValidationIssueSchema(
                field_path='applicant.address',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Complete mailing or physical address is required',
                blocking=True
            ))
        
        # State validation
        if applicant.mailing_state and not is_valid_state(applicant.mailing_state):
            errors.append(ValidationIssueSchema(
                field_path='applicant.mailing_state',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_VALUE,
                message='Invalid state code',
                current_value=applicant.mailing_state
            ))
        
        # ZIP validation
        if applicant.mailing_zip and not is_valid_zip(applicant.mailing_zip):
            errors.append(ValidationIssueSchema(
                field_path='applicant.mailing_zip',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_FORMAT,
                message='Invalid ZIP code format',
                current_value=applicant.mailing_zip
            ))
        
        missing_fields = applicant.get_missing_fields()
        completeness = self._calculate_entity_completeness(applicant)
        
        return EntityValidationSchema(
            entity_type='applicant',
            is_valid=len([e for e in errors if e.blocking]) == 0,
            is_complete=applicant.is_complete(),
            completeness_percentage=completeness,
            missing_fields=missing_fields,
            errors=errors,
            warnings=warnings,
            field_validations=field_validations
        )
    
    def validate_location(
        self,
        location: PropertyLocation,
        strict_mode: bool = False,
        index: int = 0
    ) -> EntityValidationSchema:
        """Validate property location entity."""
        errors: List[ValidationIssueSchema] = []
        warnings: List[ValidationIssueSchema] = []
        
        prefix = f'locations[{index}]'
        
        # Required fields
        if not location.address_line1:
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.address_line1',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Street address is required',
                blocking=True
            ))
        
        if not location.city:
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.city',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='City is required',
                blocking=True
            ))
        
        if not location.state:
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.state',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='State is required',
                blocking=True
            ))
        elif not is_valid_state(location.state):
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.state',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_VALUE,
                message='Invalid state code',
                current_value=location.state
            ))
        
        if not location.zip_code:
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.zip_code',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='ZIP code is required',
                blocking=True
            ))
        elif not is_valid_zip(location.zip_code):
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.zip_code',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_FORMAT,
                message='Invalid ZIP code format',
                current_value=location.zip_code
            ))
        
        # Year built
        if location.year_built:
            if not is_valid_year(location.year_built):
                errors.append(ValidationIssueSchema(
                    field_path=f'{prefix}.year_built',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.INVALID_VALUE,
                    message='Invalid year built',
                    current_value=location.year_built
                ))
        elif strict_mode:
            warnings.append(ValidationIssueSchema(
                field_path=f'{prefix}.year_built',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Year built is recommended'
            ))
        
        # Values
        if location.building_value and not is_valid_currency(location.building_value):
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.building_value',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_VALUE,
                message='Invalid building value',
                current_value=location.building_value
            ))
        
        if location.total_insured_value:
            if not is_valid_currency(location.total_insured_value):
                errors.append(ValidationIssueSchema(
                    field_path=f'{prefix}.total_insured_value',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.INVALID_VALUE,
                    message='Invalid total insured value',
                    current_value=location.total_insured_value
                ))
            elif location.total_insured_value <= 0:
                errors.append(ValidationIssueSchema(
                    field_path=f'{prefix}.total_insured_value',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.INVALID_VALUE,
                    message='Total insured value must be greater than zero',
                    current_value=location.total_insured_value
                ))
        
        missing_fields = location.get_missing_fields()
        completeness = self._calculate_entity_completeness(location)
        
        return EntityValidationSchema(
            entity_type='location',
            entity_id=location.location_number,
            is_valid=len([e for e in errors if e.blocking]) == 0,
            is_complete=location.is_complete(),
            completeness_percentage=completeness,
            missing_fields=missing_fields,
            errors=errors,
            warnings=warnings
        )
    
    def validate_coverage(
        self,
        coverage: Coverage,
        strict_mode: bool = False
    ) -> EntityValidationSchema:
        """Validate coverage entity."""
        errors: List[ValidationIssueSchema] = []
        warnings: List[ValidationIssueSchema] = []
        
        # Dates
        if not coverage.effective_date:
            warnings.append(ValidationIssueSchema(
                field_path='coverage.effective_date',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Effective date is recommended'
            ))
        
        if not coverage.expiration_date:
            warnings.append(ValidationIssueSchema(
                field_path='coverage.expiration_date',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Expiration date is recommended'
            ))
        
        if coverage.effective_date and coverage.expiration_date:
            if coverage.expiration_date <= coverage.effective_date:
                errors.append(ValidationIssueSchema(
                    field_path='coverage.expiration_date',
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.INVALID_VALUE,
                    message='Expiration date must be after effective date',
                    blocking=True
                ))
        
        # Limits
        if coverage.building_limit and not is_valid_currency(coverage.building_limit):
            errors.append(ValidationIssueSchema(
                field_path='coverage.building_limit',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.INVALID_VALUE,
                message='Invalid building limit',
                current_value=coverage.building_limit
            ))
        
        missing_fields = coverage.get_missing_fields()
        completeness = self._calculate_entity_completeness(coverage)
        
        return EntityValidationSchema(
            entity_type='coverage',
            is_valid=len([e for e in errors if e.blocking]) == 0,
            is_complete=coverage.is_complete(),
            completeness_percentage=completeness,
            missing_fields=missing_fields,
            errors=errors,
            warnings=warnings
        )
    
    def validate_loss(
        self,
        loss: LossHistory,
        strict_mode: bool = False,
        index: int = 0
    ) -> EntityValidationSchema:
        """Validate loss history entity."""
        errors: List[ValidationIssueSchema] = []
        warnings: List[ValidationIssueSchema] = []
        
        prefix = f'loss_history[{index}]'
        
        # Required fields
        if not loss.loss_date:
            errors.append(ValidationIssueSchema(
                field_path=f'{prefix}.loss_date',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Loss date is required',
                blocking=True
            ))
        
        if not loss.loss_amount and not loss.paid_amount:
            warnings.append(ValidationIssueSchema(
                field_path=f'{prefix}.loss_amount',
                severity=ValidationSeverity.WARNING,
                category=ValidationCategory.REQUIRED_FIELD,
                message='Loss amount or paid amount should be provided'
            ))
        
        missing_fields = loss.get_missing_fields()
        completeness = self._calculate_entity_completeness(loss)
        
        return EntityValidationSchema(
            entity_type='loss',
            is_valid=len([e for e in errors if e.blocking]) == 0,
            is_complete=loss.is_complete(),
            completeness_percentage=completeness,
            missing_fields=missing_fields,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_cross_fields(self, submission: Submission) -> List[ValidationIssueSchema]:
        """Validate relationships between fields."""
        issues: List[ValidationIssueSchema] = []
        
        # Check TIV consistency
        if submission.locations and submission.coverage:
            location_tiv = sum(
                float(loc.total_insured_value or 0) for loc in submission.locations
            )
            
            if submission.coverage.building_limit:
                building_limit = float(submission.coverage.building_limit)
                if abs(location_tiv - building_limit) / max(location_tiv, building_limit) > 0.1:
                    issues.append(ValidationIssueSchema(
                        field_path='coverage.building_limit',
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.INCONSISTENT_DATA,
                        message=f'Coverage limit (${building_limit:,.0f}) differs significantly from location TIV (${location_tiv:,.0f})',
                        related_fields=['locations.total_insured_value']
                    ))
        
        return issues
    
    def _validate_business_rules(
        self,
        submission: Submission,
        strict_mode: bool
    ) -> List[ValidationIssueSchema]:
        """Validate business-specific rules."""
        issues: List[ValidationIssueSchema] = []
        
        # Rule: Must have at least one location
        if len(submission.locations) == 0:
            issues.append(ValidationIssueSchema(
                field_path='locations',
                severity=ValidationSeverity.ERROR,
                category=ValidationCategory.BUSINESS_RULE,
                message='At least one property location is required',
                blocking=True,
                rule_id='BR001'
            ))
        
        # Rule: High-value properties require additional info
        for i, loc in enumerate(submission.locations):
            if loc.total_insured_value and float(loc.total_insured_value) > 10_000_000:
                if not loc.sprinkler_system or not loc.protection_class:
                    issues.append(ValidationIssueSchema(
                        field_path=f'locations[{i}]',
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.BUSINESS_RULE,
                        message='High-value properties should include sprinkler and protection class information',
                        rule_id='BR002'
                    ))
        
        return issues
    
    def _calculate_completeness(self, submission: Submission) -> int:
        """Calculate overall submission completeness percentage."""
        total_score = 0
        max_score = 0
        
        # Applicant (30%)
        max_score += 30
        if submission.applicant:
            total_score += int(self._calculate_entity_completeness(submission.applicant) * 0.3)
        
        # Locations (30%)
        max_score += 30
        if submission.locations:
            loc_scores = [self._calculate_entity_completeness(loc) for loc in submission.locations]
            avg_loc = sum(loc_scores) / len(loc_scores) if loc_scores else 0
            total_score += int(avg_loc * 0.3)
        
        # Coverage (25%)
        max_score += 25
        if submission.coverage:
            total_score += int(self._calculate_entity_completeness(submission.coverage) * 0.25)
        
        # Loss History (15%)
        max_score += 15
        if submission.loss_history:
            total_score += 15
        else:
            total_score += 10  # Partial credit if no losses
        
        return min(100, int((total_score / max_score) * 100))
    
    def _calculate_entity_completeness(self, entity: Any) -> int:
        """Calculate entity completeness percentage."""
        if hasattr(entity, 'to_dict'):
            data = entity.to_dict()
            total_fields = len([k for k in data.keys() if k != 'metadata'])
            filled_fields = len([v for v in data.values() if v is not None and v != ''])
            
            if total_fields == 0:
                return 0
            
            return int((filled_fields / total_fields) * 100)
        
        return 0
    
    def _calculate_quality_score(
        self,
        errors: List[ValidationIssueSchema],
        warnings: List[ValidationIssueSchema],
        completeness: int
    ) -> float:
        """Calculate data quality score."""
        base_score = completeness
        
        # Deduct for errors
        error_penalty = len(errors) * 5
        warning_penalty = len(warnings) * 2
        
        quality_score = max(0, base_score - error_penalty - warning_penalty)
        
        return round(quality_score, 2)
    
    def health_check(self) -> Dict[str, Any]:
        """Check validation service health."""
        try:
            return {
                'status': 'healthy',
                'service': 'ValidationService',
                'rules_loaded': len(self.validation_rules),
                'message': 'Validation service is operational'
            }
        except Exception as e:
            logger.error(f"Validation service health check failed: {e}")
            return {
                'status': 'unhealthy',
                'service': 'ValidationService',
                'error': str(e)
            }


# Global service instance
_validation_service: Optional[ValidationService] = None


def get_validation_service() -> ValidationService:
    """
    Get or create validation service singleton.
    
    Returns:
        ValidationService instance
    """
    global _validation_service
    
    if _validation_service is None:
        _validation_service = ValidationService()
    
    return _validation_service