import scrapy
import scrapy_splash as scrapys
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .div_tree import build_div_tree

__navigation__ = 0
__picture__ = 1
__header_nav__ = 2
__other__ = 3

__autohome__ = 'autohome'
__sohu__ = 'sohu'
__ocean__ = 'ocean'


class StaticsSpider(scrapy.Spider):
    name = 'statics'
    start_urls = [
        'https://car.autohome.com.cn/photo/series/33372/1/4415683.html#pvareaid=2042264',
        # 'http://db.auto.sina.com.cn/photo/',
        # 'http://price.pcauto.com.cn/cars/pic.html',
    ]
    base_url = 'http://car.autohome.com.cn'

    def start_requests(self):
        self.web_parameter = {
            'link_num': 0,
            'img_num': 0,
            'content_length': 0,
            'tag_num': 0,
        }
        for item in self.start_urls:
            yield scrapys.SplashRequest(
                item, callback=self.parse, args={'wait': 0.5})

    def write2file(self, leaf, str_input, _type_):
        with open('classify_{}.data'.format(_type_), 'a') as f:
            self.web_parameter['link_num'] = len(leaf.find_all('a'))
            self.web_parameter['img_num'] = len(leaf.find_all('img'))
            self.web_parameter['content_length'] = len(str(leaf))
            self.web_parameter['tag_num'] = len(
                [tag for tag in leaf.find_all(True)])
            f.write("{},{},{},{},{},{}\n".format(
                self.web_parameter['link_num'], self.web_parameter['img_num'], self.web_parameter['content_length'], self.web_parameter['tag_num'], _type_, str_input))

    def parse(self, response):
        html = response.body
        tree = build_div_tree(html)
        soup = tree.get_root().soup_get()
        write2file = self.write2file
        divs = []

        #@ carhome
        # __navigation__ = 0
        leaf = soup.find('div', class_='cartree')
        if leaf is not None:
            write2file(leaf, 'cartree', __navigation__)
            for a in leaf.find_all('a'):
                url = a['href']
                url = urljoin(self.base_url, url)
                yield scrapys.SplashRequest(url, callback=self.parse, args={'wait': 0.5})
            divs.append(leaf)

        leaf = soup.find('div', class_='uibox-con')
        if leaf is not None:
            write2file(leaf, 'uibox-con', __navigation__)
            for a in leaf.find_all('a'):
                url = a['href']
                url = urljoin(self.base_url, url)
                yield scrapys.SplashRequest(url, callback=self.parse, args={'wait': 0.5})
            divs.append(leaf)
        leaf = soup.find('div', class_='uibox-con-search')
        if leaf is not None:
            write2file(leaf, 'uibox-con-search', __navigation__)
            for a in leaf.find_all('a'):
                url = a['href']
                url = urljoin(self.base_url, url)
                yield scrapys.SplashRequest(url, callback=self.parse, args={'wait': 0.5})
            divs.append(leaf)
        ### __picture__ = 1
        # 转换思路？先全部标为0，之后再直接搜img然后对图片标1，读取的时候注意一下列就行了
        leaf = soup.find('div', class_='main')
        if leaf is not None:
            write2file(leaf, 'main', __picture__)
            divs.append(leaf)
        ### __header_nav__ = 2
        leaf = soup.find('div', class_='header-nav')
        if leaf is not None:
            write2file(leaf, 'header-nav', __header_nav__)
            divs.append(leaf)  # 这个推入的是引用但是不需要做深拷贝因为leaf重新赋值之后id会改变
        ### __other__ = 3
        for leaf in soup.find_all('div', lambda d: d not in divs):
            write2file(leaf, 'other', __other__)

        #@ sohu
        # __navigation__ = 0

        ### __picture__ = 1
        # leaf = soup.find('div',class_='pic')
        # leaf = soup.find('div',class_='side')

        ### __header_nav__ = 2
        # leaf = soup.find()

        ### __other__ = 3
