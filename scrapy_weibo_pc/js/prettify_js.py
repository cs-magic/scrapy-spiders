# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 21:28
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

from common import Json
#
# Json.save_json(Json.read_json("province_dict.json"), "prettify_province.json")
# Json.save_json(Json.read_json("weiboCityList.json"), "prettify_weiboCityList.json")

city_dict = Json.read_json("prettify_weiboCityList.json")

from collections import defaultdict
city_code_dict = dict()
for province_name, province_dict in city_dict.items():
	city_code_dict[province_dict["code"]] = list(province_dict["city"].values())

Json.save_json(city_code_dict, "weibo_city_code.json")