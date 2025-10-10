"""
Health check and status routes for SubmitEZ API.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
from app.core.services import (
    get_extraction_service,
    get_validation_service,
    get_generation_service,
    get_submission_service
)
from app.infrastructure.database import check_database_health
from app.infrastructure.storage import get_supabase_storage
from app.core.processors import get_processor_factory
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')


@health_bp.route('', methods=['GET'])
@health_bp.route('/', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': current_app.config['APP_NAME'],
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with component status.
    
    Returns:
        200: All components healthy
        503: One or more components unhealthy
    """
    try:
        logger.info("Running detailed health check")
        
        # Check database
        db_health = check_database_health()
        
        # Check storage
        storage = get_supabase_storage()
        storage_health = storage.health_check()
        
        # Check processors
        processor_factory = get_processor_factory()
        processor_health = processor_factory.health_check()
        
        # Check services
        extraction_service = get_extraction_service()
        extraction_health = extraction_service.health_check()
        
        validation_service = get_validation_service()
        validation_health = validation_service.health_check()
        
        generation_service = get_generation_service()
        generation_health = generation_service.health_check()
        
        submission_service = get_submission_service()
        submission_health = submission_service.health_check()
        
        # Aggregate results
        components = {
            'database': db_health,
            'storage': storage_health,
            'processors': processor_health,
            'extraction_service': extraction_health,
            'validation_service': validation_health,
            'generation_service': generation_health,
            'submission_service': submission_health
        }
        
        # Determine overall status
        all_healthy = all(
            component.get('status') == 'healthy'
            for component in components.values()
        )
        
        overall_status = 'healthy' if all_healthy else 'degraded'
        status_code = 200 if all_healthy else 503
        
        response = {
            'status': overall_status,
            'service': current_app.config['APP_NAME'],
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'components': components
        }
        
        logger.info(f"Health check completed: {overall_status}")
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': current_app.config['APP_NAME'],
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check - is the service ready to accept requests?
    
    Returns:
        200: Service is ready
        503: Service is not ready
    """
    try:
        # Check critical components
        db_health = check_database_health()
        
        if db_health.get('status') != 'healthy':
            return jsonify({
                'ready': False,
                'reason': 'Database not available',
                'timestamp': datetime.utcnow().isoformat()
            }), 503
        
        storage = get_supabase_storage()
        storage_health = storage.health_check()
        
        if storage_health.get('status') != 'healthy':
            return jsonify({
                'ready': False,
                'reason': 'Storage not available',
                'timestamp': datetime.utcnow().isoformat()
            }), 503
        
        return jsonify({
            'ready': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            'ready': False,
            'reason': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    Liveness check - is the service alive?
    
    Returns:
        200: Service is alive
    """
    return jsonify({
        'alive': True,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@health_bp.route('/status', methods=['GET'])
def status():
    """
    Service status information.
    
    Returns:
        200: Status information
    """
    try:
        # Get processor info
        processor_factory = get_processor_factory()
        processor_info = processor_factory.get_processor_info()
        
        # Get configuration info
        config_info = {
            'environment': current_app.config['ENV'],
            'debug': current_app.config['DEBUG'],
            'max_upload_size_mb': current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024),
            'allowed_extensions': list(current_app.config['ALLOWED_EXTENSIONS']),
            'extraction_timeout': current_app.config['EXTRACTION_TIMEOUT'],
            'generation_timeout': current_app.config['GENERATION_TIMEOUT']
        }
        
        return jsonify({
            'service': current_app.config['APP_NAME'],
            'version': '1.0.0',
            'environment': current_app.config['ENV'],
            'configuration': config_info,
            'processors': processor_info,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Service metrics endpoint.
    
    Returns:
        200: Service metrics
    """
    try:
        from app.infrastructure.database.repositories import SubmissionRepository
        
        # Get submission statistics
        repo = SubmissionRepository()
        stats = repo.get_statistics()
        
        metrics_data = {
            'service': current_app.config['APP_NAME'],
            'submissions': stats,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(metrics_data), 200
        
    except Exception as e:
        logger.error(f"Metrics failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@health_bp.route('/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint.
    
    Returns:
        200: Pong response
    """
    return jsonify({
        'message': 'pong',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@health_bp.route('/version', methods=['GET'])
def version():
    """
    Service version information.
    
    Returns:
        200: Version information
    """
    return jsonify({
        'service': current_app.config['APP_NAME'],
        'version': '1.0.0',
        'api_version': 'v1',
        'build_date': '2025-01-15',
        'environment': current_app.config['ENV']
    }), 200


@health_bp.route('/info', methods=['GET'])
def info():
    """
    Service information endpoint.
    
    Returns:
        200: Service information
    """
    return jsonify({
        'service': current_app.config['APP_NAME'],
        'description': 'Commercial Insurance Submission Automation Platform',
        'version': '1.0.0',
        'documentation': '/api/docs',
        'health': {
            'basic': '/health',
            'detailed': '/health/detailed',
            'ready': '/health/ready',
            'live': '/health/live'
        },
        'endpoints': {
            'submissions': '/api/submissions',
            'health': '/health'
        },
        'supported_formats': list(current_app.config['ALLOWED_EXTENSIONS']),
        'max_file_size_mb': current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    }), 200