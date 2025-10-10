"""
Abstract base document processor.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseProcessor(ABC):
    """
    Abstract base class for document processors.
    
    Follows Open/Closed Principle - new document types can be added
    by creating new processor classes without modifying existing code.
    """
    
    def __init__(self):
        """Initialize document processor."""
        self.supported_extensions: List[str] = []
        self.supported_mime_types: List[str] = []
    
    @abstractmethod
    def can_process(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if processor can handle this file.
        
        Args:
            file_path: Path to file
            mime_type: Optional MIME type
            
        Returns:
            True if processor can handle this file
        """
        pass
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from document.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    def extract_tables(self, file_path: str) -> List[List[List[str]]]:
        """
        Extract tables from document.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cell values
        """
        pass
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract document metadata.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with metadata
        """
        file = Path(file_path)
        
        return {
            'filename': file.name,
            'extension': file.suffix.lower(),
            'size_bytes': file.stat().st_size if file.exists() else 0,
            'processor': self.__class__.__name__
        }
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process document and extract all information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with extracted data
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Extract text
            text = self.extract_text(file_path)
            
            # Extract tables
            tables = self.extract_tables(file_path)
            
            # Extract metadata
            metadata = self.extract_metadata(file_path)
            
            result = {
                'text': text,
                'tables': tables,
                'metadata': metadata,
                'success': True,
                'error': None
            }
            
            logger.info(
                f"Successfully processed {file_path}: "
                f"{len(text)} chars, {len(tables)} tables"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            
            return {
                'text': '',
                'tables': [],
                'metadata': self.extract_metadata(file_path),
                'success': False,
                'error': str(e)
            }
    
    def validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate file before processing.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        file = Path(file_path)
        
        # Check if file exists
        if not file.exists():
            return False, f"File not found: {file_path}"
        
        # Check if file is readable
        if not file.is_file():
            return False, f"Not a file: {file_path}"
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if file.stat().st_size > max_size:
            return False, f"File too large: {file.stat().st_size} bytes (max {max_size})"
        
        # Check if processor can handle this file
        if not self.can_process(file_path):
            return False, f"Processor cannot handle this file type"
        
        return True, None
    
    def get_page_count(self, file_path: str) -> Optional[int]:
        """
        Get number of pages in document.
        
        Args:
            file_path: Path to file
            
        Returns:
            Number of pages or None if not applicable
        """
        # Default implementation - override in subclasses
        return None
    
    def extract_images(self, file_path: str) -> List[bytes]:
        """
        Extract images from document.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of image data as bytes
        """
        # Default implementation - override in subclasses
        return []
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ''
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def split_into_sections(self, text: str) -> Dict[str, str]:
        """
        Split document text into logical sections.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary mapping section names to content
        """
        # Default implementation - override in subclasses for document-specific logic
        return {'full_text': text}
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about this processor.
        
        Returns:
            Dictionary with processor details
        """
        return {
            'name': self.__class__.__name__,
            'supported_extensions': self.supported_extensions,
            'supported_mime_types': self.supported_mime_types,
            'can_extract_tables': True,
            'can_extract_images': False,
            'can_get_page_count': False
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check processor health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Get processor info as a basic health check
            info = self.get_processor_info()
            
            return {
                'status': 'healthy',
                'processor': self.__class__.__name__,
                'message': 'Processor is available',
                'info': info
            }
            
        except Exception as e:
            logger.error(f"Processor health check failed: {e}")
            return {
                'status': 'unhealthy',
                'processor': self.__class__.__name__,
                'error': str(e)
            }