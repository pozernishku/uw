# -*- coding: utf-8 -*- csv
import scrapy, os
from scrapy.http.request import Request
from scrapy.selector import Selector

class OhiopdfSpider(scrapy.Spider): 
    name = 'ohiopdf'
    allowed_domains = ['www.ohiohouse.gov']
    start_urls = ['http://www.ohiohouse.gov/committee/standing-committees']

    def parse(self, response):
        href = response.xpath('//h3/a[@class="black"]/@href').extract()[26] #can be replaced with loop over all 27 committees
        yield Request(response.urljoin(href), callback=self.parsedate)

    def parsedate(self, response):
        i = -1
        dates = response.xpath('//div[@class="collapsibleListHeader"]/h3/text()').extract()
        for date in dates:
            i += 1
            collist = response.xpath('//div[@class="collapsibleList"]').extract()[i]
            yield Request(response.url, callback=self.parsebill, meta={'collapsibleList': collist, 'date': date }, dont_filter=True)

    def parsebill(self, response): # td[3] - org td[4] - stance
        tbl1 = Selector(text=response.meta.get('collapsibleList')).xpath('//table/tr/th[contains(text(), "Organization")]/ancestor::table/tr/td[3]/text()').extract()
        tbl2 = Selector(text=response.meta.get('collapsibleList')).xpath('//table/tr/th[contains(text(), "Organization")]/ancestor::table/tr/td[4]/text()').extract()
        tbl3 = Selector(text=response.meta.get('collapsibleList')).xpath('//table/tr/th[contains(text(), "Organization")]/ancestor::table/tr/td[2]/preceding::table/tr/th[contains(text(), "Bill")]/ancestor::table/tr/td[1]/a/text()').extract()
        
        tbl1 = ['none'] if not tbl1 else tbl1
        tbl2 = ['none'] if not tbl2 else tbl2
        tbl3 = ['none'] if not tbl3 else tbl3
        zlist = list(zip(tbl1, tbl2))
        for org, stance in zlist:
            yield {
                'organization': org,
                'stance': stance,
                'bill': ', '.join(tbl3),
                'date': response.meta.get('date')
            }
