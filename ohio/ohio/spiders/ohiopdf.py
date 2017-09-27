# -*- coding: utf-8 -*- csv
import scrapy, os
from scrapy.http.request import Request
from scrapy.selector import Selector

class OhiopdfSpider(scrapy.Spider): 
    name = 'ohiopdf'
    allowed_domains = ['www.ohiohouse.gov']
    start_urls = ['http://www.ohiohouse.gov/committee/standing-committees']

    def parse(self, response):
        #Code below is automatic scraping (for all committees). Takes once long time and not error free.
        '''
        for x in response.xpath('//h3/a[@class="black"]').extract():
            folder = Selector(text=x).xpath('//a/text()').extract_first()
            os.makedirs('./' + folder )
            os.chdir('./' + folder )
            yield Request(response.urljoin(Selector(text=x).xpath('//a/@href').extract_first()), callback=self.parsedate, meta={'fol': folder })
            os.chdir('../')
        '''
        #Code below is manual scraping (for selected committee). Takes time for every separate committee and more error free. Change indeces extract()[5] in following two lines:
        folder = response.xpath('//h3/a[@class="black"]/text()').extract()[26]
        href = response.xpath('//h3/a[@class="black"]/@href').extract()[26]
        os.makedirs('./' + folder)
        os.chdir('./' + folder)
        yield Request(response.urljoin(href), callback=self.parsedate, meta={'fol': folder})
        os.chdir('../')

    def parsedate(self, response):
        i = -1
        for x in response.xpath('//div[@class="collapsibleListHeader"]/h3/text()').extract():
            folder = './' + response.meta.get('fol') + '/' + x
            os.makedirs(folder)
            os.chdir(folder)
            i += 1
            yield Request(response.url, callback=self.parsebill, meta={'table': response.xpath('//div[@class="collapsibleList"]').extract()[i], 'fol': folder }, dont_filter=True )
            os.chdir('../')
            os.chdir('../')

    def parsebill(self, response):
        tbl = Selector(text=response.meta.get('table')).response.xpath('//td/a[not(contains(text(), "Download")) and (contains(@href, ".pdf") or not(contains(@href, ".pdf"))  ) and not(contains(@href, "../")) and not(contains(@href, ".ics") ) ]').extract()
        for x in tbl:
            folder = './' + response.meta.get('fol') + '/' + Selector(text=x).xpath('//a/text()').extract_first()
            os.makedirs(folder)
            os.chdir(folder)
            
            link = Selector(text=x).xpath('//a/@href').extract_first()
            link = link if link is not None and link != '' else response.url
            yield Request(link, callback=self.parsesave, meta={'descr': response.meta.get('table'), 'fol': folder }, dont_filter=True)

            os.chdir('../')
            os.chdir('../')
            os.chdir('../')

    def parsesave(self, response):
        filename = response.url.split('/')[-1] if response.url.split('/')[-1].split('.')[-1] == 'pdf' else 'There is no PDF file on the site'
        os.chdir('./' + response.meta.get('fol') )

        with open('Organization, Stance, etc.htm', 'wb') as f:
            f.write(response.meta.get('descr').encode())

        with open(filename, 'wb') as f:
            f.write(response.body)
            os.chdir('../')
            os.chdir('../')
            os.chdir('../')
