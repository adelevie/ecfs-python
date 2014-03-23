import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
import re
import time

PROCEEDING = "14-28"

def page_url_template(**kwargs):
    proceeding = kwargs.get("proceeding")
    page_number = kwargs.get("page_number")
    url = "http://apps.fcc.gov/ecfs/comment_search/execute?proceeding=%s&pageSize=100&pageNumber=%s" % (proceeding, page_number)
    return url

def comment_urls_from_page_url(page_url, **kwargs):
    response = requests.get(page_url)
    text = response.text
    soup = BeautifulSoup(text)
    urls = soup.find_all("a")
    found_count = 0
    comment_urls = []
    for url in urls:
        href = url.attrs.get('href', None)
        if href:
            parsed = urlparse("http://apps.fcc.gov"+href)
            if parsed.path == "/ecfs/comment/view":
                id = id_from_comment_url(href)
                comment_url = "http://apps.fcc.gov/ecfs/comment/view?id=%s" % id_from_comment_url(href)
                comment_urls.append(comment_url)
    print "Found %s comment urls on page %s." % (len(comment_urls), kwargs.get('page_number'))
    return {
        "page_url": page_url,
        "comment_urls": comment_urls,
        "page_number": kwargs.get('page_number')
    }

def id_from_comment_url(comment_url):
    txt=comment_url

    re1='(\\?)' # Any Single Character 1
    re2='(id)'  # Word 1
    re3='(=)'   # Any Single Character 2
    re4='(\\d+)'    # Integer Number 1

    rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        c1=m.group(1)
        word1=m.group(2)
        c2=m.group(3)
        int1=m.group(4)
        # txt2re.com ftw
        return int1

class FccProceeding(object):
    def __init__(self, **kwargs):
        self.docket_number = kwargs.get('docket_number')
        self.sleep = kwargs.get('sleep', None)

    def get_comment_urls(self):
        comment_urls = []
        if self.sleep:
            time.sleep(self.sleep)
        results_page = requests.post(
            "http://apps.fcc.gov/ecfs/comment_search/execute",
            {
                "proceeding": PROCEEDING,
                "pageSize": "100"
            }
        )
        results_page_soup = BeautifulSoup(results_page.text)
        links = [link for link in results_page_soup.find_all("a") if link.get("href", None) is not None]
        last_page_tag = results_page_soup.find("a", text="Last")
        last_page_number = int(
                               urlparse(
                                   last_page_tag.get("href")
                               ).query.split("pageNumber=")[1]
                            )
        print "This docket has %s pages." % last_page_number
        total_to_find = last_page_number*100
        total_found = 0
        print "That's approximately %s filings." % total_to_find
        page_numbers = range(1, last_page_number+1)
        for page_number in page_numbers:
            page_url = page_url_template(proceeding=PROCEEDING, page_number=page_number)
            urls = comment_urls_from_page_url(page_url, page_number=page_number)
            comment_urls.append(urls)
            just_found = len(urls.get('comment_urls'))
            total_found = total_found + just_found
            percent = (float(total_found)/(total_to_find))*100
            print "%s/%s (%s %%)" % (total_found, total_to_find, percent)
        return comment_urls

proceeding = FccProceeding(docket_number="14-28")
comment_urls = proceeding.get_comment_urls()
