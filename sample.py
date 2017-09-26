"""
In Hawaii, committee reports reference witness testimony in natural language.
For example, "Testimony in support of this measure was submitted by Hawaii
Long Term Care Association, ..."

See http://www.capitol.hawaii.gov/session2002/commreports/SR68_SD1_SSCR3343_.htm

Available 1999-present.
"""

from scrapy.spiders import Spider, Request
from states.items import Report

class StateSpider(Spider):

    def start_requests(self):
        # For each chamber-year 1999-present there is a page of links to committee reports.
        index_urls = ['http://www.capitol.hawaii.gov/session{}/commreports/'.format(year) 
        for year in range(1999, 2017)]
        for url in index_urls:
            yield Request(url, self.parse_year)

    def parse_year(self, response):
        report_urls = response.xpath("//a[matches(@href, 'html', 'i')]")
        report_urls = [url.extract() for url in report_urls if url.extract()]
        for url in report_urls:
            yield Request(url, self.parse_report)

    def parse_report(self, response):
        body = response.xpath('//body[text()]').extract()
        report = Report()
        report['text'] = body
        report['bill'] = None # Pull from URL, e.g. 'SR68'
        report['committee'] = None # Pull from signature
        report['session'] = None # Pull from URL
        report['url'] = response.url
        return report