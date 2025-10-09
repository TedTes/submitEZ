"""
Common validation utilities for SubmitEZ.
"""

import re
from typing import Optional, Any, List, Dict
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException


def is_valid_email(email: str) -> bool:
    """
    Validate email address.
    
    Args:
        email: Email address string
        
    Returns:
        True if email is valid
    """
    if not email:
        return False
    
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def is_valid_phone(phone: str, country_code: str = 'US') -> bool:
    """
    Validate phone number.
    
    Args:
        phone: Phone number string
        country_code: ISO country code (default: US)
        
    Returns:
        True if phone is valid
    """
    if not phone:
        return False
    
    try:
        parsed = phonenumbers.parse(phone, country_code)
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False


def format_phone(phone: str, country_code: str = 'US') -> Optional[str]:
    """
    Format phone number to standard format.
    
    Args:
        phone: Phone number string
        country_code: ISO country code
        
    Returns:
        Formatted phone number or None if invalid
    """
    if not phone:
        return None
    
    try:
        parsed = phonenumbers.parse(phone, country_code)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.E164
            )
    except NumberParseException:
        pass
    
    return None


def is_valid_fein(fein: str) -> bool:
    """
    Validate Federal Employer Identification Number (FEIN).
    
    Format: XX-XXXXXXX
    
    Args:
        fein: FEIN string
        
    Returns:
        True if FEIN is valid format
    """
    if not fein:
        return False
    
    # Remove any non-digit characters
    clean_fein = re.sub(r'\D', '', fein)
    
    # Must be exactly 9 digits
    if len(clean_fein) != 9:
        return False
    
    # First two digits cannot be 00, 07, 08, 09, 17, 18, 19, or 78-79
    first_two = clean_fein[:2]
    if first_two in ['00', '07', '08', '09', '17', '18', '19', '78', '79']:
        return False
    
    return True


def format_fein(fein: str) -> Optional[str]:
    """
    Format FEIN to standard XX-XXXXXXX format.
    
    Args:
        fein: FEIN string
        
    Returns:
        Formatted FEIN or None if invalid
    """
    if not is_valid_fein(fein):
        return None
    
    clean_fein = re.sub(r'\D', '', fein)
    return f"{clean_fein[:2]}-{clean_fein[2:]}"


def is_valid_zip(zip_code: str) -> bool:
    """
    Validate US ZIP code.
    
    Accepts: 12345 or 12345-6789
    
    Args:
        zip_code: ZIP code string
        
    Returns:
        True if ZIP code is valid
    """
    if not zip_code:
        return False
    
    # 5-digit ZIP
    pattern_5 = r'^\d{5}$'
    # ZIP+4
    pattern_9 = r'^\d{5}-\d{4}$'
    
    return bool(re.match(pattern_5, zip_code) or re.match(pattern_9, zip_code))


def is_valid_state(state: str) -> bool:
    """
    Validate US state abbreviation.
    
    Args:
        state: 2-letter state code
        
    Returns:
        True if state code is valid
    """
    if not state or len(state) != 2:
        return False
    
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
    }
    
    return state.upper() in valid_states


def is_valid_naics(naics: str) -> bool:
    """
    Validate NAICS code.
    
    NAICS codes are 2-6 digits.
    
    Args:
        naics: NAICS code string
        
    Returns:
        True if NAICS code is valid format
    """
    if not naics:
        return False
    
    clean_naics = re.sub(r'\D', '', naics)
    return 2 <= len(clean_naics) <= 6


def is_valid_year(year: Any, min_year: int = 1800, max_year: Optional[int] = None) -> bool:
    """
    Validate year value.
    
    Args:
        year: Year value (int or string)
        min_year: Minimum valid year
        max_year: Maximum valid year (default: current year + 1)
        
    Returns:
        True if year is valid
    """
    try:
        year_int = int(year)
        
        if max_year is None:
            from datetime import datetime
            max_year = datetime.now().year + 1
        
        return min_year <= year_int <= max_year
    except (ValueError, TypeError):
        return False


def is_valid_currency(amount: Any) -> bool:
    """
    Validate currency amount.
    
    Args:
        amount: Currency amount (float, int, or string)
        
    Returns:
        True if amount is valid
    """
    try:
        value = float(amount)
        return value >= 0
    except (ValueError, TypeError):
        return False


def is_not_empty(value: Any) -> bool:
    """
    Check if value is not empty.
    
    Args:
        value: Any value to check
        
    Returns:
        True if value is not None and not empty string
    """
    if value is None:
        return False
    
    if isinstance(value, str):
        return bool(value.strip())
    
    return True


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string
        
    Returns:
        True if URL is valid format
    """
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return bool(url_pattern.match(url))


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present and not empty.
    
    Args:
        data: Dictionary of data
        required_fields: List of required field names
        
    Returns:
        List of missing or empty field names
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not is_not_empty(data[field]):
            missing_fields.append(field)
    
    return missing_fields


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string value.
    
    Args:
        value: String to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ''
    
    # Strip whitespace
    sanitized = value.strip()
    
    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char == '\n')
    
    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def normalize_whitespace(value: str) -> str:
    """
    Normalize whitespace in string.
    
    Args:
        value: String to normalize
        
    Returns:
        String with normalized whitespace
    """
    if not value:
        return ''
    
    # Replace multiple spaces with single space
    return ' '.join(value.split())