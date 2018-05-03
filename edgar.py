"""
File: edgar.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

SEC EDGAR Form D Web Scraping

Collection of functions to extract Form D data from
the SEC's EDGAR online data tool. This library forms
the basis for Form D scraping and parsing.
"""
from __future__ import print_function
from __future__ import unicode_literals
import sys
import os
import argparse
import urllib2, socket
import re
import datetime
import ssl
try:
    import ujson as json
except ImportError:
    import json
from bs4 import BeautifulSoup
import pprint as pp
import pickle
import gzip
import time
from parse_form_d import extract_issuer_info, extract_address, extract_offering_data

reload(sys)
sys.setdefaultencoding('utf8')


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--single", action="store_true", help="Parse single file from yesterday.")
    parser.add_argument("-q", "--quarter", action="store_true", help="Get all filings in last quarter.")
    parser.add_argument("--all", action="store_true", help="Get all filings since Q3 1994.")
    parser.add_argument("-p", "--pickle", action="store_true", help="Use pickled data instead of scraping.")
    parser.add_argument("--full", action="store_true", help="Use pickled data instead of scraping.")
    parser.add_argument("-c", "--complete", action="store_true", help="use complete_formd.pkl data.")
    args = parser.parse_args()
    return args


def main():
    args = parse_command_line()
    
    base_url = "https://www.sec.gov/Archives/edgar/daily-index/"
    archive_url = "https://www.sec.gov/Archives/"

    if args.single:
        now = datetime.datetime.now() 
        yesterday = now - datetime.timedelta(days=1)
        filings = single_day(yesterday)
        print(filings)

    elif args.quarter:
        # get all files for the last quarter
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        year = yesterday.strftime("%Y")
        quarter_num = (yesterday.month-1)//3 + 1
        quarter = "QTR{0}".format(quarter_num)
        quarter_url = "{0}{1}/{2}/".format(base_url, year, quarter)
        form_files = traverse(quarter_url)
        print(form_files)
        with open("last_quarter_form_files.pkl", "wb") as f:
            pickle.dump(form_files, f)

    elif args.all:
        # get all files for all time
        base_url = "https://www.sec.gov/Archives/edgar/full-index/"
        form_files = full_index_traverse(base_url)
        print(form_files)
        with open("all_form_files_fullindex.pkl", "wb") as f:
            pickle.dump(form_files, f)

    elif args.pickle:
        if args.complete:
            # use the complete list of form files to scrape all historical data
            with open("complete_formd.pkl", "rb") as f:
                form_files = pickle.load(f)   

            filings = {}
            for i, rel_link in enumerate(form_files):
                full_url = archive_url + rel_link
                try:
                    contents = get_file_contents(full_url)
                except ssl.SSLError as e:
                    time.sleep(2)
                    try:
                        contents = get_file_contents(full_url)
                    except ssl.SSLError as e:
                        contents = {}
                except ValueError as e:
                    print("Value Error hit - empty contents")
                    contents = {}
                filings[full_url] = contents
                
                # save periodically to deal with unanticipated parsing errors
                if i % 2000 == 0 and i != 0:
                    print(i)
                    print("saving...")
                    with open("scraped_formd_dict_{0}.json".format(i % 24000), "wb") as f:
                        json.dump(filings, f)
                    print("saved.")
                    time.sleep(1)
            # final save
            with open("scraped_formd_dict_{0}.json".format(i % 24000), "wb") as f:
                json.dump(filings, f)
            
        else:
            # only get file contents for one quarter of data based on -q flag output
            with open("last_quarter_form_files.pkl", "rb") as f:
                form_files = pickle.load(f)

            filings = {}
            for idx_file in form_files:
                rel_list = get_relative_links(idx_file)
                for i, url in enumerate(rel_list):
                    full_url = archive_url + url
                    contents = get_file_contents(full_url)
                    filings[i] = contents
            print(filings)

    elif args.full:
        with open("all_form_files_fullindex.pkl", "rb") as f:
            all_form_files = pickle.load(f)

        all_form_files = all_form_files[90:]
        all_urls = []
        total_len = 0
        for i, form_file in enumerate(all_form_files):

            links = get_relative_links(form_file)
            all_urls = all_urls + links
            total_len += len(links)
            print("{0}: {1}".format(form_file, total_len))
            if i == 100:
                print(len(all_urls))


            with open("form_d_links_{0}.pkl".format(i+100), "wb") as f:
                pickle.dump(all_urls, f)
    return 0


def single_day(day):
    """
    Retrieves the filings for a single day of Form D publication.

    Args:
        day: dt.Datetime object specifying a date to scrape
    Return:
        filings: dictionary of filings where the key is the 
            full url of the filing and the value is a dict
            of the relevant contents as pulled by the 
            get_file_contents() function from parse_form_d.py
    """
    base_url = "https://www.sec.gov/Archives/edgar/daily-index/"
    archive_url = "https://www.sec.gov/Archives/"

    formatted_day = day.strftime("%Y%m%d")
    year = day.strftime("%Y")
    
    quarter_num = (day.month-1)//3 + 1
    quarter = "QTR{0}".format(quarter_num)

    idx_file = "{3}/{0}/{1}/form.{2}.idx".format(year, quarter, formatted_day, base_url)
    
    rel_url_list = get_relative_links(idx_file)

    filings = {}
    for i, url in enumerate(rel_url_list):
        full_url = archive_url + url
        contents = get_file_contents(full_url)
        print(i)
        filings[full_url] = contents

    return filings


def get_relative_links(idx_file):
    """
    Uses regular expressions to extract the relative urls
    for Form D and Form D/A filings.

    Args:
        idx_file - url to form filings
    Returns:
        rel_url_list - list of strings of form "edgar/data/[numbers]/[filename].txt"
    """
    response = get_page(idx_file)

    # handles gzip-compressed files
    if idx_file.endswith(".gz"):
        with open("temp.txt", "w") as f:
            content = response.read()
            f.write(content)
            f.close()
        
        with gzip.open("temp.txt", "rb") as f:
            data = f.readlines()
        os.remove("temp.txt")
    else:
        data = response.readlines()

    rel_url_pattern = re.compile(r"edgar/data/[\S]+txt")
    rel_url_list = []
    for i, line in enumerate(data):
        # check if the line is for a Form D or Form D/A
        line = unicode(line, errors="replace")
        if line.startswith("D ") or line.startswith("D/A "):
            # if so, get the url at the end
            match = re.search(rel_url_pattern, line)
            
            if match == None:
                print("Failed to parse Form D line")
            else:
                rel_url = match.group(0)
            
            rel_url_list.append(rel_url)
    
    return rel_url_list


def get_file_contents(url):
    """
    Get the Form D or D/A file contents from the given url.

    Args:
        url - full url for a valid Form
    Returns:
        contents_dict - dict with four keys as follows:
            Primary Issuer: contains contact info for primary issuer
            Secondary Issuers: contains info about secondary issuers
            Related People: info on key individuals working at firm
            Offering Data: all numerical data and fund type data
            See parse_formd.py for more information.
    """
    soup = make_soup(url)
    if soup.xml == None:
        return {}
    form_d = soup.xml.edgarsubmission

    # get primary issuer info
    primary_issuer = form_d.primaryissuer
    pr_issuer_info = extract_issuer_info(primary_issuer)

    # issuer list
    secondary_issuers = []
    sec_issuer_list = form_d.issuerlist
    if sec_issuer_list != None:
        for issuer in sec_issuer_list.contents:
            if issuer.name == "over100issuerflag":
                continue
            if issuer == "\n":
                continue
            secondary_issuers.append(extract_issuer_info(issuer))
    
    # related persons
    related_people = []
    people = form_d.relatedpersonslist

    for person in people.find_all("relatedpersoninfo"):
        first_name = person.relatedpersonname.firstname.string
        last_name = person.relatedpersonname.lastname.string
        address = extract_address(person.relatedpersonaddress)
        
        relationships = []
        for rel in person.relatedpersonrelationshiplist.children:
            relationships.append(rel.string)

        related_people.append({"first_name": first_name, 
                                "last_name": last_name, 
                                "address": address, 
                                "relationships": relationships})

    # offering data
    off_data = form_d.offeringdata
    offering_data = extract_offering_data(off_data)
    
    # assemble the data together
    contents_dict = {}
    contents_dict["Primary Issuer"] = pr_issuer_info
    contents_dict["Secondary Issuers"] = secondary_issuers
    contents_dict["Related People"] = related_people
    contents_dict["Offering Data"] = offering_data

    return contents_dict


def traverse(url):
    """
    Recursively traverse the EDGAR data directory tree 
    and return the names of all form files.

    Args:
        url - base url from which to begin the recursive traversal.
    Returns:
        form_files - list of filenames to each be parsed by get_links_list
    """
    form_files = []
    url_json = url + "index.json"
    response = get_page(url_json)
    data = json.load(response)
    items = data["directory"]["item"]
    
    for rel_link in items:
        href = rel_link["href"]
        full_link = url + href

        # if the item is a subdirectory, traverse it
        if rel_link["type"] == "dir":
            print(href)
            form_files = form_files + traverse(full_link)
        
        # if the item is a file, add to list
        if rel_link["type"] == "file":
            if href.startswith("form"):
                form_files.append(full_link)
    
    return form_files

def full_index_traverse(url):
    """
    Recursively traverse the EDGAR data directory tree 
    and return the names of all form files.

    Args:
        url - base url from which to begin the recursive traversal.
    Returns:
        form_files - list of filenames to each be parsed by get_links_list
    """
    form_files = []
    url_json = url + "index.json"
    response = get_page(url_json)
    data = json.load(response)
    items = data["directory"]["item"]
    
    for rel_link in items:
        href = rel_link["href"]
        full_link = url + href

        # if the item is a subdirectory, traverse it
        if rel_link["type"] == "dir":
            print(href)
            form_files = form_files + full_index_traverse(full_link)
        
        # if the item is a file, add to list
        if rel_link["type"] == "file":
            if href.startswith("form.idx"):
                form_files.append(full_link)
    
    return form_files


#### Helper Functions for Web Scraping
def make_soup(url):
    response = get_page(url)

    if response == 0:
        print("    Could not get page: {0}".format(url), file=sys.stderr)
        return BeautifulSoup("", 'html.parser')

    html = "".join(response.readlines())

    return BeautifulSoup(html, 'lxml')
    
def get_page(url):
    try:
        socket.setdefaulttimeout(2)
        response = urllib2.urlopen(url)
    except urllib2.URLError as e:
        return 0
    except socket.timeout as e:
        return 0
    return response
    

if __name__ == '__main__':
    main()
