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


class PageStatus(Enum):

    UNKNOWN  = "待定"

    NoPaging = "没有分页"

    NormalPagingWithoutPage = "正常分页，开启分页"
    NormalPagingWithPage    = "正常分页，开始解析"

    BeyondPagingOfDay  = "分页过多，开启小时"
    BeyondPagingOfHour = "分页过多，开启按省"
    BeyondPagingOfProv = "分页过多，开启按市"
    BeyondPagingOfAll  = "分页过多，无法再分！"


class Page:

    MAX_PAGES = 50

    def __init__(self, url, page_status: PageStatus, ):
        self.url = url
        self.page_status = page_status
        self.param_dict = self._get_param_dict()

    def _get_param_dict(self):
        param_dict = dict(i.split("=", 1) for i in self.url.split('?')[-1].split("&"))
        param_dict.setdefault("page", 1)

        assert 'timescope' in param_dict
        timescope_m = re.match(r'custom:(\d+)-(\d+)-(\d+)-(\d+):(\d+)-(\d+)-(\d+)-(\d+)', param_dict["timescope"])
        param_dict["time_list"] = sy, sm, sd, sh, ey, em, ed, eh = list(timescope_m.groups())

        param_dict.setdefault('region', 'custom:0:0')
        regionscope_m = re.match(r'custom:(\d+):(\d+)', param_dict["region"])
        param_dict["region_list"] = prov, city = list(regionscope_m.groups())

        return param_dict

    @staticmethod
    def get_url_from_param_dict(param_dict):
        base_url = 'https://s.weibo.com/weibo?'
        assert "time_list" in param_dict
        assert "region_list" in param_dict
        base_url += 'q={}&'.format(param_dict["q"])
        base_url += 'timescope=custom:{}-{}-{}-{}:{}-{}-{}-{}&'.format(*param_dict["time_list"])
        base_url += 'region=custom:{}:{}'.format(*param_dict["region"])
        return base_url

    def get_sub_pages(self, pages):
        if pages < self.MAX_PAGES:
            yield None
        elif self.page_status == PageStatus.BeyondPagingOfDay:
            assert self.param_dict["time_list"][3] == 0 and self.param_dict["time_list"][7] == 24
            param_dict = copy.deepcopy(self.param_dict)
            for hour in range(24):
                param_dict["time_list"][3] = hour
                param_dict["time_list"][7] = hour + 1
                yield Page(self.get_url_from_param_dict(param_dict), PageStatus.BeyondPagingOfHour)
        elif self.page_status == PageStatus.BeyondPagingOfHour:
            # TODO: prov, city
            pass





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
        self.redis.srem(response.meta["key"], response.url)
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
        for request in start_requests:
            if not self.redis.exists(request.url):
                self.redis.sadd(request.url, request.url)
            urls = self.redis.smembers(request.url)
            for url in urls:
                url = url.decode()
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
        cookie = '''SINAGLOBAL=7551193299492.775.1581107872253; UOR=login.sina.com.cn,s.weibo.com,login.sina.com.cn; SCF=Asr3ivn_z8NujEk_O5ZHkJRNx8BlbfgKic22Hb4VrkAc3dYhI7i3Fzvk53cVYL-q3AiFz3tpndlgPBqkJBe6jU0.; SUHB=0FQq93CXRi_Pt8; SUB=_2AkMpO6jDf8NxqwJRmfoSyGjqboRxyA3EieKfZ1kYJRMxHRl-yT92qm4ZtRB6AruGK5TmuVGwVrp0hvsEF0NWnSQMs0aD; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhqVIm7j8y9lvXzlDaeEi8E; _s_tentry=-; Apache=7664145430573.335.1583828590494; ULV=1583828590658:16:4:4:7664145430573.335.1583828590494:1583793352241'''
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