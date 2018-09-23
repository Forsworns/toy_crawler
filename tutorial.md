# dependency

### tools
* python 3.5.2

* google chrome 67.0.3396.99

* chrome driver 2.40.565498

* docker tool box 18.03.0

* RedisDesktopManager 0.9.3

* Redis for Windows 3.0.503 (a cli on [github](https://github.com/ServiceStack/redis-windows)) 

  ```shell
  cd redis4windows
  redis-server.exe redis.windows.conf
  redis-cli.exe
  # or try run.bat
  ```
### pipy packages

* scrapy 1.5.0

* scrapy-splash 0.7.2
  ``` shell
  docker run -p 8050:8050 scrapinghub/splash
  # or docker start scrapinghub/splash
  # use docker ps -a to check all the containers
  # we can use the daocloud to speedup the image pulling
  # or try run_splash.bat
  ### DON'T FORGET TO START THIS IMAGE ###
  ```

* scrapy-redis 0.6.8

* redis 2.10.6

* hiredis 0.2.0

* selenium 3.13.0

* beautifulsoup 4 4.6.0 

* bitarray 0.8.3 (optional)

* pybloom 2.0.0 (optional)



# Creating a prj

use `scrapy startproject xxx` to create a project using template

create a xx.py under xxx/spiders to create my own spider

in this file we write a spider class which subclasses the `scrapy.Spider`.

the subclass defines following attributes:

* name: this must be unique for spiders within a project
* start_requests(): must return requests spider crawl from
* start_urls: used by the default `start_requests()`
* parse(): a callback method to handle the response downloaded for each of the requests made

# Run a spider

use `scrapy crawl xxx` and use argument `-o xx.json` to save the information. We can also modify the `tutorial/pipelines.py` to implement an item pipline for complex storing. Some of the original prj doesn't supply directory check and create, so this section is very important! 

# Extracting data

use `scrapy shell "http://quotes.toscrape.com/page/1/"` on windows

in this way, we can learn how to extract data with Scrapy

for example, we can use `response.css('title')` to get a wrapped selector, and use `extract()` to get the text (use `css('title::text')`instead of `css('title')`)

remember `css()` return a list, so if we want to get a string object, we can use the index to select the element or we can use `extract_first()` to get the first element and avoid the IndexError.

use `re()` for a regular expression matching

# Following links

for example, we want to get the href of the anchor to the next page

```html
<ul class="pager">
    <li class="next">
        <a href="/page/2/">
            Next <span aria-hidden="true">&rarr;</span>
        </a>
    </li>
</ul>
```

we can use  css selector`response.css('li.next a::attr(href)').extract_first()` to get the href.

if we get the relative href, there are two ways:

```python
for href in response.css('li.next a'):
	response.follow(href, callback=self.parse)
```

or

```python
next_page = response.css('li.next a::attr(href)').extract_first()
if next_page is not None:
	next_page = response.urljoin(next_page)
    yield scrapy.Request(next_page, callback=self.parse)
```

# Other details

1. The `DUPEFILTER_CLASS` is to set whether visit the same page.

2. use `Request.meta` to pass a parameter like this:

   ```python
   def parse1(self,response):
   	request = scrapy.Request("http://fff",callback=self.parse2)
   	request.meta['first'] = item
       yield request
   def parse2(self,response):
       item = response.meta['first']
   ```

   it means that the argument was add to request and the we yield request, call the callback, the modified request was pass into the parse2 method

3. use `getattr(self, 'tag', None)` to receive the tag argument via shell terminal.

4. use [terminal/per-spider/project setting](https://docs.scrapy.org/en/latest/topics/settings.html#std:setting-ITEM_PIPELINES) to set the spider, pipeline, etc

5. when download file, use [`image pipeline`](https://docs.scrapy.org/en/latest/topics/media-pipeline.html) or [`item pipline`]('https://docs.scrapy.org/en/latest/intro/overview.html'),and don't forget to do configuration

6. The dynamic website should add **scrapy_splash** to the prj and start the service with the corresponding docker image

7. we can request from this [website](http://www.xicidaili.com/nn/) to get proxy_ip in case that the server check out we are request frequently

8. To avoid duplicate requests or files, we can use **scrapy_redis** plus pybloom to modify the setting of scrapy framework

9. 真香: I tried to implement the div_tree with my hand in css selector, but failed, finally, I only want to say:"How delicious the beautiful soup is!". And waste lots of time to try to contact redis in the docker container from my own host system, however it's exciting to use the redis windows port on the github.

10. Succeed to modify the source code of scrapy to add another instruction for scrapy, which is to start plenty of crawler at the same time

11. use the middleware to avoid IP or  user-agent check, set the `COOKIES_ENABLED` as False in the `settings.py` to disable the loacal cookie check from the website or we can set `DOWNLOAD_DELAY` to set a time delay for the spider.

12. use sklearn to classify the content to choose a crawl template

13. when we set the proxy for scrapy, three are two ways: the first is setting the parameter in the meta of the spider, the second is setting the middleware.

    However, we can't do these when we use scrapy_splash because it use the proxy to serve the excuation of Javascript

14. We can use spider.name to check which the spider is in the pipline, if we have many spiders in one project but want to set different piplines
