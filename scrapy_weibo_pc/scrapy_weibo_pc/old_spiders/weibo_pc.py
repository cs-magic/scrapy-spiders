# -*- coding: utf-8 -*-
from urllib import parse
from datetime import datetime, timedelta
import re
import json
import time
import scrapy
from scrapy.exceptions import IgnoreRequest, CloseSpider
from scrapy.shell import inspect_response


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False


def get_last_date_of_this_month(y, m):
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    elif is_leap_year(y) and m == 2:
        return 29
    else:
        return 28

import os
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEIBO_PROVINCE_DICT_PATH = "js/province_dict.json"
province_dict_path = os.path.join(PROJECT_DIR, WEIBO_PROVINCE_DICT_PATH)
p_dict = json.load(open(province_dict_path, "r", encoding="utf-8"))

def split_hour(s_y, s_m, s_d, s_h, e_y, e_m, e_d, e_h, p=0):
    assert s_y <= e_y
    if s_y < e_y:
        # 输入第24小时，微博会自动跳转到次日0小时
        # 理应是x日0小时到x+1日0小时，或x日0小时到x日24小时
        # 但微博在选择框里只提供到23小时，但是程序可以写到24小时，不影响结果
        m_y = (s_y + e_y) // 2
        yield s_y, s_m, s_d, s_h, m_y, 12, 31, 24, p
        yield m_y+1, 1, 1, 0, e_y, e_m, e_d, e_h, p

    else:
        # 以下年份相同
        assert s_m <= e_m
        if s_m < e_m:
            m_m = (s_m + e_m) // 2
            l_d_m_m = get_last_date_of_this_month(s_y, m_m)
            yield s_y, s_m, s_d, s_h, s_y, m_m, l_d_m_m, 24, p
            yield s_y, m_m+1, 1, 0, s_y, e_m, e_d, e_h, p
        else:   # 以下年份、月份相同
            assert s_d <= e_d
            if s_d < e_d:
                m_d = (s_d + e_d) // 2
                yield s_y, s_m, s_d, s_h, s_y, s_m, m_d, 24, p
                yield s_y, s_m, m_d+1, 0, s_y, s_m, e_d, e_h, p
                # 以下年月日均相同，微博的算法是左开右闭,因此m_h不用加一；
                # 前面的加一是为了模式转换
            elif s_h < e_h - 1:
                m_h = (s_h + e_h) // 2
                yield s_y, s_m, s_d, s_h, s_y, s_m, s_d, m_h, p
                yield s_y, s_m, s_d, m_h, s_y, s_m, s_d, e_h, p
            elif p == 0:
                for p_i in p_dict:
                    # 由于在JSON中键是整数的字符串格式，所以要先转化成整数
                    p_i = int(p_i)
                    if p_i != 0:
                        yield s_y, s_m, s_d, s_h, s_y, s_m, s_d, e_h, p_i
            else:
                raise Exception("WOC???????????")


def get_params(keyword, s_y, s_m, s_d, s_h, e_y, e_m, e_d, e_h, p,  sort_by="scope", include="suball"):
    include_set = {"suball", "hasimg", "hasvideo", "hasmusic", "haslink"}
    sort_dict = {
        "typeall": "1",
        "xsort": "hot",
        "scope": "ori",
        "atten": "1",
        "vip": "1",
        "category": "4",
        "viewpoint": "1"
    }
    params = {
        "q": keyword,
        "timescope": "custom:{:d}-{:02d}-{:02d}-{:d}:{:d}-{:02d}-{:02d}-{:d}".format(s_y, s_m, s_d, s_h, e_y, e_m, e_d, e_h),
        "region": "custom:{}:1000".format(p),
        "Refer": "g"
    }
    params[sort_by] = sort_dict[sort_by]
    params[include] = "1"
    return params


def convert_time(post_time: str) -> datetime:
    """
    在微博列表页的消息时间是比较难以精确的，可以点进去看到详细时间，所以本函数只精确到分钟
    :param post_time:
    :return:
    """
    NOW_YEAR = datetime.now().year
    NOW_MONTH = datetime.now().month
    NOW_DAY = datetime.now().day

    def get_cur_time():
        now = datetime.now()
        return datetime(now.year, now.month, now.day, now.hour, now.minute)

    if "年" in post_time:
        match_pattern = re.compile(r'(\d+)年(\d+)月(\d+)日 (\d+):(\d+)')
        return datetime(*map(int, match_pattern.match(post_time).groups()))

    elif "月" in post_time:
        match_pattern = re.compile(r'(\d+)月(\d+)日 (\d+):(\d+)')
        return datetime(NOW_YEAR, *map(int, match_pattern.match(post_time).groups()))

    elif "秒前" in post_time:
        return get_cur_time()

    elif "分钟前"in post_time:
        past_minute = int(re.match("\d+", post_time).group())
        return get_cur_time() - timedelta(minutes=past_minute)

    elif "今天" in post_time:
        hour, minute = map(int, re.match("今天(\d+):(\d+)", post_time).groups())
        return datetime(NOW_YEAR, NOW_MONTH, NOW_DAY, hour, minute)

    else:
        raise Exception("Can't recognize post_time of {}".format(post_time))


class ParseListSpider(scrapy.Spider):
    name = 'weibo_pc'
    allowed_domains = ['s.weibo.com']

    custom_settings = {
        'LOG_LEVEL': "DEBUG",
        "DEPTH_PRIORITY": -1,
        'DOWNLOAD_DELAY': 0.25,
    }

    WEIBO_SEARCH_URL = 'https://s.weibo.com/weibo?'
    MAX_PAGE = 50

    def _wait_page(self, response, now_time=0, MAX_WAIT=10):
        if not response.css(".card-no-result"):
            return True

        time.sleep(1)
        if now_time >= MAX_WAIT:
            raise Exception("Can't load this page {}".format(response.url))
        self.logger.info("Waiting the page loading completely....")
        return self._wait_page(response, now_time+1, MAX_WAIT)

    def _print_page(self, response):
        s_y, s_m, s_d, s_h, e_y, e_m, e_d, e_h, p = response.meta["filters"]
        if s_y == e_y and s_m == e_m and s_d == e_d:
            period_str = "{}/{:2d}/{:2d} {:2d} - {:2d}".format(s_y, s_m, s_d, s_h, e_h)
        else:
            period_str = "{}/{:2d}/{:2d} {:2d} - {}/{:2d}/{:2d} {:2d}".format(*response.meta["filters"])

        page_match = re.search("&page=(\d+)", response.url)
        page_int = int(page_match.group(1)) if page_match else 1
        self.logger.debug("Visiting: {} ({:02d}) [{}], Latency: {:.4f} {}".format(
            period_str, page_int, p_dict[str(p)] if p != 0 else "ALL", response.meta["download_latency"], response.url))

    def _url_from_params(self, params):
        url =  self.WEIBO_SEARCH_URL + parse.urlencode(params)
        # self.logger.debug("Visiting {}".format(url))
        return url

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return cls(
            settings = crawler.settings,
        )

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.keyword = settings["KEYWORD"]

    def start_requests(self):
        for filters in [
            (2020, 1, 1, 0, 2020, 2, 1, 0, 0),
        ]:
            self.logger.debug("Started {}".format(filters))
            params = get_params(self.keyword, *filters)
            yield scrapy.Request(self._url_from_params(params), dont_filter=True, meta={"filters": filters})

    def parse(self, response):
        # self.logger.debug("Parsing page....")
        self._print_page(response)

        # inspect_response(response, self)

        if response.css(".m-page li").__len__() >= self.MAX_PAGE:
            for priority_fade, filters in enumerate(split_hour(*response.meta["filters"])):
                params_child = get_params(self.keyword, *filters)
                # self.logger.info("Have split period from {} to {}".format(response.meta["period"], period_i))
                yield scrapy.Request(self._url_from_params(params_child), meta={"filters": filters},
                                     callback=self.parse, dont_filter=True,
                                     priority=response.request.priority - priority_fade)

        elif response.css(".card-no-result"):
            yield {
                "_id": response.url,
                "coll": "failed",
            }

        else:
            for card_node in response.css("#pl_feedlist_index .card-wrap"):
                # 页面主要部分为pl_feedlist_main，包含作变的pl_feedlist_index和右边的pl_band_index
                card_text_node = card_node.xpath(
                    ".//p[@node-type='feed_list_content_full' or @node-type='feed_list_content']")[-1]
                content = card_text_node.xpath("string(.)").get().strip().strip("收起全文d").strip("\u200b")

                # 在这里存储链接时，不能用 {key: value}的方式，用[{'name': name, 'value': value}]要好
                ref_dict = [{
                    "name": a_node.xpath("string(.)").get(),
                    "href": a_node.attrib["href"],
                    "area": True if a_node.css(".ficon_cd_place") else False,
                } for a_node in card_text_node.css("a")]
                image_urls = card_node.css(".media-piclist img::attr(src)").getall()

                poster_node = card_node.css(".name")[0]
                poster_dict = {
                    "nick_name": poster_node.xpath("@nick-name").get(),
                    "home_page": poster_node.xpath("@href").get(),
                    "avatar": card_node.css(".avator a::attr(href)").get(),
                    "identities": poster_node.xpath("./following-sibling::a/@title").getall(),
                    "platform": card_node.css(".from a:nth-child(2)::text").get()
                }

                post_time = card_node.css(".from a::text").get().strip()
                post_time = convert_time(post_time)

                forward_cnt = int(card_node.css(".card-act li:nth-child(2)").re_first("\d+", 0))
                comment_cnt = int(card_node.css(".card-act li:nth-child(3)").re_first("\d+", 0))
                like_cnt    = int(card_node.css(".card-act li:nth-child(4) em").re_first("\d+", 0))
                statistic   = {
                    "forward_cnt": forward_cnt,
                    "comment_cnt": comment_cnt,
                    "like_cnt": like_cnt
                }

                yield {
                    "_id": card_node.attrib["mid"],  # id字段是后续加载的，放在前面解析会显示一个函数，而非结果
                    "coll": post_time.strftime("%Y-%m-%d"),

                    "content": content,
                    "ref_dict": ref_dict,
                    "poster_dict": poster_dict,
                    "image_urls": image_urls,
                    "post_time": post_time,
                    "statistic": statistic,
                }

            # inspect_response(response, self)

            next_page = response.css(".next::attr(href)").get()
            if next_page:
                yield response.follow(next_page, dont_filter=True, meta=response.meta)
