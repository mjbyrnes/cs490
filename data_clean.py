"""
File: data_clean.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

Converting scraped JSON data into usable data frame format for data analysis.
"""
from __future__ import print_function
from __future__ import unicode_literals
import sys
import pandas as pd
try:
    import ujson as json
except ImportError:
    import json
import pprint as pp
import glob

reload(sys)
sys.setdefaultencoding('utf8')


def main():
    json_files = glob.glob("data/json_data/scraped_formd_dict_*")
    print(json_files)
    make_df_from_json(json_files, "all_data.csv")
    

def make_df_from_json(json_files, out_file):
    """
    Converts JSON data output from the EDGAR scraper to a usable
    Pandas data frame format for classification.
    """
    table = [["name", 
             "cik", 
             "city",
             "state",
             "street1",
             "street2",
             "zip_code",
             "year_of_incorp", 
             "min_inv", 
             "tot_off", 
             "tot_sold", 
             "tot_rem", 
             "ind_group_type", 
             "has_non_accred", 
             "num_non_accred", 
             "tot_num_inv"
             ]]   

    for json_dict in json_files:

        with open(json_dict, "rb") as f:
            data = json.load(f)
        print(json_dict)

        for i, key in enumerate(data):
            # if i % 1000 == 0:
            #     print(i)
            entry = data[key] 
            if entry == {}:
                #print("missing entry {0}".format(i))
                continue
            row = []

            primary_issuer = entry["Primary Issuer"]
            cik = primary_issuer["cik"]
            name = primary_issuer["entity_name"]
            phone = primary_issuer["phone"]
            year_of_incorp = primary_issuer["year_of_incorp"]
            address = primary_issuer["address"]
            city = address["city"]
            state = address["state"]
            street1 = address["street1"]
            street2 = address["street2"]
            zip_code = address["zip_code"]

            secondary_issuers = entry["Secondary Issuers"]
            related_people = entry["Related People"]
            
            offering_data = entry["Offering Data"]
            min_inv = offering_data["min_investment_accepted"]
            tot_off = offering_data["total_offering_amount"]
            tot_sold = offering_data["total_amount_sold"]
            tot_rem = offering_data["total_remaining"]
            ind_group_type = offering_data["ind_group_type"]
            has_non_accred = offering_data["has_non_accred"]
            num_non_accred = offering_data["num_non_accred"]
            tot_num_inv = offering_data["tot_num_inv"]            

            row = [name, 
                    cik, 
                    city,
                    state,
                    street1,
                    street2,
                    zip_code,
                    year_of_incorp,
                    min_inv,
                    tot_off,
                    tot_sold,
                    tot_rem,
                    ind_group_type,
                    has_non_accred,
                    num_non_accred,
                    tot_num_inv
                    ]

            table.append(row)

    df = pd.DataFrame(table)
    df.to_csv(out_file)

    return 0


if __name__ == '__main__':
    main()
