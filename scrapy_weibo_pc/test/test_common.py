# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/12 13:17
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

from scrapy_weibo_pc.common import *


params = ["口罩", 2020, 1, 3, 20, 24, 0, 0, "s1", "s2"]
# params = ('口罩', 2020, 1, 3, 20, 21, '34', 1, 's1', 's2')

def get_all(params):
	items = get_next_params_list(*params)
	if items:
		for item in items:
			# yield item
			yield from get_all(item)
	else:
		yield params

for item in get_all(params):
	print(item)