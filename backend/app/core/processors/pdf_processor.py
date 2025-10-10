"""
PDF document processor for text and table extraction.
"""

from typing import Optional, List, Dict, Any
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from app.core.processors.base_processor import BaseProcessor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFProcessor(BaseProcessor):
    """
    Processor for PDF documents using PyMuPDF and pdfplumber.
    
    Uses:
    - PyMuPDF (fitz) for fast text extraction and metadata
    - pdfplumber for reliable table extraction
    """
    
    def __init__(self):
        """Initialize PDF processor."""
        super().__init__()
        self.supported_extensions = ['.pdf']
        self.supported_mime_types = ['application/pdf']
    
    def can_process(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if processor can handle PDF files.
        
        Args:
            file_path: Path to file
            mime_type: Optional MIME type
            
        Returns:
            True if file is PDF
        """
        file = Path(file_path)
        
        # Check extension
        if file.suffix.lower() in self.supported_extensions:
            return True
        
        # Check MIME type
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        return False
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text_parts = []
            
            # Open PDF with PyMuPDF
            doc = fitz.open(file_path)
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    text_parts.append(text)
            
            doc.close()
            
            # Combine all text
            full_text = '\n\n'.join(text_parts)
            
            # Clean text
            full_text = self.clean_text(full_text)
            
            logger.debug(f"Extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_tables(self, file_path: str) -> List[List[List[str]]]:
        """
        Extract tables from PDF using pdfplumber.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of tables (each table is list of rows)
        """
        try:
            all_tables = []
            
            # Open PDF with pdfplumber
            with pdfplumber.open(file_path) as pdf:
                # Extract tables from each page
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    if tables:
                        for table in tables:
                            # Filter out empty rows and clean cells
                            cleaned_table = []
                            for row in table:
                                if row and any(cell for cell in row):
                                    cleaned_row = [
                                        str(cell).strip() if cell else ''
                                        for cell in row
                                    ]
                                    cleaned_table.append(cleaned_row)
                            
                            if cleaned_table:
                                all_tables.append(cleaned_table)
            
            logger.debug(f"Extracted {len(all_tables)} tables from PDF")
            
            return all_tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            return []
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with metadata
        """
        metadata = super().extract_metadata(file_path)
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(file_path)
            
            # Get PDF metadata
            pdf_metadata = doc.metadata
            
            metadata.update({
                'page_count': len(doc),
                'title': pdf_metadata.get('title', ''),
                'author': pdf_metadata.get('author', ''),
                'subject': pdf_metadata.get('subject', ''),
                'creator': pdf_metadata.get('creator', ''),
                'producer': pdf_metadata.get('producer', ''),
                'creation_date': pdf_metadata.get('creationDate', ''),
                'modification_date': pdf_metadata.get('modDate', ''),
                'is_encrypted': doc.is_encrypted,
                'is_pdf': True
            })
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {e}")
        
        return metadata
    
    def get_page_count(self, file_path: str) -> Optional[int]:
        """
        Get number of pages in PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            return page_count
            
        except Exception as e:
            logger.error(f"Error getting PDF page count: {e}")
            return None
    
    def extract_text_by_page(self, file_path: str) -> List[str]:
        """
        Extract text from each page separately.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of text strings (one per page)
        """
        try:
            pages_text = []
            
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages_text.append(self.clean_text(text))
            
            doc.close()
            
            return pages_text
            
        except Exception as e:
            logger.error(f"Error extracting text by page: {e}")
            return []
    
    def extract_images(self, file_path: str) -> List[bytes]:
        """
        Extract images from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of image data as bytes
        """
        try:
            images = []
            
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image['image']
                    images.append(image_bytes)
            
            doc.close()
            
            logger.debug(f"Extracted {len(images)} images from PDF")
            
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []
    
    def is_scanned_pdf(self, file_path: str) -> bool:
        """
        Check if PDF is scanned (image-based) or text-based.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned
        """
        try:
            text = self.extract_text(file_path)
            
            # If very little text extracted, likely scanned
            if len(text.strip()) < 100:
                return True
            
            # Check ratio of text to pages
            page_count = self.get_page_count(file_path)
            if page_count:
                chars_per_page = len(text) / page_count
                
                # Less than 50 characters per page suggests scanned
                if chars_per_page < 50:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking if PDF is scanned: {e}")
            return False
    
    def search_text(self, file_path: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for text in PDF.
        
        Args:
            file_path: Path to PDF file
            search_term: Text to search for
            
        Returns:
            List of matches with page numbers and positions
        """
        try:
            matches = []
            
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_instances = page.search_for(search_term)
                
                for inst in text_instances:
                    matches.append({
                        'page': page_num + 1,
                        'term': search_term,
                        'rect': inst
                    })
            
            doc.close()
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching PDF: {e}")
            return []
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get PDF processor information.
        
        Returns:
            Dictionary with processor details
        """
        info = super().get_processor_info()
        info.update({
            'can_extract_images': True,
            'can_get_page_count': True,
            'can_extract_by_page': True,
            'can_detect_scanned': True,
            'can_search': True,
            'libraries': ['PyMuPDF', 'pdfplumber']
        })
        return info


# Global PDF processor instance
_pdf_processor: Optional[PDFProcessor] = None


def get_pdf_processor() -> PDFProcessor:
    """
    Get or create PDF processor singleton.
    
    Returns:
        PDFProcessor instance
    """
    global _pdf_processor
    
    if _pdf_processor is None:
        _pdf_processor = PDFProcessor()
    
    return _pdf_processor