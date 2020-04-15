# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/3/23 19:52
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmail.com
# ------------------------------------
import json
import pymongo

result_json_path = '../result.json'
data = json.load(open(result_json_path, 'r', encoding='utf-8'))


uri = pymongo.MongoClient()
db = uri['scrapy_douban']
coll = db['film_seeds']

for cat, cat_contents in data.items():
	for item in cat_contents:
		item['category'] = cat
		coll.insert_one(item)