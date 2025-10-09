"""
Abstract base storage interface for file operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseStorage(ABC):
    """
    Abstract base class for file storage operations.
    
    Supports Dependency Inversion Principle - allows swapping
    storage implementations (Supabase, S3, Local, etc.) without
    changing business logic.
    """
    
    def __init__(self, bucket_name: str):
        """
        Initialize storage with bucket name.
        
        Args:
            bucket_name: Name of storage bucket/container
        """
        self.bucket_name = bucket_name
    
    @abstractmethod
    def upload_file(
        self,
        file_data: BinaryIO,
        file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to storage.
        
        Args:
            file_data: File binary data
            file_path: Path/key for file in storage
            content_type: MIME type of file
            metadata: Additional metadata
            
        Returns:
            Dictionary with file info (url, path, size, etc.)
        """
        pass
    
    @abstractmethod
    def download_file(self, file_path: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            File binary data
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            True if file exists
        """
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get signed URL for file access.
        
        Args:
            file_path: Path/key of file in storage
            expires_in: URL expiration time in seconds
            
        Returns:
            Signed URL for file access
        """
        pass
    
    @abstractmethod
    def list_files(
        self,
        prefix: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in storage bucket.
        
        Args:
            prefix: Filter files by path prefix
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        pass
    
    @abstractmethod
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            File metadata dictionary
        """
        pass
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy file within storage.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if copied successfully
        """
        try:
            # Default implementation: download and re-upload
            file_data = self.download_file(source_path)
            metadata = self.get_file_metadata(source_path)
            
            self.upload_file(
                file_data,
                destination_path,
                content_type=metadata.get('content_type'),
                metadata=metadata
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move file within storage.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if moved successfully
        """
        try:
            # Copy then delete
            if self.copy_file(source_path, destination_path):
                return self.delete_file(source_path)
            return False
            
        except Exception as e:
            logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            File size in bytes or None if not found
        """
        try:
            metadata = self.get_file_metadata(file_path)
            return metadata.get('size')
        except Exception as e:
            logger.error(f"Error getting file size for {file_path}: {e}")
            return None
    
    def batch_delete(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Delete multiple files.
        
        Args:
            file_paths: List of file paths to delete
            
        Returns:
            Dictionary mapping file paths to deletion success
        """
        results = {}
        
        for file_path in file_paths:
            try:
                results[file_path] = self.delete_file(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check storage service health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Try to list files to verify connection
            self.list_files(limit=1)
            
            return {
                'status': 'healthy',
                'bucket': self.bucket_name,
                'message': 'Storage connection is working'
            }
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                'status': 'unhealthy',
                'bucket': self.bucket_name,
                'error': str(e)
            }