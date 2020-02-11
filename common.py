# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/9 1:37
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

import json
import logging

logger_common = logging.getLogger("LOGGER_COMMON")
logger_common.setLevel(logging.DEBUG)


class Cookie:

	@staticmethod
	def cookie_jar2dict(cookie_jar: list) -> dict:
		return dict((i["name"], i["value"]) for i in cookie_jar)

	@staticmethod
	def cookie_jar2str(cookie_jar: list) -> str:
		return "".join(["{}={};".format(i["name"], i["value"]) for i in cookie_jar])

	@staticmethod
	def cookie_dict2str(cookie_dict: dict) -> str:
		return "".join(["{}={};".format(i, j) for i, j in cookie_dict.items()])

	@staticmethod
	def cookie_str2dict(cookie_str: str) -> dict:
		return dict(i.split("=", 1) for i in cookie_str.split(";") if i)


class Json:

	@staticmethod
	def read_json(json_file: str) -> [list, dict]:
		return json.load(open(json_file, "r", encoding="utf-8"))

	@staticmethod
	def save_json(json_data: [list, dict], save_to_path: str) -> None:
		json.dump(json_data, open(save_to_path, "w", encoding="utf-8"),
		          ensure_ascii=False, indent=4)
