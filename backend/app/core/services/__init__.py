"""
Core services package for SubmitEZ.
"""

from .extraction_service import ExtractionService, get_extraction_service

__all__ = [
    'ExtractionService',
    'get_extraction_service'
]