"""
File: edgar.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Date: 1/31/2018
Python Version: 2.7

Draft of SEC EDGAR Form D retrieval
"""
from __future__ import print_function
from __future__ import unicode_literals
import sys
import argparse
import urllib2, socket
import re
import datetime
from bs4 import BeautifulSoup
from StringIO import StringIO

reload(sys)
sys.setdefaultencoding('utf8')


def parse_command_line():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-f", "--founded", action="store_true", help="Include if you want founding years.")
    # parser.add_argument("-i", "--insiders", action="store_true", help="Include if you want insider transaction info.")
    # parser.add_argument("-w", "--wikipedia", action="store_true")
    # parser.add_argument("tickers", nargs="*", help="List of tickers or CSV files.")
    args = parser.parse_args()
    return args

def main():
    #args = parse_command_line()

    # url = "https://www.sec.gov/Archives/edgar/daily-index/index.json"
    # response = get_page(url)
    # # soup = make_soup()
    # data = json.loads(response.read())
    # print(data)
    # pp.pprint(data)
    # list_of_files = data["directory"]["item"]
    # print(list_of_files)
    quarters = ["QTR1", "QTR2", "QTR3", "QTR4"]
    year = "2018"
    #now = datetime.datetime.now()
    #today = now.strftime("%Y%m%d")
    #print(today)
    #url = "https://www.sec.gov/Archives/edgar/daily-index/{0}/{1}/crawler.{2}.idx".format(year, quarters[0], today)
    #url = "https://www.sec.gov/Archives/edgar/daily-index/{0}/{1}/crawler.20180131.idx".format(year, quarters[0])
    url = "https://www.sec.gov/Archives/edgar/daily-index/{0}/{1}/form.20180206.idx".format(year, quarters[0])
    #urllib2.urlretrieve(url, "temp")
    # with open("form.20180206.idx") as f:
    #     url = f.read()
    #with open("temp", "r") as f:
    #pd.read_csv(f, sep="|")
    
    response = get_page(url)
    data = response.readlines()
    
    test_string = "1-A/A       Hologram USA Networks Inc.                                    1723480     20180206    edgar/data/1723480/0001493152-18-001482.txt         "
    

    pattern = re.compile(r"([\w\-/]+)\s+([\w\.]+(\s[\w\.]+)*)\s+(\d+)\s+(\d+)\s+([\w\/\.\-]+)")#+\s?[a-zA-Z0-9]+$") \s+(\d+)\s+([\w/\-]+)
    res = re.match(pattern, test_string)

    for i in range(pattern.groups+1):
        print(res.group(i))


    return 0
    for i, line in enumerate(data):
        parsed = re.match(pattern, line)
        form_type = parsed.group(1)
        company_name = parsed.group(2)
        cik = parsed.group(4) # group(3) is meaningless
        date = parsed.group(5)
        url = parsed.group(6)
        #if i == 10:
        # if line.startswith("Form Type"):
        #     guide = line
        #     comp_name_idx = guide.find("Company Name")
        #     cik_idx = guide.find("CIK")
        #     date_idx = guide.find("Date Filed")
        #     url_idx = guide.find("File Name")
        # if i == 12:
        #     print(line[:comp_name_idx])
        #     print(line[comp_name_idx:cik_idx])
        #     print(line[cik_idx:date_idx])
        #     print(line[date_idx:url_idx])
        #     print(line[url_idx:])
        #    return 0
        #if line.startswith("D ") or line.startswith("D/A "):
        #    print(line)

    

def make_soup(url):
    response = get_page(url)

    if response == 0:
        print("    Could not get page: {0}".format(url[-4:]), file=sys.stderr)
        return BeautifulSoup("", 'html.parser')

    html = "".join(response.readlines())

    return BeautifulSoup(html, 'html.parser')
    

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
