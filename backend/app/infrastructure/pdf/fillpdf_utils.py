"""
PDF Template Filling Utilities 
Uses fillpdf library to fill actual ACORD PDF templates with data.

Features:
- Fill AcroForm fields using canonical mappings
- Handle checkboxes, text fields, dates, money formatting
- Support repeating rows (hazards, locations, etc.)
- Safe field resolution (won't crash on missing fields)
- Generate filled PDFs from templates folder

Usage:
    from fillpdf_utils import fill_acord_template
    
    data = {'applicant': {'business_name': 'ABC Corp'}, ...}
    output_path = fill_acord_template('126', data, 'output/acord_126_filled.pdf')
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
import fillpdf
from fillpdf import fillpdfs

from app.infrastructure.pdf.acord_field_mappings import (
    get_mapping, 
    resolve_field_name, 
    on_value, 
    format_hint,
    Mapping
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "templates"


# -----------------------------------------------------------------------------
# Core Filling Functions
# -----------------------------------------------------------------------------

def fill_acord_template(
    form_type: str,
    data: Dict[str, Any],
    output_path: str,
    template_id: Optional[str] = None
) -> str:
    """
    Fill an ACORD PDF template with data.
    
    Args:
        form_type: ACORD form type ('125', '126', '130', '140')
        data: Nested dictionary with canonical keys matching field mappings
        output_path: Where to save the filled PDF
        template_id: Optional specific template version to use
        
    Returns:
        Path to filled PDF
        
    Raises:
        FileNotFoundError: If template PDF doesn't exist
        ValueError: If form_type is unsupported
    """
    # Get template path
    template_path = get_template_path(form_type)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    # Get mapping for this form
    mapping = get_mapping(form_type, template_id)
    
    # Build PDF field data
    pdf_data = build_pdf_data(data, mapping)
    
    # Fill the PDF
    logger.info(f"Filling ACORD {form_type} template: {template_path}")
    logger.debug(f"PDF field data: {pdf_data}")
    
    fillpdfs.write_fillable_pdf(
        str(template_path),
        output_path,
        pdf_data,
        flatten=False  # Keep form editable
    )
    
    logger.info(f"Generated filled PDF: {output_path}")
    return output_path


def build_pdf_data(data: Dict[str, Any], mapping: Mapping) -> Dict[str, Any]:
    """
    Convert canonical data to PDF field dictionary.
    
    Args:
        data: Nested data with canonical keys
        mapping: Field mapping configuration
        
    Returns:
        Flat dictionary ready for fillpdf: {pdf_field_name: value}
    """
    pdf_data = {}
    field_map = mapping.get("field_map", {})
    
    for canonical_key, pdf_field_template in field_map.items():
        # Handle repeating fields (e.g., hazards[].class_code)
        if "[]" in canonical_key:
            _process_repeating_field(canonical_key, pdf_field_template, data, mapping, pdf_data)
        else:
            _process_simple_field(canonical_key, pdf_field_template, data, mapping, pdf_data)
    
    return pdf_data


def _process_simple_field(
    canonical_key: str,
    pdf_field_template: str,
    data: Dict[str, Any],
    mapping: Mapping,
    pdf_data: Dict[str, Any]
):
    """Process a simple (non-repeating) field."""
    # Get value from nested data
    value = get_nested_value(data, canonical_key)
    
    if value is None:
        return
    
    # Get the actual PDF field name
    pdf_field = resolve_field_name(mapping, canonical_key)
    if pdf_field is None:
        logger.warning(f"No PDF field mapping for: {canonical_key}")
        return
    
    # Handle checkboxes
    if canonical_key in mapping.get("checkbox_on", {}):
        pdf_data[pdf_field] = on_value(mapping, canonical_key) if value else ""
        return
    
    # Format the value
    formatted_value = format_value(value, format_hint(mapping, canonical_key))
    pdf_data[pdf_field] = formatted_value


def _process_repeating_field(
    canonical_key: str,
    pdf_field_template: str,
    data: Dict[str, Any],
    mapping: Mapping,
    pdf_data: Dict[str, Any]
):
    """
    Process repeating fields (e.g., hazards[].class_code).
    
    Example:
        canonical_key = "hazards[].class_code"
        group = "hazards"
        field_key = "class_code"
        data = {"hazards": [{"class_code": "12345"}, {"class_code": "67890"}]}
    """
    # Parse the canonical key
    parts = canonical_key.split("[].")
    if len(parts) != 2:
        logger.warning(f"Invalid repeating field format: {canonical_key}")
        return
    
    group_key, field_key = parts
    
    # Get the array data
    array_data = get_nested_value(data, group_key)
    if not isinstance(array_data, list):
        return
    
    # Process each row
    for row_index, row_data in enumerate(array_data):
        if not isinstance(row_data, dict):
            continue
        
        # Get value from row
        value = row_data.get(field_key)
        if value is None:
            continue
        
        # Resolve PDF field name with row index
        pdf_field = resolve_field_name(mapping, canonical_key, row_index=row_index, group=group_key)
        if pdf_field is None:
            logger.warning(f"No PDF field for row {row_index}: {canonical_key}")
            continue
        
        # Format and assign
        full_canonical_key = f"{group_key}[].{field_key}"
        formatted_value = format_value(value, format_hint(mapping, full_canonical_key))
        pdf_data[pdf_field] = formatted_value


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_nested_value(data: Dict[str, Any], key: str) -> Any:
    """
    Get value from nested dictionary using dot notation.
    
    Args:
        data: Nested dictionary
        key: Dot-separated key (e.g., 'applicant.mailing.city')
        
    Returns:
        Value or None if not found
        
    Example:
        data = {'applicant': {'mailing': {'city': 'Chicago'}}}
        get_nested_value(data, 'applicant.mailing.city')  # Returns 'Chicago'
    """
    keys = key.split('.')
    value = data
    
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return None
        
        if value is None:
            return None
    
    return value


def format_value(value: Any, hint: Optional[str]) -> str:
    """
    Format a value based on format hint.
    
    Args:
        value: Raw value
        hint: Format hint (e.g., 'date:mm/dd/yyyy', 'money:$#,###')
        
    Returns:
        Formatted string
    """
    if value is None:
        return ""
    
    # No formatting hint - just convert to string
    if hint is None:
        return str(value)
    
    # Parse hint
    parts = hint.split(":", 1)
    format_type = parts[0]
    format_spec = parts[1] if len(parts) > 1 else ""
    
    # Date formatting
    if format_type == "date":
        return format_date(value, format_spec)
    
    # Money formatting
    elif format_type == "money":
        return format_money(value, format_spec)
    
    # Number formatting
    elif format_type == "number":
        return format_number(value, format_spec)
    
    # Unknown format - just stringify
    return str(value)


def format_date(value: Any, spec: str) -> str:
    """
    Format date value.
    
    Args:
        value: Date value (datetime, date, or string)
        spec: Format specification (e.g., 'mm/dd/yyyy')
        
    Returns:
        Formatted date string
    """
    if isinstance(value, str):
        # Try to parse if it's a string
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value  # Return as-is if can't parse
    
    if not isinstance(value, datetime):
        return str(value)
    
    # Convert spec to strftime format
    spec = spec.replace('mm', '%m').replace('dd', '%d').replace('yyyy', '%Y').replace('yy', '%y')
    
    try:
        return value.strftime(spec)
    except:
        return str(value)


def format_money(value: Any, spec: str) -> str:
    """
    Format money value.
    
    Args:
        value: Numeric value
        spec: Format specification (e.g., '$#,###')
        
    Returns:
        Formatted money string
    """
    try:
        if isinstance(value, str):
            # Remove common non-numeric characters
            value = value.replace('$', '').replace(',', '').strip()
        
        num_value = float(value)
        
        # Format with thousands separator
        if '$' in spec:
            return f"${num_value:,.2f}"
        else:
            return f"{num_value:,.2f}"
    except:
        return str(value)


def format_number(value: Any, spec: str) -> str:
    """
    Format numeric value.
    
    Args:
        value: Numeric value
        spec: Format specification (e.g., '#,###' or '#.###')
        
    Returns:
        Formatted number string
    """
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        
        num_value = float(value)
        
        # Determine decimal places
        if '.' in spec:
            decimal_places = spec.count('#') - spec.index('.') - 1
            if ',' in spec:
                return f"{num_value:,.{decimal_places}f}"
            else:
                return f"{num_value:.{decimal_places}f}"
        else:
            if ',' in spec:
                return f"{num_value:,.0f}"
            else:
                return f"{num_value:.0f}"
    except:
        return str(value)


def get_template_path(form_type: str) -> Path:
    """
    Get the path to an ACORD template PDF.
    
    Args:
        form_type: ACORD form type ('125', '126', '130', '140')
        
    Returns:
        Path to template PDF
    """
    filename = f"ACORD_{form_type}.pdf"
    return TEMPLATES_DIR / filename


# -----------------------------------------------------------------------------
# Inspection & Debugging
# -----------------------------------------------------------------------------

def list_pdf_fields(form_type: str) -> Dict[str, Any]:
    """
    List all fields in an ACORD template PDF.
    
    Args:
        form_type: ACORD form type
        
    Returns:
        Dictionary of field names and their properties
    """
    template_path = get_template_path(form_type)
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    try:
        fields = fillpdfs.get_form_fields(str(template_path))
        return fields if fields else {}
    except Exception as e:
        logger.error(f"Error reading PDF fields: {e}")
        return {}


def print_mapping_coverage(form_type: str, data: Dict[str, Any]):
    """
    Debug helper: print which data fields map to PDF fields.
    
    Args:
        form_type: ACORD form type
        data: Data dictionary to check
    """
    mapping = get_mapping(form_type)
    pdf_data = build_pdf_data(data, mapping)
    
    print(f"\n=== ACORD {form_type} Mapping Coverage ===")
    print(f"Total PDF fields mapped: {len(pdf_data)}")
    print("\nMapped fields:")
    for pdf_field, value in sorted(pdf_data.items()):
        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"  {pdf_field}: {value_preview}")
    
    print("\nUnmapped canonical keys:")
    field_map = mapping.get("field_map", {})
    for canonical_key in field_map.keys():
        if "[]" not in canonical_key:  # Skip repeating fields for simplicity
            value = get_nested_value(data, canonical_key)
            if value is None:
                print(f"  {canonical_key} (no data)")