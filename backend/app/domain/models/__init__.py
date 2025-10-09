"""
Domain models package for SubmitEZ.
"""

from .applicant import Applicant
from .property_location import PropertyLocation
from .coverage import Coverage
from .loss_history import LossHistory
from .submission import Submission

__all__ = [
    'Applicant',
    'PropertyLocation',
    'Coverage',
    'LossHistory',
    'Submission'
]