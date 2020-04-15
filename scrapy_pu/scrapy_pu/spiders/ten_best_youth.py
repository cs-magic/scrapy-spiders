# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response


class TenBestYouthSpider(scrapy.Spider):
    name = 'ten_best_youth'
    allowed_domains = ['nau.pocketuni.net']

    def start_requests(self):
        base_url = 'http://nau.pocketuni.net/index.php?app=event&mod=Front&act=player&id=1865459&p='
        for page in range(1, 6):
            url = base_url + str(page)
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        # inspect_response(response, self)
        for li in response.css('.person_list li'):
            name = li.css('a::attr(title)').get()
            class_ = li.css('.person_list_prov:nth-child(3)::text').get()
            vote = li.css('.person_list_prov:nth-child(4) span::text').get()
            n_photos = li.css('.person_list_prov:nth-child(5) a:nth-child(1) span::text').re_first("\d+")
            n_videos = li.css('.person_list_prov:nth-child(5) a:nth-child(2) span::text').re_first("\d+")
            n_comments = li.css('.person_list_prov:nth-child(5) a:nth-child(3) span::text').re_first("\d+")
            url_photos = li.css('.person_list_prov:nth-child(5) a:nth-child(1)::attr(href)').get()
            img_urls = li.css('img::attr(src)').getall()
            url_videos = li.css('.person_list_prov:nth-child(5) a:nth-child(2)::attr(href)').get()
            url_comments = li.css('.person_list_prov:nth-child(5) a:nth-child(3)::attr(href)').get()
            url_person = li.xpath('.//a/@href').get()

            item = {
                "name": name,
                "class": class_,
                "vote": vote,
                "n_photos": n_photos,
                "n_videos": n_videos,
                "n_comments": n_comments,
                "url_photos": url_photos,
                "url_videos": url_videos,
                "url_comments": url_comments,
                "url_person": url_person,
                "image_urls": img_urls,
            }

            yield response.follow(url_person, callback=self.parse_person, meta={"item": item})

    def parse_person(self, response):
        # inspect_response(response, self)
        item = response.meta['item']
        item["intro"] = "\n".join(response.css('.person_right_dp p::text').getall())
        item["file_urls"] = response.xpath(".//strong/following-sibling::a[1]/@href").getall()
        item["image_urls"].extend(response.css('.person_desc_photo_list img::attr(src)').getall())
        yield item






        pass
