import scrapy


class QuotesSpider(scrapy.Spider):  # 必须继承自scrapy.Spider类
    name = "quotes"

    """ def start_requests(self):  # 用于开始请求的函数
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    """
    # 这里也可以直接简写成
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]

    def parse(self, response):  # 用于解析的函数，作为回调函数传入
        page = response.url.split("/")[-2]  # 通过split将URL字符串分割成list取倒数第二个
        filename = 'quote-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Save file %s' % filename)  # yield前打印
        # 将具体解析的实现进一步分割出去
        temp = {}
        for item in self.my_transfer(response):
            temp.update(dict(item))
        yield temp
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)  # 这里将相对地址拼接到URL中
            yield scrapy.Request(next_page, callback=self.parse)
        # 这段可以更加简洁，不必合并URL不必解析文本
        """ for href in response.css('li.next a'):
            response.follow(href, callback=self.parse)
        """

    def my_transfer(self, response):
        for item in response.css("div.quote"):
            title = item.css("span.text::text").extract_first().strip()
            person = item.css("small::text").extract_first().strip()
            tags = item.css("a.tag::text").extract_first().strip()
            yield {
                'title': title,
                'person': person,
                'tags': tags
            }
