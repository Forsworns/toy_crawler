# 这个网站有下载限制
import json
import scrapy
import re

cookies = {
    'JSESSIONID': '4DC478DC213732074FDBE0A24178BA23'
}  # 这个是验证登录状态用的cookie，仅在第一次请求下载链接时需要，获取下载链接第二次请求不需要了
# 有时会过期orz这个时候读到的是登录页面……需要登录以后回来重新指派cookie，可以直接进application下面cookies里面取


class ModelxiaSpider(scrapy.Spider):
    name = 'modelxia'

    def start_requests(self):
        for i in range(2, 3):
            url = 'http://s.3dxia.com/list.html?keyword=%E6%B1%BD%E8%BD%A6&st=0&page={}'.format(
                i)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        for item in response.css('.delayLoading'):
            href = item.css('::attr(src)').extract_first()
            order = re.findall(r"\d+", href)[2]
            url = "http://www.3dxia.com/commodityDetail/getDownLoadCommodityUrl.do?skuId={}".format(
                order)
            request = scrapy.Request(
                url, cookies=cookies, callback=self.parse_again)
            request.meta['filename'] = order
            yield request

    def parse_again(self, response):
        """ 
        self.log('---------------------------')
        self.log(response.body.decode())
        self.log('---------------------------') """
        response_data = json.loads(response.body.decode())
        response_data['order'] = response.meta['filename']
        yield response_data  # 开启后下载压缩文件
