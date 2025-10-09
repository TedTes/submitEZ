"""
Applicant domain model - represents the insured business entity.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Applicant:
    """
    Represents an insurance applicant (insured business).
    
    Attributes:
        business_name: Legal business name
        dba_name: Doing Business As name
        fein: Federal Employer Identification Number
        naics_code: North American Industry Classification System code
        naics_description: Description of NAICS code
        business_type: Type of entity (Corporation, LLC, Partnership, etc.)
        years_in_business: Number of years operating
        contact_name: Primary contact person
        contact_title: Contact's title/position
        email: Primary email address
        phone: Primary phone number
        website: Company website URL
        mailing_address: Mailing address details
        physical_address: Physical location address details
        description: Business description or operations summary
        metadata: Additional custom fields
    """
    
    # Business Information
    business_name: str
    fein: Optional[str] = None
    dba_name: Optional[str] = None
    naics_code: Optional[str] = None
    naics_description: Optional[str] = None
    business_type: Optional[str] = None
    years_in_business: Optional[int] = None
    description: Optional[str] = None
    
    # Contact Information
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None
    
    # Mailing Address
    mailing_address_line1: Optional[str] = None
    mailing_address_line2: Optional[str] = None
    mailing_city: Optional[str] = None
    mailing_state: Optional[str] = None
    mailing_zip: Optional[str] = None
    mailing_country: str = 'USA'
    
    # Physical Address
    physical_address_line1: Optional[str] = None
    physical_address_line2: Optional[str] = None
    physical_city: Optional[str] = None
    physical_state: Optional[str] = None
    physical_zip: Optional[str] = None
    physical_country: str = 'USA'
    
    # Additional fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Strip whitespace from string fields
        string_fields = [
            'business_name', 'dba_name', 'fein', 'naics_code', 'naics_description',
            'business_type', 'description', 'contact_name', 'contact_title',
            'email', 'phone', 'fax', 'website',
            'mailing_address_line1', 'mailing_address_line2', 'mailing_city',
            'mailing_state', 'mailing_zip', 'mailing_country',
            'physical_address_line1', 'physical_address_line2', 'physical_city',
            'physical_state', 'physical_zip', 'physical_country'
        ]
        
        for field_name in string_fields:
            value = getattr(self, field_name)
            if value and isinstance(value, str):
                setattr(self, field_name, value.strip())
        
        # Uppercase state codes
        if self.mailing_state:
            self.mailing_state = self.mailing_state.upper()
        if self.physical_state:
            self.physical_state = self.physical_state.upper()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Applicant':
        """Create instance from dictionary."""
        # Filter only known fields
        valid_fields = {
            f.name for f in cls.__dataclass_fields__.values()
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def get_full_mailing_address(self) -> str:
        """Get formatted mailing address."""
        parts = []
        
        if self.mailing_address_line1:
            parts.append(self.mailing_address_line1)
        if self.mailing_address_line2:
            parts.append(self.mailing_address_line2)
        
        city_state_zip = []
        if self.mailing_city:
            city_state_zip.append(self.mailing_city)
        if self.mailing_state:
            city_state_zip.append(self.mailing_state)
        if self.mailing_zip:
            city_state_zip.append(self.mailing_zip)
        
        if city_state_zip:
            parts.append(', '.join(city_state_zip))
        
        if self.mailing_country and self.mailing_country != 'USA':
            parts.append(self.mailing_country)
        
        return '\n'.join(parts)
    
    def get_full_physical_address(self) -> str:
        """Get formatted physical address."""
        parts = []
        
        if self.physical_address_line1:
            parts.append(self.physical_address_line1)
        if self.physical_address_line2:
            parts.append(self.physical_address_line2)
        
        city_state_zip = []
        if self.physical_city:
            city_state_zip.append(self.physical_city)
        if self.physical_state:
            city_state_zip.append(self.physical_state)
        if self.physical_zip:
            city_state_zip.append(self.physical_zip)
        
        if city_state_zip:
            parts.append(', '.join(city_state_zip))
        
        if self.physical_country and self.physical_country != 'USA':
            parts.append(self.physical_country)
        
        return '\n'.join(parts)
    
    def has_complete_mailing_address(self) -> bool:
        """Check if mailing address is complete."""
        return all([
            self.mailing_address_line1,
            self.mailing_city,
            self.mailing_state,
            self.mailing_zip
        ])
    
    def has_complete_physical_address(self) -> bool:
        """Check if physical address is complete."""
        return all([
            self.physical_address_line1,
            self.physical_city,
            self.physical_state,
            self.physical_zip
        ])
    
    def get_display_name(self) -> str:
        """Get display name (business name or DBA)."""
        if self.dba_name:
            return f"{self.business_name} (DBA: {self.dba_name})"
        return self.business_name
    
    def is_complete(self) -> bool:
        """Check if applicant has minimum required information."""
        required_fields = [
            self.business_name,
            self.fein or self.naics_code,  # At least one identifier
        ]
        return all(required_fields) and (
            self.has_complete_mailing_address() or 
            self.has_complete_physical_address()
        )
    
    def get_missing_fields(self) -> list[str]:
        """Get list of missing critical fields."""
        missing = []
        
        if not self.business_name:
            missing.append('business_name')
        if not self.fein and not self.naics_code:
            missing.append('fein_or_naics_code')
        if not self.has_complete_mailing_address() and not self.has_complete_physical_address():
            missing.append('complete_address')
        
        return missing
    
    def __str__(self) -> str:
        """String representation."""
        return f"Applicant(business_name='{self.business_name}', fein='{self.fein}')"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Applicant(business_name='{self.business_name}', "
            f"fein='{self.fein}', naics='{self.naics_code}')"
        )