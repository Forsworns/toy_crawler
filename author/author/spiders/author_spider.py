import scrapy


class AuthorSpider(scrapy.Spider):
    name = 'author'
    start_urls = [
        'http://quotes.toscrape.com/'
    ]

    def parse(self, response):
        for href in response.css('span a'):
            yield response.follow(href, callback=self.parse_author)
        for href in response.css('.pager a'):
            yield response.follow(href, callback=self.parse)

    def parse_author(self, response):
        def extract_helper(string):
            return response.css(string + '::text').extract_first().strip()
        yield {
            'author-title': extract_helper('.author-title'),
            'author-born-date': extract_helper('.author-born-date'),
            'author-born-location': extract_helper('.author-born-location')
        }
