import re
import scrapy
#from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor

from sport_crawler.items import SportItem


START_DOMAIN = "XXXXXX.net"
START_URL = "http://www.XXXXXXX.net/XXXXXXX/XXXXXXX.html"

def get_next_url(index): 
    return "http://www.XXXXXXX.net/XXXXXX/XXXXXXXXX/" + str(index) + ".html"

def in_domain(url):
    pattern_str = "^http://(\w*\.)*"+START_DOMAIN+"/XXXXXXX/XXXXXXX/.+"
    pattern = re.compile(pattern_str)
    return pattern.match(url)

class SportSpider(scrapy.Spider):
    name = "sport_crawler"
    allowed_domains = [ START_DOMAIN ]
    start_urls = [ START_URL ]

    start_index = 4579701

    def parse(self, response): 
        print("###########parse start###########")
        #exit(0)
        web_code = response.text.encode('utf8')
        #soup = BeautifulSoup(web_code, 'html.parser')
        
        item = SportItem()
        item['link'] = "aaaaaaa"

        name = response.selector.xpath('//h1/text()').extract()
        if len(name) == 0:
            item['name'] = "Untitle.txt"
        else:
            name = name[0]
            item['name'] = name.encode("utf8", "ignore") + ".txt"
        print(item['name'])
        #print("!!!!!++++++!!!!")

        docs = response.selector.xpath('//div[@id="content"]').extract()
        if len(docs) == 0:
            item['doc'] = "Empty"
        else:
            doc = ""
            for line in docs:
                doc += line.encode("utf8", "ignore")
                doc += "\n"
            item['doc'] = doc # (doc[0]).encode("utf8", "ignore")
            # print("!!!!!-^^^^^^^-!!!!")
        print(item['doc'])
        # print("!!!!!-----!!!!")
        yield item
        yield scrapy.Request(get_next_url(self.start_index))
        self.start_index += 1
        if self.start_index == 4579839:
            exit(0)
        selectors = response.selector.xpath('//a')
        for selector in selectors:
            urls = selector.xpath('@href').extract()
            if len(urls) == 0:
                continue
            next_url = response.urljoin(urls[0])
            print(next_url)
            # print("!!!!!!!!!")
            if in_domain(next_url):
                item = SportItem()
                item['link'] = next_url
                yield item
            yield scrapy.Request(next_url)


