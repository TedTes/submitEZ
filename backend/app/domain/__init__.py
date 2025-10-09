"""
Domain layer package for SubmitEZ.

Contains business entities and domain logic.
"""

from .models import Applicant, PropertyLocation, Coverage, LossHistory, Submission

__all__ = [
    'Applicant',
    'PropertyLocation',
    'Coverage',
    'LossHistory',
    'Submission'
]