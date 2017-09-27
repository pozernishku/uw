# -*- coding: utf-8 -*- csv
import scrapy, os
from scrapy.http.request import Request
from scrapy.selector import Selector

class OhiopdfSpider(scrapy.Spider): 
    name = 'ohiopdf'
    allowed_domains = ['www.ohiohouse.gov']
    start_urls = ['http://www.ohiohouse.gov/committee/standing-committees']

    def parse(self, response):
        comm = response.xpath('//h3/a[@class="black"]/text()').extract()[0]
        href = response.xpath('//h3/a[@class="black"]/@href').extract()[0]
        yield Request(response.urljoin(href), callback=self.parsedate, meta={'comm': comm})

    def parsedate(self, response):
        i = -1
        dates = response.xpath('//div[@class="collapsibleListHeader"]/h3/text()').extract()
        for date in dates:
            i += 1
            collapsibleList = response.xpath('//div[@class="collapsibleList"]').extract()[i]
            yield Request(response.url, callback=self.parsebill, meta={'collapsibleList': collapsibleList }, dont_filter=True)

    def parsebill(self, response):
        tbl = Selector(text=response.meta.get('collapsibleList')).response.xpath('//td/a[not(contains(text(), "Download")) and (contains(@href, ".pdf") or not(contains(@href, ".pdf"))  ) and not(contains(@href, "../")) and not(contains(@href, ".ics") ) ]').extract()
        for x in tbl:
            link = Selector(text=x).xpath('//a/@href').extract_first()
            link = link if link is not None and link != '' else response.url