"""
Document processors package for SubmitEZ.
"""

from .base_processor import BaseProcessor
from .pdf_processor import PDFProcessor, get_pdf_processor

__all__ = [
    'BaseProcessor',
    'PDFProcessor',
    'get_pdf_processor'
]