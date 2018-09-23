import scrapy
import scrapy_splash as scrapys
from urllib.parse import urljoin


class OnroadSpider(scrapy.Spider):
    name = 'onroad'
    base_url = 'https://image.baidu.com/'
    start_urls = [
        'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&fm=detail&lm=-1&st=-1&sf=2&fmq=1530860183045_R_D&fm=detail&pv=&ic=0&nc=1&z=&se=&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E5%8D%A1%E5%8F%A3%E6%8A%93%E6%8B%8D%E8%BD%A6%E8%BE%86%E8%BD%A6%E7%89%8C%E5%9B%BE%E7%89%87',
        'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1530863081392_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E5%8D%A1%E5%8F%A3%E6%8A%93%E6%8B%8D',
        'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1530863177933_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E5%8D%A1%E5%8F%A3%E6%B1%BD%E8%BD%A6'
    ]

    def start_requests(self):
        for item in self.start_urls:
            yield scrapys.SplashRequest(
                item, callback=self.parse, args={'wait': 0.5})

    def parse(self, response):
        for item in response.css('div.imgbox'):
            href = item.css('a::attr(href)').extract_first()
            href = urljoin(self.base_url, href)
            yield scrapys.SplashRequest(
                href, callback=self.img_parse, args={'wait': 0.5})

    def img_parse(self, response):
        for item in response.css('img.currentImg'):
            src = item.css('::attr(src)').extract_first()
            yield {
                'url': src
            }
