# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import scrapy
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
import random

import pymongo
uri = pymongo.MongoClient()
db  = uri['scrapy_douban']


ips = '''

'''

def convert_ips(ips) -> list:
    return list(map(lambda x: "http://" + x, filter(lambda x: x and not x.startswith("#"), ips.splitlines())))

ip_list = convert_ips(ips)

def fetch_more_ip():
    URL_FETCH_IP = 'http://http.tiqu.alicdns.com/getip3?num=10&type=1&pro=310000&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
    import requests
    res = requests.get(URL_FETCH_IP)
    return res.text

def check_ip_list(N=10):
    if len(ip_list) < N:
        new_ip_list = convert_ips(fetch_more_ip())
        print("Added {} ips.".format(len(new_ip_list)))
        ip_list.extend(new_ip_list)




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

    def __init__(self):
        self.coll = db['film_seeds']

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
        # for r in start_requests:
        #     yield r

        for item in self.coll.find({'status': {"$exists": False}}).limit(0):
            url = item['url']
            yield scrapy.Request(url, meta={"_id": item['_id']}, dont_filter=True)

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
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def __init__(self):
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

        # return None

        check_ip_list()
        request.meta["proxy"] = random.choice(ip_list)

        return None

    def remove_proxy(self, request, spider):
        proxy = request.meta['proxy']
        try:
            ip_list.remove(proxy)
        except:
            pass
        spider.logger.warning("Remaining: [{}/{}], Remove one proxy {}".format(
            len(ip_list), len(ip_list), proxy))

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest

        if not response.status == 200:
            self.remove_proxy(request, spider)
            spider.logger.warning({"Status": response.status})
        elif "检测到有异常请求从您的IP发出，请登录再试!" in response.text:
            self.remove_proxy(request, spider)
            spider.logger.warning({"IP_Warning": response.text})
        else:
            return response
        return request

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        spider.logger.warning({"Exception": exception})
        self.remove_proxy(request, spider)
        return request

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def spider_closed(self, spider):
        import json
        json.dump(ip_list, open("proxies.json", "w"))


