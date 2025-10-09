"""
Domain models package for SubmitEZ.
"""

from .applicant import Applicant
from .property_location import PropertyLocation
from .coverage import Coverage

__all__ = [
    'Applicant',
    'PropertyLocation',
    'Coverage'
]