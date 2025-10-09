"""
Loss History domain model - represents insurance claims history.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import date


@dataclass
class LossHistory:
    """
    Represents a single insurance loss/claim.
    
    Attributes:
        loss_date: Date of loss occurrence
        claim_number: Claim reference number
        loss_type: Type/cause of loss (Fire, Water, Wind, Theft, etc.)
        loss_description: Detailed description of loss
        
        loss_amount: Total amount of loss
        paid_amount: Amount paid by insurer
        reserved_amount: Amount reserved for claim
        deductible: Deductible applied
        
        claim_status: Status (Open, Closed, Pending, Denied)
        date_reported: Date claim was reported
        date_closed: Date claim was closed
        
        location_affected: Which location/property affected
        coverage_type: Type of coverage (Property, Liability, etc.)
        
        at_fault: Whether insured was at fault
        subrogation: Whether subrogation was pursued
        litigation: Whether claim involved litigation
        
        claimant_name: Name of claimant (for liability)
        injury_type: Type of injury (for liability claims)
        
        metadata: Additional custom fields
    """
    
    # Loss/Claim Identification
    loss_date: date
    claim_number: Optional[str] = None
    loss_type: Optional[str] = None  # Fire, Water, Wind, Theft, Liability, etc.
    loss_description: Optional[str] = None
    cause_of_loss: Optional[str] = None
    
    # Financial Details
    loss_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    reserved_amount: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    recoveries: Optional[Decimal] = None
    
    # Claim Status
    claim_status: str = 'Open'  # Open, Closed, Pending, Denied, Withdrawn
    date_reported: Optional[date] = None
    date_closed: Optional[date] = None
    days_to_close: Optional[int] = None
    
    # Location and Coverage
    location_affected: Optional[str] = None
    location_address: Optional[str] = None
    coverage_type: Optional[str] = None  # Property, General Liability, Auto, etc.
    coverage_line: Optional[str] = None  # Building, Contents, BI, Bodily Injury, etc.
    policy_number: Optional[str] = None
    
    # Liability-Specific Fields
    claimant_name: Optional[str] = None
    claimant_type: Optional[str] = None  # Customer, Employee, Vendor, Third Party
    injury_type: Optional[str] = None  # Bodily Injury, Property Damage, etc.
    injury_description: Optional[str] = None
    medical_only: Optional[bool] = None
    lost_time: Optional[bool] = None
    
    # Flags
    at_fault: Optional[bool] = None
    subrogation: Optional[bool] = None
    litigation: Optional[bool] = None
    fraud_suspected: Optional[bool] = None
    catastrophe: Optional[bool] = None
    catastrophe_code: Optional[str] = None
    
    # Additional Information
    adjuster_name: Optional[str] = None
    adjuster_company: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Custom fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Strip whitespace from string fields
        string_fields = [
            'claim_number', 'loss_type', 'loss_description', 'cause_of_loss',
            'claim_status', 'location_affected', 'location_address',
            'coverage_type', 'coverage_line', 'policy_number',
            'claimant_name', 'claimant_type', 'injury_type', 'injury_description',
            'catastrophe_code', 'adjuster_name', 'adjuster_company',
            'notes', 'internal_notes'
        ]
        
        for field_name in string_fields:
            value = getattr(self, field_name)
            if value and isinstance(value, str):
                setattr(self, field_name, value.strip())
        
        # Calculate days to close if dates available
        if self.date_reported and self.date_closed and not self.days_to_close:
            self.days_to_close = (self.date_closed - self.date_reported).days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        
        # Convert Decimal to float for JSON serialization
        decimal_fields = [
            'loss_amount', 'paid_amount', 'reserved_amount',
            'deductible', 'recoveries'
        ]
        
        for field_name in decimal_fields:
            if data.get(field_name) is not None:
                data[field_name] = float(data[field_name])
        
        # Convert date objects to ISO format strings
        date_fields = ['loss_date', 'date_reported', 'date_closed']
        for field_name in date_fields:
            if data.get(field_name):
                data[field_name] = data[field_name].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LossHistory':
        """Create instance from dictionary."""
        # Convert numeric strings to Decimal
        decimal_fields = [
            'loss_amount', 'paid_amount', 'reserved_amount',
            'deductible', 'recoveries'
        ]
        
        for field_name in decimal_fields:
            if field_name in data and data[field_name] is not None:
                try:
                    data[field_name] = Decimal(str(data[field_name]))
                except:
                    data[field_name] = None
        
        # Convert date strings to date objects
        date_fields = ['loss_date', 'date_reported', 'date_closed']
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
    
    def is_closed(self) -> bool:
        """Check if claim is closed."""
        return self.claim_status.lower() in ['closed', 'denied', 'withdrawn']
    
    def is_open(self) -> bool:
        """Check if claim is still open."""
        return self.claim_status.lower() in ['open', 'pending']
    
    def get_net_paid(self) -> Decimal:
        """Calculate net amount paid (paid - recoveries)."""
        net = self.paid_amount or Decimal('0')
        if self.recoveries:
            net -= self.recoveries
        return net
    
    def get_incurred(self) -> Decimal:
        """Calculate incurred amount (paid + reserved)."""
        incurred = Decimal('0')
        if self.paid_amount:
            incurred += self.paid_amount
        if self.reserved_amount:
            incurred += self.reserved_amount
        return incurred
    
    def is_significant(self, threshold: Decimal = Decimal('10000')) -> bool:
        """Check if loss exceeds threshold amount."""
        if self.loss_amount:
            return self.loss_amount >= threshold
        if self.paid_amount:
            return self.paid_amount >= threshold
        return False
    
    def get_loss_age_days(self) -> int:
        """Calculate number of days since loss occurred."""
        from datetime import date as date_type
        today = date_type.today()
        return (today - self.loss_date).days
    
    def is_recent(self, years: int = 5) -> bool:
        """Check if loss occurred within specified years."""
        age_days = self.get_loss_age_days()
        return age_days <= (years * 365)
    
    def get_display_summary(self) -> str:
        """Get human-readable loss summary."""
        parts = []
        
        if self.loss_date:
            parts.append(self.loss_date.strftime('%Y-%m-%d'))
        
        if self.loss_type:
            parts.append(self.loss_type)
        
        if self.loss_amount:
            parts.append(f"${self.loss_amount:,.2f}")
        elif self.paid_amount:
            parts.append(f"${self.paid_amount:,.2f}")
        
        if self.claim_status:
            parts.append(f"({self.claim_status})")
        
        return ' - '.join(parts)
    
    def is_complete(self) -> bool:
        """Check if loss has minimum required information."""
        return all([
            self.loss_date,
            self.loss_type or self.cause_of_loss,
            self.loss_amount or self.paid_amount,
            self.claim_status
        ])
    
    def get_missing_fields(self) -> list[str]:
        """Get list of missing critical fields."""
        missing = []
        
        if not self.loss_date:
            missing.append('loss_date')
        if not self.loss_type and not self.cause_of_loss:
            missing.append('loss_type_or_cause')
        if not self.loss_amount and not self.paid_amount:
            missing.append('loss_amount_or_paid')
        if not self.claim_status:
            missing.append('claim_status')
        
        return missing
    
    def __str__(self) -> str:
        """String representation."""
        return f"LossHistory({self.get_display_summary()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"LossHistory(date='{self.loss_date}', "
            f"type='{self.loss_type}', "
            f"amount={self.loss_amount}, "
            f"status='{self.claim_status}')"
        )