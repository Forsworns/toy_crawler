from bs4 import BeautifulSoup
from bs4.element import Tag
from queue import PriorityQueue
import urllib.request


class Node(object):
    def __init__(self, soup, level, dfs_num, father=None):
        [script.decompose() for script in soup.find_all('script')]
        self.dfs_num = dfs_num
        self.level = level
        self.content = soup  # beautifulsoup 对象
        self.length = -1 * len(str(soup))  # 用于处理优先级
        self.father = father
        self.children = []

    def level_get(self):
        return self.level

    def length_get(self):
        return -1 * self.length

    def dfs_num_get(self):
        return self.dfs_num

    def children_add(self, child):
        if child is not None:
            self.children.append(child)
        return self.children

    def soup_get(self):
        # 返回soup形式的网页内容
        return self.content

    def __cmp__(self, other):
        return cmp(self.length, other.length)

    def __lt__(self, other):
        return self.length < other.length


class Tree(object):
  # 节点都是选择器，内容是soup
    def __init__(self, soup):
        self.content = soup
        self.root = Node(soup, 0, 0)
        self.serve_queue = list()
        self.leaves = PriorityQueue()

    def get_root(self):
        return self.root

    def get_largest_leaves(self, amount):
        if amount < self.leaves.qsize():
            leaves = [self.leaves.get() for _ in range(0, amount)]
            return leaves
        else:
            print("叶子请求数目过多")
            leaves = [self.leaves.get() for _ in range(0, self.leaves.qsize())]
            return leaves


def isLeaf(soup):
    for child in soup.children:
        if type(child) == Tag:
            if child.name != u'div':
                return True
    return False


def build_div_tree(html, debug=False):
    soup = BeautifulSoup(html.decode(), 'html.parser')
    level = 0
    dfs_num = 0
    soup_item = soup.body
    # print(*[child.name for child in soup.html.contents if type(child) == Tag])
    website_tree = Tree(soup_item)
    parent_node = website_tree.get_root()
    # 之后的不是叶子就不会加入到serve_queue中，默认根结点不是叶子

    while soup_item is not None:
        for child in soup_item.find_all('div'):
            if child in soup_item.children:
                dfs_num = dfs_num + 1
                level = parent_node.level_get() + 1
                tree_node = Node(child, level, dfs_num, parent_node)
                if isLeaf(child):
                    # 如果是叶子那么根据内容长度放入叶子的优先队列
                    website_tree.leaves.put(tree_node)
                else:
                    website_tree.serve_queue.append((child, tree_node))
                parent_node.children_add(tree_node)

        if website_tree.serve_queue != []:
            soup_item, parent_node = website_tree.serve_queue.pop(0)
        else:
            soup_item = None

    if debug:
        print_test(website_tree)
    return website_tree


def print_test(tree):
    print('*************test*****************')
    item = tree.get_root()
    q = []
    while True:
        children = item.children_add(None)
        [q.append(child) for child in children]
        print('-----------------------------')
        print(item.level)
        print(item.content.attrs)
        print('father')
        if item.father is not None:
            print(item.father.content.attrs)
        print('children')
        print(*[child.content.name for child in children])
        [print(child.content.attrs) for child in children]
        print('length')
        print(item.length_get())
        print('---------------------------')
        if q != []:
            item = q.pop(0)
        else:
            break
    print('******************************')


if __name__ == '__main__':
    url = 'http://www.xicidaili.com/'
    req = urllib.request.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
    website = urllib.request.urlopen(req)
    html = website.read()
    with open("web.html", "w", encoding='utf-8') as f:
        f.write(html.decode())
    build_div_tree(html, True)
