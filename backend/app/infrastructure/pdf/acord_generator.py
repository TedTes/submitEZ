"""
ACORD form PDF generator for insurance submissions.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from app.infrastructure.pdf.base_pdf_generator import BasePDFGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ACORDGenerator(BasePDFGenerator):
    """
    Generator for ACORD forms (125, 140, etc.).
    
    Currently generates ACORD-style forms using ReportLab.
    Can be enhanced to fill actual ACORD PDF templates using fillpdf.
    """
    
    FORM_TYPES = {
        '125': 'Commercial Insurance Application',
        '140': 'Property Section',
        '126': 'Commercial General Liability Section',
        '130': 'Workers Compensation Application'
    }
    
    def __init__(self, form_type: str = '125'):
        """
        Initialize ACORD generator.
        
        Args:
            form_type: ACORD form type (125, 140, etc.)
        """
        super().__init__()
        
        if form_type not in self.FORM_TYPES:
            raise ValueError(f"Unsupported ACORD form type: {form_type}")
        
        self.form_type = form_type
        self.form_name = self.FORM_TYPES[form_type]
    
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate ACORD PDF from data.
        
        Args:
            data: Submission data
            output_path: Optional output file path
            
        Returns:
            Path to generated PDF
        """
        try:
            # Generate PDF bytes
            pdf_bytes = self.generate_to_bytes(data)
            
            # Determine output path
            if output_path is None:
                filename = self.get_output_filename(data, prefix=f"ACORD_{self.form_type}")
                output_path = str(self.output_dir / filename)
            
            # Save to file
            return self.save_to_file(pdf_bytes, output_path)
            
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
            # Validate data
            is_valid, errors = self.validate_data(data)
            if not is_valid:
                logger.warning(f"Data validation warnings: {errors}")
            
            # Generate based on form type
            if self.form_type == '125':
                return self._generate_acord_125(data)
            elif self.form_type == '140':
                return self._generate_acord_140(data)
            else:
                raise NotImplementedError(f"Form {self.form_type} not yet implemented")
            
        except Exception as e:
            logger.error(f"Error generating ACORD PDF bytes: {e}")
            raise
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate data for ACORD form.
        
        Args:
            data: Submission data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for applicant
        if 'applicant' not in data or not data['applicant']:
            errors.append("Missing applicant information")
        else:
            applicant = data['applicant']
            if not applicant.get('business_name'):
                errors.append("Missing business name")
        
        # Check for locations (for property forms)
        if self.form_type in ['125', '140']:
            if 'locations' not in data or not data['locations']:
                errors.append("Missing property locations")
        
        # Check for coverage
        if 'coverage' not in data or not data['coverage']:
            errors.append("Missing coverage information")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    def get_required_fields(self) -> list[str]:
        """Get required fields for ACORD form."""
        base_fields = ['applicant', 'coverage']
        
        if self.form_type in ['125', '140']:
            base_fields.append('locations')
        
        return base_fields
    
    def _generate_acord_125(self, data: Dict[str, Any]) -> bytes:
        """
        Generate ACORD 125 - Commercial Insurance Application.
        
        Args:
            data: Submission data
            
        Returns:
            PDF bytes
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, "ACORD 125")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.3*inch, "Commercial Insurance Application")
        
        # Date
        c.setFont("Helvetica", 10)
        today = datetime.now().strftime("%m/%d/%Y")
        c.drawString(width - 2.5*inch, height - 1*inch, f"Date: {today}")
        
        y_position = height - 2*inch
        
        # Applicant Information
        applicant = data.get('applicant', {})
        self._draw_section(c, y_position, "APPLICANT INFORMATION")
        y_position -= 0.3*inch
        
        self._draw_field(c, 1*inch, y_position, "Business Name:", applicant.get('business_name', ''))
        y_position -= 0.25*inch
        
        if applicant.get('dba_name'):
            self._draw_field(c, 1*inch, y_position, "DBA:", applicant.get('dba_name', ''))
            y_position -= 0.25*inch
        
        # Address
        mailing = f"{applicant.get('mailing_address_line1', '')}"
        if applicant.get('mailing_address_line2'):
            mailing += f", {applicant.get('mailing_address_line2')}"
        self._draw_field(c, 1*inch, y_position, "Mailing Address:", mailing)
        y_position -= 0.25*inch
        
        city_state_zip = f"{applicant.get('mailing_city', '')}, {applicant.get('mailing_state', '')} {applicant.get('mailing_zip', '')}"
        self._draw_field(c, 1*inch, y_position, "", city_state_zip)
        y_position -= 0.25*inch
        
        # Contact Info
        self._draw_field(c, 1*inch, y_position, "Phone:", applicant.get('phone', ''))
        self._draw_field(c, 4*inch, y_position, "Email:", applicant.get('email', ''))
        y_position -= 0.25*inch
        
        # FEIN and NAICS
        self._draw_field(c, 1*inch, y_position, "FEIN:", applicant.get('fein', ''))
        self._draw_field(c, 4*inch, y_position, "NAICS:", applicant.get('naics_code', ''))
        y_position -= 0.5*inch
        
        # Property Locations
        locations = data.get('locations', [])
        if locations:
            self._draw_section(c, y_position, "PROPERTY LOCATIONS")
            y_position -= 0.3*inch
            
            for i, location in enumerate(locations[:3], 1):  # Limit to 3 for space
                loc_num = location.get('location_number', str(i))
                address = f"{location.get('address_line1', '')}, {location.get('city', '')}, {location.get('state', '')}"
                self._draw_field(c, 1*inch, y_position, f"Location {loc_num}:", address)
                y_position -= 0.2*inch
                
                # Property values
                building_val = location.get('building_value', 0)
                contents_val = location.get('contents_value', 0)
                values = f"Building: ${building_val:,.0f}  Contents: ${contents_val:,.0f}"
                self._draw_field(c, 1.5*inch, y_position, "", values)
                y_position -= 0.3*inch
            
            y_position -= 0.2*inch
        
        # Coverage Information
        coverage = data.get('coverage', {})
        if coverage and y_position > 2*inch:
            self._draw_section(c, y_position, "COVERAGE REQUESTED")
            y_position -= 0.3*inch
            
            eff_date = coverage.get('effective_date', '')
            exp_date = coverage.get('expiration_date', '')
            self._draw_field(c, 1*inch, y_position, "Policy Period:", f"{eff_date} to {exp_date}")
            y_position -= 0.3*inch
            
            # Limits
            if coverage.get('building_limit'):
                self._draw_field(c, 1*inch, y_position, "Building Limit:", f"${coverage.get('building_limit'):,.0f}")
                y_position -= 0.2*inch
            
            if coverage.get('contents_limit'):
                self._draw_field(c, 1*inch, y_position, "Contents Limit:", f"${coverage.get('contents_limit'):,.0f}")
                y_position -= 0.2*inch
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, 0.5*inch, "ACORD 125 (2016/03)")
        c.drawString(width - 3*inch, 0.5*inch, "Generated by SubmitEZ")
        
        c.save()
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated ACORD 125 PDF ({len(pdf_bytes)} bytes)")
        
        return pdf_bytes
    
    def _generate_acord_140(self, data: Dict[str, Any]) -> bytes:
        """
        Generate ACORD 140 - Property Section.
        
        Args:
            data: Submission data
            
        Returns:
            PDF bytes
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, "ACORD 140")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.3*inch, "Property Section")
        
        y_position = height - 2*inch
        
        # Applicant
        applicant = data.get('applicant', {})
        self._draw_field(c, 1*inch, y_position, "Named Insured:", applicant.get('business_name', ''))
        y_position -= 0.5*inch
        
        # Property Schedule
        locations = data.get('locations', [])
        if locations:
            self._draw_section(c, y_position, "PROPERTY SCHEDULE")
            y_position -= 0.3*inch
            
            # Table headers
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1*inch, y_position, "Loc")
            c.drawString(1.5*inch, y_position, "Address")
            c.drawString(4*inch, y_position, "Building")
            c.drawString(5*inch, y_position, "Contents")
            c.drawString(6*inch, y_position, "BI")
            y_position -= 0.2*inch
            
            c.setFont("Helvetica", 8)
            
            for i, location in enumerate(locations, 1):
                loc_num = location.get('location_number', str(i))
                address = f"{location.get('city', '')}, {location.get('state', '')}"
                building = location.get('building_value', 0)
                contents = location.get('contents_value', 0)
                bi = location.get('business_income_value', 0)
                
                c.drawString(1*inch, y_position, str(loc_num))
                c.drawString(1.5*inch, y_position, address[:30])
                c.drawString(4*inch, y_position, f"${building:,.0f}")
                c.drawString(5*inch, y_position, f"${contents:,.0f}")
                c.drawString(6*inch, y_position, f"${bi:,.0f}")
                
                y_position -= 0.2*inch
                
                if y_position < 2*inch:
                    break
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(1*inch, 0.5*inch, "ACORD 140 (2008/01)")
        c.drawString(width - 3*inch, 0.5*inch, "Generated by SubmitEZ")
        
        c.save()
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated ACORD 140 PDF ({len(pdf_bytes)} bytes)")
        
        return pdf_bytes
    
    def _draw_section(self, c: canvas.Canvas, y: float, title: str):
        """Draw section header."""
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, y, title)
        c.line(1*inch, y - 0.05*inch, 7.5*inch, y - 0.05*inch)
        c.setFont("Helvetica", 10)
    
    def _draw_field(self, c: canvas.Canvas, x: float, y: float, label: str, value: str):
        """Draw field label and value."""
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 9)
        label_width = c.stringWidth(label, "Helvetica-Bold", 9)
        c.drawString(x + label_width + 0.1*inch, y, str(value))


# Global ACORD generator instances
_acord_generators: Dict[str, ACORDGenerator] = {}


def get_acord_generator(form_type: str = '125') -> ACORDGenerator:
    """
    Get or create ACORD generator for form type.
    
    Args:
        form_type: ACORD form type (125, 140, etc.)
        
    Returns:
        ACORDGenerator instance
    """
    global _acord_generators
    
    if form_type not in _acord_generators:
        _acord_generators[form_type] = ACORDGenerator(form_type)
    
    return _acord_generators[form_type]