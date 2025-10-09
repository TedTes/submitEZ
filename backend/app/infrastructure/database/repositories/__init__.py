"""
Repository package for SubmitEZ.
"""

from .base_repository import BaseRepository
from .submission_repository import SubmissionRepository

__all__ = [
    'BaseRepository',
    'SubmissionRepository'
]