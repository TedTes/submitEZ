"""
Supabase storage implementation for file operations.
"""

from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
import io
from app.infrastructure.storage.base_storage import BaseStorage
from app.infrastructure.database import get_storage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseStorage(BaseStorage):
    """
    Concrete implementation of storage using Supabase Storage.
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize Supabase storage.
        
        Args:
            bucket_name: Name of storage bucket (defaults to config)
        """
        if bucket_name is None:
            import os
            bucket_name = os.getenv('SUPABASE_BUCKET', 'submissions')
        
        super().__init__(bucket_name)
        self._storage_client = None
    
    @property
    def storage_client(self):
        """Get Supabase storage client (lazy loading)."""
        if self._storage_client is None:
            self._storage_client = get_storage()
        return self._storage_client
    
    @property
    def bucket(self):
        """Get bucket reference."""
        return self.storage_client.from_(self.bucket_name)
    
    def upload_file(
        self,
        file_data: BinaryIO,
        file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Supabase Storage.
        
        Args:
            file_data: File binary data
            file_path: Path/key for file in storage
            content_type: MIME type of file
            metadata: Additional metadata
            
        Returns:
            Dictionary with file info
        """
        try:
            # Read file data if it's a file-like object
            if hasattr(file_data, 'read'):
                file_bytes = file_data.read()
            else:
                file_bytes = file_data
            
            # Prepare upload options
            file_options = {}
            if content_type:
                file_options['content-type'] = content_type
            if metadata:
                file_options['x-upsert'] = 'true'  # Allow overwrite
            
            # Upload to Supabase
            response = self.bucket.upload(
                path=file_path,
                file=file_bytes,
                file_options=file_options
            )
            
            # Get public URL
            public_url = self.bucket.get_public_url(file_path)
            
            logger.info(f"Uploaded file to Supabase: {file_path}")
            
            return {
                'path': file_path,
                'url': public_url,
                'bucket': self.bucket_name,
                'size': len(file_bytes) if isinstance(file_bytes, bytes) else None,
                'content_type': content_type,
                'uploaded_at': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            raise
    
    def download_file(self, file_path: str) -> bytes:
        """
        Download file from Supabase Storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            File binary data
        """
        try:
            response = self.bucket.download(file_path)
            
            logger.debug(f"Downloaded file from Supabase: {file_path}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from Supabase Storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            True if deleted successfully
        """
        try:
            self.bucket.remove([file_path])
            
            logger.info(f"Deleted file from Supabase: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists in Supabase Storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            True if file exists
        """
        try:
            # Try to get file info
            files = self.bucket.list(path=file_path)
            
            # Check if exact file exists in results
            return any(f['name'] == file_path.split('/')[-1] for f in files)
            
        except Exception as e:
            logger.debug(f"Error checking file existence {file_path}: {e}")
            return False
    
    def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Get signed URL for file access.
        
        Args:
            file_path: Path/key of file in storage
            expires_in: URL expiration time in seconds
            
        Returns:
            Signed URL for file access
        """
        try:
            # Create signed URL
            signed_url = self.bucket.create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            return signed_url['signedURL']
            
        except Exception as e:
            logger.error(f"Error creating signed URL for {file_path}: {e}")
            # Fallback to public URL
            return self.bucket.get_public_url(file_path)
    
    def list_files(
        self,
        prefix: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in Supabase Storage bucket.
        
        Args:
            prefix: Filter files by path prefix
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            # List files with optional prefix
            options = {}
            if limit:
                options['limit'] = limit
            if prefix:
                options['prefix'] = prefix
            
            files = self.bucket.list(path=prefix or '', **options)
            
            # Format file information
            result = []
            for file in files:
                result.append({
                    'name': file.get('name'),
                    'path': f"{prefix}/{file.get('name')}" if prefix else file.get('name'),
                    'size': file.get('metadata', {}).get('size'),
                    'content_type': file.get('metadata', {}).get('mimetype'),
                    'created_at': file.get('created_at'),
                    'updated_at': file.get('updated_at'),
                    'last_accessed_at': file.get('last_accessed_at')
                })
            
            return result[:limit] if limit else result
            
        except Exception as e:
            logger.error(f"Error listing files with prefix {prefix}: {e}")
            return []
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata from Supabase Storage.
        
        Args:
            file_path: Path/key of file in storage
            
        Returns:
            File metadata dictionary
        """
        try:
            # Get file list to find metadata
            path_parts = file_path.rsplit('/', 1)
            if len(path_parts) > 1:
                prefix, filename = path_parts
            else:
                prefix = ''
                filename = file_path
            
            files = self.bucket.list(path=prefix)
            
            # Find matching file
            for file in files:
                if file.get('name') == filename:
                    return {
                        'name': file.get('name'),
                        'path': file_path,
                        'size': file.get('metadata', {}).get('size'),
                        'content_type': file.get('metadata', {}).get('mimetype'),
                        'created_at': file.get('created_at'),
                        'updated_at': file.get('updated_at'),
                        'last_accessed_at': file.get('last_accessed_at'),
                        'bucket': self.bucket_name
                    }
            
            raise FileNotFoundError(f"File not found: {file_path}")
            
        except Exception as e:
            logger.error(f"Error getting file metadata for {file_path}: {e}")
            raise
    
    def batch_delete(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Delete multiple files from Supabase Storage.
        
        Args:
            file_paths: List of file paths to delete
            
        Returns:
            Dictionary mapping file paths to deletion success
        """
        try:
            # Supabase supports batch delete
            self.bucket.remove(file_paths)
            
            logger.info(f"Batch deleted {len(file_paths)} files from Supabase")
            
            # Return success for all
            return {path: True for path in file_paths}
            
        except Exception as e:
            logger.error(f"Error batch deleting files: {e}")
            # Fallback to individual deletion
            return super().batch_delete(file_paths)
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy file within Supabase Storage.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if copied successfully
        """
        try:
            # Supabase doesn't have native copy, so download and re-upload
            file_data = self.download_file(source_path)
            metadata = self.get_file_metadata(source_path)
            
            self.upload_file(
                io.BytesIO(file_data),
                destination_path,
                content_type=metadata.get('content_type')
            )
            
            logger.info(f"Copied file from {source_path} to {destination_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return False
    
    def create_bucket_if_not_exists(self) -> bool:
        """
        Create bucket if it doesn't exist.
        
        Returns:
            True if bucket exists or was created
        """
        try:
            # Check if bucket exists by trying to list files
            self.bucket.list(path='', limit=1)
            return True
            
        except Exception as e:
            logger.warning(f"Bucket {self.bucket_name} may not exist: {e}")
            try:
                # Try to create bucket (requires admin privileges)
                self.storage_client.create_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
                return True
            except Exception as create_error:
                logger.error(f"Failed to create bucket: {create_error}")
                return False


# Global storage instance
_storage_instance: Optional[SupabaseStorage] = None


def get_supabase_storage() -> SupabaseStorage:
    """
    Get or create Supabase storage singleton.
    
    Returns:
        SupabaseStorage instance
    """
    global _storage_instance
    
    if _storage_instance is None:
        _storage_instance = SupabaseStorage()
    
    return _storage_instance