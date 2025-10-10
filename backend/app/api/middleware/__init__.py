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
    validate_file_upload_request
)

__all__ = [
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
    'validate_file_upload_request'
]