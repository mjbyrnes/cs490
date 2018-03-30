"""
File: edgar.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

SEC EDGAR Form D Web Scraping

Collection of functions to extract Form D data from
the SEC's EDGAR online data tool.
"""
from __future__ import print_function
from __future__ import unicode_literals
import sys
import os
import argparse
import urllib2, socket
import re
import datetime
import json
from bs4 import BeautifulSoup
import pprint as pp
import pickle
import gzip
from parse_formd import extract_issuer_info, extract_address, extract_offering_data

reload(sys)
sys.setdefaultencoding('utf8')


def parse_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--single", action="store_true", help="Parse single file from yesterday.")
    parser.add_argument("-q", "--quarter", action="store_true", help="Get all filings in last quarter.")
    parser.add_argument("--all", action="store_true", help="Get all filings since Q3 1994.")
    
    args = parser.parse_args()
    return args


def main():
    args = parse_command_line()
    
    quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
    start_year = 1994
    cur_year = 2018
    years = []
    for i in range(cur_year - start_year + 1):
        years.append(start_year + i)
    
    base_url = "https://www.sec.gov/Archives/edgar/daily-index/"

    if args.single:
        now = datetime.datetime.now() 
        yesterday = now - datetime.timedelta(days=1)
        
        formatted_yesterday = yesterday.strftime("%Y%m%d")
        year = yesterday.strftime("%Y")
        
        quarter_num = (yesterday.month-1)//3 + 1
        quarter = "QTR{0}".format(quarter_num)
    
        idx_file = "{3}/{0}/{1}/form.{2}.idx".format(year, quarter, formatted_yesterday, base_url)
        gz_idx = "{0}2014/QTR2/form.20140626.idx.gz".format(base_url)
        
        #rel_url_list = get_relative_links(idx_file)
        rel_url_list = get_relative_links(gz_idx)
        #print(rel_url_list)
        first_form = rel_url_list[0]
        archive_url = "https://www.sec.gov/Archives/"
        full_url = archive_url + first_form

        contents = get_file_contents(full_url)

    elif args.quarter:
        # get all for the last quarter
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
        # get all for all time
        form_files = traverse(base_url)
        print(form_files)

        with open("all_form_files.pkl", "wb") as f:
            pickle.dump(form_files, f)

    return 0


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
    url = "https://www.sec.gov/Archives/edgar/data/1729740/0001729740-18-000001.txt"
    response = get_page(url)
    data = response.read()
    #print(data)
    #e = xml.etree.ElementTree.fromstring(data).getroot()

    soup = make_soup(url)
    form_d = soup.xml.edgarsubmission

    # get primary issuer info
    primary_issuer = form_d.primaryissuer
    pr_issuer_info = extract_issuer_info(primary_issuer)

    # issuer list
    secondary_issuers = []
    sec_issuer_list = form_d.issuerlist
    if sec_issuer_list != None:
        for issuer in sec_issuer_list.children:
            secondary_issuers.append(extract_issuer_info(issuer))
    
    # related persons
    related_people = []
    people = form_d.relatedpersonslist

    for person in people.find_all("relatedpersoninfo"):
        print(person)
        first_name = person.relatedpersonname.firstname.string
        last_name = person.relatedpersonname.lastname.string
        address = extract_address(person.relatedpersonaddress)
        
        relationships = []
        for rel in person.relatedpersonrelationshiplist.children:
            relationships.append(rel.string)

        related_people.append([first_name, last_name, address, relationships])

    # offering data
    off_data = form_d.offeringdata
    offering_data = extract_offering_data(off_data)
    
    # print(pr_issuer_info)
    # print(secondary_issuers)
    # print(related_people)
    # print(offering_data)
    contents_dict = {}
    contents_dict["Primary Issuer"] = pr_issuer_info
    contents_dict["Secondary Issuers"] = secondary_issuers
    contents_dict["Related People"] = related_people
    contents_dict["Offering Data"] = offering_data

    return contents_dict


#### Helper Functions for Web Scraping

def make_soup(url):
    response = get_page(url)

    if response == 0:
        print("    Could not get page: {0}".format(url[-4:]), file=sys.stderr)
        return BeautifulSoup("", 'html.parser')

    html = "".join(response.readlines())

    return BeautifulSoup(html, 'lxml')
    

def get_page(url):
    try:
        socket.setdefaulttimeout(5)
        response = urllib2.urlopen(url)
    except urllib2.URLError as e:
        return 0
    except socket.timeout as e:
        return 0
    return response
    

if __name__ == '__main__':
    main()
