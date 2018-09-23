import scrapy
import scrapy_splash as scrapys
from urllib.parse import urljoin
from .redis_bloom import BloomFilter


class CarhomeSpider(scrapy.Spider):
    name = 'carhome'
    '''
    allowed_domains = ["httpbin.ort/get"]
    start_urls = ['http://httpbin.org/get']

    def parse(self, response):
        print(response.text)
    '''
    base_url = 'https://car.autohome.com.cn'
    start_urls = [
        'https://car.autohome.com.cn/pic/'
    ]

    def start_requests(self):
        self.bf = BloomFilter(key='carhome')
        for item in self.start_urls:
            yield scrapys.SplashRequest(
                item, callback=self.parse, args={'wait': 0.5})

    def parse(self, response):
        # 品牌选项
        for item in response.css('.cartree ul li a'):
            # for item in response.css('#b134'):  # 调试用，爬取开上面
            url = item.css('::attr(href)').extract_first()
            url = urljoin(self.base_url, url)
            if self.bf.isContains(url):
                continue
            else:
                self.bf.insert(url)
                brand = item.css('::text').extract_first()
                request = scrapys.SplashRequest(
                    url, callback=self.brand_parse, args={'wait': 0.5})
                request.meta['brand'] = brand.strip()
                yield request

    def brand_parse(self, response):
        # 车系选项
        for item in response.css('.cartree ul li.current dl dd a'):
            # for item in response.css('#series_2368'):  # 调试用，爬取开上面
            url = item.css('::attr(href)').extract_first()
            url = urljoin(self.base_url, url)
            series = item.css('::text').extract_first()
            request = scrapys.SplashRequest(
                url, callback=self.series_parse, args={'wait': 0.5})
            request.meta['brand'] = response.meta['brand']
            request.meta['series'] = series.strip()
            yield request

    def series_parse(self, response):
        # 选择车型选项
        for item in response.css('div.search-pic dl'):
            urls = item.css('dd a::attr(href)').extract()
            kinds = item.css('dd a::text').extract()
            years = item.css('dt::text').extract()
            for url, year, kind in zip(urls, years, kinds):
                url = urljoin(self.base_url, url)
                kind = year + kind
                request = scrapys.SplashRequest(
                    url, callback=self.kind_parse, args={'wait': 0.5})
                request.meta['brand'] = response.meta['brand']
                request.meta['series'] = response.meta['series']
                request.meta['kind'] = kind.strip()
                yield request

    def kind_parse(self, response):
        # 选择外观选项
        for item in response.css('div.search-pic li'):
            if item.css('::text').extract_first() == '车身外观':
                url = item.css('a::attr(href)').extract_first()
                url = urljoin(self.base_url, url)
                request = scrapys.SplashRequest(
                    url, callback=self.img_parse, args={'wait': 0.5})
                request.meta['brand'] = response.meta['brand']
                request.meta['series'] = response.meta['series']
                request.meta['kind'] = response.meta['kind']
                yield request

    """ def more_parse(self, response):
        # 相当于点击更多，都是上一步筛选完实际就会全部显示了
        if response.css('a.more') != []:
            for item in response.css('a.more'):
                url = item.css('a::attr(href)').extract_first()
                url = urljoin(self.base_url, url)
                request = scrapys.SplashRequest(
                    url, callback=self.img_parse, args={'wait': 0.5})
                request.meta['brand'] = response.meta['brand']
                request.meta['series'] = response.meta['series']
                request.meta['kind'] = response.meta['kind']
                yield request
 """

    def img_parse(self, response):
        # 点击各个图片
        for item in response.css('.uibox-con ul li'):
            url = item.css('a::attr(href)').extract_first()
            url = urljoin(self.base_url, url)
            request = scrapys.SplashRequest(
                url, callback=self.return_item, args={'wait': 0.5})
            request.meta['brand'] = response.meta['brand']
            request.meta['series'] = response.meta['series']
            request.meta['kind'] = response.meta['kind']
            yield request

    def return_item(self, response):
        # 对点开的图片进行下载
        for item in response.css('div#main div.pic img'):
            url = item.css('::attr(src)').extract_first()
            url = urljoin(self.base_url, url)
            yield {
                'brand': response.meta['brand'],
                'series': response.meta['series'],
                'kind': response.meta['kind'],
                'url': url
            }
