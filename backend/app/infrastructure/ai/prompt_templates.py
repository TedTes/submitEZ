"""
LLM prompt templates for data extraction.
"""

from typing import Dict, Any


# System prompts for different extraction tasks
SYSTEM_PROMPT_BASE = """You are an expert insurance data extraction assistant. Your task is to extract structured information from insurance documents with high accuracy.

Guidelines:
- Extract only information that is explicitly stated in the document
- If information is not found, use null
- Maintain data integrity and consistency
- Pay attention to dates, numbers, and contact information
- For currency amounts, extract numeric values only (no symbols)
- For dates, use ISO format (YYYY-MM-DD) when possible"""


SYSTEM_PROMPT_APPLICANT = """You are extracting applicant/insured business information from insurance documents.

Focus on:
- Business legal name and DBA
- Federal Employer Identification Number (FEIN)
- NAICS code and business type
- Contact information (name, email, phone)
- Business addresses (mailing and physical)
- Years in business

Be precise with:
- FEIN format (XX-XXXXXXX)
- Email addresses
- Phone numbers
- State codes (2-letter abbreviations)
- ZIP codes"""


SYSTEM_PROMPT_PROPERTY = """You are extracting property location information from insurance documents.

Focus on:
- Complete property addresses
- Building characteristics (year built, construction type, occupancy)
- Property values (building, contents, business income, total insured value)
- Protection features (sprinkler systems, alarms, protection class)
- Building systems (roof, electrical, plumbing updates)

Be precise with:
- Year built (4-digit year)
- Construction types (frame, masonry, fire resistive, etc.)
- Protection class (1-10)
- Currency amounts (extract numeric values)"""


SYSTEM_PROMPT_COVERAGE = """You are extracting insurance coverage information from insurance documents.

Focus on:
- Policy type and term dates
- Coverage limits (building, contents, business income, liability)
- Deductibles (various types)
- Special coverages and endorsements
- Premium information

Be precise with:
- Dates (ISO format YYYY-MM-DD)
- Currency amounts (extract numeric values)
- Deductible types (wind/hail, earthquake, flood)
- Policy term duration"""


SYSTEM_PROMPT_LOSS = """You are extracting loss history/claims information from insurance documents.

Focus on:
- Loss dates and claim numbers
- Loss types and causes
- Financial amounts (loss amount, paid, reserved)
- Claim status (open, closed, pending, denied)
- Location and coverage affected

Be precise with:
- Loss dates (ISO format YYYY-MM-DD)
- Currency amounts (extract numeric values)
- Claim status terminology
- Loss types (fire, water, wind, theft, liability)"""


# JSON schemas for structured extraction
APPLICANT_SCHEMA = {
    "type": "object",
    "properties": {
        "business_name": {"type": "string", "description": "Legal business name"},
        "dba_name": {"type": ["string", "null"], "description": "Doing Business As name"},
        "fein": {"type": ["string", "null"], "description": "Federal Employer ID (XX-XXXXXXX)"},
        "naics_code": {"type": ["string", "null"], "description": "NAICS code (2-6 digits)"},
        "naics_description": {"type": ["string", "null"], "description": "NAICS description"},
        "business_type": {"type": ["string", "null"], "description": "Corporation, LLC, Partnership, etc."},
        "years_in_business": {"type": ["integer", "null"], "description": "Years in operation"},
        "contact_name": {"type": ["string", "null"], "description": "Primary contact person"},
        "contact_title": {"type": ["string", "null"], "description": "Contact's title"},
        "email": {"type": ["string", "null"], "description": "Email address"},
        "phone": {"type": ["string", "null"], "description": "Phone number"},
        "website": {"type": ["string", "null"], "description": "Website URL"},
        "mailing_address_line1": {"type": ["string", "null"]},
        "mailing_address_line2": {"type": ["string", "null"]},
        "mailing_city": {"type": ["string", "null"]},
        "mailing_state": {"type": ["string", "null"], "description": "2-letter state code"},
        "mailing_zip": {"type": ["string", "null"], "description": "ZIP code"},
        "physical_address_line1": {"type": ["string", "null"]},
        "physical_address_line2": {"type": ["string", "null"]},
        "physical_city": {"type": ["string", "null"]},
        "physical_state": {"type": ["string", "null"], "description": "2-letter state code"},
        "physical_zip": {"type": ["string", "null"], "description": "ZIP code"}
    },
    "required": ["business_name"]
}


PROPERTY_LOCATION_SCHEMA = {
    "type": "object",
    "properties": {
        "location_number": {"type": ["string", "null"], "description": "Location identifier"},
        "address_line1": {"type": "string", "description": "Street address"},
        "address_line2": {"type": ["string", "null"]},
        "city": {"type": "string"},
        "state": {"type": "string", "description": "2-letter state code"},
        "zip_code": {"type": "string"},
        "year_built": {"type": ["integer", "null"], "description": "4-digit year"},
        "construction_type": {"type": ["string", "null"], "description": "Frame, Masonry, etc."},
        "occupancy_type": {"type": ["string", "null"], "description": "Office, Retail, Warehouse, etc."},
        "total_square_feet": {"type": ["integer", "null"]},
        "number_of_stories": {"type": ["integer", "null"]},
        "building_value": {"type": ["number", "null"], "description": "Numeric value only"},
        "contents_value": {"type": ["number", "null"], "description": "Numeric value only"},
        "business_income_value": {"type": ["number", "null"], "description": "Numeric value only"},
        "total_insured_value": {"type": ["number", "null"], "description": "Numeric value only"},
        "protection_class": {"type": ["string", "null"], "description": "1-10"},
        "sprinkler_system": {"type": ["boolean", "null"]},
        "alarm_system": {"type": ["boolean", "null"]},
        "roof_year": {"type": ["integer", "null"], "description": "Year roof installed/replaced"}
    },
    "required": ["address_line1", "city", "state", "zip_code"]
}


COVERAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "policy_type": {"type": ["string", "null"], "description": "Property, Liability, etc."},
        "effective_date": {"type": ["string", "null"], "description": "ISO format YYYY-MM-DD"},
        "expiration_date": {"type": ["string", "null"], "description": "ISO format YYYY-MM-DD"},
        "building_limit": {"type": ["number", "null"], "description": "Numeric value only"},
        "contents_limit": {"type": ["number", "null"], "description": "Numeric value only"},
        "business_income_limit": {"type": ["number", "null"], "description": "Numeric value only"},
        "building_deductible": {"type": ["number", "null"], "description": "Numeric value only"},
        "contents_deductible": {"type": ["number", "null"], "description": "Numeric value only"},
        "wind_hail_deductible": {"type": ["string", "null"], "description": "Amount or percentage"},
        "general_aggregate_limit": {"type": ["number", "null"], "description": "Numeric value only"},
        "each_occurrence_limit": {"type": ["number", "null"], "description": "Numeric value only"},
        "replacement_cost": {"type": ["boolean", "null"]},
        "coinsurance_percentage": {"type": ["integer", "null"], "description": "80, 90, or 100"}
    }
}


LOSS_HISTORY_SCHEMA = {
    "type": "object",
    "properties": {
        "loss_date": {"type": "string", "description": "ISO format YYYY-MM-DD"},
        "claim_number": {"type": ["string", "null"]},
        "loss_type": {"type": ["string", "null"], "description": "Fire, Water, Wind, Theft, etc."},
        "loss_description": {"type": ["string", "null"]},
        "loss_amount": {"type": ["number", "null"], "description": "Numeric value only"},
        "paid_amount": {"type": ["number", "null"], "description": "Numeric value only"},
        "claim_status": {"type": "string", "description": "Open, Closed, Pending, Denied"},
        "location_affected": {"type": ["string", "null"]}
    },
    "required": ["loss_date"]
}


# Multi-location extraction schema
MULTIPLE_LOCATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "locations": {
            "type": "array",
            "items": PROPERTY_LOCATION_SCHEMA
        }
    }
}


# Multiple losses extraction schema
MULTIPLE_LOSSES_SCHEMA = {
    "type": "object",
    "properties": {
        "losses": {
            "type": "array",
            "items": LOSS_HISTORY_SCHEMA
        }
    }
}


def get_extraction_prompt(
    extraction_type: str,
    document_text: str,
    additional_context: str = ""
) -> tuple[str, Dict[str, Any]]:
    """
    Get prompt and schema for extraction type.
    
    Args:
        extraction_type: Type of extraction (applicant, property, coverage, loss)
        document_text: Document text to extract from
        additional_context: Additional context or instructions
        
    Returns:
        Tuple of (system_prompt, schema)
    """
    extraction_map = {
        'applicant': (SYSTEM_PROMPT_APPLICANT, APPLICANT_SCHEMA),
        'property': (SYSTEM_PROMPT_PROPERTY, PROPERTY_LOCATION_SCHEMA),
        'coverage': (SYSTEM_PROMPT_COVERAGE, COVERAGE_SCHEMA),
        'loss': (SYSTEM_PROMPT_LOSS, LOSS_HISTORY_SCHEMA),
        'locations': (SYSTEM_PROMPT_PROPERTY, MULTIPLE_LOCATIONS_SCHEMA),
        'losses': (SYSTEM_PROMPT_LOSS, MULTIPLE_LOSSES_SCHEMA)
    }
    
    if extraction_type not in extraction_map:
        raise ValueError(f"Unknown extraction type: {extraction_type}")
    
    system_prompt, schema = extraction_map[extraction_type]
    
    # Add additional context if provided
    if additional_context:
        system_prompt = f"{system_prompt}\n\nAdditional Context:\n{additional_context}"
    
    return system_prompt, schema


def build_extraction_user_prompt(
    document_text: str,
    extraction_type: str,
    hints: Dict[str, Any] = None
) -> str:
    """
    Build user prompt for extraction.
    
    Args:
        document_text: Document text
        extraction_type: Type of extraction
        hints: Optional extraction hints
        
    Returns:
        Formatted user prompt
    """
    prompt = f"Extract {extraction_type} information from the following document:\n\n"
    prompt += f"{document_text}\n\n"
    
    if hints:
        prompt += f"Extraction hints:\n{hints}\n\n"
    
    prompt += "Return the extracted information as a JSON object matching the schema."
    
    return prompt