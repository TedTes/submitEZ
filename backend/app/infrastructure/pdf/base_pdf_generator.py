"""
Abstract base PDF generator interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BasePDFGenerator(ABC):
    """
    Abstract base class for PDF generation.
    
    Supports Dependency Inversion Principle - allows different
    PDF generation strategies without changing business logic.
    """
    
    def __init__(self):
        """Initialize PDF generator."""
        self._output_dir = None
    
    @property
    def output_dir(self) -> Path:
        """Get output directory for generated PDFs."""
        if self._output_dir is None:
            import os
            self._output_dir = Path(os.getenv('OUTPUT_DIR', '/tmp/submitez-output'))
            self._output_dir.mkdir(parents=True, exist_ok=True)
        return self._output_dir
    
    @abstractmethod
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate PDF from data.
        
        Args:
            data: Data dictionary to populate PDF
            output_path: Optional output file path
            
        Returns:
            Path to generated PDF file
        """
        pass
    
    @abstractmethod
    def generate_to_bytes(
        self,
        data: Dict[str, Any]
    ) -> bytes:
        """
        Generate PDF as bytes without saving to file.
        
        Args:
            data: Data dictionary to populate PDF
            
        Returns:
            PDF content as bytes
        """
        pass
    
    @abstractmethod
    def validate_data(
        self,
        data: Dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Validate data before PDF generation.
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass
    
    def get_required_fields(self) -> list[str]:
        """
        Get list of required fields for this PDF type.
        
        Returns:
            List of required field names
        """
        return []
    
    def get_output_filename(
        self,
        data: Dict[str, Any],
        prefix: str = "document"
    ) -> str:
        """
        Generate output filename based on data.
        
        Args:
            data: Data dictionary
            prefix: Filename prefix
            
        Returns:
            Generated filename
        """
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try to get applicant name for filename
        applicant_name = None
        if 'applicant' in data:
            applicant_name = data['applicant'].get('business_name')
        elif 'business_name' in data:
            applicant_name = data['business_name']
        
        if applicant_name:
            # Clean name for filename
            clean_name = "".join(
                c for c in applicant_name if c.isalnum() or c in (' ', '-', '_')
            ).strip()
            clean_name = clean_name.replace(' ', '_')[:50]
            filename = f"{prefix}_{clean_name}_{timestamp}.pdf"
        else:
            filename = f"{prefix}_{timestamp}.pdf"
        
        return filename
    
    def save_to_file(
        self,
        pdf_bytes: bytes,
        output_path: str
    ) -> str:
        """
        Save PDF bytes to file.
        
        Args:
            pdf_bytes: PDF content as bytes
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"Saved PDF to: {output_file}")
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error saving PDF to {output_path}: {e}")
            raise
    
    def get_pdf_info(
        self,
        pdf_path: str
    ) -> Dict[str, Any]:
        """
        Get information about generated PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF info
        """
        try:
            from pathlib import Path
            
            pdf_file = Path(pdf_path)
            
            if not pdf_file.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            return {
                'path': str(pdf_file),
                'filename': pdf_file.name,
                'size_bytes': pdf_file.stat().st_size,
                'size_mb': round(pdf_file.stat().st_size / (1024 * 1024), 2),
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return {
                'path': pdf_path,
                'exists': False,
                'error': str(e)
            }
    
    def cleanup_temp_files(self):
        """Clean up temporary files if any."""
        pass
    
    def batch_generate(
        self,
        data_list: list[Dict[str, Any]],
        output_dir: Optional[str] = None
    ) -> list[str]:
        """
        Generate multiple PDFs in batch.
        
        Args:
            data_list: List of data dictionaries
            output_dir: Output directory for all PDFs
            
        Returns:
            List of generated PDF paths
        """
        results = []
        
        for i, data in enumerate(data_list):
            try:
                if output_dir:
                    filename = self.get_output_filename(data, prefix=f"document_{i+1}")
                    output_path = str(Path(output_dir) / filename)
                else:
                    output_path = None
                
                pdf_path = self.generate(data, output_path)
                results.append(pdf_path)
                
            except Exception as e:
                logger.error(f"Error generating PDF {i+1}: {e}")
                results.append(None)
        
        return results
    
    def merge_pdfs(
        self,
        pdf_paths: list[str],
        output_path: str
    ) -> str:
        """
        Merge multiple PDFs into one.
        
        Args:
            pdf_paths: List of PDF file paths to merge
            output_path: Output path for merged PDF
            
        Returns:
            Path to merged PDF
        """
        try:
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            for pdf_path in pdf_paths:
                if Path(pdf_path).exists():
                    merger.append(pdf_path)
                else:
                    logger.warning(f"PDF not found, skipping: {pdf_path}")
            
            merger.write(output_path)
            merger.close()
            
            logger.info(f"Merged {len(pdf_paths)} PDFs to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check PDF generator health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Test with minimal data
            test_data = {'test': 'health_check'}
            
            # Try to generate PDF bytes
            pdf_bytes = self.generate_to_bytes(test_data)
            
            return {
                'status': 'healthy',
                'generator': self.__class__.__name__,
                'can_generate': len(pdf_bytes) > 0,
                'message': 'PDF generator is working'
            }
            
        except Exception as e:
            logger.error(f"PDF generator health check failed: {e}")
            return {
                'status': 'unhealthy',
                'generator': self.__class__.__name__,
                'error': str(e)
            }