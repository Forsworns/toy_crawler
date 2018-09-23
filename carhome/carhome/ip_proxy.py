import time
import json
import urllib.request
from bs4 import BeautifulSoup


def ip_get():
    url = 'http://www.xicidaili.com/'
    req = urllib.request.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
    website = urllib.request.urlopen(req)
    print(website.getcode())
    if website.getcode() == 200:
        html = website.read()
        soup = BeautifulSoup(html, 'lxml')
        ip = []
        countries = soup.select('img[alt="Cn"]')
        for country in countries:
            ip_td = country.parent.next_sibling.next_sibling  # 第一个兄弟是换行符
            port_td = country.parent.next_sibling.next_sibling.next_sibling.next_sibling
            ip.append({'ipaddr': ip_td.string + ':' + port_td.string})
        with open('carhome\\ip.json', 'w') as f:
            json.dump(ip, f)


if __name__ == '__main__':
    ip_get()
