"""
API middleware package for SubmitEZ.
"""

from .error_handler import (
    register_error_handlers,
    SubmitEZError,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ExtractionError,
    GenerationError,
    StorageError,
    DatabaseError,
    create_error_response,
    validate_request_data,
    validate_file_upload_request as validate_file_upload_helper
)

from .request_validator import (
    validate_json_request,
    validate_file_upload_request,
    validate_query_params,
    validate_uuid,
    validate_pagination,
    validate_content_type,
    validate_enum,
    validate_request_size,
    RequestValidator
)

__all__ = [
    # Error handlers
    'register_error_handlers',
    'SubmitEZError',
    'ValidationError',
    'NotFoundError',
    'UnauthorizedError',
    'ForbiddenError',
    'ConflictError',
    'ExtractionError',
    'GenerationError',
    'StorageError',
    'DatabaseError',
    'create_error_response',
    'validate_request_data',
    'validate_file_upload_helper',
    
    # Request validators
    'validate_json_request',
    'validate_file_upload_request',
    'validate_query_params',
    'validate_uuid',
    'validate_pagination',
    'validate_content_type',
    'validate_enum',
    'validate_request_size',
    'RequestValidator'
]