"""
Submission service - main business logic coordinator.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
from werkzeug.datastructures import FileStorage
from app.domain.models import Submission, Applicant, PropertyLocation, Coverage, LossHistory
from app.infrastructure.database.repositories import SubmissionRepository
from app.infrastructure.storage import get_supabase_storage
from app.core.services import (
    get_extraction_service,
    get_validation_service,
    get_generation_service
)
from app.utils.logger import get_logger
from app.utils.file_utils import (
    validate_file_upload,
    sanitize_filename,
    generate_unique_filename,
    get_file_info
)

logger = get_logger(__name__)


class SubmissionService:
    """
    Main orchestrator for submission workflow.
    
    Coordinates the complete submission lifecycle:
    1. Create submission
    2. Upload documents
    3. Extract data (AI + processors)
    4. Validate data (business rules)
    5. Generate PDFs (ACORD + carrier forms)
    6. Download/deliver package
    
    This is the primary entry point for all submission operations.
    """
    
    def __init__(self):
        """Initialize submission service."""
        self.repository = SubmissionRepository()
        self.storage = get_supabase_storage()
        self.extraction_service = get_extraction_service()
        self.validation_service = get_validation_service()
        self.generation_service = get_generation_service()
        
        # Temporary upload directory
        self.upload_dir = Path('/tmp/submitez-uploads')
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def create_submission(
        self,
        client_name: Optional[str] = None,
        broker_name: Optional[str] = None,
        broker_email: Optional[str] = None,
        carrier_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Submission:
        """
        Create a new submission.
        
        Args:
            client_name: Client/project name  # ← ADD THIS LINE
            broker_name: Broker/agent name
            broker_email: Broker email
            carrier_name: Target carrier name
            notes: Initial notes
            
        Returns:
            Created submission entity
        """
        try:
            logger.info("Creating new submission")
            
            # Create submission entity
            submission = Submission(
                status='draft',
                client_name=client_name,
                broker_name=broker_name,
                broker_email=broker_email,
                carrier_name=carrier_name,
                notes=notes
            )
            
            # Save to database
            saved_submission = self.repository.create(submission)
            
            logger.info(f"Created submission: {saved_submission.id}")
            
            return saved_submission
            
        except Exception as e:
            logger.error(f"Error creating submission: {e}")
            raise
    
    def get_submission(self, submission_id: str) -> Optional[Submission]:
        """
        Get submission by ID.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            Submission entity or None
        """
        try:
            return self.repository.get_by_id(submission_id)
        except Exception as e:
            logger.error(f"Error getting submission {submission_id}: {e}")
            raise
    
    def list_submissions(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = 50
    ) -> List[Submission]:
        """
        List submissions with optional filtering.
        
        Args:
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of submissions
        """
        try:
            if status:
                return self.repository.get_by_status(status, limit)
            else:
                return self.repository.get_all(limit=limit)
        except Exception as e:
            logger.error(f"Error listing submissions: {e}")
            raise
    
    def update_submission(
        self,
        submission_id: str,
        data: Dict[str, Any]
    ) -> Optional[Submission]:
        """
        Update submission data.
        
        Args:
            submission_id: Submission identifier
            data: Update data dictionary
            
        Returns:
            Updated submission
        """
        try:
            logger.info(f"Updating submission {submission_id}")
            
            # Convert domain models if present
            if 'applicant' in data and isinstance(data['applicant'], dict):
                data['applicant'] = Applicant.from_dict(data['applicant'])
            
            if 'locations' in data and isinstance(data['locations'], list):
                data['locations'] = [
                    PropertyLocation.from_dict(loc) if isinstance(loc, dict) else loc
                    for loc in data['locations']
                ]
            
            if 'coverage' in data and isinstance(data['coverage'], dict):
                data['coverage'] = Coverage.from_dict(data['coverage'])
            
            if 'loss_history' in data and isinstance(data['loss_history'], list):
                data['loss_history'] = [
                    LossHistory.from_dict(loss) if isinstance(loss, dict) else loss
                    for loss in data['loss_history']
                ]
            
            # Convert to dict for database update
            update_dict = {}
            for key, value in data.items():
                if hasattr(value, 'to_dict'):
                    update_dict[key] = value.to_dict()
                elif isinstance(value, list) and value and hasattr(value[0], 'to_dict'):
                    update_dict[key] = [v.to_dict() for v in value]
                else:
                    update_dict[key] = value
            
            return self.repository.update(submission_id, update_dict)
            
        except Exception as e:
            logger.error(f"Error updating submission {submission_id}: {e}")
            raise
    
    def delete_submission(self, submission_id: str) -> bool:
        """
        Delete submission and associated files.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting submission {submission_id}")
            
            # Delete generated files
            self.generation_service.delete_generated_files(submission_id)
            
            # Delete uploaded files
            prefix = f"submissions/{submission_id}/uploaded/"
            uploaded_files = self.storage.list_files(prefix=prefix)
            if uploaded_files:
                file_paths = [f['path'] for f in uploaded_files]
                self.storage.batch_delete(file_paths)
            
            # Delete from database
            return self.repository.delete(submission_id)
            
        except Exception as e:
            logger.error(f"Error deleting submission {submission_id}: {e}")
            raise
    
    def upload_files(
        self,
        submission_id: str,
        files: List[FileStorage]
    ) -> Dict[str, Any]:
        """
        Upload files for submission.
        
        Args:
            submission_id: Submission identifier
            files: List of file uploads
            
        Returns:
            Upload result dictionary
        """
        try:
            logger.info(f"Uploading {len(files)} files for submission {submission_id}")
            
            submission = self.get_submission(submission_id)
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            uploaded_files = []
            errors = []
            
            for file in files:
                try:
                    # Validate file
                    is_valid, error = validate_file_upload(file)
                    if not is_valid:
                        errors.append({
                            'filename': file.filename,
                            'error': error
                        })
                        continue
                    
                    # Generate unique filename
                    safe_filename = sanitize_filename(file.filename)
                    unique_filename = generate_unique_filename(safe_filename)
                    
                    # Save temporarily
                    local_path = self.upload_dir / unique_filename
                    file.save(str(local_path))
                    
                    # Upload to storage
                    storage_path = f"submissions/{submission_id}/uploaded/{unique_filename}"
                    
                    with open(local_path, 'rb') as f:
                        upload_result = self.storage.upload_file(
                            file_data=f,
                            file_path=storage_path,
                            content_type=file.content_type,
                            metadata={
                                'submission_id': submission_id,
                                'original_filename': file.filename,
                                'uploaded_at': datetime.utcnow().isoformat()
                            }
                        )
                    
                    file_info = {
                        'filename': unique_filename,
                        'original_filename': file.filename,
                        'storage_path': storage_path,
                        'url': upload_result.get('url'),
                        'size_bytes': upload_result.get('size'),
                        'content_type': file.content_type,
                        'uploaded_at': datetime.utcnow().isoformat()
                    }
                    
                    uploaded_files.append(file_info)
                    
                    # Add to submission
                    self.repository.add_uploaded_file(submission_id, file_info)
                    
                    # Clean up temp file
                    local_path.unlink(missing_ok=True)
                    
                except Exception as e:
                    logger.error(f"Error uploading file {file.filename}: {e}")
                    errors.append({
                        'filename': file.filename,
                        'error': str(e)
                    })
            
            # Update submission status
            if uploaded_files:
                self.repository.update_status(submission_id, 'uploaded')
            
            result = {
                'submission_id': submission_id,
                'total_files': len(files),
                'successful_uploads': len(uploaded_files),
                'failed_uploads': len(errors),
                'uploaded_files': uploaded_files,
                'errors': errors
            }
            
            logger.info(
                f"Upload completed: {result['successful_uploads']}/{result['total_files']} successful"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error uploading files: {e}")
            raise
    
    def extract_data(self, submission_id: str) -> Dict[str, Any]:
        """
        Extract data from uploaded files.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            Extraction result
        """
        try:
            logger.info(f"Starting extraction for submission {submission_id}")
            
            submission = self.get_submission(submission_id)
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            # Update status
            self.repository.update_status(submission_id, 'extracting')
            
            # Get uploaded files
            if not submission.uploaded_files:
                raise ValueError("No uploaded files to extract from")
            
            # Download files to temp directory
            file_paths = []
            for file_info in submission.uploaded_files:
                storage_path = file_info['storage_path']
                local_path = self.upload_dir / file_info['filename']
                
                file_data = self.storage.download_file(storage_path)
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                
                file_paths.append(str(local_path))
            
            # Extract data
            extraction_result = self.extraction_service.extract_from_files(
                file_paths=file_paths,
                submission_id=submission_id
            )
            
            # Update submission with extracted data
            extracted_data = extraction_result.get('extracted_data', {})
            
            update_data = {}
            
            if not submission.client_name and  extracted_data.get('applicant'):
                update_data['applicant'] = Applicant.from_dict(extracted_data['applicant'])
            
            if extracted_data.get('locations'):
                update_data['locations'] = [
                    PropertyLocation.from_dict(loc) for loc in extracted_data['locations']
                ]
            
            if extracted_data.get('coverage'):
                update_data['coverage'] = Coverage.from_dict(extracted_data['coverage'])
            
            if extracted_data.get('loss_history'):
                update_data['loss_history'] = [
                    LossHistory.from_dict(loss) for loss in extracted_data['loss_history']
                ]
            
            # Save extraction metadata
            self.repository.set_extraction_metadata(
                submission_id,
                extraction_result,
                extraction_result.get('overall_confidence')
            )
            
            # Update submission
            if update_data:
                self.update_submission(submission_id, update_data)
            
            # Update status
            self.repository.update_status(submission_id, 'extracted')
            
            # Clean up temp files
            for file_path in file_paths:
                Path(file_path).unlink(missing_ok=True)
            
            logger.info(f"Extraction completed for submission {submission_id}")
            
            return extraction_result
            
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            self.repository.update_status(submission_id, 'error')
            raise
    
    def validate_data(self, submission_id: str, strict_mode: bool = False) -> Dict[str, Any]:
        """
        Validate submission data.
        
        Args:
            submission_id: Submission identifier
            strict_mode: Enable strict validation
            
        Returns:
            Validation result
        """
        try:
            logger.info(f"Starting validation for submission {submission_id}")
            
            submission = self.get_submission(submission_id)
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            # Update status
            self.repository.update_status(submission_id, 'validating')
            
            # Validate
            validation_result = self.validation_service.validate_submission(
                submission,
                strict_mode
            )
            
            # Save validation results
            errors = [e.dict() for e in validation_result.errors]
            warnings = [w.dict() for w in validation_result.warnings]
            
            self.repository.set_validation_results(
                submission_id,
                errors,
                warnings
            )
            
            # Update status
            self.repository.update_status(submission_id, 'validated')
            
            logger.info(
                f"Validation completed: {validation_result.total_errors} errors, "
                f"{validation_result.total_warnings} warnings"
            )
            
            return validation_result.dict()
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            self.repository.update_status(submission_id, 'error')
            raise
    
    def generate_forms(
        self,
        submission_id: str,
        forms: Optional[List[str]] = None,
        carrier_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate submission forms.
        
        Args:
            submission_id: Submission identifier
            forms: List of forms to generate
            carrier_name: Carrier name for carrier-specific forms
            
        Returns:
            Generation result
        """
        try:
            logger.info(f"Starting generation for submission {submission_id}")
            
            submission = self.get_submission(submission_id)
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            # Check if validated
            if not submission.is_valid:
                raise ValueError("Submission must be validated before generation")
            
            # Update status
            self.repository.update_status(submission_id, 'generating')
            
            # Generate forms
            generation_result = self.generation_service.generate_submission_package(
                submission=submission,
                forms=forms,
                carrier_name=carrier_name or submission.carrier_name
            )
            
            # Save generated file references
            for file_info in generation_result.get('generated_files', []):
                self.repository.add_generated_file(submission_id, file_info)
            
            # Update status
            self.repository.update_status(submission_id, 'completed')
            
            logger.info(f"Generation completed for submission {submission_id}")
            
            return generation_result
            
        except Exception as e:
            logger.error(f"Error generating forms: {e}")
            self.repository.update_status(submission_id, 'error')
            raise
    
    def get_download_package(self, submission_id: str) -> Dict[str, Any]:
        """
        Get download package with all generated files.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            Package information
        """
        try:
            submission = self.get_submission(submission_id)
            if not submission:
                raise ValueError(f"Submission {submission_id} not found")
            
            # Get generated files
            generated_files = self.generation_service.get_generated_files(submission_id)
            
            package = {
                'submission_id': submission_id,
                'status': submission.status,
                'applicant_name': submission.applicant.business_name if submission.applicant else None,
                'total_files': len(generated_files),
                'files': generated_files,
                'created_at': submission.created_at.isoformat(),
                'completed_at': submission.generated_at.isoformat() if submission.generated_at else None
            }
            
            return package
            
        except Exception as e:
            logger.error(f"Error getting download package: {e}")
            raise
    
    def process_submission_workflow(
        self,
        submission_id: str,
        skip_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Execute complete submission workflow.
        
        Args:
            submission_id: Submission identifier
            skip_validation: Skip validation step
            
        Returns:
            Workflow result
        """
        try:
            logger.info(f"Starting complete workflow for submission {submission_id}")
            
            workflow_result = {
                'submission_id': submission_id,
                'steps': {}
            }
            
            # Step 1: Extract
            try:
                extraction_result = self.extract_data(submission_id)
                workflow_result['steps']['extraction'] = {
                    'status': 'completed',
                    'confidence': extraction_result.get('overall_confidence')
                }
            except Exception as e:
                workflow_result['steps']['extraction'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                return workflow_result
            
            # Step 2: Validate
            if not skip_validation:
                try:
                    validation_result = self.validate_data(submission_id)
                    workflow_result['steps']['validation'] = {
                        'status': 'completed',
                        'is_valid': validation_result.get('is_valid'),
                        'errors': validation_result.get('total_errors')
                    }
                    
                    if not validation_result.get('is_valid'):
                        logger.warning("Validation failed, skipping generation")
                        return workflow_result
                        
                except Exception as e:
                    workflow_result['steps']['validation'] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    return workflow_result
            
            # Step 3: Generate
            try:
                generation_result = self.generate_forms(submission_id)
                workflow_result['steps']['generation'] = {
                    'status': 'completed',
                    'files_generated': generation_result.get('successful_forms')
                }
            except Exception as e:
                workflow_result['steps']['generation'] = {
                    'status': 'failed',
                    'error': str(e)
                }
            
            workflow_result['overall_status'] = 'completed'
            
            logger.info(f"Complete workflow finished for submission {submission_id}")
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Error in submission workflow: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check submission service health."""
        try:
            extraction_health = self.extraction_service.health_check()
            validation_health = self.validation_service.health_check()
            generation_health = self.generation_service.health_check()
            
            all_healthy = all([
                extraction_health.get('status') == 'healthy',
                validation_health.get('status') == 'healthy',
                generation_health.get('status') == 'healthy'
            ])
            
            return {
                'status': 'healthy' if all_healthy else 'degraded',
                'service': 'SubmissionService',
                'components': {
                    'extraction': extraction_health,
                    'validation': validation_health,
                    'generation': generation_health
                }
            }
            
        except Exception as e:
            logger.error(f"Submission service health check failed: {e}")
            return {
                'status': 'unhealthy',
                'service': 'SubmissionService',
                'error': str(e)
            }


# Global service instance
_submission_service: Optional[SubmissionService] = None


def get_submission_service() -> SubmissionService:
    """
    Get or create submission service singleton.
    
    Returns:
        SubmissionService instance
    """
    global _submission_service
    
    if _submission_service is None:
        _submission_service = SubmissionService()
    
    return _submission_service