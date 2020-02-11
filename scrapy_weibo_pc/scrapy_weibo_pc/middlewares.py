# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Request, Spider
from scrapy.http import Response
from redis import StrictRedis
import random
from scrapy.exceptions import IgnoreRequest
from idna.core import IDNAError


class ScrapyWeiboPcSpiderMiddleware(object):
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


class ScrapyWeiboPcDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

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


class RedisMiddleware(object):

    def __init__(self):
        self.redis = StrictRedis(db=13)
        self.redis_key = "weibo_pc_valid"

    def process_request(self, request: Request, spider: Spider):
        accounts = self.redis.hkeys(self.redis_key)
        if not accounts:
            raise IgnoreRequest("No accounts.")
        else:
            ac_name = random.choice(accounts)
            ac_cookie = self.redis.hget(self.redis_key, ac_name).decode()
            spider.logger.debug("Using account: {}".format(ac_name))
            request.headers.setdefault("cookie", ac_cookie)

    def process_response(self, request, response, spider):
        if response.status == 200:
            return response
        if "captcha" in response.url or response.status == 302:
            spider.logger.error("RESPONSE: 访问过于频繁！需手动登录微博解除禁止！")
            raise IgnoreRequest()


if __name__ == '__main__':
    """
    test cookies
    """
    test_url = 'https://s.weibo.com/weibo?q=%E5%8F%A3%E7%BD%A9&timescope=custom%3A2020-01-07-0%3A2020-01-07-24&region=custom%3A0%3A0&Refer=g&scope=ori&suball=1'
    rm = RedisMiddleware()
    r  = rm.redis
    r_key = rm.redis_key
    accounts = r.hkeys(r_key)
    import json
    ac_cookie  = json.loads(r.hget(r_key, random.choice(accounts)))["ac_cookie_str"]
    print(ac_cookie)
    import requests_html
    import urllib3
    urllib3.disable_warnings()
    s = requests_html.HTMLSession()
    res = s.get(test_url, headers={"Cookie": ac_cookie}, verify=False)
    assert res.html.find(".next") != []