import re
from bs4 import BeautifulSoup
import requests

import copy


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
    raw_xml = requests.get(feed_url).text
    req_counter = 1

    prev_hrefs = {}

    feed_soup = BeautifulSoup(raw_xml, "xml")
    all_str_tags = feed_soup.findAll(string=True)

    for txt in all_str_tags:
        inner_feed_soup = BeautifulSoup(copy.deepcopy(txt), "html.parser")
        all_a_tags = inner_feed_soup.findAll("a", href=True)

        for a in all_a_tags:
            pattern = re.compile(pattern_to_expand)
            if pattern.match(a["href"]):
                if a["href"] in prev_hrefs:
                    element = prev_hrefs[a["href"]]
                else:
                    # request the webpage
                    print(f"Parsing {a['href'] }")

                    req_counter += 1
                    site_xml = requests.get(a["href"]).text
                    site_soup = BeautifulSoup(site_xml, "html.parser")

                    element = site_soup.find(*bs4_find_all_params)

                    prev_hrefs[a["href"]] = copy.deepcopy(element)

                if element != None:
                    a.parent.insert_after(element)

        txt.replace_with(inner_feed_soup)

    # Get plain text, because CDATA tag is lost in parser
    str_feed = str(feed_soup)
    str_feed = str_feed.replace("<description>", "<description><![CDATA[")
    str_feed = str_feed.replace("</description>", "]]></description>")

    print(f"Number of requests made: {req_counter}")
    return str(str_feed)


if __name__ == "__main__":
    feed_in = "https://anchor.fm/s/19b5cbd8/podcast/rss"
    url_pattern = "https://laernorsknaa.com/*"
    element_pattern = ("div", {"class": "wp-block-group__inner-container"})
    feed_out = expand_rss_to_url(feed_in, url_pattern, element_pattern)

    myfile = open("build/rss.xml", "w", encoding="utf-8")
    myfile.write(feed_out)

    feed_in2 = "https://anchor.fm/s/4adac90c/podcast/rss"
    feed_out2 = expand_rss_to_url(feed_in2, url_pattern, element_pattern)

    myfile2 = open("build/rss2.xml", "w", encoding="utf-8")
    myfile2.write(feed_out2)
