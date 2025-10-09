"""
Database infrastructure package for SubmitEZ.
"""

from .supabase_client import (
    SupabaseClient,
    get_supabase_client,
    get_db,
    get_table,
    get_storage,
    check_database_health
)

__all__ = [
    'SupabaseClient',
    'get_supabase_client',
    'get_db',
    'get_table',
    'get_storage',
    'check_database_health'
]