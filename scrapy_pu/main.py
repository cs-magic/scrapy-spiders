# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/3/24 21:58
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmail.com
# ------------------------------------

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings())
process.crawl('ten_best_youth')
process.start()