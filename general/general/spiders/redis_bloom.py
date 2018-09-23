import redis
from hashlib import md5
# 仿自 GitHub：LiuXingMing
# 使用布隆滤波器减少空间开销？
# 或者转换思路，创建一个图片哈希表，一个页面哈希表，页面哈希表有时间限制？还是对单个页面设定时间限制？（如果一个周期过久可能会导致死循环），那么键值是否还需要？有了ttl以后键值不必存储时间了


class BloomHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
            return (self.cap - 1) & ret


class BloomFilter(object):
    def __init__(self, host='127.0.0.1', port=6379, blockNum=1, db=0, key='Bloomfilter'):
        self.server = redis.StrictRedis(host=host, port=port, db=db)
        self.bit_size = 1 << 31
        self.key = key
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            # 根据不同的种子初始化不同的哈希函数
            self.hashfunc.append(BloomHash(self.bit_size, seed))

    def isContains(self, str_input):
        if str_input is None:
            return False
        m5 = md5()
        m5.update(str_input.encode('utf-8'))
        str_input = m5.hexdigest()
        ret = True
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            # 如果某个字符串存在，那么应该其对应的每一位都是1
            location = f.hash(str_input)
            ret = ret & self.server.getbit(name, location)
        return ret

    def insert(self, str_input):
        # 将链接地址经md5哈希之后，再次哈希计算出经布隆滤波器计算后的位置结果，然后将该位置1
        m5 = md5()
        m5.update(str_input.encode('utf-8'))
        str_input = m5.hexdigest()
        # 当只有一块时都存入到了bit串0中
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            location = f.hash(str_input)
            self.server.setbit(name, location, 1)


if __name__ == '__main__':
    bf = BloomFilter(key='test')
    if bf.isContains("www.bilibili.com"):
        print("right")
    else:
        print("wrong")
        bf.insert("www.bilibili.com")
