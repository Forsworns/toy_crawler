import scrapy


class ModelSpider(scrapy.Spider):
    name = 'models'
    start_urls = [
        'http://www.shejiben.com/search.php?searchType=3&q=%E6%B1%BD%E8%BD%A6'
    ]

    def parse(self, response):
        for item in response.css('li.img'):
            yield {
                'href': item.css('a::attr(href)').extract_first(),
                'filename': item.css('a img::attr(alt)').extract_first()
            }
        next_page = response.css('#nextpageid::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
