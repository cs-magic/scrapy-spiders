# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyPuPipeline(object):
    def process_item(self, item, spider):
        return item


import os
from urllib.parse import urlparse

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

import requests


class MyFilesPipeline(FilesPipeline):

    def handle_redirect(self, file_url):
        response = requests.head(file_url)
        if response.status_code == 302:
            file_url = response.headers["Location"]
        return file_url

    def get_media_requests(self, item, info):
        for file_ind, file_url in enumerate(item["file_urls"], 1):
            file_url = self.handle_redirect(file_url)
            yield scrapy.Request(file_url, meta={"file_name": "{}_{}".format(item['name'], file_ind)})

    def file_path(self, request, response=None, info=None):
        file_path = '{}.{}'.format(request.meta['file_name'], request.url.split('.')[-1])
        return file_path


class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_ind, image_url in enumerate(item["image_urls"], 1):
            image_url = image_url.split("?", 1)[0]
            yield scrapy.Request(image_url, meta={"image_name": "{}_{}".format(item['name'], image_ind)})

    def file_path(self, request, response=None, info=None):
        image_path = '{}.jpg'.format(request.meta['image_name'])
        return image_path