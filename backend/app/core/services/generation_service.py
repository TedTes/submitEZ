"""
Generation service for orchestrating PDF generation.

Refactored to support:
- Intelligent form selection based on submission data
- Canonical data structure transformation
- Template-based PDF filling
- Better error handling and reporting
"""

from typing import Optional, List, Dict, Any, Set
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
    - Intelligent form selection based on data
    - ACORD form generation (125, 126, 130, 140)
    - Carrier-specific form generation
    - File storage and URL generation
    - Batch generation and error handling
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
        carrier_name: Optional[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete submission package.
        
        Args:
            submission: Submission entity
            forms: List of forms to generate (e.g., ['125', '126'])
                   If None and auto_detect=True, intelligently selects forms
            carrier_name: Optional carrier name for carrier-specific forms
            auto_detect: Automatically detect which forms to generate based on data
            
        Returns:
            Generation result with file paths and URLs
        """
        generation_id = str(uuid4())
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting generation for submission {submission.id}")
            
            # Convert submission to canonical data structure
            data = self._prepare_canonical_data(submission)
            
            # Determine which forms to generate
            if forms is None and auto_detect:
                forms = self._detect_required_forms(data, submission)
                logger.info(f"Auto-detected forms: {forms}")
            elif forms is None:
                # Default forms
                forms = ['125']
            
            generated_files = []
            errors = []
            
            # Generate ACORD forms
            for form_type in forms:
                try:
                    file_info = self.generate_acord_form(
                        data=data,
                        form_type=form_type,
                        submission=submission
                    )
                    generated_files.append(file_info)
                except Exception as e:
                    logger.error(f"Error generating ACORD {form_type}: {e}")
                    errors.append({
                        'form_type': f'ACORD {form_type}',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Generate carrier-specific form if requested
            if carrier_name:
                try:
                    file_info = self.generate_carrier_form(
                        data=data,
                        carrier_name=carrier_name,
                        submission=submission
                    )
                    generated_files.append(file_info)
                except Exception as e:
                    logger.error(f"Error generating carrier form: {e}")
                    errors.append({
                        'form_type': f'{carrier_name} Application',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
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
        submission: Submission
    ) -> Dict[str, Any]:
        """
        Generate ACORD form.
        
        Args:
            data: Canonical data structure
            form_type: ACORD form type ('125', '126', '130', '140')
            submission: Submission entity
            
        Returns:
            File information dictionary
        """
        try:
            logger.info(f"Generating ACORD {form_type} for submission {submission.id}")
            
            # Get ACORD generator
            generator = get_acord_generator(form_type)
            
            # Validate data before generation
            is_valid, validation_errors = generator.validate_data(data)
            if not is_valid:
                logger.warning(
                    f"Data validation warnings for ACORD {form_type}: {validation_errors}"
                )
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ACORD_{form_type}_{submission.id[:8]}_{timestamp}.pdf"
            local_path = str(self.output_dir / filename)
            
            # Generate PDF
            pdf_path = generator.generate(data, local_path)
            
            # Upload to storage
            storage_path = self._get_storage_path(submission, filename)
            
            with open(pdf_path, 'rb') as f:
                upload_result = self.storage.upload_file(
                    file_data=f,
                    file_path=storage_path,
                    content_type='application/pdf',
                    metadata={
                        'submission_id': submission.id,
                        'form_type': f'ACORD {form_type}',
                        'generated_at': datetime.utcnow().isoformat(),
                        'validation_warnings': len(validation_errors) if validation_errors else 0
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
                'generated_at': datetime.utcnow().isoformat(),
                'validation_warnings': validation_errors if validation_errors else []
            }
            
            logger.info(f"Successfully generated ACORD {form_type}: {filename}")
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error generating ACORD {form_type}: {e}")
            raise
    
    def generate_carrier_form(
        self,
        data: Dict[str, Any],
        carrier_name: str,
        submission: Submission
    ) -> Dict[str, Any]:
        """
        Generate carrier-specific form.
        
        Args:
            data: Canonical data structure
            carrier_name: Carrier name
            submission: Submission entity
            
        Returns:
            File information dictionary
        """
        try:
            logger.info(f"Generating {carrier_name} form for submission {submission.id}")
            
            # Get carrier generator
            generator = get_carrier_generator(carrier_name)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_carrier = carrier_name.replace(' ', '_')
            filename = f"{safe_carrier}_Application_{submission.id[:8]}_{timestamp}.pdf"
            local_path = str(self.output_dir / filename)
            
            # Generate PDF
            pdf_path = generator.generate(data, local_path)
            
            # Upload to storage
            storage_path = self._get_storage_path(submission, filename)
            
            with open(pdf_path, 'rb') as f:
                upload_result = self.storage.upload_file(
                    file_data=f,
                    file_path=storage_path,
                    content_type='application/pdf',
                    metadata={
                        'submission_id': submission.id,
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
            
            logger.info(f"Successfully generated {carrier_name} form: {filename}")
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error generating carrier form: {e}")
            raise
    
    def _detect_required_forms(
        self,
        data: Dict[str, Any],
        submission: Submission
    ) -> List[str]:
        """
        Intelligently detect which ACORD forms are needed based on data.
        
        Args:
            data: Canonical data structure
            submission: Submission entity
            
        Returns:
            List of form types to generate
        """
        forms: Set[str] = set()
        
        # Always include ACORD 125 (Commercial Application)
        forms.add('125')
        
        # Check for General Liability data
        if self._has_gl_data(data):
            forms.add('126')
            logger.info("Detected General Liability data → adding ACORD 126")
        
        # Check for Workers Compensation data
        if self._has_wc_data(data):
            forms.add('130')
            logger.info("Detected Workers Comp data → adding ACORD 130")
        
        # Check for Property data
        if self._has_property_data(data):
            forms.add('140')
            logger.info("Detected Property data → adding ACORD 140")
        
        return sorted(list(forms))
    
    def _has_gl_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains General Liability information."""
        # Check for GL-specific fields
        limits = data.get('limits', {})
        coverage = data.get('coverage', {})
        
        gl_indicators = [
            'general_aggregate' in limits,
            'products_aggregate' in limits,
            'each_occurrence' in limits,
            'occurrence' in coverage,
            'claims_made' in coverage,
            'hazards' in data and len(data.get('hazards', [])) > 0
        ]
        
        return any(gl_indicators)
    
    def _has_wc_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains Workers Compensation information."""
        # Check for WC-specific fields
        wc_indicators = [
            'payroll' in data,
            'employee_count' in data.get('applicant', {}),
            'class_codes' in data and any('payroll' in str(cc).lower() for cc in data.get('class_codes', []))
        ]
        
        return any(wc_indicators)
    
    def _has_property_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains Property information."""
        # Check for property-specific fields
        locations = data.get('locations', [])
        
        if not locations:
            return False
        
        # Check if locations have property values
        for location in locations:
            if isinstance(location, dict):
                property_indicators = [
                    'building_value' in location,
                    'contents_value' in location,
                    'business_income_value' in location,
                    'construction_type' in location,
                    'protection_class' in location
                ]
                if any(property_indicators):
                    return True
        
        return False
    
    def _prepare_canonical_data(self, submission: Submission) -> Dict[str, Any]:
        """
        Transform submission entity to canonical data structure.
        
        Args:
            submission: Submission entity
            
        Returns:
            Canonical data dictionary matching field mappings
        """
        # Extract applicant data
        applicant_data = self._extract_applicant_data(submission)
        
        # Extract coverage data
        coverage_data = self._extract_coverage_data(submission)
        
        # Extract limits data
        limits_data = self._extract_limits_data(submission)
        
        # Extract locations data
        locations_data = self._extract_locations_data(submission)
        
        # Extract hazards/classifications data
        hazards_data = self._extract_hazards_data(submission)
        
        # Compile canonical structure
        canonical_data = {
            'applicant': applicant_data,
            'coverage': coverage_data,
            'limits': limits_data,
            'locations': locations_data,
            'hazards': hazards_data,
            'broker': self._extract_broker_data(submission),
            'signatures': self._extract_signatures_data(submission),
            'metadata': {
                'submission_id': submission.id,
                'extracted_at': submission.extracted_at.isoformat() if submission.extracted_at else None,
                'client_name': submission.client_name
            }
        }
        
        logger.debug(f"Prepared canonical data with {len(canonical_data)} top-level keys")
        
        return canonical_data
    
    def _extract_applicant_data(self, submission: Submission) -> Dict[str, Any]:
        """Extract applicant data in canonical format."""
        applicant = submission.applicant
        
        if not applicant:
            return {}
        
        return {
            'business_name': applicant.business_name,
            'dba_name': applicant.dba_name,
            'mailing': {
                'line1': applicant.mailing_address_line1,
                'line2': applicant.mailing_address_line2,
                'city': applicant.mailing_city,
                'state': applicant.mailing_state,
                'postal': applicant.mailing_zip
            },
            'physical': {
                'line1': applicant.physical_address_line1,
                'line2': applicant.physical_address_line2,
                'city': applicant.physical_city,
                'state': applicant.physical_state,
                'postal': applicant.physical_zip
            } if applicant.physical_address_line1 else None,
            'fein': applicant.fein,
            'year_established': applicant.year_established,
            'entity_type': applicant.entity_type,
            'website': applicant.website,
            'contact_name': applicant.contact_name,
            'contact_phone': applicant.contact_phone,
            'contact_email': applicant.contact_email,
            'description': applicant.business_description
        }
    
    def _extract_coverage_data(self, submission: Submission) -> Dict[str, Any]:
        """Extract coverage data in canonical format."""
        coverage = submission.coverage
        
        if not coverage:
            return {}
        
        return {
            'effective_date': coverage.effective_date,
            'expiration_date': coverage.expiration_date,
            'occurrence': coverage.coverage_type == 'occurrence' if hasattr(coverage, 'coverage_type') else None,
            'claims_made': coverage.coverage_type == 'claims_made' if hasattr(coverage, 'coverage_type') else None
        }
    
    def _extract_limits_data(self, submission: Submission) -> Dict[str, Any]:
        """Extract limits data in canonical format."""
        coverage = submission.coverage
        
        if not coverage:
            return {}
        
        return {
            'general_aggregate': getattr(coverage, 'general_aggregate', None),
            'products_aggregate': getattr(coverage, 'products_aggregate', None),
            'personal_adv_injury': getattr(coverage, 'personal_advertising_injury', None),
            'each_occurrence': getattr(coverage, 'each_occurrence', None),
            'damage_to_premises': getattr(coverage, 'fire_damage', None),
            'medical_expense': getattr(coverage, 'medical_expense', None)
        }
    
    def _extract_locations_data(self, submission: Submission) -> List[Dict[str, Any]]:
        """Extract locations data in canonical format."""
        locations = submission.locations or []
        
        return [
            {
                'location_number': loc.location_number,
                'address': {
                    'line1': loc.address_line1,
                    'line2': loc.address_line2,
                    'city': loc.city,
                    'state': loc.state,
                    'postal': loc.zip_code
                },
                'building_value': loc.building_value,
                'contents_value': loc.contents_value,
                'business_income_value': loc.business_income_value,
                'construction_type': loc.construction_type,
                'year_built': loc.year_built,
                'protection_class': loc.protection_class,
                'occupancy': loc.occupancy
            }
            for loc in locations
            if loc
        ]
    
    def _extract_hazards_data(self, submission: Submission) -> List[Dict[str, Any]]:
        """Extract hazards/classifications data in canonical format."""
        # This would come from extracted data or manual entry
        # For now, return empty list
        return []
    
    def _extract_broker_data(self, submission: Submission) -> Dict[str, Any]:
        """Extract broker data in canonical format."""
        return {
            'name': getattr(submission, 'broker_name', None),
            'contact': getattr(submission, 'broker_contact', None),
            'email': getattr(submission, 'broker_email', None),
            'phone': getattr(submission, 'broker_phone', None)
        }
    
    def _extract_signatures_data(self, submission: Submission) -> Dict[str, Any]:
        """Extract signature data in canonical format."""
        return {
            'producer': {
                'name': getattr(submission, 'producer_name', None),
                'date': datetime.utcnow()
            },
            'insured': {
                'name': submission.applicant.business_name if submission.applicant else None,
                'date': datetime.utcnow()
            }
        }
    
    def _get_storage_path(self, submission: Submission, filename: str) -> str:
        """
        Get storage path for generated file.
        
        Args:
            submission: Submission entity
            filename: File name
            
        Returns:
            Storage path string
        """
        user_id = submission.user_id or 'default-user'
        project_name = submission.client_name or submission.id
        safe_project = project_name.lower().replace(' ', '-')[:50]
        
        return f"{user_id}/projects/{safe_project}/generated/{filename}"
    
    def get_generated_files(self, submission_id: str) -> List[Dict[str, Any]]:
        """
        Get list of generated files for submission.
        
        Args:
            submission_id: Submission identifier
            
        Returns:
            List of file information dictionaries
        """
        # This would query storage or database for generated files
        # Implementation depends on how you track generated files
        logger.info(f"Retrieving generated files for submission {submission_id}")
        return []
    
    def regenerate_forms(
        self,
        submission: Submission,
        forms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Regenerate forms (useful after data corrections).
        
        Args:
            submission: Submission entity
            forms: List of forms to regenerate (None = auto-detect)
            
        Returns:
            Generation result
        """
        logger.info(f"Regenerating forms for submission {submission.id}")
        return self.generate_submission_package(submission, forms, auto_detect=True)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check generation service health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check output directory
            output_dir_exists = self.output_dir.exists()
            
            # Check storage connection
            storage_healthy = self.storage.health_check() if hasattr(self.storage, 'health_check') else True
            
            # Check template availability
            template_dir = Path(__file__).parent.parent.parent.parent / 'templates'
            templates_exist = template_dir.exists()
            
            available_templates = []
            if templates_exist:
                available_templates = [
                    f.stem for f in template_dir.glob('ACORD_*.pdf')
                ]
            
            is_healthy = output_dir_exists and storage_healthy and len(available_templates) > 0
            
            return {
                'status': 'healthy' if is_healthy else 'degraded',
                'output_dir': str(self.output_dir),
                'output_dir_exists': output_dir_exists,
                'storage_connected': storage_healthy,
                'templates_available': available_templates,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Global service instance
_generation_service: Optional[GenerationService] = None


def get_generation_service() -> GenerationService:
    """Get or create generation service singleton."""
    global _generation_service
    if _generation_service is None:
        _generation_service = GenerationService()
    return _generation_service