"""
Request validator middleware for input validation.
"""

from flask import request
from functools import wraps
from typing import Callable, List, Optional, Any
from werkzeug.datastructures import FileStorage
from app.api.middleware.error_handler import ValidationError
from app.utils.file_utils import (
    allowed_file,
    get_file_extension,
    validate_file_upload,
    ALLOWED_EXTENSIONS
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_json_request(required_fields: Optional[List[str]] = None):
    """
    Decorator to validate JSON request data.
    
    Args:
        required_fields: List of required field names
        
    Usage:
        @validate_json_request(['name', 'email'])
        def create_user():
            data = request.get_json()
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON content type
            if not request.is_json:
                raise ValidationError(
                    message="Request must be JSON",
                    payload={'content_type': request.content_type}
                )
            
            # Get JSON data
            try:
                data = request.get_json()
            except Exception as e:
                raise ValidationError(
                    message="Invalid JSON in request body",
                    payload={'error': str(e)}
                )
            
            # Validate required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    raise ValidationError(
                        message=f"Missing required fields: {', '.join(missing_fields)}",
                        payload={'missing_fields': missing_fields}
                    )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_file_upload_request(
    required: bool = True,
    max_files: Optional[int] = None,
    allowed_extensions: Optional[set] = None
):
    """
    Decorator to validate file upload requests.
    
    Args:
        required: Whether file upload is required
        max_files: Maximum number of files allowed
        allowed_extensions: Set of allowed file extensions
        
    Usage:
        @validate_file_upload_request(required=True, max_files=5)
        def upload_files():
            files = request.files.getlist('files')
            # ... handle upload
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if files are present
            if 'files' not in request.files:
                if required:
                    raise ValidationError(
                        message="No files provided in request",
                        payload={'field': 'files'}
                    )
                else:
                    return f(*args, **kwargs)
            
            # Get uploaded files
            files = request.files.getlist('files')
            
            # Check if at least one file
            if required and not files:
                raise ValidationError(
                    message="At least one file is required",
                    payload={'field': 'files'}
                )
            
            # Check max files limit
            if max_files and len(files) > max_files:
                raise ValidationError(
                    message=f"Maximum {max_files} files allowed",
                    payload={
                        'max_files': max_files,
                        'received_files': len(files)
                    }
                )
            
            # Validate each file
            extensions = allowed_extensions or ALLOWED_EXTENSIONS
            errors = []
            
            for file in files:
                # Check if file has filename
                if not file.filename:
                    errors.append({
                        'error': 'Missing filename'
                    })
                    continue
                
                # Validate file
                is_valid, error = validate_file_upload(file, allowed_extensions=extensions)
                if not is_valid:
                    errors.append({
                        'filename': file.filename,
                        'error': error
                    })
            
            if errors:
                raise ValidationError(
                    message="File validation failed",
                    payload={
                        'errors': errors,
                        'allowed_extensions': list(extensions)
                    }
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_query_params(allowed_params: Optional[List[str]] = None):
    """
    Decorator to validate query parameters.
    
    Args:
        allowed_params: List of allowed parameter names
        
    Usage:
        @validate_query_params(['status', 'limit', 'offset'])
        def list_submissions():
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if allowed_params:
                invalid_params = []
                for param in request.args.keys():
                    if param not in allowed_params:
                        invalid_params.append(param)
                
                if invalid_params:
                    raise ValidationError(
                        message=f"Invalid query parameters: {', '.join(invalid_params)}",
                        payload={
                            'invalid_params': invalid_params,
                            'allowed_params': allowed_params
                        }
                    )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_uuid(param_name: str = 'id'):
    """
    Decorator to validate UUID path parameter.
    
    Args:
        param_name: Name of the parameter to validate
        
    Usage:
        @validate_uuid('submission_id')
        def get_submission(submission_id):
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import re
            
            # Get parameter value
            param_value = kwargs.get(param_name)
            
            if param_value:
                # UUID regex pattern
                uuid_pattern = re.compile(
                    r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
                    re.IGNORECASE
                )
                
                if not uuid_pattern.match(str(param_value)):
                    raise ValidationError(
                        message=f"Invalid UUID format for parameter '{param_name}'",
                        payload={
                            'parameter': param_name,
                            'value': param_value
                        }
                    )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_pagination(
    max_limit: int = 100,
    default_limit: int = 50
):
    """
    Decorator to validate and normalize pagination parameters.
    
    Args:
        max_limit: Maximum allowed limit
        default_limit: Default limit if not provided
        
    Usage:
        @validate_pagination(max_limit=100)
        def list_items():
            limit = request.args.get('limit', type=int)
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate limit
            limit = request.args.get('limit', default_limit, type=int)
            if limit < 1:
                raise ValidationError(
                    message="Limit must be at least 1",
                    payload={'limit': limit}
                )
            
            if limit > max_limit:
                raise ValidationError(
                    message=f"Limit cannot exceed {max_limit}",
                    payload={
                        'limit': limit,
                        'max_limit': max_limit
                    }
                )
            
            # Validate offset
            offset = request.args.get('offset', 0, type=int)
            if offset < 0:
                raise ValidationError(
                    message="Offset must be non-negative",
                    payload={'offset': offset}
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_content_type(allowed_types: List[str]):
    """
    Decorator to validate request content type.
    
    Args:
        allowed_types: List of allowed content types
        
    Usage:
        @validate_content_type(['application/json'])
        def create_item():
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_type = request.content_type
            
            if content_type not in allowed_types:
                raise ValidationError(
                    message=f"Invalid content type: {content_type}",
                    payload={
                        'received_content_type': content_type,
                        'allowed_types': allowed_types
                    }
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_enum(field: str, allowed_values: List[Any], location: str = 'json'):
    """
    Decorator to validate enum field values.
    
    Args:
        field: Field name to validate
        allowed_values: List of allowed values
        location: Where to find the field ('json', 'args', 'form')
        
    Usage:
        @validate_enum('status', ['draft', 'submitted', 'completed'])
        def update_status():
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get value based on location
            if location == 'json':
                data = request.get_json() or {}
                value = data.get(field)
            elif location == 'args':
                value = request.args.get(field)
            elif location == 'form':
                value = request.form.get(field)
            else:
                raise ValueError(f"Invalid location: {location}")
            
            # Validate if value is present
            if value is not None and value not in allowed_values:
                raise ValidationError(
                    message=f"Invalid value for '{field}': {value}",
                    payload={
                        'field': field,
                        'value': value,
                        'allowed_values': allowed_values
                    }
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_request_size(max_size_mb: int = 16):
    """
    Decorator to validate request size.
    
    Args:
        max_size_mb: Maximum request size in megabytes
        
    Usage:
        @validate_request_size(max_size_mb=50)
        def upload_large_file():
            # ... handle request
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            max_size_bytes = max_size_mb * 1024 * 1024
            
            content_length = request.content_length
            if content_length and content_length > max_size_bytes:
                raise ValidationError(
                    message=f"Request size exceeds {max_size_mb}MB limit",
                    payload={
                        'max_size_mb': max_size_mb,
                        'received_size_mb': round(content_length / (1024 * 1024), 2)
                    }
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class RequestValidator:
    """
    Request validator class for more complex validation scenarios.
    """
    
    @staticmethod
    def validate_submission_create(data: dict) -> None:
        """Validate submission creation data."""
        # Optional fields - no validation needed for create
        pass
    
    @staticmethod
    def validate_submission_update(data: dict) -> None:
        """Validate submission update data."""
        # Validate applicant if provided
        if 'applicant' in data:
            RequestValidator._validate_applicant(data['applicant'])
        
        # Validate locations if provided
        if 'locations' in data:
            if not isinstance(data['locations'], list):
                raise ValidationError(
                    message="Locations must be an array",
                    payload={'field': 'locations'}
                )
            
            for i, location in enumerate(data['locations']):
                RequestValidator._validate_location(location, i)
        
        # Validate coverage if provided
        if 'coverage' in data:
            RequestValidator._validate_coverage(data['coverage'])
    
    @staticmethod
    def _validate_applicant(applicant: dict) -> None:
        """Validate applicant data."""
        if 'business_name' in applicant:
            if not applicant['business_name'] or not isinstance(applicant['business_name'], str):
                raise ValidationError(
                    message="Business name must be a non-empty string",
                    payload={'field': 'applicant.business_name'}
                )
    
    @staticmethod
    def _validate_location(location: dict, index: int) -> None:
        """Validate location data."""
        required_fields = ['address_line1', 'city', 'state', 'zip_code']
        missing = []
        
        for field in required_fields:
            if field not in location or not location[field]:
                missing.append(field)
        
        if missing:
            raise ValidationError(
                message=f"Location {index}: missing required fields",
                payload={
                    'location_index': index,
                    'missing_fields': missing
                }
            )
    
    @staticmethod
    def _validate_coverage(coverage: dict) -> None:
        """Validate coverage data."""
        # Validate dates if provided
        if 'effective_date' in coverage and 'expiration_date' in coverage:
            from datetime import datetime
            
            try:
                eff_date = datetime.fromisoformat(str(coverage['effective_date']))
                exp_date = datetime.fromisoformat(str(coverage['expiration_date']))
                
                if exp_date <= eff_date:
                    raise ValidationError(
                        message="Expiration date must be after effective date",
                        payload={'field': 'coverage.expiration_date'}
                    )
            except (ValueError, TypeError):
                pass  # Let business logic handle date format validation
    
    @staticmethod
    def validate_extraction_request(data: dict) -> None:
        """Validate extraction request data."""
        required_fields = ['submission_id']
        missing = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing.append(field)
        
        if missing:
            raise ValidationError(
                message=f"Missing required fields: {', '.join(missing)}",
                payload={'missing_fields': missing}
            )
    
    @staticmethod
    def validate_generation_request(data: dict) -> None:
        """Validate generation request data."""
        required_fields = ['submission_id']
        missing = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing.append(field)
        
        if missing:
            raise ValidationError(
                message=f"Missing required fields: {', '.join(missing)}",
                payload={'missing_fields': missing}
            )
        
        # Validate forms if provided
        if 'forms' in data:
            if not isinstance(data['forms'], list):
                raise ValidationError(
                    message="Forms must be an array",
                    payload={'field': 'forms'}
                )
            
            allowed_forms = ['125', '140', '126', '130']
            invalid_forms = [f for f in data['forms'] if f not in allowed_forms]
            
            if invalid_forms:
                raise ValidationError(
                    message=f"Invalid form types: {', '.join(invalid_forms)}",
                    payload={
                        'invalid_forms': invalid_forms,
                        'allowed_forms': allowed_forms
                    }
                )