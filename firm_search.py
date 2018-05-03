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
    #bridge()

    name = "Farallon"
    address = "One Maritime Plaza, Suite 2100, San Francisco, CA 94111"
    
    tokens = nltk.word_tokenize(name.lower())
    firm_info = [name, address, "Hedge Fund"]
    queries = prepare_searches(firm_info)
    best_urls = cross_reference(queries)
    return 0


def page_parse():
    name_results, name_urls = get_google_pages(name)
    print(name_urls)
    good_urls = []
    for url in name_urls:
        if url.startswith("https://www.bloomberg.com/"):
            bloomberg = parse_bloomberg(url)
        if url.startswith("https://www.wikipedia.org"):
            wiki = parse_wiki(url)
        if url.startswith("https://whalewisdom.com"):
            whale = parse_whale(url)
        if name.lower() in url and "capital" in url:
            good_urls.append(url)
        for token in tokens:
            if token in url:
                pass
                #good_urls.append(token)
                #print(url)
    print(good_urls)
    
    cyrus = name_results[0]
    text = cyrus.getText()
    clean_text = " ".join(text.split())
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    sentences = tokenizer.tokenize(clean_text)

    results = extract_aum(sentences)
    print(results)


def cross_reference(queries):
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



def bridge():
    name = "Bridgewater Associates"
    address = "1 Glendinning Pl, Westport, CT 06880"

    name_results, name_urls = get_google_pages(name)
    add_results, add_urls = get_google_pages(address)
    
    # get results that appear for both the name and the address - this tends to give the correct website
    double_hits = [x for x in name_urls if x in add_urls]

    page_text = []
    for url in double_hits:
        for result in name_results:
            if result.url == url:
                text = result.getText()
                
                clean_text = " ".join(text.split())
                #print(clean_text)
                page_text.append(clean_text)

    bwater = page_text[0]
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    sentences = tokenizer.tokenize(bwater)

    results = extract_aum(sentences)
    print(results)


def extract_aum(sentences):
    pattern = re.compile(r'\$[\d\.\,]+\s[b|m]illion')
    occurrences = []
    for sent in sentences:
        m = re.search(pattern, sent)
        if m:
            aum = m.group(0)
            context = sent
            occurrences.append((aum, context))
        # if "$" in sent:
        #     print(sent)
        #     aum = sent
    return occurrences

# parse Bloomberg search result
def parse_bloomberg(url):
    soup = make_soup(url)
    description = soup.find("p", {"id": "bDesc"})
    website = soup.find("a", {"class": "link_sb"})
    if description != None:
        print(description.contents)
    if website != None:
        print(website.contents)
    pass

# parses Wikipedia search results
def parse_wiki(url):
    pass

# parses Whale Wisdom search result
def parse_whale(url):
    pass


def extract_quality_urls(urls):
    high_quality = []
    for url in urls:
        if url.startswith("https://en.wikipedia.org/"):
            high_quality.append(url)
        if url.startswith("https://www.bloomberg.com/"):
            high_quality.append(url)


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