import scrapy


class ImageSpider(scrapy.Spider):
    name = 'images'
    start_urls = [
        "https://www.bilibili.com/"
    ]

    def parse(self, response):
        for item in response.css("img::attr(src)").extract():
            yield {'url': item}
