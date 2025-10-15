"""
SubmitEZ Utilities Package
"""

from .logger import (
    setup_logger,
    get_logger,
    LoggerMixin,
    log_function_call,
    log_execution_time
)

from .file_utils import (
    allowed_file,
    get_file_extension,
    get_mime_type,
    validate_mime_type,
    sanitize_filename,
    generate_unique_filename,
    get_file_size,
    format_file_size,
    validate_file_size,
    calculate_file_hash,
    validate_file_upload,
    ensure_directory_exists,
    delete_file_safe,
    get_file_info,
    ALLOWED_EXTENSIONS,
    MIME_TYPE_MAP,
    convert_to_json_serializable
)

from .validation_utils import (
    is_valid_email,
    is_valid_phone,
    format_phone,
    is_valid_fein,
    format_fein,
    is_valid_zip,
    is_valid_state,
    is_valid_naics,
    is_valid_year,
    is_valid_currency,
    is_not_empty,
    is_valid_url,
    validate_required_fields,
    sanitize_string,
    normalize_whitespace
)

__all__ = [
    # Logger
    'setup_logger',
    'get_logger',
    'LoggerMixin',
    'log_function_call',
    'log_execution_time',
    
    # File utilities
    'allowed_file',
    'get_file_extension',
    'get_mime_type',
    'validate_mime_type',
    'sanitize_filename',
    'generate_unique_filename',
    'get_file_size',
    'format_file_size',
    'validate_file_size',
    'calculate_file_hash',
    'validate_file_upload',
    'ensure_directory_exists',
    'delete_file_safe',
    'get_file_info',
    'ALLOWED_EXTENSIONS',
    'MIME_TYPE_MAP',
    
    # Validation utilities
    'is_valid_email',
    'is_valid_phone',
    'format_phone',
    'is_valid_fein',
    'format_fein',
    'is_valid_zip',
    'is_valid_state',
    'is_valid_naics',
    'is_valid_year',
    'is_valid_currency',
    'is_not_empty',
    'is_valid_url',
    'validate_required_fields',
    'sanitize_string',
    'normalize_whitespace',
    'convert_to_json_serializable'
]