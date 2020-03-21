# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/3/10 17:02
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

# 'followall' is the name of one of the spiders of the project.
process.crawl('weibo_pc')
process.start() # the script will block here until the crawling is finished