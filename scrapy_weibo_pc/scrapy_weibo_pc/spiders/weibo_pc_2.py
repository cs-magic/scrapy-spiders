# -*- coding: utf-8 -*-
import scrapy
from collections import namedtuple

try:
    from scrapy_weibo_pc.scrapy_weibo_pc.settings import *
except:
    from scrapy_weibo_pc.settings import *


class WeiboPc2Spider(scrapy.Spider):
    name = 'weibo_pc_2'
    allowed_domains = ['s.weibo.com']
    start_urls = ['http://s.weibo.com/']

    # TODO: Update using new design


    def parse(self, response):
        pass
