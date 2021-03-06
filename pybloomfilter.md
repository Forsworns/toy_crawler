##布隆滤波器

该库的原理是做一个长为m位的位图，之后随机取k个哈希函数依次对输入的元素（此处以url为例）进行哈希映射，映射到位图中的某个位置上，那么url会对应一个k位的二进制串，但是由于哈希函数可能产生碰撞的原因会有冲突，可能有假正例（Falsepositives，不存在但是查询时找到了），但是不会有假反例（Falsenegatives，存在但是查询不到）。

布隆滤波器有以下两个操作：

* 添加，添加操作会对输入元素依次执行k个哈希函数，然后去将该位置1
* 查询，查询操作会对输入元素依次执行k个哈希函数，然后查看该位是否为1

错误率（Falsepositives）推导：

首先我们假设哈希函数的输出均匀分布在$(1,m)$

1. 添加元素时，一次哈希后某一位未被置位的可能性为
	$$1-\frac{1}{m}$$
2. 那么经过k次哈希后该位未被置位的可能性为
	$$(1-\frac{1}{m})^{k}$$
3.  相应地输入n个元素后，该位图中某一位仍然没有被置位的可能性为
	$$(1-\frac{1}{m})^{nk}$$
4. 那么接下来进行查询时，假设被查询元素并不在集合中，但是依次执行k个哈希函数后均得到1的概率为
	$$((1-\frac{1}{m})^{nk})^{k}$$
	即$$(1-e^{-\frac{kn}{m}})^{k}$$

