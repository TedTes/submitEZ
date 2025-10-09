"""
File handling utilities for SubmitEZ.
"""

import os
import mimetypes
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Set
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'docx', 'doc'}

MIME_TYPE_MAP = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/msword': 'doc',
}


def allowed_file(filename: str, allowed_extensions: Optional[Set[str]] = None) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (default: ALLOWED_EXTENSIONS)
        
    Returns:
        True if file extension is allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension without dot (e.g., 'pdf')
    """
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_mime_type(filename: str) -> Optional[str]:
    """
    Get MIME type from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME type string or None
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def validate_mime_type(mime_type: str) -> bool:
    """
    Validate if MIME type is allowed.
    
    Args:
        mime_type: MIME type string
        
    Returns:
        True if MIME type is allowed
    """
    return mime_type in MIME_TYPE_MAP


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Use Werkzeug's secure_filename
    safe_name = secure_filename(filename)
    
    # Ensure filename isn't too long
    if len(safe_name) > max_length:
        name, ext = os.path.splitext(safe_name)
        name = name[:max_length - len(ext)]
        safe_name = name + ext
    
    return safe_name


def generate_unique_filename(filename: str, prefix: str = '') -> str:
    """
    Generate unique filename with timestamp and hash.
    
    Args:
        filename: Original filename
        prefix: Optional prefix for filename
        
    Returns:
        Unique filename
    """
    import time
    import uuid
    
    # Get extension
    ext = get_file_extension(filename)
    
    # Generate unique identifier
    timestamp = int(time.time() * 1000)
    unique_id = uuid.uuid4().hex[:8]
    
    # Build filename
    parts = [prefix, str(timestamp), unique_id]
    parts = [p for p in parts if p]  # Remove empty parts
    
    unique_name = '_'.join(parts)
    
    return f"{unique_name}.{ext}" if ext else unique_name


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def validate_file_size(file_path: str, max_size_mb: int = 16) -> Tuple[bool, Optional[str]]:
    """
    Validate file size against maximum.
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        size_bytes = get_file_size(file_path)
        max_bytes = max_size_mb * 1024 * 1024
        
        if size_bytes > max_bytes:
            actual_size = format_file_size(size_bytes)
            max_size = format_file_size(max_bytes)
            return False, f"File size {actual_size} exceeds maximum {max_size}"
        
        return True, None
    except Exception as e:
        return False, f"Error validating file size: {str(e)}"


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate file hash for integrity checking.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of file hash
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def validate_file_upload(
    file: FileStorage,
    max_size_mb: int = 16,
    allowed_extensions: Optional[Set[str]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Args:
        file: Werkzeug FileStorage object
        max_size_mb: Maximum file size in MB
        allowed_extensions: Set of allowed extensions
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "No filename provided"
    
    # Check file extension
    if not allowed_file(file.filename, allowed_extensions):
        ext = get_file_extension(file.filename)
        return False, f"File type '.{ext}' not allowed. Allowed types: {', '.join(allowed_extensions or ALLOWED_EXTENSIONS)}"
    
    # Check MIME type if available
    if file.mimetype and not validate_mime_type(file.mimetype):
        return False, f"Invalid file type: {file.mimetype}"
    
    # Check file size if available
    if hasattr(file, 'content_length') and file.content_length:
        max_bytes = max_size_mb * 1024 * 1024
        if file.content_length > max_bytes:
            actual_size = format_file_size(file.content_length)
            max_size = format_file_size(max_bytes)
            return False, f"File size {actual_size} exceeds maximum {max_size}"
    
    return True, None


def ensure_directory_exists(directory: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def delete_file_safe(file_path: str) -> bool:
    """
    Safely delete file, ignoring errors.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False


def get_file_info(file_path: str) -> dict:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    stat = path.stat()
    
    return {
        'name': path.name,
        'extension': path.suffix.lstrip('.'),
        'size_bytes': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'mime_type': get_mime_type(str(path)),
        'created_at': stat.st_ctime,
        'modified_at': stat.st_mtime,
        'is_file': path.is_file(),
        'exists': path.exists(),
    }