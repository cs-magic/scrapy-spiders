# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/12 13:12
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------
import os
import re
import json
from datetime import datetime, timedelta
from urllib import parse
try:
    from .scrapy_weibo_pc.settings import PROJECT_DIR
except:
    from scrapy_weibo_pc.settings import PROJECT_DIR


weibo_city_code_dict = json.load(open(os.path.join(PROJECT_DIR, "js/weibo_city_code.json"), "r"))

def get_url_from_params(keyword, y, m, d, sh, eh, p, c, sort_by="scope", include="suball") -> str:
    WEIBO_SEARCH_URL = 'https://s.weibo.com/weibo?'
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
    param_dict = {
        "q": keyword,
        "timescope": "custom:{:d}-{:02d}-{:02d}-{:d}:{:d}-{:02d}-{:02d}-{:d}".format(y, m, d, sh, y, m, d, eh),
        "region": "custom:{}:{}".format(p, c),
        "Refer": "g"
    }
    param_dict[sort_by] = sort_dict[sort_by]
    param_dict[include] = "1"
    return  WEIBO_SEARCH_URL + parse.urlencode(param_dict)

def get_next_params_list(keyword, y, m, d, sh, eh, p, c, sort_by="scope", include="suball"):
    if eh > sh + 1:
        return [(keyword, y, m, d, h, h+1, p, c, sort_by, include) for h in range(sh, eh)]
    elif str(p) == "0":
        return [(keyword, y, m, d, sh, eh, _p, c, sort_by, include) for _p in weibo_city_code_dict.keys() if _p != "0"]
    elif str(c) == "0":
        return [(keyword, y, m, d, sh, eh, p, _c, sort_by, include) for _c in weibo_city_code_dict[str(p)]]
    else:
        return []

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
