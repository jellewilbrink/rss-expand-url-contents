import feedparser
import re
from bs4 import BeautifulSoup, CData
import requests
import aiohttp
import asyncio
import copy

import pprint


def expand_rss_to_url(
    feed_url: str, pattern_to_expand: str, bs4_find_all_params: tuple
) -> str:
    """ 
    NOTE: only looks in the summary and summary detailed sections (ideally). Acutally, filters for [[!CDATA]] and parses those

    Args:
        - feed_url: url of rss to expand.
        - pattern_to_expand: (regex) pattern for urls that need expanding.
        - bs4_find_all_params: parameters to be fed to the bs4.findAll() method, aka a selector for html elements that need to be parsed from the site.

    Returns:
        - RSS feed output without the urls, but instead the text found on those pages.
    """
    # fp = feedparser.parse(feed_url)
    raw_xml = requests.get(feed_in).text

    count=0
    feed_soup = BeautifulSoup(raw_xml, 'html.parser')
    all_str_tags = feed_soup.findAll(string=True)
    for txt in all_str_tags:
        
        inner_feed_soup = BeautifulSoup(copy.deepcopy(txt), 'lxml')
        all_a_tags = inner_feed_soup.findAll('a', href=True)

        for a in all_a_tags:

            pattern = re.compile(pattern_to_expand)
            if pattern.match(a["href"]):
                print(f"Parsing {a['href'] }")

                site_xml = requests.get(a["href"]).text
                site_soup = BeautifulSoup(site_xml, 'html.parser')

                element = site_soup.find(*bs4_find_all_params)

                if element != None:
                    a.replace_with(element)

        txt.replace_with(inner_feed_soup)

    return str(feed_soup)


if __name__ == "__main__":
    feed_in = "https://anchor.fm/s/19b5cbd8/podcast/rss"
    url_pattern="https://laernorsknaa.com/no_request*"
    element_pattern=("div",{'class': 'wp-block-group__inner-container'})
    feed_out = expand_rss_to_url(feed_in, url_pattern, element_pattern)

    myfile = open("build/rss.xml", "w", encoding='utf-8')
    myfile.write(feed_out)
