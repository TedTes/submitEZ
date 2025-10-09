"""
Supabase client singleton for database connections.
"""

from supabase import create_client, Client
from typing import Optional
import os
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseClient:
    """
    Singleton class for Supabase client management.
    Ensures single connection pool across application.
    """
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase client if not already initialized."""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client with configuration."""
        try:
            # Get configuration from environment
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                raise ValueError(
                    "Missing Supabase credentials. "
                    "Please set SUPABASE_URL and SUPABASE_KEY environment variables."
                )
            
            # Create Supabase client
            self._client = create_client(url, key)
            
            # Test connection
            self._test_connection()
            
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def _test_connection(self):
        """Test database connection."""
        try:
            # Simple query to test connection
            response = self._client.table('submissions').select('id').limit(1).execute()
            logger.debug("Supabase connection test successful")
        except Exception as e:
            logger.warning(f"Supabase connection test failed (table may not exist yet): {e}")
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def get_table(self, table_name: str):
        """
        Get table reference for queries.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table reference
        """
        return self.client.table(table_name)
    
    def get_storage(self):
        """
        Get storage reference for file operations.
        
        Returns:
            Storage reference
        """
        return self.client.storage
    
    def health_check(self) -> dict:
        """
        Check database health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Try a simple query
            self._client.table('submissions').select('id').limit(1).execute()
            
            return {
                'status': 'healthy',
                'database': 'connected',
                'message': 'Supabase connection is working'
            }
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }
    
    def close(self):
        """Close Supabase connection."""
        # Supabase Python client doesn't require explicit closing
        # but we provide this method for consistency
        logger.info("Supabase client cleanup called")
        self._client = None


# Global client instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """
    Get or create Supabase client singleton.
    
    Returns:
        SupabaseClient instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    
    return _supabase_client


def get_db() -> Client:
    """
    Get Supabase database client.
    
    Returns:
        Supabase Client instance
    """
    return get_supabase_client().client


def get_table(table_name: str):
    """
    Get table reference for queries.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Table reference
    """
    return get_supabase_client().get_table(table_name)


def get_storage():
    """
    Get storage reference for file operations.
    
    Returns:
        Storage reference
    """
    return get_supabase_client().get_storage()


def check_database_health() -> dict:
    """
    Check database connection health.
    
    Returns:
        Health status dictionary
    """
    return get_supabase_client().health_check()