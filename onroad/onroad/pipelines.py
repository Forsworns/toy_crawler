# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import os
import re
from scrapy.exceptions import DropItem


class OnroadPipeline(object):
    def process_item(self, item, spider):
        url = item['url']
        request = scrapy.Request(url)
        request.meta['url'] = url
        download = spider.crawler.engine.download(request, spider)
        download.addBoth(self.return_item, item)
        return download

    def return_item(self, response, item):
        if response.status != 200:
            return item
        name = response.meta['url'].split('/')[-1]
        name = re.search(r'((\w|-|=|&)*).(\w*)$', name)[0]
        """ 
        print('******************')
        print(name) """
        work_dir = os.getcwd()
        download_dir = "{}\\downloads".format(
            work_dir)
        filename = "{}\\{}".format(download_dir, name)
        if not os.path.exists(filename):
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            with open(filename, "wb") as f:
                f.write(response.body)
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.url_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.url_seen:
            raise DropItem("Duplicate item found!%s", item)
        else:
            self.url_seen.add(item['url'])
            return item
