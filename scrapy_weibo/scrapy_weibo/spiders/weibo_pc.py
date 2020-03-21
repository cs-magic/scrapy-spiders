# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import IgnoreRequest, CloseSpider
from scrapy.shell import inspect_response

import re
from urllib import parse
from datetime import datetime, timedelta


def check_pages(response: scrapy.http.Response) -> int:
    # TODO 这个算法可能并不稳健
    return response.css(".m-page li").__len__()


def get_weibo_url_of_searching_one_date(key, the_date) -> str:
    if isinstance(the_date, datetime):
        the_date = datetime.strftime(the_date, "%Y-%m-%d")
    url = 'https://s.weibo.com/weibo?' \
          'q={key_quoted}&' \
          'scope=ori&' \
          'typeall=1&' \
          'suball=1&' \
          'timescope=custom:{d}-0:{d}-24&' \
          'Refer=g'.format(
        key_quoted = parse.quote(key),
        d = the_date,
    )
    return url

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


def _parse_url(url: str):
    # url_parsed = parse.parse_qs(parse.urlparse(url).query)
    url_parsed = dict(i.split("=", 1) for i in url.split("?")[-1].split("&"))
    url_parsed["q"] = parse.unquote(url_parsed['q'])
    return {"keyword": url_parsed["q"], "timescope": url_parsed["timescope"],
            "region": url_parsed.get("region", "0:0"), "page": url_parsed.get("page", None)}

class WeiboPcSpider(scrapy.Spider):
    name = 'weibo_pc'
    allowed_domains = ['s.weibo.com']

    BASE_URL = 'https://s.weibo.com/weibo'
    KEYWORDS = [
        "#武汉市委书记回应歧视湖北人#"
    ]
    START_DATE = "2020-01-27"
    END_DATE   = "2020-01-29"

    def start_requests(self):
        for key in self.KEYWORDS:
            self.st = datetime.strptime(self.START_DATE, "%Y-%m-%d")
            self.et = datetime.strptime(self.END_DATE,   "%Y-%m-%d")
            for dates_shift in range((self.et - self.st).days + 1):
                the_date = self.st + timedelta(days=dates_shift)
                url = get_weibo_url_of_searching_one_date(key=key, the_date=the_date)
                yield scrapy.Request(url)

    def parse_weibo_page(self, response):
        self.logger.info(_parse_url(response.url))
        # BUG原因之一：切分过细访问到了一些不存在数据的页面，这个时候通过这个.m-error可筛选掉
        # BUG原因之二：因为网络或其他未知原因，导致信息尚未加载出来而报错，这种情况可以通过重新续爬解决
        if not response.css(".m-error"):
            for card_node in response.css("#pl_feedlist_index .card-wrap"):
                # 页面主要部分为pl_feedlist_main，包含作变的pl_feedlist_index和右边的pl_band_index
                """
                下一句在没有爬取到数据的页面时会报错，但**请让它报错**，这样可以终止当时的网络环境，以支持未来续爬
                """
                card_text_node = card_node.xpath(".//p[@node-type='feed_list_content_full' or @node-type='feed_list_content']")[-1]
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

                post_time = convert_time(card_node.css(".from a::text").get().strip())
                statistic = {
                    "forward_cnt": int(card_node.css(".card-act li:nth-child(2)").re_first("\d+", 0)),
                    "comment_cnt": int(card_node.css(".card-act li:nth-child(3)").re_first("\d+", 0)),
                    "like_cnt": int(card_node.css(".card-act li:nth-child(4) em").re_first("\d+", 0))
                }

                yield {
                    "coll": 'data',
                    "_id": card_node.attrib["mid"],  # id字段是后续加载的，放在前面解析会显示一个函数，而非结果
                    "content": content,
                    "ref_dict": ref_dict,
                    "poster_dict": poster_dict,
                    "image_urls": image_urls,
                    "post_time": post_time,
                    "statistic": statistic,
                }

        params = _parse_url(response.url)
        yield {
            "coll": "history",
            **params,
            "_id": re.search("custom:2020-(\d\d-\d\d)", params["timescope"]).group(1),
            "pages": 1,

        }


    def parse(self, response):
        # self.logger.info(_parse_url(response.url))
        # inspect_response(response, self)
        if check_pages(response) == 0:
            new_url = "{}&page={}".format(response.url, 1)
            yield scrapy.Request(new_url, meta=response.meta, callback=self.parse_weibo_page)
        elif "page=" in response.url:
            yield from self.parse_weibo_page(response)
        else:
            for page in range(1, check_pages(response)+1):
                new_url = "{}&page={}".format(response.url, page)
                yield scrapy.Request(new_url, meta=response.meta, callback=self.parse_weibo_page)

            if check_pages(response) == 50:
                self.logger.warning("Pages 50 from {}".format(response.url))