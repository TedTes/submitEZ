"""
Extraction service for orchestrating document processing and AI extraction.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
from app.core.processors import get_processor_factory
from app.infrastructure.ai import get_openai_client, get_extraction_prompt
from app.infrastructure.storage import get_supabase_storage
from app.domain.models import Applicant, PropertyLocation, Coverage, LossHistory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractionService:
    """
    Service for orchestrating document extraction workflow.
    
    Coordinates:
    - Document processing (text/table extraction)
    - AI-powered data extraction
    - Field mapping and validation
    - Confidence scoring
    """
    
    def __init__(self):
        """Initialize extraction service."""
        self.processor_factory = get_processor_factory()
        self.llm_client = get_openai_client()
        self.storage = get_supabase_storage()
    
    def extract_from_file(
        self,
        file_path: str,
        submission_id: str,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a single file.
        
        Args:
            file_path: Path to file
            submission_id: Submission identifier
            mime_type: Optional MIME type
            
        Returns:
            Extraction result dictionary
        """
        extraction_id = str(uuid4())
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting extraction for file: {file_path}")
            
            # Step 1: Process document
            processed = self.processor_factory.process_file(file_path, mime_type)
            
            if not processed.get('success'):
                return {
                    'extraction_id': extraction_id,
                    'submission_id': submission_id,
                    'status': 'failed',
                    'error': processed.get('error'),
                    'file_path': file_path
                }
            
            # Step 2: Extract structured data using AI
            extracted_data = self._extract_with_llm(
                text=processed.get('text', ''),
                tables=processed.get('tables', []),
                metadata=processed.get('metadata', {})
            )
            
            # Step 3: Calculate confidence scores
            extraction_result = self._calculate_confidence(extracted_data)
            
            # Step 4: Build result
            result = {
                'extraction_id': extraction_id,
                'submission_id': submission_id,
                'status': 'completed',
                'file_path': file_path,
                'processor_used': processed.get('processor'),
                'started_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'duration_seconds': (datetime.utcnow() - start_time).total_seconds(),
                'extracted_data': extraction_result,
                'metadata': processed.get('metadata', {})
            }
            
            logger.info(f"Extraction completed for {file_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from file {file_path}: {e}")
            return {
                'extraction_id': extraction_id,
                'submission_id': submission_id,
                'status': 'failed',
                'error': str(e),
                'file_path': file_path,
                'started_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat()
            }
    
    def extract_from_files(
        self,
        file_paths: List[str],
        submission_id: str,
        mime_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract data from multiple files.
        
        Args:
            file_paths: List of file paths
            submission_id: Submission identifier
            mime_types: Optional list of MIME types
            
        Returns:
            Combined extraction result
        """
        extraction_id = str(uuid4())
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting batch extraction for {len(file_paths)} files")
            
            # Process each file
            file_results = []
            for i, file_path in enumerate(file_paths):
                mime_type = mime_types[i] if mime_types and i < len(mime_types) else None
                result = self.extract_from_file(file_path, submission_id, mime_type)
                file_results.append(result)
            
            # Merge extracted data from all files
            merged_data = self._merge_extraction_results(file_results)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(file_results)
            
            result = {
                'extraction_id': extraction_id,
                'submission_id': submission_id,
                'status': 'completed',
                'total_files': len(file_paths),
                'successful_files': sum(1 for r in file_results if r.get('status') == 'completed'),
                'failed_files': sum(1 for r in file_results if r.get('status') == 'failed'),
                'started_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat(),
                'duration_seconds': (datetime.utcnow() - start_time).total_seconds(),
                'overall_confidence': overall_confidence,
                'extracted_data': merged_data,
                'file_results': file_results
            }
            
            logger.info(f"Batch extraction completed: {result['successful_files']}/{len(file_paths)} successful")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in batch extraction: {e}")
            return {
                'extraction_id': extraction_id,
                'submission_id': submission_id,
                'status': 'failed',
                'error': str(e),
                'started_at': start_time.isoformat(),
                'completed_at': datetime.utcnow().isoformat()
            }
    
    def _extract_with_llm(
        self,
        text: str,
        tables: List[List[List[str]]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data using LLM.
        
        Args:
            text: Extracted text
            tables: Extracted tables
            metadata: Document metadata
            
        Returns:
            Extracted structured data
        """
        try:
            extracted = {
                'applicant': None,
                'locations': [],
                'coverage': None,
                'loss_history': []
            }
            
            # Extract applicant information
            applicant_data = self._extract_applicant(text)
            if applicant_data:
                extracted['applicant'] = applicant_data
            
            # Extract property locations
            locations = self._extract_locations(text, tables)
            if locations:
                extracted['locations'] = locations
            
            # Extract coverage information
            coverage_data = self._extract_coverage(text)
            if coverage_data:
                extracted['coverage'] = coverage_data
            
            # Extract loss history
            losses = self._extract_losses(text, tables)
            if losses:
                extracted['loss_history'] = losses
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return {}
    
    def _extract_applicant(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract applicant information using LLM."""
        try:
            system_prompt, schema = get_extraction_prompt('applicant', text)
            
            result = self.llm_client.extract_structured_data(
                text=text,
                schema=schema,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Add confidence score
            result['confidence'] = self._estimate_field_confidence(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting applicant: {e}")
            return None
    
    def _extract_locations(
        self,
        text: str,
        tables: List[List[List[str]]]
    ) -> List[Dict[str, Any]]:
        """Extract property locations using LLM."""
        try:
            system_prompt, schema = get_extraction_prompt('locations', text)
            
            # Include table data in context if available
            context = text
            if tables:
                context += "\n\nTable Data:\n"
                for i, table in enumerate(tables):
                    context += f"\nTable {i+1}:\n"
                    for row in table[:10]:  # Limit rows
                        context += " | ".join(row) + "\n"
            
            result = self.llm_client.extract_structured_data(
                text=context,
                schema=schema,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            locations = result.get('locations', [])
            
            # Add confidence to each location
            for location in locations:
                location['confidence'] = self._estimate_field_confidence(location)
            
            return locations
            
        except Exception as e:
            logger.error(f"Error extracting locations: {e}")
            return []
    
    def _extract_coverage(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract coverage information using LLM."""
        try:
            system_prompt, schema = get_extraction_prompt('coverage', text)
            
            result = self.llm_client.extract_structured_data(
                text=text,
                schema=schema,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            result['confidence'] = self._estimate_field_confidence(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting coverage: {e}")
            return None
    
    def _extract_losses(
        self,
        text: str,
        tables: List[List[List[str]]]
    ) -> List[Dict[str, Any]]:
        """Extract loss history using LLM."""
        try:
            system_prompt, schema = get_extraction_prompt('losses', text)
            
            # Include table data for loss runs
            context = text
            if tables:
                context += "\n\nLoss Run Tables:\n"
                for i, table in enumerate(tables):
                    context += f"\nTable {i+1}:\n"
                    for row in table[:20]:
                        context += " | ".join(row) + "\n"
            
            result = self.llm_client.extract_structured_data(
                text=context,
                schema=schema,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            losses = result.get('losses', [])
            
            # Add confidence to each loss
            for loss in losses:
                loss['confidence'] = self._estimate_field_confidence(loss)
            
            return losses
            
        except Exception as e:
            logger.error(f"Error extracting losses: {e}")
            return []
    
    def _estimate_field_confidence(self, data: Dict[str, Any]) -> float:
        """
        Estimate confidence score for extracted data.
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        if not data:
            return 0.0
        
        # Count populated fields
        total_fields = 0
        populated_fields = 0
        
        for key, value in data.items():
            if key == 'confidence':
                continue
            
            total_fields += 1
            if value is not None and value != '':
                populated_fields += 1
        
        if total_fields == 0:
            return 0.0
        
        # Base confidence on field completion
        completion_ratio = populated_fields / total_fields
        
        # Adjust based on critical fields
        critical_boost = 0.0
        if data.get('business_name') or data.get('address_line1'):
            critical_boost = 0.1
        
        confidence = min(1.0, completion_ratio + critical_boost)
        
        return round(confidence, 2)
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence scores for extraction result."""
        result = extracted_data.copy()
        
        # Calculate overall confidence
        confidences = []
        
        if extracted_data.get('applicant'):
            confidences.append(extracted_data['applicant'].get('confidence', 0.0))
        
        if extracted_data.get('locations'):
            loc_confidences = [loc.get('confidence', 0.0) for loc in extracted_data['locations']]
            if loc_confidences:
                confidences.append(sum(loc_confidences) / len(loc_confidences))
        
        if extracted_data.get('coverage'):
            confidences.append(extracted_data['coverage'].get('confidence', 0.0))
        
        if extracted_data.get('loss_history'):
            loss_confidences = [loss.get('confidence', 0.0) for loss in extracted_data['loss_history']]
            if loss_confidences:
                confidences.append(sum(loss_confidences) / len(loss_confidences))
        
        overall = sum(confidences) / len(confidences) if confidences else 0.0
        result['overall_confidence'] = round(overall, 2)
        
        return result
    
    def _merge_extraction_results(self, file_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge extraction results from multiple files.
        
        Args:
            file_results: List of file extraction results
            
        Returns:
            Merged extraction data
        """
        merged = {
            'applicant': None,
            'locations': [],
            'coverage': None,
            'loss_history': []
        }
        
        for result in file_results:
            if result.get('status') != 'completed':
                continue
            
            extracted = result.get('extracted_data', {})
            
            # Merge applicant (use highest confidence)
            if extracted.get('applicant'):
                if merged['applicant'] is None:
                    merged['applicant'] = extracted['applicant']
                else:
                    existing_conf = merged['applicant'].get('confidence', 0.0)
                    new_conf = extracted['applicant'].get('confidence', 0.0)
                    if new_conf > existing_conf:
                        merged['applicant'] = extracted['applicant']
            
            # Merge locations (combine all)
            if extracted.get('locations'):
                merged['locations'].extend(extracted['locations'])
            
            # Merge coverage (use highest confidence)
            if extracted.get('coverage'):
                if merged['coverage'] is None:
                    merged['coverage'] = extracted['coverage']
                else:
                    existing_conf = merged['coverage'].get('confidence', 0.0)
                    new_conf = extracted['coverage'].get('confidence', 0.0)
                    if new_conf > existing_conf:
                        merged['coverage'] = extracted['coverage']
            
            # Merge losses (combine all)
            if extracted.get('loss_history'):
                merged['loss_history'].extend(extracted['loss_history'])
        
        return merged
    
    def _calculate_overall_confidence(self, file_results: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence from multiple file results."""
        confidences = []
        
        for result in file_results:
            if result.get('status') == 'completed':
                extracted = result.get('extracted_data', {})
                if extracted.get('overall_confidence'):
                    confidences.append(extracted['overall_confidence'])
        
        if not confidences:
            return 0.0
        
        return round(sum(confidences) / len(confidences), 2)
    
    def health_check(self) -> Dict[str, Any]:
        """Check extraction service health."""
        try:
            processor_health = self.processor_factory.health_check()
            llm_health = self.llm_client.health_check()
            storage_health = self.storage.health_check()
            
            all_healthy = all([
                processor_health.get('status') == 'healthy',
                llm_health.get('status') == 'healthy',
                storage_health.get('status') == 'healthy'
            ])
            
            return {
                'status': 'healthy' if all_healthy else 'degraded',
                'service': 'ExtractionService',
                'components': {
                    'processors': processor_health,
                    'llm': llm_health,
                    'storage': storage_health
                }
            }
            
        except Exception as e:
            logger.error(f"Extraction service health check failed: {e}")
            return {
                'status': 'unhealthy',
                'service': 'ExtractionService',
                'error': str(e)
            }


# Global service instance
_extraction_service: Optional[ExtractionService] = None


def get_extraction_service() -> ExtractionService:
    """
    Get or create extraction service singleton.
    
    Returns:
        ExtractionService instance
    """
    global _extraction_service
    
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    
    return _extraction_service