# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import scrapy
from scrapy.exceptions import DropItem
# 以下两个类会在每个item被处理时创建对象调用
# process_item 为处理时调用，必须实现


class ImagesPipeline(object):
    def process_item(self, item, spider):
        request = scrapy.Request("http:{}".format(item['url']))
        download = spider.crawler.engine.download(request, spider)
        download.addBoth(self.return_item, item)
        return download

    def return_item(self, response, item):
        if response.status != 200:
            # request fail
            return item
        url = item['url']
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = "{}.png".format(url_hash)
        with open(filename, "wb") as f:
            f.write(response.body)
        item["filename"] = filename
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.urls_seen = set()  # 记录被观测到的url，定义成类属性

    def process_item(self, item, spider):
        if(item['url'] in self.urls_seen):
            raise DropItem("Duplicare item found!%s" % item)
        else:
            self.urls_seen.add(item['url'])
            return item


"""
# 当url是一个非编码形式的需要转换到编码以后按格式化输入拼接到绝对地址
"http://localhost:8050/png?url={}".format(
    urllib.parse.quote(url))
 """
