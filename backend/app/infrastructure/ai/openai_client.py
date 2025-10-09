"""
OpenAI client implementation for LLM operations.
"""

import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
import tiktoken
from app.infrastructure.ai.base_llm import BaseLLM
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient(BaseLLM):
    """
    OpenAI GPT implementation of LLM interface.
    """
    
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        'gpt-4-turbo-preview': {'input': 10.00, 'output': 30.00},
        'gpt-4': {'input': 30.00, 'output': 60.00},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        'gpt-4o': {'input': 5.00, 'output': 15.00},
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60}
    }
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize OpenAI client.
        
        Args:
            model_name: OpenAI model name (defaults to config)
            api_key: OpenAI API key (defaults to env var)
        """
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if model_name is None:
            model_name = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        
        super().__init__(model_name, api_key)
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable."
            )
        
        self._client = OpenAI(api_key=self.api_key)
        self._tokenizer = None
    
    @property
    def tokenizer(self):
        """Get tiktoken tokenizer for model."""
        if self._tokenizer is None:
            try:
                # Get encoding for model
                if 'gpt-4' in self.model_name:
                    encoding_name = 'cl100k_base'
                elif 'gpt-3.5' in self.model_name:
                    encoding_name = 'cl100k_base'
                else:
                    encoding_name = 'cl100k_base'
                
                self._tokenizer = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Could not load tokenizer: {e}")
                self._tokenizer = None
        
        return self._tokenizer
    
    def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from text using OpenAI.
        
        Args:
            text: Input text to extract from
            schema: JSON schema defining expected output structure
            system_prompt: System/instruction prompt
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Extracted data matching schema
        """
        try:
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # Add user message with text and schema
            user_content = f"""Extract information from the following text according to the schema.

Text:
{text}

Schema:
{json.dumps(schema, indent=2)}

Return ONLY a valid JSON object matching the schema. Do not include any explanations or markdown."""
            
            messages.append({
                'role': 'user',
                'content': user_content
            })
            
            # Call OpenAI API with JSON mode
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={'type': 'json_object'}
            )
            
            # Parse response
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            # Log token usage
            usage = response.usage
            logger.info(
                f"OpenAI extraction: {usage.prompt_tokens} input tokens, "
                f"{usage.completion_tokens} output tokens"
            )
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI extraction error: {e}")
            raise
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text completion using OpenAI.
        
        Args:
            prompt: User prompt
            system_prompt: System/instruction prompt
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Log token usage
            usage = response.usage
            logger.debug(
                f"OpenAI completion: {usage.prompt_tokens} input tokens, "
                f"{usage.completion_tokens} output tokens"
            )
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        try:
            if self.tokenizer:
                return len(self.tokenizer.encode(text))
            else:
                # Rough estimate: 1 token ≈ 4 characters
                return len(text) // 4
                
        except Exception as e:
            logger.warning(f"Token counting error: {e}")
            # Fallback estimate
            return len(text) // 4
    
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
        pricing = self.PRICING.get(self.model_name)
        
        if not pricing:
            logger.warning(f"No pricing info for model {self.model_name}")
            return 0.0
        
        # Calculate cost per million tokens
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        
        total_cost = input_cost + output_cost
        
        return round(total_cost, 6)
    
    def extract_with_function_calling(
        self,
        text: str,
        function_definition: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract using OpenAI function calling.
        
        Args:
            text: Input text
            function_definition: Function definition for extraction
            system_prompt: System prompt
            
        Returns:
            Extracted function arguments
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': text
            })
            
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                functions=[function_definition],
                function_call={'name': function_definition['name']},
                temperature=0.1
            )
            
            # Extract function arguments
            function_call = response.choices[0].message.function_call
            arguments = json.loads(function_call.arguments)
            
            logger.info(f"Function calling extraction completed")
            
            return arguments
            
        except Exception as e:
            logger.error(f"Function calling error: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get OpenAI model information.
        
        Returns:
            Dictionary with model details
        """
        info = super().get_model_info()
        info.update({
            'provider': 'OpenAI',
            'supports_json_mode': True,
            'supports_function_calling': True,
            'pricing': self.PRICING.get(self.model_name, {})
        })
        return info


# Global OpenAI client instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client(
    model_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> OpenAIClient:
    """
    Get or create OpenAI client singleton.
    
    Args:
        model_name: OpenAI model name
        api_key: OpenAI API key
        
    Returns:
        OpenAIClient instance
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = OpenAIClient(model_name, api_key)
    
    return _openai_client