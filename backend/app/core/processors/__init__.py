"""
Document processors package for SubmitEZ.
"""

from .base_processor import BaseProcessor
from .pdf_processor import PDFProcessor, get_pdf_processor
from .excel_processor import ExcelProcessor, get_excel_processor
from .acord_processor import ACORDProcessor, get_acord_processor
from .processor_factory import (
    ProcessorFactory,
    get_processor_factory,
    get_processor_for_file,
    process_document
)

__all__ = [
    'BaseProcessor',
    'PDFProcessor',
    'get_pdf_processor',
    'ExcelProcessor',
    'get_excel_processor',
    'ACORDProcessor',
    'get_acord_processor',
    'ProcessorFactory',
    'get_processor_factory',
    'get_processor_for_file',
    'process_document'
]