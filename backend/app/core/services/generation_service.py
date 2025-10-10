"""
Generation service for orchestrating PDF generation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from app.domain.models import Submission
from app.infrastructure.pdf import get_acord_generator, get_carrier_generator
from app.infrastructure.storage import get_supabase_storage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GenerationService:
    """
    Service for orchestrating PDF generation workflow.
    
    Coordinates:
    - ACORD form generation (125, 140)
    - Carrier-specific form generation
    - File storage and URL generation
    - Batch generation
    """
    
    def __init__(self):
        """Initialize generation service."""
        self.storage = get_supabase_storage()
        self.output_dir = Path('/tmp/submitez-output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_submission_package(
        self,
        submission: Submission,
        forms: Optional[List[str]] = None,
        carrier_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete submission package.
        
        Args:
            submission: Submission entity
            forms: List of forms to generate (default: ['125', '140'])
            carrier_name: Optional carrier name for carrier-specific forms
            
        Returns:
            Generation result with file paths and URLs
        """
        generation_id = str(uuid4())
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting generation for submission {submission.id}")
            
            if forms is None:
                forms = ['125', '140']
            
            generated_files = []
            errors = []
            
            # Convert submission to data dictionary
            data = self._prepare_data(submission)
            
            # Generate ACORD forms
            for form_type in forms:
                try:
                    file_info = self.generate_acord_form(
                        data=data,
                        form_type=form_type,
                        submission_id=submission.id
                    )
                    generated_files.append(file_info)
                except Exception as e:
                    logger.error(f"Error generating ACORD {form_type}: {e}")
                    errors.append({
                        'form_type': f'ACORD {form_type}',
                        'error': str(e)
                    })
            
            # Generate carrier-specific form if requested
            if carrier_name:
                try:
                    file_info = self.generate_carrier_form(
                        data=data,
                        carrier_name=carrier_name,
                        submission_id=submission.id
                    )
                    generated_files.append(file_info)
                except Exception as e:
                    logger.error(f"Error generating carrier form: {e}")
                    errors.append({
                        'form_type': f'{carrier_name} Application',
                        'error': str(e)
                    })
            
            # Calculate result
            result = {
                'generation_id': generation_id,
                'submission_id': submission.id,
                'status': 'completed' if generated_files else 'failed',
                'total_forms': len(forms) + (1 if carrier_name else 0),
                'successful_forms': len(generated_files),
                'failed_forms': len(errors),
                'started_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'duration_seconds': (datetime.utcnow() - start_time).total_seconds(),
                'generated_files': generated_files,
                'errors': errors
            }
            
            logger.info(
                f"Generation completed: {result['successful_forms']}/{result['total_forms']} successful"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generation service: {e}")
            return {
                'generation_id': generation_id,
                'submission_id': submission.id,
                'status': 'failed',
                'error': str(e),
                'started_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat()
            }
    
    def generate_acord_form(
        self,
        data: Dict[str, Any],
        form_type: str,
        submission_id: str
    ) -> Dict[str, Any]:
        """
        Generate ACORD form.
        
        Args:
            data: Submission data
            form_type: ACORD form type ('125', '140')
            submission_id: Submission identifier
            
        Returns:
            File information dictionary
        """
        try:
            logger.info(f"Generating ACORD {form_type}")
            
            # Get ACORD generator
            generator = get_acord_generator(form_type)
            
            # Generate filename
            filename = f"ACORD_{form_type}_{submission_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            local_path = str(self.output_dir / filename)
            
            # Generate PDF
            pdf_path = generator.generate(data, local_path)
            
            # Upload to storage
            storage_path = f"submissions/{submission_id}/generated/{filename}"
            
            with open(pdf_path, 'rb') as f:
                upload_result = self.storage.upload_file(
                    file_data=f,
                    file_path=storage_path,
                    content_type='application/pdf',
                    metadata={
                        'submission_id': submission_id,
                        'form_type': f'ACORD {form_type}',
                        'generated_at': datetime.utcnow().isoformat()
                    }
                )
            
            # Get signed URL
            signed_url = self.storage.get_file_url(storage_path, expires_in=3600)
            
            file_info = {
                'form_type': f'ACORD {form_type}',
                'filename': filename,
                'local_path': pdf_path,
                'storage_path': storage_path,
                'url': signed_url,
                'size_bytes': upload_result.get('size'),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated ACORD {form_type}: {filename}")
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error generating ACORD {form_type}: {e}")
            raise
    
    def generate_carrier_form(
        self,
        data: Dict[str, Any],
        carrier_name: str,
        submission_id: str
    ) -> Dict[str, Any]:
        """
        Generate carrier-specific form.
        
        Args:
            data: Submission data
            carrier_name: Carrier name
            submission_id: Submission identifier
            
        Returns:
            File information dictionary
        """
        try:
            logger.info(f"Generating {carrier_name} carrier form")
            
            # Get carrier generator
            generator = get_carrier_generator(carrier_name)
            
            # Generate filename
            safe_carrier = carrier_name.replace(' ', '_')
            filename = f"{safe_carrier}_Application_{submission_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            local_path = str(self.output_dir / filename)
            
            # Generate PDF
            pdf_path = generator.generate(data, local_path)
            
            # Upload to storage
            storage_path = f"submissions/{submission_id}/generated/{filename}"
            
            with open(pdf_path, 'rb') as f:
                upload_result = self.storage.upload_file(
                    file_data=f,
                    file_path=storage_path,
                    content_type='application/pdf',
                    metadata={
                        'submission_id': submission_id,
                        'form_type': f'{carrier_name} Application',
                        'generated_at': datetime.utcnow().isoformat()
                    }
                )
            
            # Get signed URL
            signed_url = self.storage.get_file_url(storage_path, expires_in=3600)
            
            file_info = {
                'form_type': f'{carrier_name} Application',
                'filename': filename,
                'local_path': pdf_path,
                'storage_path': storage_path,
                'url': signed_url,
                'size_bytes': upload_result.get('size'),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated {carrier_name} form: {filename}")
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error generating carrier form: {e}")
            raise
    
    def generate_summary_report(
        self,
        submission: Submission,
        submission_id: str
    ) -> Dict[str, Any]:
        """
        Generate summary report PDF.
        
        Args:
            submission: Submission entity
            submission_id: Submission identifier
            
        Returns:
            File information dictionary
        """
        try:
            logger.info("Generating summary report")
            
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas as pdf_canvas
            
            # Generate filename
            filename = f"Summary_Report_{submission_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            local_path = str(self.output_dir / filename)
            
            # Create PDF
            c = pdf_canvas.Canvas(local_path, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, height - 72, "Submission Summary Report")
            
            # Submission details
            y = height - 120
            c.setFont("Helvetica", 12)
            
            if submission.applicant:
                c.drawString(72, y, f"Business: {submission.applicant.business_name}")
                y -= 20
            
            c.drawString(72, y, f"Submission ID: {submission.id}")
            y -= 20
            c.drawString(72, y, f"Status: {submission.status}")
            y -= 20
            c.drawString(72, y, f"Created: {submission.created_at.strftime('%Y-%m-%d')}")
            y -= 40
            
            # Statistics
            c.setFont("Helvetica-Bold", 14)
            c.drawString(72, y, "Statistics")
            y -= 25
            
            c.setFont("Helvetica", 12)
            c.drawString(72, y, f"Total Locations: {len(submission.locations)}")
            y -= 20
            c.drawString(72, y, f"Total Losses: {len(submission.loss_history)}")
            y -= 20
            c.drawString(72, y, f"Total TIV: ${submission.get_total_tiv():,.0f}")
            y -= 20
            c.drawString(72, y, f"Completeness: {submission.get_completeness_percentage()}%")
            
            c.save()
            
            # Upload to storage
            storage_path = f"submissions/{submission_id}/generated/{filename}"
            
            with open(local_path, 'rb') as f:
                upload_result = self.storage.upload_file(
                    file_data=f,
                    file_path=storage_path,
                    content_type='application/pdf',
                    metadata={
                        'submission_id': submission_id,
                        'form_type': 'Summary Report',
                        'generated_at': datetime.utcnow().isoformat()
                    }
                )
            
            signed_url = self.storage.get_file_url(storage_path, expires_in=3600)
            
            file_info = {
                'form_type': 'Summary Report',
                'filename': filename,
                'local_path': local_path,
                'storage_path': storage_path,
                'url': signed_url,
                'size_bytes': upload_result.get('size'),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated summary report: {filename}")
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise
    
    def _prepare_data(self, submission: Submission) -> Dict[str, Any]:
        """
        Prepare submission data for PDF generation.
        
        Args:
            submission: Submission entity
            
        Returns:
            Data dictionary
        """
        data = {
            'submission_id': submission.id,
            'applicant': submission.applicant.to_dict() if submission.applicant else {},
            'locations': [loc.to_dict() for loc in submission.locations],
            'coverage': submission.coverage.to_dict() if submission.coverage else {},
            'loss_history': [loss.to_dict() for loss in submission.loss_history]
        }
        
        return data
    
    def get_generated_files(self, submission_id: str) -> List[Dict[str, Any]]:
        """
        Get list of generated files for submission.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            List of file information dictionaries
        """
        try:
            prefix = f"submissions/{submission_id}/generated/"
            files = self.storage.list_files(prefix=prefix)
            
            # Add signed URLs
            for file in files:
                file['url'] = self.storage.get_file_url(file['path'], expires_in=3600)
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting generated files: {e}")
            return []
    
    def download_file(self, storage_path: str) -> bytes:
        """
        Download generated file.
        
        Args:
            storage_path: Path to file in storage
            
        Returns:
            File bytes
        """
        try:
            return self.storage.download_file(storage_path)
        except Exception as e:
            logger.error(f"Error downloading file {storage_path}: {e}")
            raise
    
    def delete_generated_files(self, submission_id: str) -> bool:
        """
        Delete all generated files for submission.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            True if successful
        """
        try:
            files = self.get_generated_files(submission_id)
            file_paths = [f['path'] for f in files]
            
            if file_paths:
                self.storage.batch_delete(file_paths)
                logger.info(f"Deleted {len(file_paths)} generated files for {submission_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting generated files: {e}")
            return False
    
    def regenerate_forms(
        self,
        submission: Submission,
        forms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Regenerate forms (delete old, generate new).
        
        Args:
            submission: Submission entity
            forms: List of forms to regenerate
            
        Returns:
            Generation result
        """
        try:
            # Delete existing generated files
            self.delete_generated_files(submission.id)
            
            # Generate new files
            return self.generate_submission_package(submission, forms)
            
        except Exception as e:
            logger.error(f"Error regenerating forms: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check generation service health."""
        try:
            storage_health = self.storage.health_check()
            
            # Check if output directory is writable
            test_file = self.output_dir / '.health_check'
            test_file.touch()
            test_file.unlink()
            output_writable = True
            
            return {
                'status': 'healthy' if storage_health.get('status') == 'healthy' else 'degraded',
                'service': 'GenerationService',
                'components': {
                    'storage': storage_health,
                    'output_directory': {
                        'path': str(self.output_dir),
                        'writable': output_writable
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Generation service health check failed: {e}")
            return {
                'status': 'unhealthy',
                'service': 'GenerationService',
                'error': str(e)
            }


# Global service instance
_generation_service: Optional[GenerationService] = None


def get_generation_service() -> GenerationService:
    """
    Get or create generation service singleton.
    
    Returns:
        GenerationService instance
    """
    global _generation_service
    
    if _generation_service is None:
        _generation_service = GenerationService()
    
    return _generation_service