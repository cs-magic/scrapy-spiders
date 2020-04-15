# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

uri = pymongo.MongoClient()
db = uri['scrapy_douban']
coll_seed =  db['film_seeds']
coll_content = db['film_content']


class ScrapyDoubanPipeline(object):
    def process_item(self, item, spider):
        if item['status'] == 'finished':
            coll_content.insert_one(item)

        coll_seed.update({"_id": item["_id"]}, {"$set": {"status": item['status']}})
        return item
