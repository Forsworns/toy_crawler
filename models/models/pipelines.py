# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import scrapy
import re
import os
from scrapy.exceptions import DropItem
# selenium 配合 chrome 的无头浏览器
from selenium import webdriver

# 以下两个类会在每个item被处理时创建对象调用
# process_item 为处理时调用，必须实现

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# 这里若使用无头浏览器必须挂代理才可以运行，但是仍然无法正常下载
# 基于chromedriver2.40和chrome 67.0.3396.99，selenium为最新版
download_path = os.getcwd() + "\\downloads"
prefs = {
    'profile.default_content_settings.popups': 0,
    'download.default_directory': download_path
}
chrome_options.add_experimental_option('prefs', prefs)
# print(chrome_options)
browser = webdriver.Chrome(chrome_options=chrome_options)


class ModelsPipeline(object):
    def process_item(self, item, spider):
        order = re.findall(r"\d+", item['href'])[0]
        url = "http://mx.shejiben.com/m{}.html".format(order)
        browser.get(url)
        if(browser.current_url == url):
            browser.execute_script('$("#down_btn").click()')
        """ # 使用浏览器去点会有失焦的情况换用执行jQuery
        button = browser.find_element_by_id('down_btn')
        button.click()
 """
        """ # 最初找到的post接口可惜不能直接用有的页面可能可以直接post可以参考这个来实现
        url = "http://mx.shejiben.com/m.php?ajax_addshare=1"
        formdata = {
            'title': "大众汽车max汽车3d模型下载",
            'url': "http://mx.shejiben.com/m{}.html".format(order),
            'comment': "模型",
            'image': '',
            'sta_type': "model",
            'rar': order,
        }
        request = scrapy.FormRequest(
            url=url,
            formdata=formdata
        )
        download = spider.crawler.engine.download(request, spider)
        download.addBoth(self.return_item, item)
        return download 

    def return_item(self, response, item):
        if response.status != 200:
            # request fail
            return item
        url = item['href']
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = "{}{}.html".format(item['filename'], url_hash)
        with open(filename, "wb") as f:
            f.write(response.body)
        item["filename"] = filename
        return item """

    def close_spider(self, spider):
        if browser is not None:
            browser.close()


class DuplicatesPipeline(object):
    def __init__(self):
        self.urls_seen = set()  # 记录被观测到的href，定义成类属性，相当于一个静态变量

    def process_item(self, item, spider):
        if(item['href'] in self.urls_seen):
            raise DropItem("Duplicare item found!%s" % item)
        else:
            self.urls_seen.add(item['href'])
            return item
