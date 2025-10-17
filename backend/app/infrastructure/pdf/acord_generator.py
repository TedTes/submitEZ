"""
ACORD form PDF generator for insurance submissions.

Refactored to use template-based filling with fillpdf instead of ReportLab generation.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import tempfile

from app.infrastructure.pdf.base_pdf_generator import BasePDFGenerator
from app.infrastructure.pdf.fillpdf_utils import (
    fill_acord_template,
    get_template_path,
    list_pdf_fields
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ACORDGenerator(BasePDFGenerator):
    """
    Generator for ACORD forms (125, 126, 130, 140).
    
    Uses actual ACORD PDF templates from templates/ folder and fills them
    with extracted data using canonical field mappings.
    """
    
    FORM_TYPES = {
        '125': 'Commercial Insurance Application',
        '126': 'Commercial General Liability Section',
        '130': 'Workers Compensation Application',
        '140': 'Property Section'
    }
    
    def __init__(self, form_type: str = '125'):
        """
        Initialize ACORD generator.
        
        Args:
            form_type: ACORD form type ('125', '126', '130', '140')
        """
        super().__init__()
        
        if form_type not in self.FORM_TYPES:
            raise ValueError(
                f"Unsupported ACORD form type: {form_type}. "
                f"Supported: {list(self.FORM_TYPES.keys())}"
            )
        
        self.form_type = form_type
        self.form_name = self.FORM_TYPES[form_type]
        
        # Verify template exists
        template_path = get_template_path(form_type)
        if not template_path.exists():
            logger.warning(
                f"Template not found: {template_path}. "
                f"Please add ACORD_{form_type}.pdf to backend/templates/"
            )
    
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate ACORD PDF from data by filling template.
        
        Args:
            data: Submission data with canonical keys
            output_path: Optional output file path
            
        Returns:
            Path to generated PDF
        """
        try:
            # Validate template exists
            template_path = get_template_path(self.form_type)
            if not template_path.exists():
                raise FileNotFoundError(
                    f"ACORD {self.form_type} template not found: {template_path}. "
                    f"Please add it to backend/templates/"
                )
            
            # Determine output path
            if output_path is None:
                filename = self.get_output_filename(
                    data, 
                    prefix=f"ACORD_{self.form_type}"
                )
                output_path = str(self.output_dir / filename)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Fill template
            logger.info(f"Generating ACORD {self.form_type}: {output_path}")
            filled_path = fill_acord_template(
                form_type=self.form_type,
                data=data,
                output_path=output_path
            )
            
            logger.info(f"Successfully generated ACORD {self.form_type}")
            return filled_path
            
        except FileNotFoundError as e:
            logger.error(f"Template file error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating ACORD {self.form_type}: {e}")
            raise
    
    def generate_to_bytes(self, data: Dict[str, Any]) -> bytes:
        """
        Generate ACORD PDF as bytes.
        
        Args:
            data: Submission data
            
        Returns:
            PDF content as bytes
        """
        try:
            # Generate to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=f'_acord_{self.form_type}.pdf',
                delete=False
            ) as tmp_file:
                tmp_path = tmp_file.name
            
            # Generate PDF
            self.generate(data, tmp_path)
            
            # Read bytes
            with open(tmp_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Clean up temp file
            try:
                Path(tmp_path).unlink()
            except:
                pass
            
            logger.info(f"Generated ACORD {self.form_type} ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating ACORD PDF bytes: {e}")
            raise
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate data before PDF generation.
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Get required fields for this form type
        required_fields = self._get_form_required_fields()
        
        # Check required fields
        for field_path in required_fields:
            if not self._has_nested_value(data, field_path):
                errors.append(f"Missing required field: {field_path}")
        
        # Form-specific validation
        if self.form_type == '125':
            errors.extend(self._validate_acord_125(data))
        elif self.form_type == '126':
            errors.extend(self._validate_acord_126(data))
        elif self.form_type == '130':
            errors.extend(self._validate_acord_130(data))
        elif self.form_type == '140':
            errors.extend(self._validate_acord_140(data))
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Data validation failed: {errors}")
        
        return is_valid, errors
    
    def get_required_fields(self) -> list[str]:
        """
        Get list of required fields for this ACORD form.
        
        Returns:
            List of required field paths in canonical format
        """
        return self._get_form_required_fields()
    
    def _get_form_required_fields(self) -> list[str]:
        """Get required fields based on form type."""
        base_fields = [
            'applicant.business_name',
            'coverage.effective_date',
        ]
        
        if self.form_type == '125':
            return base_fields + [
                'applicant.mailing.line1',
                'applicant.mailing.city',
                'applicant.mailing.state',
                'applicant.mailing.postal',
            ]
        elif self.form_type == '126':
            return base_fields + [
                'limits.general_aggregate',
                'limits.each_occurrence',
            ]
        elif self.form_type == '130':
            return base_fields + [
                'applicant.fein',
            ]
        elif self.form_type == '140':
            return base_fields + [
                'locations',  # At least one location required
            ]
        
        return base_fields
    
    def _validate_acord_125(self, data: Dict[str, Any]) -> list[str]:
        """Validate ACORD 125 specific requirements."""
        errors = []
        
        # Check dates
        coverage = data.get('coverage', {})
        eff_date = coverage.get('effective_date')
        exp_date = coverage.get('expiration_date')
        
        if eff_date and exp_date:
            if isinstance(eff_date, datetime) and isinstance(exp_date, datetime):
                if exp_date <= eff_date:
                    errors.append("Expiration date must be after effective date")
        
        return errors
    
    def _validate_acord_126(self, data: Dict[str, Any]) -> list[str]:
        """Validate ACORD 126 specific requirements."""
        errors = []
        
        # Check that at least one coverage type is selected
        coverage = data.get('coverage', {})
        if not coverage.get('occurrence') and not coverage.get('claims_made'):
            errors.append("Must select either Occurrence or Claims Made coverage")
        
        # Check limits are positive
        limits = data.get('limits', {})
        for limit_name in ['general_aggregate', 'each_occurrence']:
            value = limits.get(limit_name)
            if value is not None:
                try:
                    if float(value) <= 0:
                        errors.append(f"Limit {limit_name} must be positive")
                except (ValueError, TypeError):
                    errors.append(f"Invalid limit value for {limit_name}")
        
        return errors
    
    def _validate_acord_130(self, data: Dict[str, Any]) -> list[str]:
        """Validate ACORD 130 specific requirements."""
        errors = []
        
        # FEIN format check
        applicant = data.get('applicant', {})
        fein = applicant.get('fein', '')
        if fein and not self._is_valid_fein(fein):
            errors.append("Invalid FEIN format (should be XX-XXXXXXX)")
        
        return errors
    
    def _validate_acord_140(self, data: Dict[str, Any]) -> list[str]:
        """Validate ACORD 140 specific requirements."""
        errors = []
        
        # Check locations exist
        locations = data.get('locations', [])
        if not locations:
            errors.append("At least one property location is required")
        
        # Validate each location
        for i, location in enumerate(locations):
            if not isinstance(location, dict):
                continue
            
            # Check required location fields
            if not location.get('city'):
                errors.append(f"Location {i+1}: city is required")
            if not location.get('state'):
                errors.append(f"Location {i+1}: state is required")
        
        return errors
    
    def _has_nested_value(self, data: Dict[str, Any], path: str) -> bool:
        """Check if nested value exists and is not None/empty."""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if not isinstance(value, dict):
                return False
            value = value.get(key)
            if value is None:
                return False
        
        # Check for empty strings/lists
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
        
        return True
    
    def _is_valid_fein(self, fein: str) -> bool:
        """Check if FEIN is in valid format (XX-XXXXXXX)."""
        import re
        pattern = r'^\d{2}-\d{7}$'
        return bool(re.match(pattern, fein))
    
    def list_template_fields(self) -> Dict[str, Any]:
        """
        List all fields in the ACORD template PDF.
        
        Useful for debugging and verifying mappings.
        
        Returns:
            Dictionary of field names and properties
        """
        try:
            return list_pdf_fields(self.form_type)
        except Exception as e:
            logger.error(f"Error listing template fields: {e}")
            return {}


# -----------------------------------------------------------------------------
# Global Generator Registry
# -----------------------------------------------------------------------------

_acord_generators: Dict[str, ACORDGenerator] = {}


def get_acord_generator(form_type: str = '125') -> ACORDGenerator:
    """
    Get or create ACORD generator for form type.
    
    Args:
        form_type: ACORD form type ('125', '126', '130', '140')
        
    Returns:
        ACORDGenerator instance
    """
    global _acord_generators
    
    if form_type not in _acord_generators:
        _acord_generators[form_type] = ACORDGenerator(form_type)
    
    return _acord_generators[form_type]


def clear_generator_cache():
    """Clear the generator cache (useful for testing)."""
    global _acord_generators
    _acord_generators.clear()