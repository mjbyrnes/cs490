from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
import os
import time
import pandas as pd
import numpy as np
import sqlite3
import datetime as dt
from classifier import clean_data
from edgar import single_day
from data_clean import make_df_from_json
import argparse
try:
    import ujson as json
except ImportError:
    import json

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical", action="store_true", help="Add all historical files to database.")
    args = parser.parse_args()
    return args


def main():
    args = parse_command_line()

    if args.historical:
        tic = time.time()
        conn = sqlite3.connect("webapp/formddb.sqlite3")
        c = conn.cursor()
        
        reader = pd.read_csv("all_data.csv", header=1, chunksize=100000)
        for df in reader:
            df = df.iloc[:10,:]
            add_forms(df, c)
            conn.commit()
            return 0
                 
        toc = time.time()
        print("db_insert: %s seconds elapsed\n" % (toc-tic))
    else:
        for i in range(1,7):

            yesterday = dt.datetime.now() - dt.timedelta(days=i)    
            if yesterday.isoweekday() in range(1, 6):
                full_process_form_d(yesterday)


def full_process_form_d(day):
    """
    This function implements the full pipeline for
    (1) Scraping
    (2) Data Cleaning
    (3) Database Insertion

    Args:
        day: dt.Datetime object for the day you want to scrape
    Returns:
        nothing, but inserts data into sqlite database
    """
    # scrape the data for a day
    filings = single_day(day)
    with open("tempdata", "wb") as f:
        json.dump(filings,f)
    
    # clean it to df
    out_file = "{0}_formds".format(day)
    make_df_from_json(["tempdata"], out_file)


    # add to database
    conn = sqlite3.connect("webapp/formddb.sqlite3")
    c = conn.cursor()
    df = pd.read_csv(out_file, header=1)
    add_forms(df, c, day)
    conn.commit()
    
    # clean up intermediate data after insertion
    os.remove(out_file)
    os.remove("tempdata")


def add_forms(df, conn, date_added):
    df = clean_data(df, categorical=False)
    names = df.iloc[:,1].tolist()
    cik = df.iloc[:,2].tolist()
    city = df.iloc[:,3].tolist()
    state = df.iloc[:,4].tolist()
    street1 = df.iloc[:,5].tolist()
    street2 = df.iloc[:,6].tolist()
    zip_code = df.iloc[:,7].tolist()
    year_of_incorp = df.iloc[:,8].tolist()
    min_inv = df.iloc[:,9].tolist()
    tot_off = df.iloc[:,10].tolist()
    tot_sold = df.iloc[:,11].tolist()
    tot_rem = df.iloc[:,12].tolist()
    ind_group_type = df.iloc[:,13].tolist()
    has_non_accred = df.iloc[:,14].astype(int).tolist()
    num_non_accred = df.iloc[:,15].tolist()
    tot_num_inv = df.iloc[:,16].tolist()
    df["date_added"] = dt.datetime.strftime(date_added, "%Y-%m-%d")
    date_added = df.iloc[:,19].tolist()

    sql_vals = ", ".join('("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s, %s, %s, %s, "%s", %s, %s, "%s")' %
        (cik[i],
         names[i],
         year_of_incorp[i],
         street1[i],
         street2[i],
         zip_code[i],
         city[i],
         state[i],
         ind_group_type[i],
         min_inv[i],
         tot_off[i],
         tot_sold[i],
         tot_rem[i],
         has_non_accred[i],
         num_non_accred[i],
         tot_num_inv[i],
         date_added[i]) for i in range(len(df)))

    conn.execute("insert into analyst_formd (cik,name,year_of_incorp,street1,street2,zip_code,city,state,ind_group_type,min_investment_accepted,total_offering_amount,total_amount_sold,total_remaining,has_non_accred,num_non_accred,tot_number_investors,date_added) "
                " values {0}".format(sql_vals))
    return 0


if __name__ == "__main__":
    main()
