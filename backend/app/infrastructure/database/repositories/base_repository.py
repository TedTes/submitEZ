"""
Abstract base repository pattern for database operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Generic, TypeVar
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository implementing common CRUD operations.
    
    Following Repository pattern for clean separation between
    domain logic and data access logic.
    """
    
    def __init__(self, table_name: str):
        """
        Initialize repository.
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
        self._client = None
    
    @property
    def client(self):
        """Get database client (lazy loading)."""
        if self._client is None:
            from app.infrastructure.database import get_db
            self._client = get_db()
        return self._client
    
    @property
    def table(self):
        """Get table reference."""
        return self.client.table(self.table_name)
    
    @abstractmethod
    def _to_dict(self, entity: T) -> Dict[str, Any]:
        """
        Convert domain entity to database dictionary.
        
        Args:
            entity: Domain entity
            
        Returns:
            Dictionary for database storage
        """
        pass
    
    @abstractmethod
    def _from_dict(self, data: Dict[str, Any]) -> T:
        """
        Convert database dictionary to domain entity.
        
        Args:
            data: Database record dictionary
            
        Returns:
            Domain entity
        """
        pass
    
    def create(self, entity: T) -> T:
        """
        Create a new record.
        
        Args:
            entity: Domain entity to create
            
        Returns:
            Created entity with database-generated fields
        """
        try:
            data = self._to_dict(entity)
            
            response = self.table.insert(data).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Created {self.table_name} record")
                return self._from_dict(response.data[0])
            
            raise Exception(f"Failed to create {self.table_name} record")
            
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}")
            raise
    
    def get_by_id(self, id: str) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            id: Record identifier
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            response = self.table.select('*').eq('id', id).execute()
            
            if response.data and len(response.data) > 0:
                return self._from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting {self.table_name} by id {id}: {e}")
            raise
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Get all records with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of entities
        """
        try:
            query = self.table.select('*')
            
            if limit:
                query = query.limit(limit)
            
            if offset:
                query = query.offset(offset)
            
            response = query.execute()
            
            if response.data:
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting all {self.table_name}: {e}")
            raise
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Update record by ID.
        
        Args:
            id: Record identifier
            data: Fields to update
            
        Returns:
            Updated entity if successful, None otherwise
        """
        try:
            response = self.table.update(data).eq('id', id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Updated {self.table_name} record {id}")
                return self._from_dict(response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating {self.table_name} {id}: {e}")
            raise
    
    def delete(self, id: str) -> bool:
        """
        Delete record by ID.
        
        Args:
            id: Record identifier
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            response = self.table.delete().eq('id', id).execute()
            
            logger.info(f"Deleted {self.table_name} record {id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting {self.table_name} {id}: {e}")
            raise
    
    def exists(self, id: str) -> bool:
        """
        Check if record exists.
        
        Args:
            id: Record identifier
            
        Returns:
            True if exists, False otherwise
        """
        try:
            response = self.table.select('id').eq('id', id).execute()
            return response.data and len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking existence of {self.table_name} {id}: {e}")
            raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            filters: Filter conditions
            
        Returns:
            Number of records
        """
        try:
            query = self.table.select('id', count='exact')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            
            return response.count if response.count is not None else 0
            
        except Exception as e:
            logger.error(f"Error counting {self.table_name}: {e}")
            raise
    
    def find_by(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[T]:
        """
        Find records by filter conditions.
        
        Args:
            filters: Dictionary of field:value pairs
            limit: Maximum number of records
            
        Returns:
            List of matching entities
        """
        try:
            query = self.table.select('*')
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            
            if response.data:
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error finding {self.table_name} by filters: {e}")
            raise
    
    def find_one_by(self, filters: Dict[str, Any]) -> Optional[T]:
        """
        Find single record by filter conditions.
        
        Args:
            filters: Dictionary of field:value pairs
            
        Returns:
            Entity if found, None otherwise
        """
        results = self.find_by(filters, limit=1)
        return results[0] if results else None
    
    def batch_create(self, entities: List[T]) -> List[T]:
        """
        Create multiple records in batch.
        
        Args:
            entities: List of entities to create
            
        Returns:
            List of created entities
        """
        try:
            data_list = [self._to_dict(entity) for entity in entities]
            
            response = self.table.insert(data_list).execute()
            
            if response.data:
                logger.info(f"Batch created {len(response.data)} {self.table_name} records")
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error batch creating {self.table_name}: {e}")
            raise
    
    def batch_delete(self, ids: List[str]) -> bool:
        """
        Delete multiple records by IDs.
        
        Args:
            ids: List of record identifiers
            
        Returns:
            True if successful
        """
        try:
            response = self.table.delete().in_('id', ids).execute()
            
            logger.info(f"Batch deleted {len(ids)} {self.table_name} records")
            return True
            
        except Exception as e:
            logger.error(f"Error batch deleting {self.table_name}: {e}")
            raise