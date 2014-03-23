# ecfs-python

A Python library that scrapes fcc.gov to retrieve rulemaking information from the Electronic Comment Filing System.

## Usage

```python
from ecfs import FccProceeding

proceeding = FccProceeding(docket_number="14-28")
proceeding.get_comment_urls()
"""
[
	{
        "page_url": "http://apps.fcc.gov/ecfs/comment_search/execute?proceeding=14-28&pageSize=100&pageNumber=1",
        "comment_urls": [
        	"http://apps.fcc.gov/ecfs/comment/view?id=6017609065",
        	"...",
        ],
        "page_number": "1"
    },
    {
    	...
	},
]
http://apps.fcc.gov/ecfs/comment/view?id=6017609065
"""
```

## TODO:

- package for pip
- implement `get_comment_data_for_comment_url`. This would return information about the filing, such as date filed, name of filer, and an option to make an additional HTTP request to get the full text.
- tests (maybe)
- filter by date. This would allow you to scrape once, save the data (e.g. as json somewhere), then each day thereafter, incrementally retreive only new filings. You could then append the new filing data to the json file.

## How

There's also a Ruby cousin to this: http://github.com/adelevie/ecfs. The Ruby version takes a somewhat different approach, however. The Ruby gem downloads an Excel file that fcc.gov allows you to export. The gem then parses rows of the file to get filing information. This works really well (fast and accurate) until result sets exceed 100,000 filings. This Python library is an attempt at building a somewhat slower, ~~but more dependable FCC ECFS scraper~~*. The library eschews the spreadsheet approach, and instead visits each web page containing filing results. This means sending an HTTP request to fcc.gov for every 100 filings (the maximum displayed per page). Please don't slam fcc.gov with an irrationally large number of requests. For your convenience, I added an optional `sleep` parameter to `FccProceeding.__init__()`. It's the number of seconds the script will wait between HTTP requests to fcc.gov.

## *Limitations

Apparently, the same 10,000 document limit that is applied to spreadsheets also applies to the collection size of paginated result sets. Translation: this library suffers from the same limitations as its Ruby cousing, but takes many more HTTP requests to achieve the same results. For example, visit http://apps.fcc.gov/ecfs/comment_search/execute?proceeding=14-28&perPage=100&pageNumber=100. You'll notice a message indicating that there are more than 10,000 records in the the 14-28 docket. However, the pagination stops at page 100 (with 100 documents per page => 10,000 total docs).

# License

(c) 2014 Alan deLevie. This software is licensed under the MIT License.
