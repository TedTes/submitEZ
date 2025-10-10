"""
ACORD form processor with field mappings for insurance forms.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from app.core.processors.pdf_processor import PDFProcessor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ACORDProcessor(PDFProcessor):
    """
    Specialized processor for ACORD insurance forms.
    
    Supports:
    - ACORD 125: Commercial Insurance Application
    - ACORD 126: Commercial General Liability Section
    - ACORD 140: Property Section
    - ACORD 130: Workers Compensation Application
    
    Provides known field mappings and extraction patterns.
    """
    
    # ACORD form field mappings
    ACORD_125_FIELDS = {
        'applicant': [
            'applicant name',
            'named insured',
            'business name',
            'dba',
            'doing business as'
        ],
        'address': [
            'mailing address',
            'address',
            'street',
            'city',
            'state',
            'zip',
            'zip code'
        ],
        'contact': [
            'contact name',
            'phone',
            'telephone',
            'fax',
            'email',
            'e-mail'
        ],
        'business_info': [
            'fein',
            'federal id',
            'tax id',
            'naics',
            'sic',
            'type of business',
            'years in business',
            'business description'
        ],
        'coverage': [
            'effective date',
            'expiration date',
            'policy period',
            'coverage requested',
            'limits',
            'deductible'
        ],
        'broker': [
            'producer',
            'agent',
            'broker',
            'agency name'
        ]
    }
    
    ACORD_140_FIELDS = {
        'location': [
            'location number',
            'building number',
            'address',
            'city',
            'state',
            'zip'
        ],
        'building': [
            'year built',
            'construction',
            'construction type',
            'occupancy',
            'occupancy type',
            'square feet',
            'stories',
            'number of stories'
        ],
        'protection': [
            'protection class',
            'sprinkler',
            'sprinklered',
            'alarm',
            'fire alarm',
            'burglar alarm'
        ],
        'values': [
            'building limit',
            'contents limit',
            'business income',
            'extra expense',
            'total insured value',
            'tiv'
        ],
        'deductible': [
            'deductible',
            'wind deductible',
            'earthquake deductible',
            'flood deductible'
        ]
    }
    
    ACORD_126_FIELDS = {
        'general_liability': [
            'each occurrence',
            'general aggregate',
            'products aggregate',
            'personal injury',
            'advertising injury',
            'medical payments',
            'damage to rented premises'
        ],
        'premises': [
            'premises operations',
            'location of premises'
        ],
        'operations': [
            'operations description',
            'type of operations',
            'total payroll',
            'total sales'
        ]
    }
    
    ACORD_130_FIELDS = {
        'workers_comp': [
            'state',
            'premium basis',
            'estimated annual premium',
            'number of employees',
            'payroll'
        ],
        'class_codes': [
            'class code',
            'classification',
            'exposure'
        ]
    }
    
    # Common ACORD identifiers
    ACORD_IDENTIFIERS = [
        'acord',
        'acord 125',
        'acord 126',
        'acord 140',
        'acord 130',
        'acord corporation',
        'insurance services office'
    ]
    
    def __init__(self):
        """Initialize ACORD processor."""
        super().__init__()
        self.form_type = None
    
    def can_process(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if file is an ACORD form.
        
        Args:
            file_path: Path to file
            mime_type: Optional MIME type
            
        Returns:
            True if file is ACORD form
        """
        # Must be PDF first
        if not super().can_process(file_path, mime_type):
            return False
        
        # Check if it's an ACORD form
        return self.is_acord_form(file_path)
    
    def is_acord_form(self, file_path: str) -> bool:
        """
        Detect if PDF is an ACORD form.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if ACORD form detected
        """
        try:
            # Extract first page text for quick check
            text = self.extract_text(file_path).lower()
            
            # Check for ACORD identifiers
            for identifier in self.ACORD_IDENTIFIERS:
                if identifier.lower() in text:
                    logger.info(f"Detected ACORD form: {identifier}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting ACORD form: {e}")
            return False
    
    def detect_form_type(self, file_path: str) -> Optional[str]:
        """
        Detect specific ACORD form type.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Form type (e.g., '125', '140') or None
        """
        try:
            text = self.extract_text(file_path).lower()
            
            # Check for specific form numbers
            form_patterns = {
                '125': ['acord 125', 'form 125'],
                '126': ['acord 126', 'form 126'],
                '140': ['acord 140', 'form 140'],
                '130': ['acord 130', 'form 130']
            }
            
            for form_type, patterns in form_patterns.items():
                for pattern in patterns:
                    if pattern in text:
                        logger.info(f"Detected ACORD form type: {form_type}")
                        self.form_type = form_type
                        return form_type
            
            # Default to 125 if generic ACORD detected
            if any(identifier.lower() in text for identifier in self.ACORD_IDENTIFIERS):
                logger.info("Detected generic ACORD form, defaulting to type 125")
                self.form_type = '125'
                return '125'
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting form type: {e}")
            return None
    
    def get_field_mappings(self, form_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get field mappings for specific ACORD form type.
        
        Args:
            form_type: ACORD form type ('125', '140', etc.)
            
        Returns:
            Dictionary of field categories and their keywords
        """
        if form_type is None:
            form_type = self.form_type
        
        mappings = {
            '125': self.ACORD_125_FIELDS,
            '140': self.ACORD_140_FIELDS,
            '126': self.ACORD_126_FIELDS,
            '130': self.ACORD_130_FIELDS
        }
        
        return mappings.get(form_type, self.ACORD_125_FIELDS)
    
    def extract_acord_fields(self, file_path: str) -> Dict[str, Any]:
        """
        Extract fields from ACORD form with known mappings.
        
        Args:
            file_path: Path to ACORD PDF
            
        Returns:
            Dictionary of extracted fields by category
        """
        try:
            # Detect form type
            form_type = self.detect_form_type(file_path)
            
            # Extract text
            text = self.extract_text(file_path)
            
            # Get field mappings
            field_mappings = self.get_field_mappings(form_type)
            
            # Extract fields by category
            extracted = {
                'form_type': form_type,
                'is_acord': True,
                'raw_text': text,
                'fields': {}
            }
            
            # Search for each field category
            for category, keywords in field_mappings.items():
                extracted['fields'][category] = self._extract_category_fields(
                    text, keywords
                )
            
            logger.info(f"Extracted ACORD {form_type} fields")
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting ACORD fields: {e}")
            return {
                'form_type': None,
                'is_acord': False,
                'error': str(e)
            }
    
    def _extract_category_fields(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Extract fields for a category based on keywords.
        
        Args:
            text: Document text
            keywords: List of field keywords to search for
            
        Returns:
            Dictionary of found fields with context
        """
        found_fields = {}
        text_lower = text.lower()
        lines = text.split('\n')
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Search for keyword in text
            if keyword_lower in text_lower:
                # Find the line containing the keyword
                for i, line in enumerate(lines):
                    if keyword_lower in line.lower():
                        # Extract value (text after keyword on same or next line)
                        value = self._extract_field_value(lines, i, keyword)
                        
                        if value:
                            found_fields[keyword] = {
                                'value': value,
                                'line_number': i + 1,
                                'context': line.strip()
                            }
                        break
        
        return found_fields
    
    def _extract_field_value(
        self,
        lines: List[str],
        line_index: int,
        keyword: str
    ) -> Optional[str]:
        """
        Extract value for a field from text lines.
        
        Args:
            lines: Document lines
            line_index: Index of line containing keyword
            keyword: Field keyword
            
        Returns:
            Extracted value or None
        """
        try:
            line = lines[line_index]
            
            # Try to extract value from same line (after keyword)
            keyword_pos = line.lower().find(keyword.lower())
            if keyword_pos != -1:
                # Get text after keyword
                after_keyword = line[keyword_pos + len(keyword):].strip()
                
                # Remove common separators
                after_keyword = after_keyword.lstrip(':').lstrip('-').strip()
                
                if after_keyword:
                    return after_keyword
            
            # Try next line if current line has no value
            if line_index + 1 < len(lines):
                next_line = lines[line_index + 1].strip()
                if next_line and len(next_line) < 100:  # Reasonable length
                    return next_line
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting field value: {e}")
            return None
    
    def extract_structured_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract structured data from ACORD form.
        
        Args:
            file_path: Path to ACORD PDF
            
        Returns:
            Structured data dictionary
        """
        try:
            # Extract ACORD fields
            acord_data = self.extract_acord_fields(file_path)
            
            # Process into structured format based on form type
            form_type = acord_data.get('form_type')
            
            if form_type == '125':
                return self._structure_acord_125(acord_data)
            elif form_type == '140':
                return self._structure_acord_140(acord_data)
            elif form_type == '126':
                return self._structure_acord_126(acord_data)
            else:
                # Generic structure
                return acord_data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {'error': str(e)}
    
    def _structure_acord_125(self, acord_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure ACORD 125 data into domain model format."""
        fields = acord_data.get('fields', {})
        
        structured = {
            'form_type': '125',
            'applicant': {},
            'coverage': {},
            'broker': {}
        }
        
        # Extract applicant info
        if 'applicant' in fields:
            for key, data in fields['applicant'].items():
                if 'name' in key.lower():
                    structured['applicant']['business_name'] = data['value']
        
        if 'business_info' in fields:
            for key, data in fields['business_info'].items():
                if 'fein' in key.lower():
                    structured['applicant']['fein'] = data['value']
                elif 'naics' in key.lower():
                    structured['applicant']['naics_code'] = data['value']
        
        # Extract coverage info
        if 'coverage' in fields:
            for key, data in fields['coverage'].items():
                if 'effective' in key.lower():
                    structured['coverage']['effective_date'] = data['value']
                elif 'expiration' in key.lower():
                    structured['coverage']['expiration_date'] = data['value']
        
        return structured
    
    def _structure_acord_140(self, acord_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure ACORD 140 data into domain model format."""
        fields = acord_data.get('fields', {})
        
        structured = {
            'form_type': '140',
            'locations': []
        }
        
        # Extract location data
        location = {}
        
        if 'location' in fields:
            for key, data in fields['location'].items():
                location[key] = data['value']
        
        if 'building' in fields:
            for key, data in fields['building'].items():
                if 'year' in key.lower():
                    location['year_built'] = data['value']
                elif 'construction' in key.lower():
                    location['construction_type'] = data['value']
        
        if 'values' in fields:
            for key, data in fields['values'].items():
                if 'building' in key.lower():
                    location['building_value'] = data['value']
                elif 'contents' in key.lower():
                    location['contents_value'] = data['value']
        
        if location:
            structured['locations'].append(location)
        
        return structured
    
    def _structure_acord_126(self, acord_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure ACORD 126 data into domain model format."""
        fields = acord_data.get('fields', {})
        
        structured = {
            'form_type': '126',
            'liability_coverage': {}
        }
        
        if 'general_liability' in fields:
            for key, data in fields['general_liability'].items():
                structured['liability_coverage'][key] = data['value']
        
        return structured
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get ACORD processor information.
        
        Returns:
            Dictionary with processor details
        """
        info = super().get_processor_info()
        info.update({
            'specialization': 'ACORD Forms',
            'supported_forms': ['125', '126', '140', '130'],
            'has_field_mappings': True,
            'can_detect_form_type': True,
            'can_extract_structured': True
        })
        return info


# Global ACORD processor instance
_acord_processor: Optional[ACORDProcessor] = None


def get_acord_processor() -> ACORDProcessor:
    """
    Get or create ACORD processor singleton.
    
    Returns:
        ACORDProcessor instance
    """
    global _acord_processor
    
    if _acord_processor is None:
        _acord_processor = ACORDProcessor()
    
    return _acord_processor