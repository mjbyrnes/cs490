"""
File: parse_form_d.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

Helper functions for parsing Form D XML.
The attributes accessed in each of the below functions
is as per the Form D XML specification as described by
the following link:

https://www.sec.gov/info/edgar/formdxmltechspec.htm
"""
import datetime

def extract_issuer_info(tag):
    """
    Extract contact info for an issuer.
    Args:
        tag - primaryIssuer tag from Form D XML
    Returns:
        list of extracted values
    """
    #print("Tag:")
    #print(tag)
    cik = tag.cik.string
    entity_name = tag.entityname.string
    address = extract_address(tag.issueraddress)
    phone = tag.issuerphonenumber.string
    year_of_incorp = tag.yearofinc.value
    if year_of_incorp != None:
        year_of_incorp = year_of_incorp.string

    #return [cik, entity_name, address, phone, year_of_incorp]
    return {"cik": cik,
            "entity_name": entity_name,
            "address": address,
            "phone": phone,
            "year_of_incorp": year_of_incorp}


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
        street2 = street2.string
    city = tag.city.string
    state = tag.stateorcountry.string
    full_state_name = tag.stateorcountrydescription
    if full_state_name != None:
        full_state_name = tag.stateorcountrydescription.string
   
    zip_code = None
    if tag.zipcode != None:
        zip_code = tag.zipcode.string

    return {"street1": street1, 
            "street2": street2, 
            "city": city, 
            "state": state, 
            "full_state_name": full_state_name, 
            "zip_code": zip_code}


def extract_offering_data(off_data):
    """
    Extract offering data info for an issuer.
    Args:
        tag - offeringData tag from Form D XML
    Returns:
        list of extracted values
    """
    ind_group_type = off_data.industrygroup.industrygrouptype.string
    fund_type = off_data.industrygroup.investmentfundinfo
    if fund_type:
        fund_type = fund_type.investmentfundtype.string

    issuer_size = off_data.issuersize.string

    type_of_filing = off_data.typeoffiling
    is_amend = type_of_filing.neworamendment.isamendment.string
    if is_amend == "false":
        new = True
    else:
        new = False

    date = type_of_filing.dateoffirstsale
    yet = None
    date_of_first_sale = None
    if date != None:
        yet = date.yettooccur
        if yet != None and yet.string == 'true':
            yet_to_occur = True 
            date_of_first_sale = None
        else:
            yet_to_occur = False
            date_of_first_sale = date.value.string

    sec_types = off_data.typesofsecuritiesoffered
    is_equity = sec_types.isequitytype
    if is_equity:
        is_equity = True 
    is_debt = sec_types.isdebttype
    if is_debt:
        is_debt = True
    is_pooled_fund = sec_types.ispooledinvestmentfundtype
    if is_pooled_fund:
        is_pooled_fund = True
    is_other = sec_types.isothertype
    if is_other:
        is_other = True

    min_investment_accepted = int(off_data.minimuminvestmentaccepted.string)

    sales_amts = off_data.offeringsalesamounts
    offer_amt = sales_amts.totalofferingamount.string 
    if offer_amt == "Indefinite":
        total_offering_amount = float("inf") # this is a placeholder
        total_amount_sold = int(sales_amts.totalamountsold.string)
        total_remaining = float("inf")
    else:
        total_offering_amount = int(offer_amt)
        total_amount_sold = int(sales_amts.totalamountsold.string)
        if sales_amts.totalremaining.string == "Indefinite":
            total_remaining = float("inf")
        else:
            total_remaining = int(sales_amts.totalremaining.string)
        
    inv_info = off_data.investors
    has_non_accred = None
    num_non_accred = None
    tot_num_inv = None
    if inv_info != None:
        has_non_accred = inv_info.hasnonaccreditedinvestors.string
        if has_non_accred == "true":
            has_non_accred = True
            num_non_accred = None
            if inv_info.numbernonaccreditedinvestors != None:
                num_non_accred = inv_info.numbernonaccreditedinvestors.string
        else:
            has_non_accred = False
        tot_num_inv = inv_info.totalnumberalreadyinvested.string

    return {"ind_group_type": ind_group_type, 
            #"fund_type": fund_type,
            "issuer_size": issuer_size,
            "new": new, 
            "date_of_first_sale": date_of_first_sale,
            "is_equity": is_equity, 
            "is_debt": is_debt, 
            "is_pooled_fund": is_pooled_fund, 
            "is_other": is_other,
            "min_investment_accepted": min_investment_accepted,
            "total_offering_amount": total_offering_amount, 
            "total_amount_sold": total_amount_sold, 
            "total_remaining": total_remaining,
            "has_non_accred": has_non_accred,
            "num_non_accred": num_non_accred,
            "tot_num_inv": tot_num_inv}

