"""
Pydantic schemas package for SubmitEZ.
"""

from .submission_schema import (
    ApplicantSchema,
    PropertyLocationSchema,
    CoverageSchema,
    LossHistorySchema,
    SubmissionCreateSchema,
    SubmissionUpdateSchema,
    SubmissionResponseSchema,
    SubmissionSummarySchema
)

from .extraction_schema import (
    ExtractionStatus,
    ConfidenceLevel,
    ExtractedFieldSchema,
    ExtractedApplicantSchema,
    ExtractedPropertyLocationSchema,
    ExtractedCoverageSchema,
    ExtractedLossHistorySchema,
    DocumentExtractionSchema,
    ExtractionResultSchema,
    ExtractionRequestSchema,
    ExtractionSummarySchema
)

from .validation_schema import (
    ValidationSeverity,
    ValidationCategory,
    ValidationIssueSchema,
    FieldValidationSchema,
    EntityValidationSchema,
    ValidationResultSchema,
    ValidationRequestSchema,
    ValidationSummarySchema,
    BusinessRuleSchema,
    AutoFixSuggestionSchema,
    ValidationComparisonSchema
)

__all__ = [
    # Submission schemas
    'ApplicantSchema',
    'PropertyLocationSchema',
    'CoverageSchema',
    'LossHistorySchema',
    'SubmissionCreateSchema',
    'SubmissionUpdateSchema',
    'SubmissionResponseSchema',
    'SubmissionSummarySchema',
    
    # Extraction schemas
    'ExtractionStatus',
    'ConfidenceLevel',
    'ExtractedFieldSchema',
    'ExtractedApplicantSchema',
    'ExtractedPropertyLocationSchema',
    'ExtractedCoverageSchema',
    'ExtractedLossHistorySchema',
    'DocumentExtractionSchema',
    'ExtractionResultSchema',
    'ExtractionRequestSchema',
    'ExtractionSummarySchema',
    
    # Validation schemas
    'ValidationSeverity',
    'ValidationCategory',
    'ValidationIssueSchema',
    'FieldValidationSchema',
    'EntityValidationSchema',
    'ValidationResultSchema',
    'ValidationRequestSchema',
    'ValidationSummarySchema',
    'BusinessRuleSchema',
    'AutoFixSuggestionSchema',
    'ValidationComparisonSchema'
]