"""
Carrier-specific PDF generator for custom insurance forms.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.infrastructure.pdf.base_pdf_generator import BasePDFGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CarrierGenerator(BasePDFGenerator):
    """
    Generator for carrier-specific application forms.
    
    Creates customizable PDFs for different insurance carriers
    with their specific requirements and branding.
    """
    
    def __init__(self, carrier_name: str = "Generic"):
        """
        Initialize carrier generator.
        
        Args:
            carrier_name: Name of insurance carrier
        """
        super().__init__()
        self.carrier_name = carrier_name
    
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate carrier-specific PDF from data.
        
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
                filename = self.get_output_filename(
                    data,
                    prefix=f"{self.carrier_name.replace(' ', '_')}_Application"
                )
                output_path = str(self.output_dir / filename)
            
            # Save to file
            return self.save_to_file(pdf_bytes, output_path)
            
        except Exception as e:
            logger.error(f"Error generating carrier PDF for {self.carrier_name}: {e}")
            raise
    
    def generate_to_bytes(self, data: Dict[str, Any]) -> bytes:
        """
        Generate carrier PDF as bytes.
        
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
            
            # Generate comprehensive application
            return self._generate_application(data)
            
        except Exception as e:
            logger.error(f"Error generating carrier PDF bytes: {e}")
            raise
    
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate data for carrier form.
        
        Args:
            data: Submission data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for applicant
        if 'applicant' not in data or not data['applicant']:
            errors.append("Missing applicant information")
        
        # Check for locations
        if 'locations' not in data or not data['locations']:
            errors.append("Missing property locations")
        
        # Check for coverage
        if 'coverage' not in data or not data['coverage']:
            errors.append("Missing coverage information")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    def get_required_fields(self) -> list[str]:
        """Get required fields for carrier form."""
        return ['applicant', 'locations', 'coverage']
    
    def _generate_application(self, data: Dict[str, Any]) -> bytes:
        """
        Generate comprehensive carrier application.
        
        Args:
            data: Submission data
            
        Returns:
            PDF bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        title = Paragraph(
            f"{self.carrier_name}<br/>Commercial Property Application",
            title_style
        )
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Date
        date_text = f"Application Date: {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Applicant Information
        applicant = data.get('applicant', {})
        story.append(Paragraph("APPLICANT INFORMATION", heading_style))
        
        applicant_data = [
            ['Business Name:', applicant.get('business_name', '')],
            ['DBA:', applicant.get('dba_name', 'N/A')],
            ['FEIN:', applicant.get('fein', '')],
            ['NAICS Code:', applicant.get('naics_code', '')],
            ['Business Type:', applicant.get('business_type', '')],
            ['Years in Business:', str(applicant.get('years_in_business', ''))],
        ]
        
        applicant_table = Table(applicant_data, colWidths=[2*inch, 4*inch])
        applicant_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(applicant_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Contact Information
        contact_data = [
            ['Contact Name:', applicant.get('contact_name', '')],
            ['Phone:', applicant.get('phone', '')],
            ['Email:', applicant.get('email', '')],
        ]
        
        contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
        contact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(contact_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Mailing Address
        mailing = f"{applicant.get('mailing_address_line1', '')}"
        if applicant.get('mailing_address_line2'):
            mailing += f", {applicant.get('mailing_address_line2')}"
        mailing += f"<br/>{applicant.get('mailing_city', '')}, {applicant.get('mailing_state', '')} {applicant.get('mailing_zip', '')}"
        
        address_data = [
            ['Mailing Address:', Paragraph(mailing, styles['Normal'])]
        ]
        
        address_table = Table(address_data, colWidths=[2*inch, 4*inch])
        address_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(address_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Property Locations
        locations = data.get('locations', [])
        if locations:
            story.append(Paragraph("PROPERTY LOCATIONS", heading_style))
            
            for i, location in enumerate(locations, 1):
                loc_header = Paragraph(f"<b>Location {location.get('location_number', i)}</b>", styles['Normal'])
                story.append(loc_header)
                story.append(Spacer(1, 0.1*inch))
                
                loc_address = f"{location.get('address_line1', '')}, {location.get('city', '')}, {location.get('state', '')} {location.get('zip_code', '')}"
                
                loc_data = [
                    ['Address:', loc_address],
                    ['Year Built:', str(location.get('year_built', ''))],
                    ['Construction:', location.get('construction_type', '')],
                    ['Occupancy:', location.get('occupancy_type', '')],
                    ['Square Feet:', f"{location.get('total_square_feet', 0):,}"],
                    ['Protection Class:', location.get('protection_class', '')],
                    ['Sprinklers:', 'Yes' if location.get('sprinkler_system') else 'No'],
                ]
                
                loc_table = Table(loc_data, colWidths=[2*inch, 4*inch])
                loc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                
                story.append(loc_table)
                story.append(Spacer(1, 0.15*inch))
                
                # Property Values
                values_data = [
                    ['Building Value:', f"${location.get('building_value', 0):,.0f}"],
                    ['Contents Value:', f"${location.get('contents_value', 0):,.0f}"],
                    ['Business Income:', f"${location.get('business_income_value', 0):,.0f}"],
                    ['Total Insured Value:', f"${location.get('total_insured_value', 0):,.0f}"]
                ]
                
                values_table = Table(values_data, colWidths=[2*inch, 4*inch])
                values_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                
                story.append(values_table)
                story.append(Spacer(1, 0.3*inch))
        
        # Coverage Information
        coverage = data.get('coverage', {})
        if coverage:
            story.append(Paragraph("COVERAGE INFORMATION", heading_style))
            
            coverage_data = [
                ['Policy Type:', coverage.get('policy_type', 'Property')],
                ['Effective Date:', coverage.get('effective_date', '')],
                ['Expiration Date:', coverage.get('expiration_date', '')],
                ['Building Limit:', f"${coverage.get('building_limit', 0):,.0f}"],
                ['Contents Limit:', f"${coverage.get('contents_limit', 0):,.0f}"],
                ['Building Deductible:', f"${coverage.get('building_deductible', 0):,.0f}"],
                ['Replacement Cost:', 'Yes' if coverage.get('replacement_cost') else 'No'],
            ]
            
            coverage_table = Table(coverage_data, colWidths=[2*inch, 4*inch])
            coverage_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F0F8')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(coverage_table)
        
        # Loss History
        losses = data.get('loss_history', [])
        if losses:
            story.append(Spacer(1, 0.4*inch))
            story.append(Paragraph("LOSS HISTORY (Last 5 Years)", heading_style))
            
            loss_table_data = [['Date', 'Type', 'Amount', 'Status']]
            
            for loss in losses[:10]:  # Limit to 10 losses
                loss_table_data.append([
                    loss.get('loss_date', ''),
                    loss.get('loss_type', ''),
                    f"${loss.get('loss_amount', 0):,.0f}",
                    loss.get('claim_status', '')
                ])
            
            loss_table = Table(loss_table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            loss_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
            ]))
            
            story.append(loss_table)
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated {self.carrier_name} carrier PDF ({len(pdf_bytes)} bytes)")
        
        return pdf_bytes


# Global carrier generator instances
_carrier_generators: Dict[str, CarrierGenerator] = {}


def get_carrier_generator(carrier_name: str = "Generic") -> CarrierGenerator:
    """
    Get or create carrier generator for carrier name.
    
    Args:
        carrier_name: Name of insurance carrier
        
    Returns:
        CarrierGenerator instance
    """
    global _carrier_generators
    
    if carrier_name not in _carrier_generators:
        _carrier_generators[carrier_name] = CarrierGenerator(carrier_name)
    
    return _carrier_generators[carrier_name]