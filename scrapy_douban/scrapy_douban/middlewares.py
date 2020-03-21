# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
import random


ip_dict = {"code":0,"data":[{"ip":"58.218.201.122","port":4113,"outip":"112.64.91.133"},{"ip":"58.218.201.122","port":3782,"outip":"140.206.193.198"},{"ip":"58.218.200.253","port":7642,"outip":"103.40.223.207"},{"ip":"58.218.201.122","port":8897,"outip":"223.167.142.222"},{"ip":"58.218.201.122","port":7635,"outip":"112.64.8.220"},{"ip":"58.218.200.220","port":2358,"outip":"180.165.65.66"},{"ip":"58.218.201.114","port":3050,"outip":"183.192.75.130"},{"ip":"58.218.200.220","port":2803,"outip":"211.161.241.20"},{"ip":"58.218.201.114","port":2558,"outip":"183.192.75.130"},{"ip":"58.218.201.114","port":4572,"outip":"117.186.42.250"}],"msg":"0","success":True}


class ScrapyDoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyDoubanDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def __init__(self):
        self.proxys = list(map(lambda x: "http://{}:{}".format(x['ip'], x['port']),
                               ip_dict['data']))
        self.proxy_invalid_set = set()


    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if not self.proxys:
            raise IgnoreRequest("No proxy valid!")
        request.meta["proxy"] = random.choice(list(self.proxys))


        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if response.status == 200 and not "检测到有异常请求从您的IP发出，请登录再试!" in response.text:
            return response
        else:
            proxy = request.meta['proxy']
            try:
                self.proxys.remove(proxy)
            except:
                pass
            self.proxy_invalid_set.add(proxy)
            spider.logger.warning("Remaining: [{}/{}], Remove one proxy {}".format(
                len(self.proxys), len(ip_dict), proxy))
            return request

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        import json
        json.dump(list(self.proxy_invalid_set)), open("proxys.json", 'w')

