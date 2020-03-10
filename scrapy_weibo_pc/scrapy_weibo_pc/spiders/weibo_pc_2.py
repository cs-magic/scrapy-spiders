# -*- coding: utf-8 -*-
import scrapy
from collections import namedtuple

try:
    from scrapy_weibo_pc.scrapy_weibo_pc.settings import *
except:
    from scrapy_weibo_pc.settings import *

from redis import StrictRedis

class WeiboPc2Spider(scrapy.Spider):
    name = 'weibo_pc_2'
    allowed_domains = ['s.weibo.com']
    start_urls = ['http://s.weibo.com/']

    # TODO: Update using new design
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = StrictRedis(host="212.64.67.85", password="Mark@2019", db=13)



    def parse(self, response):
        pass
