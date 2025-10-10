"""
Submission API routes for SubmitEZ.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from app.core.services import get_submission_service
from app.api.middleware import (
    ValidationError,
    NotFoundError,
    validate_json_request,
    validate_file_upload_request,
    validate_query_params,
    validate_uuid,
    validate_pagination,
    validate_enum,
    RequestValidator
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
submission_bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')


@submission_bp.route('', methods=['POST'])
@submission_bp.route('/', methods=['POST'])
def create_submission():
    """
    Create a new submission.
    
    Request body (optional fields):
        - broker_name: string
        - broker_email: string
        - carrier_name: string
        - notes: string
    
    Returns:
        201: Submission created
        400: Invalid request
    """
    try:
        data = request.get_json() or {}
        
        service = get_submission_service()
        submission = service.create_submission(
            broker_name=data.get('broker_name'),
            broker_email=data.get('broker_email'),
            carrier_name=data.get('carrier_name'),
            notes=data.get('notes')
        )
        
        logger.info(f"Created submission: {submission.id}")
        
        return jsonify({
            'message': 'Submission created successfully',
            'submission_id': submission.id,
            'status': submission.status,
            'created_at': submission.created_at.isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        raise


@submission_bp.route('/<submission_id>', methods=['GET'])
@validate_uuid('submission_id')
def get_submission(submission_id: str):
    """
    Get submission by ID.
    
    Returns:
        200: Submission details
        404: Submission not found
    """
    try:
        service = get_submission_service()
        submission = service.get_submission(submission_id)
        
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        return jsonify(submission.to_dict()), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {e}")
        raise


@submission_bp.route('', methods=['GET'])
@submission_bp.route('/', methods=['GET'])
@validate_query_params(['status', 'limit', 'offset'])
@validate_pagination(max_limit=100, default_limit=50)
def list_submissions():
    """
    List submissions with optional filtering.
    
    Query parameters:
        - status: Filter by status
        - limit: Number of results (max 100)
        - offset: Offset for pagination
    
    Returns:
        200: List of submissions
    """
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        
        service = get_submission_service()
        submissions = service.list_submissions(status=status, limit=limit)
        
        return jsonify({
            'submissions': [s.get_summary() for s in submissions],
            'total': len(submissions),
            'limit': limit,
            'status_filter': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing submissions: {e}")
        raise


@submission_bp.route('/<submission_id>', methods=['PATCH'])
@validate_uuid('submission_id')
@validate_json_request()
def update_submission(submission_id: str):
    """
    Update submission data.
    
    Request body:
        - applicant: object (optional)
        - locations: array (optional)
        - coverage: object (optional)
        - loss_history: array (optional)
        - broker_name: string (optional)
        - carrier_name: string (optional)
        - notes: string (optional)
    
    Returns:
        200: Submission updated
        404: Submission not found
        400: Invalid data
    """
    try:
        data = request.get_json()
        
        # Validate update data
        RequestValidator.validate_submission_update(data)
        
        service = get_submission_service()
        submission = service.update_submission(submission_id, data)
        
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        logger.info(f"Updated submission: {submission_id}")
        
        return jsonify({
            'message': 'Submission updated successfully',
            'submission': submission.to_dict()
        }), 200
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error updating submission: {e}")
        raise


@submission_bp.route('/<submission_id>', methods=['DELETE'])
@validate_uuid('submission_id')
def delete_submission(submission_id: str):
    """
    Delete submission and associated files.
    
    Returns:
        200: Submission deleted
        404: Submission not found
    """
    try:
        service = get_submission_service()
        
        # Check if exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Delete
        success = service.delete_submission(submission_id)
        
        if not success:
            raise Exception("Failed to delete submission")
        
        logger.info(f"Deleted submission: {submission_id}")
        
        return jsonify({
            'message': 'Submission deleted successfully',
            'submission_id': submission_id
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting submission: {e}")
        raise


@submission_bp.route('/<submission_id>/upload', methods=['POST'])
@validate_uuid('submission_id')
@validate_file_upload_request(required=True, max_files=10)
def upload_files(submission_id: str):
    """
    Upload files for submission.
    
    Form data:
        - files: File[] (required, max 10 files)
    
    Returns:
        200: Files uploaded
        404: Submission not found
        400: Invalid files
    """
    try:
        service = get_submission_service()
        
        # Check if submission exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Get uploaded files
        files = request.files.getlist('files')
        
        # Upload files
        result = service.upload_files(submission_id, files)
        
        logger.info(
            f"Uploaded {result['successful_uploads']} files for submission {submission_id}"
        )
        
        return jsonify({
            'message': f"Uploaded {result['successful_uploads']} of {result['total_files']} files",
            'result': result
        }), 200
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise


@submission_bp.route('/<submission_id>/extract', methods=['POST'])
@validate_uuid('submission_id')
def extract_data(submission_id: str):
    """
    Extract data from uploaded files.
    
    Returns:
        200: Extraction completed
        404: Submission not found
        400: No files to extract from
    """
    try:
        service = get_submission_service()
        
        # Check if submission exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Extract data
        result = service.extract_data(submission_id)
        
        logger.info(f"Extraction completed for submission {submission_id}")
        
        return jsonify({
            'message': 'Data extraction completed',
            'result': result
        }), 200
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        raise


@submission_bp.route('/<submission_id>/validate', methods=['POST'])
@validate_uuid('submission_id')
def validate_data(submission_id: str):
    """
    Validate submission data.
    
    Request body (optional):
        - strict_mode: boolean
    
    Returns:
        200: Validation completed
        404: Submission not found
    """
    try:
        data = request.get_json() or {}
        strict_mode = data.get('strict_mode', False)
        
        service = get_submission_service()
        
        # Check if submission exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Validate
        result = service.validate_data(submission_id, strict_mode)
        
        logger.info(
            f"Validation completed for submission {submission_id}: "
            f"{result['total_errors']} errors, {result['total_warnings']} warnings"
        )
        
        return jsonify({
            'message': 'Validation completed',
            'result': result
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise


@submission_bp.route('/<submission_id>/generate', methods=['POST'])
@validate_uuid('submission_id')
def generate_forms(submission_id: str):
    """
    Generate submission forms.
    
    Request body (optional):
        - forms: array of form types ['125', '140']
        - carrier_name: string
    
    Returns:
        200: Generation completed
        404: Submission not found
        400: Submission not validated
    """
    try:
        data = request.get_json() or {}
        
        # Validate request
        if data:
            RequestValidator.validate_generation_request({
                'submission_id': submission_id,
                **data
            })
        
        service = get_submission_service()
        
        # Check if submission exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Generate forms
        result = service.generate_forms(
            submission_id,
            forms=data.get('forms'),
            carrier_name=data.get('carrier_name')
        )
        
        logger.info(
            f"Generation completed for submission {submission_id}: "
            f"{result['successful_forms']} forms generated"
        )
        
        return jsonify({
            'message': 'Form generation completed',
            'result': result
        }), 200
        
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error generating forms: {e}")
        raise


@submission_bp.route('/<submission_id>/download', methods=['GET'])
@validate_uuid('submission_id')
def get_download_package(submission_id: str):
    """
    Get download package with all generated files.
    
    Returns:
        200: Download package information
        404: Submission not found
    """
    try:
        service = get_submission_service()
        
        # Check if submission exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Get download package
        package = service.get_download_package(submission_id)
        
        return jsonify({
            'message': 'Download package ready',
            'package': package
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting download package: {e}")
        raise


@submission_bp.route('/<submission_id>/process', methods=['POST'])
@validate_uuid('submission_id')
def process_workflow(submission_id: str):
    """
    Execute complete submission workflow.
    
    Request body (optional):
        - skip_validation: boolean
    
    Returns:
        200: Workflow completed
        404: Submission not found
    """
    try:
        data = request.get_json() or {}
        skip_validation = data.get('skip_validation', False)
        
        service = get_submission_service()
        
        # Check if submission exists
        submission = service.get_submission(submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        # Process workflow
        result = service.process_submission_workflow(
            submission_id,
            skip_validation=skip_validation
        )
        
        logger.info(f"Workflow completed for submission {submission_id}")
        
        return jsonify({
            'message': 'Workflow completed',
            'result': result
        }), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error processing workflow: {e}")
        raise


@submission_bp.route('/<submission_id>/summary', methods=['GET'])
@validate_uuid('submission_id')
def get_submission_summary(submission_id: str):
    """
    Get submission summary.
    
    Returns:
        200: Submission summary
        404: Submission not found
    """
    try:
        service = get_submission_service()
        submission = service.get_submission(submission_id)
        
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")
        
        summary = submission.get_summary()
        
        return jsonify(summary), 200
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting submission summary: {e}")
        raise


@submission_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get submission statistics.
    
    Returns:
        200: Statistics
    """
    try:
        from app.infrastructure.database.repositories import SubmissionRepository
        
        repo = SubmissionRepository()
        stats = repo.get_statistics()
        
        return jsonify({
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise