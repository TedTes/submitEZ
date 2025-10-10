"""
Processor factory for automatic document processor selection.
"""

from typing import Optional, List
from pathlib import Path
from app.core.processors.base_processor import BaseProcessor
from app.core.processors.pdf_processor import get_pdf_processor
from app.core.processors.excel_processor import get_excel_processor
from app.core.processors.acord_processor import get_acord_processor
from app.utils.logger import get_logger
from app.utils.file_utils import get_file_extension, get_mime_type

logger = get_logger(__name__)


class ProcessorFactory:
    """
    Factory for creating and selecting appropriate document processors.
    
    Implements Factory Pattern for clean processor selection based on:
    - File extension
    - MIME type
    - Document content analysis
    """
    
    def __init__(self):
        """Initialize processor factory."""
        self._processors: List[BaseProcessor] = []
        self._register_processors()
    
    def _register_processors(self):
        """Register available processors in priority order."""
        # Order matters: more specific processors first
        self._processors = [
            get_acord_processor(),  # Check ACORD forms first (most specific)
            get_pdf_processor(),    # Then generic PDFs
            get_excel_processor(),  # Then Excel files
        ]
        
        logger.debug(f"Registered {len(self._processors)} processors")
    
    def get_processor(
        self,
        file_path: str,
        mime_type: Optional[str] = None
    ) -> Optional[BaseProcessor]:
        """
        Get appropriate processor for file.
        
        Args:
            file_path: Path to file
            mime_type: Optional MIME type
            
        Returns:
            Appropriate processor instance or None
        """
        try:
            # Auto-detect MIME type if not provided
            if mime_type is None:
                mime_type = get_mime_type(file_path)
            
            logger.debug(f"Selecting processor for {file_path} (MIME: {mime_type})")
            
            # Try each processor in order
            for processor in self._processors:
                if processor.can_process(file_path, mime_type):
                    logger.info(
                        f"Selected {processor.__class__.__name__} for {Path(file_path).name}"
                    )
                    return processor
            
            logger.warning(f"No processor found for {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error selecting processor for {file_path}: {e}")
            return None
    
    def get_processor_by_extension(self, extension: str) -> Optional[BaseProcessor]:
        """
        Get processor by file extension.
        
        Args:
            extension: File extension (e.g., '.pdf', '.xlsx')
            
        Returns:
            Appropriate processor or None
        """
        extension = extension.lower()
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        for processor in self._processors:
            if extension in processor.supported_extensions:
                return processor
        
        return None
    
    def get_processor_by_mime_type(self, mime_type: str) -> Optional[BaseProcessor]:
        """
        Get processor by MIME type.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            Appropriate processor or None
        """
        for processor in self._processors:
            if mime_type in processor.supported_mime_types:
                return processor
        
        return None
    
    def can_process(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if any processor can handle the file.
        
        Args:
            file_path: Path to file
            mime_type: Optional MIME type
            
        Returns:
            True if file can be processed
        """
        processor = self.get_processor(file_path, mime_type)
        return processor is not None
    
    def process_file(self, file_path: str, mime_type: Optional[str] = None) -> dict:
        """
        Process file with appropriate processor.
        
        Args:
            file_path: Path to file
            mime_type: Optional MIME type
            
        Returns:
            Processing result dictionary
        """
        try:
            # Get appropriate processor
            processor = self.get_processor(file_path, mime_type)
            
            if processor is None:
                return {
                    'success': False,
                    'error': 'No suitable processor found',
                    'file': file_path
                }
            
            # Validate file
            is_valid, error = processor.validate_file(file_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': error,
                    'file': file_path,
                    'processor': processor.__class__.__name__
                }
            
            # Process file
            result = processor.process(file_path)
            result['processor'] = processor.__class__.__name__
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file': file_path
            }
    
    def batch_process(
        self,
        file_paths: List[str],
        mime_types: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Process multiple files in batch.
        
        Args:
            file_paths: List of file paths
            mime_types: Optional list of MIME types (same length as file_paths)
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, file_path in enumerate(file_paths):
            mime_type = mime_types[i] if mime_types and i < len(mime_types) else None
            result = self.process_file(file_path, mime_type)
            results.append(result)
        
        return results
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get all supported file extensions.
        
        Returns:
            List of supported extensions
        """
        extensions = set()
        for processor in self._processors:
            extensions.update(processor.supported_extensions)
        
        return sorted(list(extensions))
    
    def get_supported_mime_types(self) -> List[str]:
        """
        Get all supported MIME types.
        
        Returns:
            List of supported MIME types
        """
        mime_types = set()
        for processor in self._processors:
            mime_types.update(processor.supported_mime_types)
        
        return sorted(list(mime_types))
    
    def get_processor_info(self) -> List[dict]:
        """
        Get information about all registered processors.
        
        Returns:
            List of processor information dictionaries
        """
        return [processor.get_processor_info() for processor in self._processors]
    
    def health_check(self) -> dict:
        """
        Check health of all processors.
        
        Returns:
            Health status dictionary
        """
        try:
            processor_health = []
            
            for processor in self._processors:
                health = processor.health_check()
                processor_health.append(health)
            
            all_healthy = all(
                p['status'] == 'healthy' for p in processor_health
            )
            
            return {
                'status': 'healthy' if all_healthy else 'degraded',
                'total_processors': len(self._processors),
                'processors': processor_health,
                'supported_extensions': self.get_supported_extensions(),
                'supported_mime_types': self.get_supported_mime_types()
            }
            
        except Exception as e:
            logger.error(f"Processor factory health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Global factory instance
_processor_factory: Optional[ProcessorFactory] = None


def get_processor_factory() -> ProcessorFactory:
    """
    Get or create processor factory singleton.
    
    Returns:
        ProcessorFactory instance
    """
    global _processor_factory
    
    if _processor_factory is None:
        _processor_factory = ProcessorFactory()
    
    return _processor_factory


def get_processor_for_file(
    file_path: str,
    mime_type: Optional[str] = None
) -> Optional[BaseProcessor]:
    """
    Convenience function to get processor for a file.
    
    Args:
        file_path: Path to file
        mime_type: Optional MIME type
        
    Returns:
        Appropriate processor or None
    """
    factory = get_processor_factory()
    return factory.get_processor(file_path, mime_type)


def process_document(file_path: str, mime_type: Optional[str] = None) -> dict:
    """
    Convenience function to process a document.
    
    Args:
        file_path: Path to file
        mime_type: Optional MIME type
        
    Returns:
        Processing result dictionary
    """
    factory = get_processor_factory()
    return factory.process_file(file_path, mime_type)