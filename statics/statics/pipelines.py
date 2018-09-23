# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class StaticsPipeline(object):
    def process_item(self, item, spider):
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
