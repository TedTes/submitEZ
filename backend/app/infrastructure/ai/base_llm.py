"""
Abstract base LLM interface for AI extraction operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    
    Supports Dependency Inversion Principle - allows swapping
    LLM providers (OpenAI, Claude, local models) without
    changing business logic.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            model_name: Name/identifier of the model
            api_key: API key for authentication
        """
        self.model_name = model_name
        self.api_key = api_key
        self._client = None
    
    @abstractmethod
    def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from text using LLM.
        
        Args:
            text: Input text to extract from
            schema: JSON schema defining expected output structure
            system_prompt: System/instruction prompt
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Extracted data matching schema
        """
        pass
    
    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt
            system_prompt: System/instruction prompt
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    def extract_with_retry(
        self,
        text: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Extract with automatic retry on failure.
        
        Args:
            text: Input text to extract from
            schema: JSON schema for output
            system_prompt: System prompt
            max_retries: Maximum retry attempts
            temperature: Model temperature
            
        Returns:
            Extracted data or empty dict on failure
        """
        for attempt in range(max_retries):
            try:
                result = self.extract_structured_data(
                    text=text,
                    schema=schema,
                    system_prompt=system_prompt,
                    temperature=temperature
                )
                return result
                
            except Exception as e:
                logger.warning(f"Extraction attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} extraction attempts failed")
                    raise
        
        return {}
    
    def extract_batch(
        self,
        texts: List[str],
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Extract from multiple texts.
        
        Args:
            texts: List of input texts
            schema: JSON schema for output
            system_prompt: System prompt
            temperature: Model temperature
            
        Returns:
            List of extracted data dictionaries
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.extract_structured_data(
                    text=text,
                    schema=schema,
                    system_prompt=system_prompt,
                    temperature=temperature
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error extracting from text {i}: {e}")
                results.append({})
        
        return results
    
    def validate_extraction(
        self,
        extracted_data: Dict[str, Any],
        required_fields: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Validate extracted data has required fields.
        
        Args:
            extracted_data: Extracted data dictionary
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in extracted_data or extracted_data[field] is None:
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        
        return is_valid, missing_fields
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Dictionary with model details
        """
        return {
            'model_name': self.model_name,
            'provider': self.__class__.__name__,
            'api_configured': self.api_key is not None
        }
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate API cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        # Default implementation - override in subclasses with actual pricing
        return 0.0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check LLM service health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple test completion
            test_result = self.generate_completion(
                prompt="Hello",
                max_tokens=5
            )
            
            return {
                'status': 'healthy',
                'model': self.model_name,
                'provider': self.__class__.__name__,
                'message': 'LLM service is working'
            }
            
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {
                'status': 'unhealthy',
                'model': self.model_name,
                'provider': self.__class__.__name__,
                'error': str(e)
            }