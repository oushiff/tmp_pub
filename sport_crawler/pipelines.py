# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exceptions import DropItem

from sport_crawler.store4crawler import URL_Store
from sport_crawler.store4crawler import get_standard_url

class SportCrawlerPipeline(object):
    def __init__(self):
        self.store = URL_Store()


    def close_spider(self, spider):
        self.store.visual()
        self.store.output()


    def process_item(self, item, spider):
        link = item['link']
        name = item['name']
        doc = item['doc']

        with open(name, "w") as fp:
            fp.write(doc)

        std_url = get_standard_url(link)
        if std_url == False:
            raise DropItem("URL Invalid item found: %s" % item)

        if self.store.is_exist(std_url):
            self.store.add_url(std_url)
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.store.add_url(std_url)
            return item
