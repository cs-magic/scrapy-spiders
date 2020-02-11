# -*- coding: utf-8 -*-

# Scrapy settings for scrapy_weibo_pc project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_weibo_pc'

SPIDER_MODULES = ['scrapy_weibo_pc.spiders']
NEWSPIDER_MODULE = 'scrapy_weibo_pc.spiders'


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False
REDIRECT_ENABLED = False

# CONCURRENT_REQUESTS = 1

MONGO_URI = "localhost:27017"
MONGO_DB  = '口罩'

CONTINUE_FROM_DB = True
from datetime import datetime
class Params:
   KEYWORD = "口罩"
   START_TIME = datetime(2020, 1, 2, 0)
   END_TIME = datetime(2020, 2, 1, 0)
   PROVINCE_CODE = 0
   CITY_CODE = 0  # city值为0或者1000都是一样的
   SORT_BY = "scope"
   INCLUDE = "suball"

import os
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


import logging
LOG_LEVEL = logging.DEBUG
LOG_FILE  = "logs/{}.logs".format(datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))

logger = logging.getLogger()
hd = logging.StreamHandler()
hd.setLevel(logging.INFO)

logger.addHandler(hd)


DOWNLOADER_MIDDLEWARES = {
   'scrapy_weibo_pc.middlewares.RedisMiddleware': 543,
}

ITEM_PIPELINES = {
   'scrapy_weibo_pc.pipelines.ScrapyWeiboPcMongoPipeline': 300,
}




# Configure maximum concurrent requests performed by Scrapy (default: 16)

# 'REDIRECT_ENABLED': False,
# 'HTTPERROR_ALLOWED_CODES': [302]

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scrapy_weibo_pc.middlewares.ScrapyWeiboPcSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
