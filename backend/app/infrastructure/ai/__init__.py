"""
AI infrastructure package for SubmitEZ.
"""

from .base_llm import BaseLLM
from .openai_client import OpenAIClient, get_openai_client
from .prompt_templates import (
    SYSTEM_PROMPT_BASE,
    SYSTEM_PROMPT_APPLICANT,
    SYSTEM_PROMPT_PROPERTY,
    SYSTEM_PROMPT_COVERAGE,
    SYSTEM_PROMPT_LOSS,
    APPLICANT_SCHEMA,
    PROPERTY_LOCATION_SCHEMA,
    COVERAGE_SCHEMA,
    LOSS_HISTORY_SCHEMA,
    MULTIPLE_LOCATIONS_SCHEMA,
    MULTIPLE_LOSSES_SCHEMA,
    get_extraction_prompt,
    build_extraction_user_prompt
)

__all__ = [
    'BaseLLM',
    'OpenAIClient',
    'get_openai_client',
    'SYSTEM_PROMPT_BASE',
    'SYSTEM_PROMPT_APPLICANT',
    'SYSTEM_PROMPT_PROPERTY',
    'SYSTEM_PROMPT_COVERAGE',
    'SYSTEM_PROMPT_LOSS',
    'APPLICANT_SCHEMA',
    'PROPERTY_LOCATION_SCHEMA',
    'COVERAGE_SCHEMA',
    'LOSS_HISTORY_SCHEMA',
    'MULTIPLE_LOCATIONS_SCHEMA',
    'MULTIPLE_LOSSES_SCHEMA',
    'get_extraction_prompt',
    'build_extraction_user_prompt'
]