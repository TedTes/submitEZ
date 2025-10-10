"""
Error handler middleware for standardized error responses.
"""

from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from typing import Tuple, Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SubmitEZError(Exception):
    """Base exception for SubmitEZ application."""
    
    def __init__(self, message: str, status_code: int = 500, payload: Dict[str, Any] = None):
        """
        Initialize error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            payload: Additional error data
        """
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        rv = dict(self.payload or ())
        rv['error'] = self.__class__.__name__
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(SubmitEZError):
    """Validation error."""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(SubmitEZError):
    """Resource not found error."""
    def __init__(self, message: str = "Resource not found", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=404, payload=payload)


class UnauthorizedError(SubmitEZError):
    """Unauthorized access error."""
    def __init__(self, message: str = "Unauthorized", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=401, payload=payload)


class ForbiddenError(SubmitEZError):
    """Forbidden access error."""
    def __init__(self, message: str = "Forbidden", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=403, payload=payload)


class ConflictError(SubmitEZError):
    """Resource conflict error."""
    def __init__(self, message: str = "Resource conflict", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=409, payload=payload)


class ExtractionError(SubmitEZError):
    """Data extraction error."""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=422, payload=payload)


class GenerationError(SubmitEZError):
    """PDF generation error."""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=500, payload=payload)


class StorageError(SubmitEZError):
    """File storage error."""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=500, payload=payload)


class DatabaseError(SubmitEZError):
    """Database operation error."""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=500, payload=payload)


def register_error_handlers(app):
    """
    Register error handlers with Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(SubmitEZError)
    def handle_submitez_error(error: SubmitEZError) -> Tuple[Dict[str, Any], int]:
        """Handle custom SubmitEZ errors."""
        logger.error(
            f"{error.__class__.__name__}: {error.message}",
            extra={
                'status_code': error.status_code,
                'payload': error.payload,
                'request_path': request.path,
                'request_method': request.method
            }
        )
        
        response = error.to_dict()
        response['path'] = request.path
        response['method'] = request.method
        
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(
            f"HTTP {error.code}: {error.description}",
            extra={
                'request_path': request.path,
                'request_method': request.method
            }
        )
        
        response = {
            'error': error.name,
            'message': error.description,
            'status_code': error.code,
            'path': request.path,
            'method': request.method
        }
        
        return jsonify(response), error.code
    
    @app.errorhandler(400)
    def handle_bad_request(error) -> Tuple[Dict[str, Any], int]:
        """Handle 400 Bad Request errors."""
        response = {
            'error': 'BadRequest',
            'message': 'Invalid request data',
            'status_code': 400,
            'path': request.path
        }
        return jsonify(response), 400
    
    @app.errorhandler(404)
    def handle_not_found(error) -> Tuple[Dict[str, Any], int]:
        """Handle 404 Not Found errors."""
        response = {
            'error': 'NotFound',
            'message': 'The requested resource was not found',
            'status_code': 404,
            'path': request.path
        }
        return jsonify(response), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error) -> Tuple[Dict[str, Any], int]:
        """Handle 405 Method Not Allowed errors."""
        response = {
            'error': 'MethodNotAllowed',
            'message': f'Method {request.method} not allowed for this endpoint',
            'status_code': 405,
            'path': request.path,
            'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else []
        }
        return jsonify(response), 405
    
    @app.errorhandler(413)
    def handle_request_entity_too_large(error) -> Tuple[Dict[str, Any], int]:
        """Handle 413 Request Entity Too Large errors."""
        max_size = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        max_size_mb = max_size / (1024 * 1024)
        
        response = {
            'error': 'RequestEntityTooLarge',
            'message': f'File size exceeds maximum limit of {max_size_mb:.0f}MB',
            'status_code': 413,
            'max_size_bytes': max_size,
            'max_size_mb': max_size_mb,
            'path': request.path
        }
        return jsonify(response), 413
    
    @app.errorhandler(415)
    def handle_unsupported_media_type(error) -> Tuple[Dict[str, Any], int]:
        """Handle 415 Unsupported Media Type errors."""
        allowed_types = app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'xlsx', 'xls', 'docx', 'doc'})
        
        response = {
            'error': 'UnsupportedMediaType',
            'message': 'Unsupported file type',
            'status_code': 415,
            'allowed_types': list(allowed_types),
            'path': request.path
        }
        return jsonify(response), 415
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(error) -> Tuple[Dict[str, Any], int]:
        """Handle 422 Unprocessable Entity errors."""
        response = {
            'error': 'UnprocessableEntity',
            'message': 'Request data is valid but cannot be processed',
            'status_code': 422,
            'path': request.path
        }
        return jsonify(response), 422
    
    @app.errorhandler(500)
    def handle_internal_server_error(error) -> Tuple[Dict[str, Any], int]:
        """Handle 500 Internal Server Error."""
        logger.error(
            f"Internal server error: {error}",
            extra={
                'request_path': request.path,
                'request_method': request.method
            },
            exc_info=True
        )
        
        response = {
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred',
            'status_code': 500,
            'path': request.path
        }
        
        # Include error details in development
        if app.debug:
            response['details'] = str(error)
        
        return jsonify(response), 500
    
    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError) -> Tuple[Dict[str, Any], int]:
        """Handle ValueError exceptions."""
        logger.warning(
            f"ValueError: {error}",
            extra={
                'request_path': request.path,
                'request_method': request.method
            }
        )
        
        response = {
            'error': 'ValueError',
            'message': str(error),
            'status_code': 400,
            'path': request.path
        }
        
        return jsonify(response), 400
    
    @app.errorhandler(KeyError)
    def handle_key_error(error: KeyError) -> Tuple[Dict[str, Any], int]:
        """Handle KeyError exceptions."""
        logger.warning(
            f"KeyError: {error}",
            extra={
                'request_path': request.path,
                'request_method': request.method
            }
        )
        
        response = {
            'error': 'KeyError',
            'message': f'Missing required field: {error}',
            'status_code': 400,
            'path': request.path
        }
        
        return jsonify(response), 400
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Handle all other unexpected exceptions."""
        logger.error(
            f"Unexpected error: {error}",
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'error_type': type(error).__name__
            },
            exc_info=True
        )
        
        response = {
            'error': 'UnexpectedError',
            'message': 'An unexpected error occurred',
            'status_code': 500,
            'path': request.path
        }
        
        # Include error details in development
        if app.debug:
            response['error_type'] = type(error).__name__
            response['details'] = str(error)
        
        return jsonify(response), 500
    
    logger.info("Error handlers registered successfully")


def create_error_response(
    error: str,
    message: str,
    status_code: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error: Error type/name
        message: Error message
        status_code: HTTP status code
        **kwargs: Additional error data
        
    Returns:
        Error response dictionary
    """
    response = {
        'error': error,
        'message': message,
        'status_code': status_code,
        'path': request.path if request else None,
        'method': request.method if request else None
    }
    
    response.update(kwargs)
    
    return response


def validate_request_data(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate request data has required fields.
    
    Args:
        data: Request data
        required_fields: List of required field names
        
    Raises:
        ValidationError: If validation fails
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            payload={'missing_fields': missing_fields}
        )


def validate_file_upload_request(files: Dict) -> None:
    """
    Validate file upload request.
    
    Args:
        files: Request files
        
    Raises:
        ValidationError: If validation fails
    """
    if not files:
        raise ValidationError(
            message="No files provided in request",
            payload={'field': 'files'}
        )
    
    if 'files' not in files:
        raise ValidationError(
            message="Missing 'files' field in request",
            payload={'field': 'files'}
        )