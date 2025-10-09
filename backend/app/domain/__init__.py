"""
Domain layer package for SubmitEZ.

Contains business entities and domain logic.
"""

from .models import Applicant, PropertyLocation

__all__ = [
    'Applicant',
    'PropertyLocation'
]