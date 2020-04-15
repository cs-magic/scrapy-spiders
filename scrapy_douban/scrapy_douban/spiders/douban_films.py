# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
from scrapy.exceptions import CloseSpider

from urllib import parse
from collections import defaultdict
import json


MAX_PAGES = 300

# root_url = 'https://movie.douban.com/tag/?'
root_url = 'https://movie.douban.com/j/new_search_subjects?'

genres_list = ['剧情','喜剧','动作','爱情','科幻','动画','悬疑','惊悚','恐怖','犯罪',
			   '同性','音乐','歌舞','传记','历史','战争','西部','奇幻','冒险','灾难','武侠', '情色']
params = {
	'sort': 'U',
	'range': '0,10', # 评分范围
	'tags': '电影',
	# 'start': '0',
	# 'genres': "剧情"
}

class DoubanFilmsSpider(scrapy.Spider):
	name = 'film_seeds'
	allowed_domains = ['douban.com', 'movie.douban.com']

	result = defaultdict(list)

	def start_requests(self):
		for genres in genres_list:
			for start in range(0, MAX_PAGES, 10):
				params.update({"genres": genres, "start": str(start)})
				target_url = root_url + parse.urlencode(params)

				yield scrapy.Request(target_url, callback=self.parse,
									 meta={"genres": params['genres']})

	def parse(self, response):
		# inspect_response(response, self)
		res = json.loads(response.text)
		if res.get('data'):
			self.result[response.meta['genres']].extend(res['data'])
		elif res.get('msg') == "检测到有异常请求从您的IP发出，请登录再试!":
			raise CloseSpider("IP异常，已关闭程序!")
		else:
			raise Exception(res)


	def close(self, reason):
		result_path = 'result.json'
		json.dump(self.result, open(result_path, "w", encoding="utf-8"),
				  ensure_ascii=False, indent=2)
		self.logger.info("Dumped data into file {}".format(result_path))

