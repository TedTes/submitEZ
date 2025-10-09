"""
Submission repository for database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.domain.models import Submission
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SubmissionRepository(BaseRepository[Submission]):
    """
    Repository for Submission entity with specific database operations.
    """
    
    def __init__(self):
        """Initialize submission repository."""
        super().__init__('submissions')
    
    def _to_dict(self, entity: Submission) -> Dict[str, Any]:
        """
        Convert Submission entity to database dictionary.
        
        Args:
            entity: Submission entity
            
        Returns:
            Dictionary for database storage
        """
        return entity.to_dict()
    
    def _from_dict(self, data: Dict[str, Any]) -> Submission:
        """
        Convert database dictionary to Submission entity.
        
        Args:
            data: Database record
            
        Returns:
            Submission entity
        """
        return Submission.from_dict(data)
    
    def get_by_status(self, status: str, limit: Optional[int] = None) -> List[Submission]:
        """
        Get submissions by status.
        
        Args:
            status: Submission status
            limit: Maximum number of records
            
        Returns:
            List of submissions
        """
        try:
            query = self.table.select('*').eq('status', status).order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            
            if response.data:
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting submissions by status {status}: {e}")
            raise
    
    def update_status(self, id: str, new_status: str) -> Optional[Submission]:
        """
        Update submission status.
        
        Args:
            id: Submission ID
            new_status: New status value
            
        Returns:
            Updated submission
        """
        try:
            data = {
                'status': new_status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Set specific timestamps based on status
            if new_status == 'extracted':
                data['extracted_at'] = datetime.utcnow().isoformat()
            elif new_status == 'validated':
                data['validated_at'] = datetime.utcnow().isoformat()
            elif new_status == 'completed':
                data['generated_at'] = datetime.utcnow().isoformat()
                data['submitted_at'] = datetime.utcnow().isoformat()
            
            return self.update(id, data)
            
        except Exception as e:
            logger.error(f"Error updating submission status {id}: {e}")
            raise
    
    def get_recent(self, limit: int = 10) -> List[Submission]:
        """
        Get most recent submissions.
        
        Args:
            limit: Number of submissions to return
            
        Returns:
            List of recent submissions
        """
        try:
            response = self.table.select('*').order('created_at', desc=True).limit(limit).execute()
            
            if response.data:
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent submissions: {e}")
            raise
    
    def search_by_applicant(self, search_term: str, limit: Optional[int] = 20) -> List[Submission]:
        """
        Search submissions by applicant name.
        
        Args:
            search_term: Search term for applicant business name
            limit: Maximum number of results
            
        Returns:
            List of matching submissions
        """
        try:
            query = self.table.select('*').ilike('applicant->>business_name', f'%{search_term}%')
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            
            if response.data:
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching submissions by applicant: {e}")
            raise
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Submission]:
        """
        Get submissions within date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of submissions
        """
        try:
            response = (
                self.table.select('*')
                .gte('created_at', start_date.isoformat())
                .lte('created_at', end_date.isoformat())
                .order('created_at', desc=True)
                .execute()
            )
            
            if response.data:
                return [self._from_dict(record) for record in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting submissions by date range: {e}")
            raise
    
    def get_pending_validation(self, limit: Optional[int] = None) -> List[Submission]:
        """
        Get submissions pending validation.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of submissions
        """
        return self.get_by_status('extracted', limit)
    
    def get_pending_generation(self, limit: Optional[int] = None) -> List[Submission]:
        """
        Get submissions pending PDF generation.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of submissions
        """
        return self.get_by_status('validated', limit)
    
    def get_completed(self, limit: Optional[int] = None) -> List[Submission]:
        """
        Get completed submissions.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of submissions
        """
        return self.get_by_status('completed', limit)
    
    def add_uploaded_file(self, id: str, file_info: Dict[str, Any]) -> Optional[Submission]:
        """
        Add uploaded file reference to submission.
        
        Args:
            id: Submission ID
            file_info: File information dictionary
            
        Returns:
            Updated submission
        """
        try:
            # Get current submission
            submission = self.get_by_id(id)
            if not submission:
                return None
            
            # Add file to list
            submission.add_uploaded_file(file_info)
            
            # Update in database
            data = {
                'uploaded_files': submission.uploaded_files,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return self.update(id, data)
            
        except Exception as e:
            logger.error(f"Error adding uploaded file to submission {id}: {e}")
            raise
    
    def add_generated_file(self, id: str, file_info: Dict[str, Any]) -> Optional[Submission]:
        """
        Add generated file reference to submission.
        
        Args:
            id: Submission ID
            file_info: File information dictionary
            
        Returns:
            Updated submission
        """
        try:
            # Get current submission
            submission = self.get_by_id(id)
            if not submission:
                return None
            
            # Add file to list
            submission.add_generated_file(file_info)
            
            # Update in database
            data = {
                'generated_files': submission.generated_files,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return self.update(id, data)
            
        except Exception as e:
            logger.error(f"Error adding generated file to submission {id}: {e}")
            raise
    
    def set_validation_results(
        self,
        id: str,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> Optional[Submission]:
        """
        Set validation results for submission.
        
        Args:
            id: Submission ID
            errors: Validation errors
            warnings: Validation warnings
            
        Returns:
            Updated submission
        """
        try:
            data = {
                'validation_errors': errors,
                'validation_warnings': warnings,
                'is_valid': len(errors) == 0,
                'validated_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return self.update(id, data)
            
        except Exception as e:
            logger.error(f"Error setting validation results for submission {id}: {e}")
            raise
    
    def set_extraction_metadata(
        self,
        id: str,
        metadata: Dict[str, Any],
        confidence: Optional[float] = None
    ) -> Optional[Submission]:
        """
        Set extraction metadata for submission.
        
        Args:
            id: Submission ID
            metadata: Extraction metadata
            confidence: Overall confidence score
            
        Returns:
            Updated submission
        """
        try:
            data = {
                'extraction_metadata': metadata,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if confidence is not None:
                data['extraction_confidence'] = confidence
            
            return self.update(id, data)
            
        except Exception as e:
            logger.error(f"Error setting extraction metadata for submission {id}: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get submission statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = {
                'total': self.count(),
                'by_status': {}
            }
            
            # Count by status
            statuses = ['draft', 'uploaded', 'extracting', 'extracted', 'validating', 
                       'validated', 'generating', 'completed', 'error']
            
            for status in statuses:
                count = self.count({'status': status})
                if count > 0:
                    stats['by_status'][status] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting submission statistics: {e}")
            raise