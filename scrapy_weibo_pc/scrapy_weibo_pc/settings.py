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

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
   'Cookie': 'un=17766091857;_s_tentry=login.sina.com.cn;ALF=1613379449;Apache=3394628681636.194.1581843452201;SCF=Asr3ivn_z8NujEk_O5ZHkJRNx8BlbfgKic22Hb4VrkAcIsr4XMcDChSFLDbG8a8ZsnUESBTpVpaQ-zNbv9M9KiE.;SINAGLOBAL=7551193299492.775.1581107872253;SSOLoginState=1581843450;SUB=_2A25zTXOjDeRhGeRG61AX8SvFzT2IHXVQO-JrrDV8PUNbmtAfLU2ikW9NUjq315N3p-k8pWFgMCDh5Sif-BEzyRHc;SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5wRY9K.D6usaX6FLKd2QEF5JpX5KMhUgL.FozRehzceK-4So22dJLoI7fSqPiu-cyyUcREehz7;SUHB=0V5kkpNGHLsUQC;ULV=1581843452342:10:10:1:3394628681636.194.1581843452201:1581577252811;un=17766091857;UOR=login.sina.com.cn,s.weibo.com,login.sina.com.cn;wvr=6;WBStorage=42212210b087ca50|undefined;'
}


ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False
REDIRECT_ENABLED = False

# CONCURRENT_REQUESTS = 1

MONGO_URI = "localhost:27017"
MONGO_DB  = '#武汉市委书记回应歧视湖北人#'

CONTINUE_FROM_DB = True
from datetime import datetime
class Params:
   KEYWORD = "#武汉市委书记回应歧视湖北人#"
   START_TIME = datetime(2020, 1, 2, 0)
   END_TIME = datetime(2020, 2, 1, 0)
   PROVINCE_CODE = 0
   CITY_CODE = 0  # city值为0或者1000都是一样的
   SORT_BY = "scope"
   INCLUDE = "suball"

import os
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
log_dir = os.path.join(PROJECT_DIR, 'logs')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

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
