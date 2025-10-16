"""
ACORD Form Field Mappings

Maps extracted submission data fields to ACORD PDF form field names.
Based on official ACORD form specifications.

Usage:
    from app.infrastructure.pdf.acord_field_mappings import get_field_mapping
    
    mapping = get_field_mapping('125')
    # Returns dict mapping your data fields to PDF field names
"""

from typing import Dict, Optional


# ============================================================================
# ACORD 125 - Commercial Insurance Application
# ============================================================================

ACORD_125_FIELD_MAP = {
    # Applicant Information
    'applicant.business_name': 'NamedInsured',
    'applicant.dba_name': 'DBA',
    'applicant.mailing_address_line1': 'MailingAddress',
    'applicant.mailing_address_line2': 'MailingAddress2',
    'applicant.mailing_city': 'City',
    'applicant.mailing_state': 'State',
    'applicant.mailing_zip': 'Zip',
    'applicant.mailing_zip_ext': 'ZipExt',
    'applicant.county': 'County',
    
    # Business Identification
    'applicant.fein': 'FEIN',
    'applicant.sic_code': 'SIC',
    'applicant.naics_code': 'NAICS',
    'applicant.website': 'Website',
    
    # Contact Information
    'applicant.contact_name': 'ContactName',
    'applicant.contact_phone': 'PhoneNumber',
    'applicant.contact_phone_ext': 'PhoneExt',
    'applicant.contact_fax': 'FaxNumber',
    'applicant.contact_email': 'EmailAddress',
    
    # Business Details
    'applicant.business_description': 'DescriptionOfOperations',
    'applicant.years_in_business': 'YearsInBusiness',
    'applicant.legal_entity_type': 'EntityType',
    'applicant.num_employees': 'NumberOfEmployees',
    'applicant.annual_revenue': 'AnnualRevenue',
    
    # Producer/Broker Information
    'broker.name': 'ProducerName',
    'broker.address': 'ProducerAddress',
    'broker.city': 'ProducerCity',
    'broker.state': 'ProducerState',
    'broker.zip': 'ProducerZip',
    'broker.contact_name': 'ProducerContactName',
    'broker.phone': 'ProducerPhone',
    'broker.email': 'ProducerEmail',
    'broker.license_number': 'ProducerLicenseNumber',
    
    # Coverage Information
    'coverage.effective_date': 'EffectiveDate',
    'coverage.expiration_date': 'ExpirationDate',
    'coverage.policy_period': 'PolicyPeriod',
    
    # Prior Insurance
    'prior_insurance.carrier_name': 'PriorCarrier',
    'prior_insurance.policy_number': 'PriorPolicyNumber',
    'prior_insurance.expiration_date': 'PriorExpirationDate',
    'prior_insurance.premium': 'PriorPremium',
    
    # Additional Information
    'submission.date': 'ApplicationDate',
    'submission.applicant_signature': 'ApplicantSignature',
    'submission.applicant_signature_date': 'ApplicantSignatureDate',
    'submission.producer_signature': 'ProducerSignature',
    'submission.remarks': 'Remarks',
}


# ============================================================================
# ACORD 126 - Commercial General Liability Section
# ============================================================================

ACORD_126_FIELD_MAP = {
    # Applicant Information (ref from 125)
    'applicant.business_name': 'NamedInsured',
    'applicant.mailing_address_line1': 'MailingAddress',
    'applicant.mailing_city': 'City',
    'applicant.mailing_state': 'State',
    'applicant.mailing_zip': 'Zip',
    
    # Coverage Requested
    'coverage.general_liability.each_occurrence': 'EachOccurrence',
    'coverage.general_liability.damage_to_premises': 'DamageToPremises',
    'coverage.general_liability.medical_expense': 'MedicalExpense',
    'coverage.general_liability.personal_injury': 'PersonalInjury',
    'coverage.general_liability.general_aggregate': 'GeneralAggregate',
    'coverage.general_liability.products_aggregate': 'ProductsAggregate',
    
    # Deductibles
    'coverage.general_liability.deductible': 'Deductible',
    
    # Premises Information
    'locations[0].address': 'PremisesAddress1',
    'locations[0].city': 'PremisesCity1',
    'locations[0].state': 'PremisesState1',
    'locations[0].zip': 'PremisesZip1',
    'locations[0].area_sq_ft': 'PremisesAreaSqFt1',
    
    'locations[1].address': 'PremisesAddress2',
    'locations[1].city': 'PremisesCity2',
    'locations[1].state': 'PremisesState2',
    'locations[1].zip': 'PremisesZip2',
    'locations[1].area_sq_ft': 'PremisesAreaSqFt2',
    
    # Operations
    'applicant.num_employees': 'TotalEmployees',
    'applicant.num_full_time': 'FullTimeEmployees',
    'applicant.num_part_time': 'PartTimeEmployees',
    'applicant.annual_payroll': 'AnnualPayroll',
    'applicant.annual_sales': 'AnnualSales',
    
    # Classification
    'classification.code': 'ClassificationCode',
    'classification.description': 'ClassificationDescription',
    'classification.premium_basis': 'PremiumBasis',
    
    # Products
    'operations.products_sold': 'ProductsSold',
    'operations.annual_products_sales': 'ProductsSalesAmount',
    'operations.products_description': 'ProductsDescription',
    
    # Additional Coverage Details
    'coverage.effective_date': 'EffectiveDate',
    'coverage.expiration_date': 'ExpirationDate',
}


# ============================================================================
# ACORD 130 - Workers Compensation Application
# ============================================================================

ACORD_130_FIELD_MAP = {
    # Applicant Information
    'applicant.business_name': 'NamedInsured',
    'applicant.dba_name': 'DBA',
    'applicant.mailing_address_line1': 'MailingAddress',
    'applicant.mailing_city': 'City',
    'applicant.mailing_state': 'State',
    'applicant.mailing_zip': 'Zip',
    'applicant.fein': 'FEIN',
    
    # Business Information
    'applicant.years_in_business': 'YearsInBusiness',
    'applicant.legal_entity_type': 'EntityType',
    'applicant.naics_code': 'NAICS',
    
    # Employee Information
    'workers_comp.total_employees': 'TotalEmployees',
    'workers_comp.full_time_employees': 'FullTimeEmployees',
    'workers_comp.part_time_employees': 'PartTimeEmployees',
    'workers_comp.owners_included': 'OwnersIncluded',
    'workers_comp.num_owners': 'NumberOfOwners',
    
    # Payroll by State
    'workers_comp.states[0].state': 'State1',
    'workers_comp.states[0].employees': 'Employees1',
    'workers_comp.states[0].annual_payroll': 'AnnualPayroll1',
    'workers_comp.states[0].class_code': 'ClassCode1',
    'workers_comp.states[0].class_description': 'ClassDescription1',
    
    'workers_comp.states[1].state': 'State2',
    'workers_comp.states[1].employees': 'Employees2',
    'workers_comp.states[1].annual_payroll': 'AnnualPayroll2',
    'workers_comp.states[1].class_code': 'ClassCode2',
    'workers_comp.states[1].class_description': 'ClassDescription2',
    
    'workers_comp.states[2].state': 'State3',
    'workers_comp.states[2].employees': 'Employees3',
    'workers_comp.states[2].annual_payroll': 'AnnualPayroll3',
    'workers_comp.states[2].class_code': 'ClassCode3',
    'workers_comp.states[2].class_description': 'ClassDescription3',
    
    # Coverage
    'coverage.effective_date': 'EffectiveDate',
    'coverage.expiration_date': 'ExpirationDate',
    'coverage.estimated_premium': 'EstimatedPremium',
    
    # Loss History
    'loss_history[0].date': 'LossDate1',
    'loss_history[0].amount_paid': 'LossAmountPaid1',
    'loss_history[0].amount_reserved': 'LossAmountReserved1',
    'loss_history[0].description': 'LossDescription1',
    'loss_history[0].status': 'LossStatus1',
    
    'loss_history[1].date': 'LossDate2',
    'loss_history[1].amount_paid': 'LossAmountPaid2',
    'loss_history[1].amount_reserved': 'LossAmountReserved2',
    'loss_history[1].description': 'LossDescription2',
    'loss_history[1].status': 'LossStatus2',
    
    # Prior Insurance
    'prior_insurance.carrier_name': 'PriorCarrier',
    'prior_insurance.policy_number': 'PriorPolicyNumber',
    'prior_insurance.expiration_date': 'PriorExpirationDate',
    
    # Additional
    'submission.applicant_signature': 'ApplicantSignature',
    'submission.signature_date': 'SignatureDate',
}


# ============================================================================
# ACORD 140 - Property Section
# ============================================================================

ACORD_140_FIELD_MAP = {
    # Applicant Information
    'applicant.business_name': 'NamedInsured',
    'applicant.mailing_address_line1': 'MailingAddress',
    'applicant.mailing_city': 'City',
    'applicant.mailing_state': 'State',
    'applicant.mailing_zip': 'Zip',
    
    # Coverage Period
    'coverage.effective_date': 'EffectiveDate',
    'coverage.expiration_date': 'ExpirationDate',
    
    # Location 1
    'locations[0].location_number': 'LocationNumber1',
    'locations[0].building_number': 'BuildingNumber1',
    'locations[0].address': 'LocationAddress1',
    'locations[0].city': 'LocationCity1',
    'locations[0].state': 'LocationState1',
    'locations[0].zip': 'LocationZip1',
    'locations[0].county': 'LocationCounty1',
    
    # Building Details 1
    'locations[0].year_built': 'YearBuilt1',
    'locations[0].num_stories': 'NumberOfStories1',
    'locations[0].total_area_sq_ft': 'TotalAreaSqFt1',
    'locations[0].construction_type': 'ConstructionType1',
    'locations[0].occupancy_type': 'OccupancyType1',
    'locations[0].roof_type': 'RoofType1',
    
    # Protection Class 1
    'locations[0].protection_class': 'ProtectionClass1',
    'locations[0].fire_district': 'FireDistrict1',
    'locations[0].distance_to_fire_station': 'DistanceToFireStation1',
    'locations[0].distance_to_hydrant': 'DistanceToHydrant1',
    
    # Sprinkler/Alarm 1
    'locations[0].sprinkler_system': 'SprinklerSystem1',
    'locations[0].sprinkler_type': 'SprinklerType1',
    'locations[0].fire_alarm': 'FireAlarm1',
    'locations[0].burglar_alarm': 'BurglarAlarm1',
    
    # Values 1
    'locations[0].building_limit': 'BuildingLimit1',
    'locations[0].contents_limit': 'ContentsLimit1',
    'locations[0].business_income_limit': 'BusinessIncomeLimit1',
    'locations[0].extra_expense_limit': 'ExtraExpenseLimit1',
    'locations[0].total_insured_value': 'TotalInsuredValue1',
    
    # Deductibles 1
    'locations[0].deductible': 'Deductible1',
    'locations[0].wind_deductible': 'WindDeductible1',
    'locations[0].earthquake_deductible': 'EarthquakeDeductible1',
    'locations[0].flood_deductible': 'FloodDeductible1',
    
    # Location 2
    'locations[1].location_number': 'LocationNumber2',
    'locations[1].building_number': 'BuildingNumber2',
    'locations[1].address': 'LocationAddress2',
    'locations[1].city': 'LocationCity2',
    'locations[1].state': 'LocationState2',
    'locations[1].zip': 'LocationZip2',
    'locations[1].year_built': 'YearBuilt2',
    'locations[1].construction_type': 'ConstructionType2',
    'locations[1].occupancy_type': 'OccupancyType2',
    'locations[1].protection_class': 'ProtectionClass2',
    'locations[1].building_limit': 'BuildingLimit2',
    'locations[1].contents_limit': 'ContentsLimit2',
    'locations[1].total_insured_value': 'TotalInsuredValue2',
    
    # Location 3
    'locations[2].location_number': 'LocationNumber3',
    'locations[2].address': 'LocationAddress3',
    'locations[2].city': 'LocationCity3',
    'locations[2].state': 'LocationState3',
    'locations[2].zip': 'LocationZip3',
    'locations[2].year_built': 'YearBuilt3',
    'locations[2].construction_type': 'ConstructionType3',
    'locations[2].building_limit': 'BuildingLimit3',
    'locations[2].contents_limit': 'ContentsLimit3',
    'locations[2].total_insured_value': 'TotalInsuredValue3',
    
    # Summary Totals
    'coverage.total_building_limit': 'TotalBuildingLimit',
    'coverage.total_contents_limit': 'TotalContentsLimit',
    'coverage.total_business_income': 'TotalBusinessIncome',
    'coverage.total_insured_value': 'TotalInsuredValue',
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_field_mapping(form_type: str) -> Dict[str, str]:
    """
    Get field mapping for a specific ACORD form type.
    
    Args:
        form_type: ACORD form number ('125', '126', '130', '140')
        
    Returns:
        Dictionary mapping data fields to PDF field names
        
    Raises:
        ValueError: If form type is not supported
    """
    mappings = {
        '125': ACORD_125_FIELD_MAP,
        '126': ACORD_126_FIELD_MAP,
        '130': ACORD_130_FIELD_MAP,
        '140': ACORD_140_FIELD_MAP,
    }
    
    if form_type not in mappings:
        raise ValueError(
            f"Unsupported ACORD form type: {form_type}. "
            f"Supported types: {', '.join(mappings.keys())}"
        )
    
    return mappings[form_type].copy()


def get_all_mappings() -> Dict[str, Dict[str, str]]:
    """
    Get all ACORD form field mappings.
    
    Returns:
        Dictionary with form types as keys and field mappings as values
    """
    return {
        '125': ACORD_125_FIELD_MAP,
        '126': ACORD_126_FIELD_MAP,
        '130': ACORD_130_FIELD_MAP,
        '140': ACORD_140_FIELD_MAP,
    }


def get_supported_forms() -> list:
    """
    Get list of supported ACORD form types.
    
    Returns:
        List of form type strings
    """
    return ['125', '126', '130', '140']