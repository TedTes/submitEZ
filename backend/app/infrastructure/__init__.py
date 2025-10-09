"""
Infrastructure layer package for SubmitEZ.

Contains external service integrations.
"""

from .database import (
    get_supabase_client,
    get_db,
    get_table,
    get_storage,
    check_database_health
)

__all__ = [
    'get_supabase_client',
    'get_db',
    'get_table',
    'get_storage',
    'check_database_health'
]