import scrapy
import scrapy_splash as scrapys
from urllib.parse import urljoin


class TeslaSpider(scrapy.Spider):
    name = 'tesla'
    start_urls = [
        'https://www.tesla.cn/'
    ]

    def parse(self, response):
        for item in response.css('a.tsla-header-nav--list_link'):
            url = item.css('::attr(href)').extract_first()
            next_page = response.urljoin(url)
            key = url.split('/')[-1]
            if key in self.callbacks:
                request = scrapys.SplashRequest(
                    next_page, callback=self.callbacks[key], args={'wait': 0.5})
                request.meta['key'] = key
                yield request
            else:
                yield None

    def models_parse(self, response):
        for item in response.css('img[src*="model"]'):  # 用*=表包含
            url = urljoin(self.start_urls[0], item.css(
                'img::attr(src)').extract_first())
            yield {
                'url': url,
                'key': response.meta['key']
            }

    def modelx_parse(self, response):
        for item in response.css('img[src*="model"]'):
            url = urljoin(self.start_urls[0], item.css(
                'img::attr(src)').extract_first())
            yield {
                'url': url,
                'key': response.meta['key']
            }

    def model3_parse(self, response):
        for item in response.css('img[src*="model"]'):
            url = urljoin(self.start_urls[0], item.css(
                'img::attr(src)').extract_first())
            yield {
                'url': url,
                'key': response.meta['key']
            }

    def roadster_parse(self, response):
        for item in response.css('img[src*="model"]'):
            url = urljoin(self.start_urls[0], item.css(
                'img::attr(src)').extract_first())
            yield {
                'url': url,
                'key': response.meta['key']
            }

    def __init__(self):
        self.callbacks = {
            'models': self.models_parse,
            'modelx': self.modelx_parse,
            'model3': self.model3_parse,
            'roadster': self.roadster_parse
        }


""" 这种写到类变量里是错误的写法，这些作为回调函数需要绑定到对象上才能正常使用否则response无法正常传入
    因此要在__init__里面写
    callbacks = {
        'models': models_parse,
        'modelx': modelx_parse,
        'model3': model3_parse
    }
可以打印出来做对比
        print('*****************')
        print(callback)
        print(self.models_parse) """
