"""
Property Location domain model - represents a physical property to be insured.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class PropertyLocation:
    """
    Represents a physical property location for insurance.
    
    Attributes:
        location_number: Unique identifier for this location
        address_line1: Street address
        address_line2: Additional address information
        city: City name
        state: State abbreviation
        zip_code: ZIP code
        country: Country (default USA)
        
        building_description: Description of building/structure
        year_built: Year building was constructed
        construction_type: Type of construction (frame, masonry, etc.)
        number_of_stories: Number of stories/floors
        total_square_feet: Total building square footage
        occupancy_type: Type of occupancy (office, retail, warehouse, etc.)
        
        protection_class: ISO protection class (1-10)
        distance_to_fire_station: Miles to nearest fire station
        distance_to_hydrant: Feet to nearest fire hydrant
        sprinkler_system: Whether sprinklered
        alarm_system: Whether has alarm system
        security_system: Whether has security system
        
        building_value: Value of building structure
        contents_value: Value of contents/equipment
        business_income_value: Business income/interruption limit
        total_insured_value: Total of all values (TIV)
        
        basement: Whether has basement
        basement_finished: Whether basement is finished
        roof_type: Type of roof
        roof_year: Year roof was installed/replaced
        heating_type: Type of heating system
        cooling_type: Type of cooling system
        electrical_year: Year electrical system updated
        plumbing_year: Year plumbing updated
        
        metadata: Additional custom fields
    """
    
    # Location identifier
    location_number: Optional[str] = None
    
    # Address
    address_line1: str = ''
    address_line2: Optional[str] = None
    city: str = ''
    state: str = ''
    zip_code: str = ''
    country: str = 'USA'
    county: Optional[str] = None
    
    # Building Details
    building_description: Optional[str] = None
    year_built: Optional[int] = None
    construction_type: Optional[str] = None
    number_of_stories: Optional[int] = None
    total_square_feet: Optional[int] = None
    occupancy_type: Optional[str] = None
    
    # Protection/Safety
    protection_class: Optional[str] = None
    distance_to_fire_station: Optional[float] = None  # miles
    distance_to_hydrant: Optional[int] = None  # feet
    sprinkler_system: Optional[bool] = None
    alarm_system: Optional[bool] = None
    security_system: Optional[bool] = None
    fire_alarm: Optional[bool] = None
    burglar_alarm: Optional[bool] = None
    
    # Values (stored as Decimal for precision)
    building_value: Optional[Decimal] = None
    contents_value: Optional[Decimal] = None
    business_income_value: Optional[Decimal] = None
    total_insured_value: Optional[Decimal] = None
    
    # Building Systems
    basement: Optional[bool] = None
    basement_finished: Optional[bool] = None
    roof_type: Optional[str] = None
    roof_year: Optional[int] = None
    heating_type: Optional[str] = None
    cooling_type: Optional[str] = None
    electrical_year: Optional[int] = None
    plumbing_year: Optional[int] = None
    updates_wiring: Optional[bool] = None
    updates_plumbing: Optional[bool] = None
    updates_heating: Optional[bool] = None
    updates_roof: Optional[bool] = None
    
    # Additional Information
    prior_losses: Optional[bool] = None
    number_of_employees: Optional[int] = None
    hours_of_operation: Optional[str] = None
    
    # Custom fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Strip whitespace from string fields
        string_fields = [
            'location_number', 'address_line1', 'address_line2',
            'city', 'state', 'zip_code', 'country', 'county',
            'building_description', 'construction_type', 'occupancy_type',
            'protection_class', 'roof_type', 'heating_type', 'cooling_type',
            'hours_of_operation'
        ]
        
        for field_name in string_fields:
            value = getattr(self, field_name)
            if value and isinstance(value, str):
                setattr(self, field_name, value.strip())
        
        # Uppercase state code
        if self.state:
            self.state = self.state.upper()
        
        # Calculate TIV if not provided
        if self.total_insured_value is None:
            self.calculate_total_insured_value()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        
        # Convert Decimal to float for JSON serialization
        for key in ['building_value', 'contents_value', 'business_income_value', 'total_insured_value']:
            if data.get(key) is not None:
                data[key] = float(data[key])
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyLocation':
        """Create instance from dictionary."""
        # Convert numeric strings to Decimal
        decimal_fields = ['building_value', 'contents_value', 'business_income_value', 'total_insured_value']
        for field_name in decimal_fields:
            if field_name in data and data[field_name] is not None:
                try:
                    data[field_name] = Decimal(str(data[field_name]))
                except:
                    data[field_name] = None
        
        # Filter only known fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def get_full_address(self) -> str:
        """Get formatted full address."""
        parts = []
        
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        
        city_state_zip = []
        if self.city:
            city_state_zip.append(self.city)
        if self.state:
            city_state_zip.append(self.state)
        if self.zip_code:
            city_state_zip.append(self.zip_code)
        
        if city_state_zip:
            parts.append(', '.join(city_state_zip))
        
        if self.country and self.country != 'USA':
            parts.append(self.country)
        
        return '\n'.join(parts)
    
    def calculate_total_insured_value(self) -> Decimal:
        """Calculate total insured value (TIV)."""
        tiv = Decimal('0')
        
        if self.building_value:
            tiv += self.building_value
        if self.contents_value:
            tiv += self.contents_value
        if self.business_income_value:
            tiv += self.business_income_value
        
        self.total_insured_value = tiv
        return tiv
    
    def has_complete_address(self) -> bool:
        """Check if address is complete."""
        return all([
            self.address_line1,
            self.city,
            self.state,
            self.zip_code
        ])
    
    def is_complete(self) -> bool:
        """Check if location has minimum required information."""
        required_fields = [
            self.has_complete_address(),
            self.year_built is not None,
            self.construction_type is not None,
            self.occupancy_type is not None,
            self.total_square_feet is not None,
            self.total_insured_value is not None and self.total_insured_value > 0
        ]
        return all(required_fields)
    
    def get_missing_fields(self) -> list[str]:
        """Get list of missing critical fields."""
        missing = []
        
        if not self.has_complete_address():
            missing.append('complete_address')
        if self.year_built is None:
            missing.append('year_built')
        if not self.construction_type:
            missing.append('construction_type')
        if not self.occupancy_type:
            missing.append('occupancy_type')
        if self.total_square_feet is None:
            missing.append('total_square_feet')
        if not self.total_insured_value or self.total_insured_value <= 0:
            missing.append('total_insured_value')
        
        return missing
    
    def get_age(self) -> Optional[int]:
        """Get building age in years."""
        if self.year_built:
            from datetime import datetime
            return datetime.now().year - self.year_built
        return None
    
    def get_display_name(self) -> str:
        """Get display name for location."""
        if self.location_number:
            return f"Location {self.location_number}: {self.city}, {self.state}"
        return f"{self.city}, {self.state}" if self.city and self.state else "Unknown Location"
    
    def __str__(self) -> str:
        """String representation."""
        return f"PropertyLocation({self.get_display_name()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"PropertyLocation(location_number='{self.location_number}', "
            f"address='{self.city}, {self.state}', "
            f"tiv={self.total_insured_value})"
        )