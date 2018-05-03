"""
File: firm_search.py
Author: Michael Byrnes
Email: michael.byrnes@yale.edu
Python Version: 2.7

Automated retrieval of Google search results for firms.
"""
from googlesearch.googlesearch import GoogleSearch
import time
import random
import nltk.data
import re
from edgar import get_page, make_soup
from collections import Counter
import pprint as pp

def main():
    # example of function usage on a well-known firm
    name = "Bridgewater Associates"
    address = "1 Glendinning Pl, Westport, CT 06880"
    
    tokens = nltk.word_tokenize(name.lower())
    firm_info = [name, address, "Hedge Fund"]
    queries = prepare_searches(firm_info)
    best_urls = cross_reference(queries)
    bwater = best_urls[0]
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    sentences = tokenizer.tokenize(bwater)

    results = extract_aum(sentences)
    print(results)
    return 0


def cross_reference(queries):
    """
    Cross-references search queries to determine important URLS.

    Args:
        queries: list of strings to search and cross-reference
    Returns:
        just_urls: list of top 10 urls in sorted order of importance
    """
    query_results = []
    for query in queries:
        results, urls = get_google_pages(query)
        print(urls)
        time.sleep(0.5)
        query_results.append((query, results, urls))
    
    all_urls = []
    for query, results, urls in query_results:
        all_urls += urls

    url_counts = Counter(all_urls)
    #pp.pprint(url_counts)

    top_10 = url_counts.most_common(10)

    pp.pprint(top_10)

    just_urls = [x[0] for x in top_10]
    print(just_urls)
    return just_urls


def prepare_searches(firm_info):
    """
    Converts firm into a list of searches for 
    cross_reference() method.

    Args:
        firm_info: tuple of firm information
    Returns:
        searches: list of searches to perform
    """
    name = firm_info[0]

    tokens = nltk.word_tokenize(name.lower())
    
    address = firm_info[1]
    
    firm_type = firm_info[2]

    related_words = ["investment", "capital"]
    # this is not real
    if firm_type == "Hedge Fund":
        related_words.append("hedge fund")
    elif firm_type == "Venture Capital":
        related_words.append("venture capital")
    elif firm_type == "Private Equity":
        related_words.append("private equity")

    if "capital" in tokens:
        tokens.remove("capital")

    searches = [name, address]

    for word in related_words:
        search = name + " " + word
        searches.append(search)

    return searches


def extract_aum(sentences):
    """
    Uses regular expression to search for a dollar amount
    and extracts the relevant sentences.
    """
    pattern = re.compile(r'\$[\d\.\,]+\s[b|m]illion')
    occurrences = []
    for sent in sentences:
        m = re.search(pattern, sent)
        if m:
            aum = m.group(0)
            context = sent
            occurrences.append((aum, context))
    return occurrences


def get_google_pages(query):
    # must set prefecth_pages to false to avoid Google blocking the request
    response = GoogleSearch().search(query, prefetch_pages=False)
    page_titles = []
    page_urls = []
    page_text = []
    #print(response.results)

    for result in response.results:
        #title = result.title
        #page_titles.append(title)
        #print(title)
        
        url = result.url
        page_urls.append(url)
        #print(url)
        #text = result.getText()
        #page_text.append(text)

        #sleep_time = random.randint(3,6)
        #time.sleep(sleep_time)
    return response.results, page_urls



if __name__ == '__main__':
    main()