# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response

import json
import logging


class DoubanFilmContentSpider(scrapy.Spider):
	name = 'film_content'
	allowed_domains = ['movie.douban.com']
	start_urls = ['http://movie.douban.com/']

	custom_settings = {
		'LOG_LEVEL': 10,
		'DOWNLOAD_TIMEOUT': 20,
		'SPIDER_MIDDLEWARES': {
			'scrapy_douban.middlewares.ScrapyDoubanSpiderMiddleware': 543,
	},
		'ITEM_PIPELINES': {
		'scrapy_douban.pipelines.ScrapyDoubanPipeline': 300,
	},
	}

	def __init__(self):
		super().__init__()
		logging.getLogger("scrapy.core.scraper").setLevel(logging.INFO)



	def parse(self, response):
		# inspect_response(response, self)
		try:
			basic_item = json.loads(response.xpath('.//script[@type="application/ld+json"]/text()').get())
			"""
			['@context', 'name', 'url', 'image', 'director', 'author', 'actor', 'datePublished', 'genre', 'duration', 'description', '@type', 'aggregateRating']
			"""
			tags = response.css('.tags-body a::text').getall()
			duration2 = response.css("#info").xpath("./span[@property='v:runtime']/text()").get()
			area = response.css("#info").xpath('./br[5]/preceding-sibling::text()')[-1].get()
			language = response.css("#info").xpath('./br[6]/preceding-sibling::text()')[-1].get()
			basic_item.update({
				'_id': response.meta['_id'],
				'status': "finished",
				'tags': tags,
				'duration2': duration2,
				'area': area,
				'language': language,
			})
		except:
			basic_item = {"_id": response.meta['_id'], "status": "failed"}
		yield basic_item





