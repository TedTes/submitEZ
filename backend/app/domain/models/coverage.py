"""
Coverage domain model - represents insurance coverage details.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import date


@dataclass
class Coverage:
    """
    Represents insurance coverage specifications.
    
    Attributes:
        policy_type: Type of policy (Property, General Liability, etc.)
        effective_date: Coverage effective date
        expiration_date: Coverage expiration date
        
        # Property Coverage
        building_limit: Building coverage limit
        contents_limit: Contents/equipment coverage limit
        business_income_limit: Business income/interruption limit
        extra_expense_limit: Extra expense limit
        
        # Deductibles
        building_deductible: Building deductible
        contents_deductible: Contents deductible
        business_income_deductible: Business income deductible (time-based)
        wind_hail_deductible: Wind/hail deductible (often percentage)
        flood_deductible: Flood deductible
        earthquake_deductible: Earthquake deductible
        
        # General Liability
        general_aggregate_limit: General aggregate limit
        products_aggregate_limit: Products/completed operations aggregate
        each_occurrence_limit: Each occurrence limit
        personal_injury_limit: Personal and advertising injury limit
        medical_payments_limit: Medical payments limit
        damage_to_premises_limit: Damage to rented premises limit
        
        # Additional Coverages
        property_in_transit: Property in transit coverage
        accounts_receivable: Accounts receivable coverage
        valuable_papers: Valuable papers coverage
        equipment_breakdown: Equipment breakdown coverage
        spoilage: Spoilage coverage
        
        # Coverage Options
        replacement_cost: Replacement cost valuation
        actual_cash_value: Actual cash value basis
        coinsurance_percentage: Coinsurance percentage
        agreed_value: Agreed value option
        blanket_coverage: Blanket coverage option
        
        # Extensions
        ordinance_or_law: Ordinance or law coverage
        utility_services: Utility services extension
        pollutant_cleanup: Pollutant cleanup coverage
        terrorism_coverage: Terrorism coverage included
        
        # Premium Information
        estimated_annual_premium: Estimated annual premium
        premium_basis: Basis for premium calculation
        
        metadata: Additional custom fields
    """
    
    # Policy Information
    policy_type: Optional[str] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    policy_term_months: Optional[int] = 12
    
    # Property Coverage Limits
    building_limit: Optional[Decimal] = None
    contents_limit: Optional[Decimal] = None
    business_income_limit: Optional[Decimal] = None
    extra_expense_limit: Optional[Decimal] = None
    equipment_breakdown_limit: Optional[Decimal] = None
    
    # Property Deductibles
    building_deductible: Optional[Decimal] = None
    contents_deductible: Optional[Decimal] = None
    business_income_deductible: Optional[str] = None  # e.g., "72 hours"
    wind_hail_deductible: Optional[str] = None  # e.g., "2%" or "$5,000"
    flood_deductible: Optional[Decimal] = None
    earthquake_deductible: Optional[str] = None  # e.g., "5%"
    all_other_perils_deductible: Optional[Decimal] = None
    
    # General Liability Limits
    general_aggregate_limit: Optional[Decimal] = None
    products_aggregate_limit: Optional[Decimal] = None
    each_occurrence_limit: Optional[Decimal] = None
    personal_injury_limit: Optional[Decimal] = None
    medical_payments_limit: Optional[Decimal] = None
    damage_to_premises_limit: Optional[Decimal] = None
    
    # Additional Property Coverages
    property_in_transit: Optional[Decimal] = None
    accounts_receivable: Optional[Decimal] = None
    valuable_papers: Optional[Decimal] = None
    fine_arts: Optional[Decimal] = None
    signs: Optional[Decimal] = None
    outdoor_property: Optional[Decimal] = None
    debris_removal: Optional[Decimal] = None
    pollutant_cleanup: Optional[Decimal] = None
    spoilage: Optional[Decimal] = None
    
    # Coverage Options (Boolean flags)
    replacement_cost: Optional[bool] = None
    actual_cash_value: Optional[bool] = None
    agreed_value: Optional[bool] = None
    blanket_coverage: Optional[bool] = None
    inflation_guard: Optional[bool] = None
    
    # Coinsurance
    coinsurance_percentage: Optional[int] = None  # 80, 90, 100
    coinsurance_waived: Optional[bool] = None
    
    # Extensions and Endorsements
    ordinance_or_law_coverage: Optional[Decimal] = None
    utility_services_time_element: Optional[Decimal] = None
    electronic_data: Optional[Decimal] = None
    employee_dishonesty: Optional[Decimal] = None
    forgery: Optional[Decimal] = None
    
    # Special Coverage
    flood_coverage: Optional[bool] = None
    earthquake_coverage: Optional[bool] = None
    terrorism_coverage: Optional[bool] = None
    cyber_coverage: Optional[bool] = None
    
    # Premium Information
    estimated_annual_premium: Optional[Decimal] = None
    premium_basis: Optional[str] = None  # e.g., "building value", "gross sales"
    premium_basis_amount: Optional[Decimal] = None
    
    # Additional Coverage Notes
    special_conditions: Optional[str] = None
    exclusions: Optional[List[str]] = field(default_factory=list)
    endorsements: Optional[List[str]] = field(default_factory=list)
    
    # Custom fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Strip whitespace from string fields
        string_fields = [
            'policy_type', 'business_income_deductible', 'wind_hail_deductible',
            'earthquake_deductible', 'premium_basis', 'special_conditions'
        ]
        
        for field_name in string_fields:
            value = getattr(self, field_name)
            if value and isinstance(value, str):
                setattr(self, field_name, value.strip())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        
        # Convert Decimal to float for JSON serialization
        decimal_fields = [
            'building_limit', 'contents_limit', 'business_income_limit',
            'extra_expense_limit', 'equipment_breakdown_limit',
            'building_deductible', 'contents_deductible', 'flood_deductible',
            'all_other_perils_deductible', 'general_aggregate_limit',
            'products_aggregate_limit', 'each_occurrence_limit',
            'personal_injury_limit', 'medical_payments_limit',
            'damage_to_premises_limit', 'property_in_transit',
            'accounts_receivable', 'valuable_papers', 'fine_arts',
            'signs', 'outdoor_property', 'debris_removal',
            'pollutant_cleanup', 'spoilage', 'ordinance_or_law_coverage',
            'utility_services_time_element', 'electronic_data',
            'employee_dishonesty', 'forgery', 'estimated_annual_premium',
            'premium_basis_amount'
        ]
        
        for field_name in decimal_fields:
            if data.get(field_name) is not None:
                data[field_name] = float(data[field_name])
        
        # Convert date objects to ISO format strings
        if data.get('effective_date'):
            data['effective_date'] = data['effective_date'].isoformat()
        if data.get('expiration_date'):
            data['expiration_date'] = data['expiration_date'].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Coverage':
        """Create instance from dictionary."""
        # Convert numeric strings to Decimal
        decimal_fields = [
            'building_limit', 'contents_limit', 'business_income_limit',
            'extra_expense_limit', 'equipment_breakdown_limit',
            'building_deductible', 'contents_deductible', 'flood_deductible',
            'all_other_perils_deductible', 'general_aggregate_limit',
            'products_aggregate_limit', 'each_occurrence_limit',
            'personal_injury_limit', 'medical_payments_limit',
            'damage_to_premises_limit', 'property_in_transit',
            'accounts_receivable', 'valuable_papers', 'fine_arts',
            'signs', 'outdoor_property', 'debris_removal',
            'pollutant_cleanup', 'spoilage', 'ordinance_or_law_coverage',
            'utility_services_time_element', 'electronic_data',
            'employee_dishonesty', 'forgery', 'estimated_annual_premium',
            'premium_basis_amount'
        ]
        
        for field_name in decimal_fields:
            if field_name in data and data[field_name] is not None:
                try:
                    data[field_name] = Decimal(str(data[field_name]))
                except:
                    data[field_name] = None
        
        # Convert date strings to date objects
        date_fields = ['effective_date', 'expiration_date']
        for field_name in date_fields:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    try:
                        from datetime import datetime
                        data[field_name] = datetime.fromisoformat(data[field_name]).date()
                    except:
                        data[field_name] = None
        
        # Filter only known fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def get_total_property_limit(self) -> Decimal:
        """Calculate total property coverage limit."""
        total = Decimal('0')
        
        if self.building_limit:
            total += self.building_limit
        if self.contents_limit:
            total += self.contents_limit
        if self.business_income_limit:
            total += self.business_income_limit
        
        return total
    
    def get_policy_period_days(self) -> Optional[int]:
        """Calculate policy period in days."""
        if self.effective_date and self.expiration_date:
            return (self.expiration_date - self.effective_date).days
        return None
    
    def is_active(self, check_date: Optional[date] = None) -> bool:
        """Check if coverage is active on given date."""
        if not self.effective_date or not self.expiration_date:
            return False
        
        if check_date is None:
            check_date = date.today()
        
        return self.effective_date <= check_date <= self.expiration_date
    
    def has_property_coverage(self) -> bool:
        """Check if has any property coverage."""
        return any([
            self.building_limit,
            self.contents_limit,
            self.business_income_limit
        ])
    
    def has_liability_coverage(self) -> bool:
        """Check if has any liability coverage."""
        return any([
            self.general_aggregate_limit,
            self.each_occurrence_limit,
            self.personal_injury_limit
        ])
    
    def is_complete(self) -> bool:
        """Check if coverage has minimum required information."""
        return all([
            self.policy_type,
            self.effective_date,
            self.expiration_date,
            self.has_property_coverage() or self.has_liability_coverage()
        ])
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing critical fields."""
        missing = []
        
        if not self.policy_type:
            missing.append('policy_type')
        if not self.effective_date:
            missing.append('effective_date')
        if not self.expiration_date:
            missing.append('expiration_date')
        if not self.has_property_coverage() and not self.has_liability_coverage():
            missing.append('coverage_limits')
        
        return missing
    
    def __str__(self) -> str:
        """String representation."""
        return f"Coverage(type='{self.policy_type}', total_limit={self.get_total_property_limit()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Coverage(policy_type='{self.policy_type}', "
            f"effective='{self.effective_date}', "
            f"expiration='{self.expiration_date}')"
        )