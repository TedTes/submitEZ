"""
Storage infrastructure package for SubmitEZ.
"""

from .base_storage import BaseStorage
from .supabase_storage import SupabaseStorage, get_supabase_storage

__all__ = [
    'BaseStorage',
    'SupabaseStorage',
    'get_supabase_storage'
]