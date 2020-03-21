# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import scrapy
from scrapy import signals
from scrapy.exceptions import IgnoreRequest

import re
import copy
import pickle
from enum import Enum
from redis import StrictRedis, ConnectionPool

redis_pool = ConnectionPool(host='nanchuan.site', port=6379, password="Mark@2019", db=13)

START_KEY = "start_key"


class ScrapyWeiboSpiderMiddleware(object):
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
        following_request_cnt = 0
        for i in result:
            if isinstance(i, scrapy.Request):
                self.redis.sadd(i.meta[START_KEY], i.url)
                following_request_cnt += 1
                # spider.logger.debug("Added one url of {}".format(response.meta[START_KEY]))
            yield i
        self.redis.srem(response.meta[START_KEY], response.url)
        spider.logger.debug("Removed one, Added {}".format(following_request_cnt))


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
        for request in start_requests:
            if not self.redis.exists(request.url):
                self.redis.sadd(request.url, request.url)
            urls = self.redis.smembers(request.url)
            for url in urls:
                url = url.decode()
                request.meta[START_KEY] = request.url
                yield scrapy.Request(url, meta=request.meta)

    def spider_opened(self, spider):
        spider.logger.info('SpiderMiddleware Enabled of Spider %s' % spider.name)
        self.redis = StrictRedis(connection_pool=redis_pool)


class ScrapyWeiboDownloaderMiddleware(object):
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
        cookie = 'SINAGLOBAL=7551193299492.775.1581107872253; UOR=login.sina.com.cn,s.weibo.com,login.sina.com.cn; _s_tentry=-; Apache=7664145430573.335.1583828590494; ULV=1583828590658:16:4:4:7664145430573.335.1583828590494:1583793352241; WBtopGlobal_register_version=3d5b6de7399dfbdb; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5wRY9K.D6usaX6FLKd2QEF5JpX5K2hUgL.FozRehzceK-4So22dJLoI7fSqPiu-cyyUcREehz7; SUHB=0vJJjtbvLITdrZ; SSOLoginState=1583833634; un=17766091857; SCF=AjBlkk5Sx7YhfCzd_uNkaqmvDNrUEfT8-57k_5inETuWywqM21yRT967vXm4uy8CT4WwKGXsNQNZ7Bkrr9njt8o.; SUB=_2A25zYxJiDeRhGeRG61AX8SvFzT2IHXVQGQSqrDV8PUNbmtAfLRL2kW9NUjq31yijm1qxtf9a_Owg8pduwTZUFmYr; ALF=1584438449'
        request.headers.setdefault("Cookie", cookie)
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
        spider.logger.info('DownloaderMiddleware Enabled of Spider %s' % spider.name)


if __name__ == '__main__':
    print()