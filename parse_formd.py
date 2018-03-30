"""
File: parse_formd.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

Helper functions for parsing Form D XML.
The attributes accessed in each of the below functions
is as per the Form D XML specification as described by
the following link:

https://www.sec.gov/info/edgar/formdxmltechspec.htm
"""

def extract_issuer_info(tag):
    """
    Extract contact info for an issuer.
    Args:
        tag - primaryIssuer tag from Form D XML
    Returns:
        list of extracted values
    """
    entity_name = tag.entityname.string
    address = extract_address(tag.issueraddress)
    phone = tag.issuerphonenumber.string
    year_of_incorp = tag.yearofinc.value.string

    return [entity_name, address, phone, year_of_incorp]


def extract_address(tag):
    """
    Extract address information for an issuer or related person.
    Args:
        tag - issuerAddress tag or relatedPersonAddress tag from Form D XML
    Returns:
        list of extracted values
    """
    street1 = tag.street1.string
    street2 = tag.street2
    if street2 != None:
        street2.string
    city = tag.city.string
    state = tag.stateorcountry.string
    full_state_name = tag.stateorcountrydescription.string
    zip_code = tag.zipcode.string

    return [street1, street2, city, state, full_state_name, zip_code]


def extract_offering_data(off_data):
    """
    Extract offering data info for an issuer.
    Args:
        tag - offeringData tag from Form D XML
    Returns:
        list of extracted values
    """
    ind_group_type = off_data.industrygroup.industrygrouptype.string
    # need to error check this
    #fund_type = off_data.industrygroup.investmentfundinfo.investmentfundtype.string
    issuer_size = off_data.issuersize.string

    type_of_filing = off_data.typeoffiling
    new_or_amend = type_of_filing.neworamendment.isamendment.string
    date_of_first_sale = type_of_filing.dateoffirstsale.string

    sec_types = off_data.typesofsecuritiesoffered
    is_equity = sec_types.isequitytype
    if is_equity:
        is_equity = True 
    is_debt = sec_types.isdebttype
    if is_debt:
        is_debt = True
    #is_pooled_fund = sec_types.ispooledinvestmentfundtype.string
    #is_other = sec_types.isothertype.string

    min_investment_accepted = off_data.minimuminvestmentaccepted.string
    
    sales_amts = off_data.offeringsalesamounts
    total_offering_amount = sales_amts.totalofferingamount.string
    total_amount_sold = sales_amts.totalamountsold.string
    total_remaining = sales_amts.totalremaining.string
    
    return [ind_group_type, #fund_type,
            issuer_size,
            new_or_amend, date_of_first_sale,
            is_equity, is_debt, #is_pooled_fund, is_other,
            min_investment_accepted,
            total_offering_amount, total_amount_sold, total_remaining]

