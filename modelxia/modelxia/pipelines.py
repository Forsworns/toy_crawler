# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import json
import scrapy
import re
import os
from scrapy.exceptions import DropItem


class ModelxiaPipeline(object):
    def process_item(self, item, spider):
        if item['data'] != '':
            request = scrapy.Request(item['data'])
            download = spider.crawler.engine.download(request, spider)
            download.addBoth(self.return_item, item)
            return download
        else:
            return item

    def return_item(self, response, item):
        if response.status != 200:
            # print('*******************************************************')
            return item
        # url = item['href']
        # url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = "{}\\downloads\\{}.7z".format(
            os.getcwd(), item['order'])  # 这里导致需要在prj的根目录下启动scrapy
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                f.write(response.body)
        return item

    """ def close_spider(self, spider):
        if browser is not None:
            browser.quit() """


class DuplicatesPipeline(object):
    def __init__(self):
        self.url_seen = set()

    def process_item(self, item, spider):
        if item['order'] in self.url_seen:
            raise DropItem("Duplicate item found!%s" % item)
        else:
            self.url_seen.add(item['order'])
            return item
