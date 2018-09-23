import scrapy
from scrapy.linkextractors import LinkExtractor
import scrapy_splash as scrapys
from div_tree import build_div_tree
from sklearn import svm, tree, neighbors, neural_network, naive_bayes
from sklearn.model_selection import train_test_split
import numpy as np
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import redis
import time
# type
__navigation__ = 0
__picture__ = 1
__header_nav__ = 2
__other__ = 3


class GeneralSpider(scrapy.Spider):
    name = 'general'
    # allowed_domains = ['car.autohome.com.cn']
    base_url = 'https://car.autohome.com.cn'
    start_urls = [
        'https://car.autohome.com.cn/pic/',
        # 'http://db.auto.sina.com.cn/photo/s1933.html'
        # 'https://car.autohome.com.cn/pic/#pvareaid=2042194',
        # 'https://car.autohome.com.cn/photo/series/33372/1/4415683.html#pvareaid=2042264'
        # 'http://db.auto.sina.com.cn/photo/c92384-1-1-0-0-1.html#130009605'
        # 'http://price.pcauto.com.cn/cars/sg9550/'
        # 'http://price.pcauto.com.cn/cars/image/5166792-1-sg9550-o1-1.html'
    ]
    # 问题:
    # 切换城市部分和左侧边栏均为叶子且长度均很大
    # img部分占页面内容比例很小，长度短
    # 当前特征区分度不高，难以区分边栏和其他的部分，见数据0和数据3，后来3直接弃用了

    def start_requests(self):
        self.link_server = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)
        self.img_server = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)
        # 读取数据建立模型
        data = np.loadtxt('classify_0.data', dtype=float,
                          delimiter=',', usecols=(0, 1, 2, 3, 4))
        x, y = np.split(data, (4,), axis=1)  # 参数设置
        for i in range(1, 4):  # 是否跳过other项它不好分辨，other在classify_3里面
            data = np.loadtxt('classify_{}.data'.format(
                i), dtype=float, delimiter=',', usecols=(0, 1, 2, 3, 4))
            if len(data) > 150:
                data = data[0:150, :]
            x_temp, y_temp = np.split(data, (4,), axis=1)  # 参数设置
            x = np.vstack((x, x_temp))
            y = np.vstack((y, y_temp))
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, random_state=1, train_size=0.8)
        # svm
        # self.model = svm.SVC(kernel='rbf')
        # decision tree
        # self.model = tree.DecisionTreeClassifier()
        # knn
        # self.model = neighbors.KNeighborsClassifier()
        # bayes
        self.model = naive_bayes.MultinomialNB()
        # MLP
        # self.model = neural_network.MLPClassifier(
        #   solver='lbfgs', activation='tanh')
        # to fit the model
        self.model.fit(x_train, y_train.ravel())

        for item in self.start_urls:
            yield scrapys.SplashRequest(
                item, callback=self.parse, args={'wait': 0.5})

    def parse(self, response):
        # 建树
        tree = build_div_tree(response.body, False)

        # 建完树后对content大的前几个叶子统计分析其类型参数，用来对其归类
        web_parameter = {
            'link_num': 0,
            'img_num': 0,
            'content_length': 0,
            'tag_num': 0,
            'div_name': ''
        }
        leaves = tree.get_largest_leaves(80)
        for leaf in leaves:
            # 建立分类用数据
            web_parameter['link_num'] = len(leaf.soup_get(
            ).find_all('a'))
            web_parameter['img_num'] = len(leaf.soup_get(
            ).find_all('img'))
            web_parameter['content_length'] = leaf.length_get()
            web_parameter['tag_num'] = len(
                [tag for tag in leaf.soup_get().find_all(True)])
            try:
                web_parameter['div_name'] = leaf.soup_get()['class']
            except Exception as e:
                web_parameter['div_name'] = '[]'
                print('该标签不含class')
            else:
                pass
            x_hat = np.array([[web_parameter['link_num'], web_parameter['img_num'],
                               web_parameter['content_length'], web_parameter['tag_num']]])
            y_hat = self.model.predict(x_hat)[0]

            # 这里写入新分类结果数据，考虑是否要使用这部分重新建模
            with open('classify_res.data', 'a') as f:
                f.write("{},{},{},{},{},{}\n".format(web_parameter['link_num'], web_parameter['img_num'],
                                                     web_parameter['content_length'], web_parameter['tag_num'], y_hat, web_parameter['div_name']))

            # 这里根据分类寻找一个模板，进行处理，将请求过的链接写入数据库或借用一个轻量的布隆滤波器
            if y_hat == __navigation__:
                for a in leaf.soup_get().find_all('a', attrs={'href': True}):
                    url = a['href']
                    url = urljoin(self.base_url, url)
                    if self.link_server.exists(url):
                        continue
                    else:
                        self.link_server.setex(
                            url, 24 * 60 * 60, time.asctime(time.localtime(time.time())))
                        request = scrapys.SplashRequest(
                            url, callback=self.parse, args={'wait': 0.5})
                        yield request
            elif y_hat == __picture__:
                leaf = leaf.soup_get()
                for picture in leaf.find_all('img'):
                    url = picture['src']
                    url = urljoin(self.base_url, url)
                    if self.img_server.exists(url):
                        continue
                    else:
                        self.img_server.set(url, time.asctime(
                            time.localtime(time.time())))
                        yield {
                            'url': url
                        }
            else:
                pass
