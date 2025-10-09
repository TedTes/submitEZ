"""
Submission domain model - the aggregate root for insurance submissions.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4

from .applicant import Applicant
from .property_location import PropertyLocation
from .coverage import Coverage
from .loss_history import LossHistory


@dataclass
class Submission:
    """
    Aggregate root representing a complete insurance submission.
    
    This is the main entity that ties together all components of a submission:
    - Applicant (who is being insured)
    - Property Locations (what properties to insure)
    - Coverage (what insurance coverage is needed)
    - Loss History (claims history)
    
    Attributes:
        id: Unique submission identifier
        status: Current workflow status
        applicant: The insured business
        locations: List of property locations
        coverage: Insurance coverage details
        loss_history: List of prior losses/claims
        
        uploaded_files: List of uploaded file references
        generated_files: List of generated output file references
        
        created_at: When submission was created
        updated_at: When submission was last updated
        submitted_at: When submission was completed/submitted
        
        validation_errors: List of validation errors
        validation_warnings: List of validation warnings
        
        extraction_metadata: Metadata from AI extraction
        notes: User notes
        metadata: Additional custom fields
    """
    
    # Submission Identification
    id: str = field(default_factory=lambda: str(uuid4()))
    
    # Workflow Status
    status: str = 'draft'  # draft, uploaded, extracting, extracted, validating, validated, generating, completed, error
    
    # Core Entities
    applicant: Optional[Applicant] = None
    locations: List[PropertyLocation] = field(default_factory=list)
    coverage: Optional[Coverage] = None
    loss_history: List[LossHistory] = field(default_factory=list)
    
    # File References
    uploaded_files: List[Dict[str, Any]] = field(default_factory=list)
    generated_files: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    extracted_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    
    # Validation Results
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)
    validation_warnings: List[Dict[str, Any]] = field(default_factory=list)
    is_valid: bool = False
    
    # Extraction Metadata
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_confidence: Optional[float] = None
    
    # Additional Information
    broker_name: Optional[str] = None
    broker_email: Optional[str] = None
    carrier_name: Optional[str] = None
    effective_date_requested: Optional[str] = None
    
    # User Notes
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Custom Fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize submission after creation."""
        # Ensure timestamps are datetime objects
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert submission to dictionary."""
        data = {
            'id': self.id,
            'status': self.status,
            'applicant': self.applicant.to_dict() if self.applicant else None,
            'locations': [loc.to_dict() for loc in self.locations],
            'coverage': self.coverage.to_dict() if self.coverage else None,
            'loss_history': [loss.to_dict() for loss in self.loss_history],
            'uploaded_files': self.uploaded_files,
            'generated_files': self.generated_files,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'extracted_at': self.extracted_at.isoformat() if self.extracted_at else None,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'is_valid': self.is_valid,
            'extraction_metadata': self.extraction_metadata,
            'extraction_confidence': self.extraction_confidence,
            'broker_name': self.broker_name,
            'broker_email': self.broker_email,
            'carrier_name': self.carrier_name,
            'effective_date_requested': self.effective_date_requested,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'metadata': self.metadata
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Submission':
        """Create submission from dictionary."""
        # Convert nested objects
        if 'applicant' in data and data['applicant']:
            data['applicant'] = Applicant.from_dict(data['applicant'])
        
        if 'locations' in data and data['locations']:
            data['locations'] = [
                PropertyLocation.from_dict(loc) for loc in data['locations']
            ]
        
        if 'coverage' in data and data['coverage']:
            data['coverage'] = Coverage.from_dict(data['coverage'])
        
        if 'loss_history' in data and data['loss_history']:
            data['loss_history'] = [
                LossHistory.from_dict(loss) for loss in data['loss_history']
            ]
        
        # Convert timestamp strings to datetime
        timestamp_fields = ['created_at', 'updated_at', 'submitted_at', 'extracted_at', 'validated_at', 'generated_at']
        for field_name in timestamp_fields:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Filter only known fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def update_status(self, new_status: str):
        """Update submission status and timestamp."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Set specific timestamps based on status
        if new_status == 'extracted':
            self.extracted_at = datetime.utcnow()
        elif new_status == 'validated':
            self.validated_at = datetime.utcnow()
        elif new_status == 'completed':
            self.generated_at = datetime.utcnow()
            self.submitted_at = datetime.utcnow()
    
    def add_location(self, location: PropertyLocation):
        """Add a property location to submission."""
        self.locations.append(location)
        self.updated_at = datetime.utcnow()
    
    def add_loss(self, loss: LossHistory):
        """Add a loss history record to submission."""
        self.loss_history.append(loss)
        self.updated_at = datetime.utcnow()
    
    def add_uploaded_file(self, file_info: Dict[str, Any]):
        """Add uploaded file reference."""
        self.uploaded_files.append(file_info)
        self.updated_at = datetime.utcnow()
    
    def add_generated_file(self, file_info: Dict[str, Any]):
        """Add generated file reference."""
        self.generated_files.append(file_info)
        self.updated_at = datetime.utcnow()
    
    def set_validation_results(self, errors: List[Dict[str, Any]], warnings: List[Dict[str, Any]]):
        """Set validation results."""
        self.validation_errors = errors
        self.validation_warnings = warnings
        self.is_valid = len(errors) == 0
        self.validated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def has_applicant(self) -> bool:
        """Check if submission has applicant."""
        return self.applicant is not None and self.applicant.is_complete()
    
    def has_locations(self) -> bool:
        """Check if submission has at least one complete location."""
        return len(self.locations) > 0 and any(loc.is_complete() for loc in self.locations)
    
    def has_coverage(self) -> bool:
        """Check if submission has coverage."""
        return self.coverage is not None and self.coverage.is_complete()
    
    def get_total_locations(self) -> int:
        """Get total number of locations."""
        return len(self.locations)
    
    def get_total_losses(self) -> int:
        """Get total number of loss records."""
        return len(self.loss_history)
    
    def get_recent_losses(self, years: int = 5) -> List[LossHistory]:
        """Get losses within specified years."""
        return [loss for loss in self.loss_history if loss.is_recent(years)]
    
    def get_total_tiv(self) -> float:
        """Calculate total insured value across all locations."""
        from decimal import Decimal
        total = Decimal('0')
        for location in self.locations:
            if location.total_insured_value:
                total += location.total_insured_value
        return float(total)
    
    def is_complete_for_extraction(self) -> bool:
        """Check if submission is ready for extraction."""
        return len(self.uploaded_files) > 0 and self.status in ['uploaded', 'draft']
    
    def is_complete_for_validation(self) -> bool:
        """Check if submission is ready for validation."""
        return (
            self.status == 'extracted' and
            self.has_applicant() and
            self.has_locations()
        )
    
    def is_complete_for_generation(self) -> bool:
        """Check if submission is ready for PDF generation."""
        return (
            self.status == 'validated' and
            self.is_valid and
            self.has_applicant() and
            self.has_locations() and
            self.has_coverage()
        )
    
    def get_completeness_percentage(self) -> int:
        """Calculate submission completeness percentage."""
        total_checks = 4
        completed = 0
        
        if self.has_applicant():
            completed += 1
        if self.has_locations():
            completed += 1
        if self.has_coverage():
            completed += 1
        if self.is_valid:
            completed += 1
        
        return int((completed / total_checks) * 100)
    
    def get_missing_components(self) -> List[str]:
        """Get list of missing components."""
        missing = []
        
        if not self.has_applicant():
            missing.append('applicant')
        if not self.has_locations():
            missing.append('locations')
        if not self.has_coverage():
            missing.append('coverage')
        if not self.is_valid:
            missing.append('validation')
        
        return missing
    
    def get_summary(self) -> Dict[str, Any]:
        """Get submission summary."""
        return {
            'id': self.id,
            'status': self.status,
            'applicant_name': self.applicant.business_name if self.applicant else None,
            'total_locations': self.get_total_locations(),
            'total_losses': self.get_total_losses(),
            'total_tiv': self.get_total_tiv(),
            'completeness': self.get_completeness_percentage(),
            'is_valid': self.is_valid,
            'validation_errors_count': len(self.validation_errors),
            'validation_warnings_count': len(self.validation_warnings),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        """String representation."""
        applicant_name = self.applicant.business_name if self.applicant else 'N/A'
        return f"Submission(id='{self.id[:8]}...', applicant='{applicant_name}', status='{self.status}')"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Submission(id='{self.id}', status='{self.status}', "
            f"locations={len(self.locations)}, losses={len(self.loss_history)})"
        )