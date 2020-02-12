# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
from scrapy.exceptions import IgnoreRequest, CloseSpider

try:
    from scrapy_weibo_pc.common import *
    from scrapy_weibo_pc.scrapy_weibo_pc.settings import *
except:
    from common import *
    from scrapy_weibo_pc.settings import *



class WeiboPcSpider(scrapy.Spider):
    name = 'weibo_pc'
    allowed_domains = ['s.weibo.com']

    custom_settings = {
        "LOG_LEVEL": logging.DEBUG,
        "DOWNLOAD_DELAY": 0.3,
        'DUPEFILTER_DEBUG': True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if CONTINUE_FROM_DB:
            import pymongo
            self.uri = pymongo.MongoClient(MONGO_URI)
            self.db = self.uri[MONGO_DB]
            self.coll_history = self.db["history"]  # type: pymongo.collection

    def start_requests(self):
        st = Params.START_TIME
        et = Params.END_TIME
        s_date = st.date()
        e_date = et.date()
        days = (e_date - s_date).days
        for day_seq in range(days+1):
            day_start = max(st, datetime.combine(s_date + timedelta(day_seq), datetime.min.time()))
            day_end   = min(et, datetime.combine(s_date + timedelta(day_seq + 1), datetime.min.time()))

            params = [Params.KEYWORD, day_start.year, day_start.month, day_start.day, day_start.hour,
                      24 if day_end.hour == 0 else day_end.hour,
                      Params.PROVINCE_CODE, Params.CITY_CODE, Params.SORT_BY, Params.INCLUDE]
            yield scrapy.Request(get_url_from_params(*params), meta={"params": params, "divisible": True},
                                 errback=self.errback, callback=self.parse)
            # for request in self.yield_from_urls_in_db(params):
            #     yield request

    def start_parse(self, response):
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
                    "_id": card_node.attrib["mid"],  # id字段是后续加载的，放在前面解析会显示一个函数，而非结果
                    "coll": post_time.strftime("%Y-%m-%d"),

                    "content": content,
                    "ref_dict": ref_dict,
                    "poster_dict": poster_dict,
                    "image_urls": image_urls,
                    "post_time": post_time,
                    "statistic": statistic,
                }

        # TODO: 下一次修改一下，在param中加入page参数
        page_at = re.search("page=(\d+)", response.url)
        page_at = int(page_at.group(1)) if page_at else 1

        yield {
            "_id"           : "-".join(map(str, response.meta["params"])),
            "coll"          : "history",
            "page_url"      : response.url,
            "page_at"       : page_at,
            "params"        : response.meta["params"],
            "divisible"     : response.meta["divisible"],
            "finished"      : False if response.css(".next") else True,
        }
        # inspect_response(response, self)

        next_page = response.css(".next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, dont_filter=True, meta=response.meta)

    def parse(self, response):
        page_at = re.search("page=(\d+)", response.url)
        page_at = int(page_at.group(1)) if page_at else 1
        response_dict = dict((i, j) for i, j in response.meta.items() if i in ["params", "divisible", "depth", "download_latency"])
        response_dict.update(page=page_at)
        self.logger.info(response_dict)
        # 首先判断是否超页数，或者是否可分割
        if response.css(".m-page li").__len__() >= 50 and response.meta["divisible"]: # 页数过多，需要分割
            next_params_list = get_next_params_list(*response.meta["params"])
            # 如果还能切割的话
            if next_params_list:
                for next_params in next_params_list:
                    response.meta.update(params=next_params)
                    response_dict.update(type="dividing")
                    yield scrapy.Request(get_url_from_params(*next_params), meta=response.meta)
            # 如果不能继续切割的话
            else:
                response.meta.update(divisible=False)
                response_dict.update(type="indivisible")
                yield scrapy.Request(response.url, meta=response.meta)
        elif "page=" not in response.url:
            # 其次查询数据表的指针项
            _id = "-".join(map(str, response.meta["params"]))
            item = self.coll_history.find_one({"_id": _id})
            # 没有查询到该index页，因为当时就没广度搜录到
            if not item:
                for i in self.start_parse(response):
                    response_dict.update(type="new")
                    yield i
            # 该分录已完成
            elif item["finished"] == True:
                pass
            # 直接跳转到历史页
            else:
                response_dict.update(type="jump")
                yield scrapy.Request("{}&page={}".format(response.url, item["page_at"]),
                                     dont_filter=True, callback=self.parse, errback=self.errback, meta=response.meta)
        else:
            # 直接解析
            for i in self.start_parse(response):
                response_dict.update(type="continue")
                yield i

    def errback(self, failure):
        if failure.check(IgnoreRequest):
            raise CloseSpider("Closed Manually!")


if __name__ == '__main__':
    """
    测试数据库history内的条目是否已经全部更新
    """
    import pymongo
    uri = pymongo.MongoClient()
    db  = uri["口罩"]
    coll = db["history"] # type: pymongo.collection
    id_list = coll.distinct("_id")
    for day in range(1, 32):
        day_str = "口罩-2020-1-{}".format(day)
        assert coll.find({"_id": {"$regex": day_str}}) != []


    def add_sub_dict(*args):
        from collections import defaultdict
        data = defaultdict(dict)
        def extend_param(raw_dict, param):
            if not raw_dict.get(param):
                raw_dict[param] = defaultdict(dict)
            return dict(raw_dict[param])
        for arg in args:
            extend_param(data, arg)
        return data